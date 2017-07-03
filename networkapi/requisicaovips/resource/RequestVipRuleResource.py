# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import copy
import logging
import re

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.blockrules.models import BlockRules
from networkapi.blockrules.models import Rule
from networkapi.blockrules.models import RuleContent
from networkapi.exception import AddBlockOverrideNotDefined
from networkapi.exception import InvalidValueError
from networkapi.exception import RequestVipsNotBeenCreatedError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.requisicaovips.models import VipRequestBlockAlreadyInRule
from networkapi.requisicaovips.models import VipRequestNoBlockInRule
from networkapi.rest import RestResource
from networkapi.util import clear_newline_chr
from networkapi.util import convert_string_or_int_to_boolean
from networkapi.util import is_valid_boolean_param
from networkapi.util import is_valid_int_greater_zero_param


class RequestVipRuleResource(RestResource):

    log = logging.getLogger('RequestVipRruleResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to add block in vip rule.

        URLs: /vip/add_block/<id_vip>/<id_block>/<override>
        """

        self.log.info('Add block in rule vip')

        try:
            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations
            id_vip = kwargs.get('id_vip')
            id_block = kwargs.get('id_block')
            override = kwargs.get('override')

            if not is_valid_int_greater_zero_param(id_vip):
                self.log.error(
                    u'Parameter id_vip is invalid. Value: %s.', id_vip)
                raise InvalidValueError(None, 'id_vip', id_vip)

            if not is_valid_int_greater_zero_param(id_block):
                self.log.error(
                    u'Parameter id_block is invalid. Value: %s.', id_block)
                raise InvalidValueError(None, 'id_block', id_block)

            if not is_valid_boolean_param(override, False):
                self.log.error(
                    u'Parameter override is invalid. Value: %s.', override)
                raise InvalidValueError(None, 'override', override)
            else:
                override = convert_string_or_int_to_boolean(override)

            vip = RequisicaoVips.get_by_pk(id_vip)
            vip_map = vip.variables_to_map()
            host = vip_map['host']
            rule_applied = vip.rule_applied

            # Vip must be created
            if not vip.vip_criado:
                self.log.error(
                    u'Block can not added because VIP has not been created yet.')
                raise RequestVipsNotBeenCreatedError(None)

            ###################################################
            #         Vip Request has a rule applied          #
            ###################################################
            if rule_applied:
                block_in_rules = self.insert_block_in_rule(
                    id_block, rule_applied)

                # create new rule
                # make a copy
                new_rule_content = copy.copy(rule_applied)

                # remove the rule if is a vip rule and this rule is not applied
                if vip.rule:
                    if rule_applied != vip.rule and vip.rule.vip:
                        vip.rule.delete()

                # duplicate rule with new block
                new_rule_content.id = None
                new_rule_content.vip = vip
                count_rule_vip = Rule.objects.filter(vip=vip).count()
                diff_name = '(' + str(count_rule_vip) + \
                    ')' if count_rule_vip else ''
                new_rule_content.name = 'regra_' + host + diff_name
                new_rule_content.save(user, force_insert=True)

            ###################################################
            #        Vip Request hasn't a rule applied        #
            ###################################################
            else:
                block_in_rules, environment = self.generate_rule_contents(
                    vip, id_block)

                # create new rule
                new_rule_content = Rule()
                count_rule_vip = Rule.objects.filter(vip=vip).count()
                diff_name = '(' + str(count_rule_vip) + \
                    ')' if count_rule_vip else ''
                new_rule_content.name = 'regra_' + host + diff_name
                new_rule_content.vip = vip
                new_rule_content.environment = environment
                new_rule_content.save()

            new_content = '\n'.join(d['content'] for d in block_in_rules)

            # save contents with new rule
            for i in range(len(block_in_rules)):
                rule_content = RuleContent()
                rule_content.content = block_in_rules[i]['content']
                rule_content.order = i
                rule_content.rule = new_rule_content
                rule_content.save()

            if override or not vip.l7_filter:
                # update filter and rule with new block
                vip.l7_filter = new_content
                vip.rule = new_rule_content
                vip.filter_valid = True
                vip.save()
            else:
                self.log.error(
                    u'Block can not be added because there is already a rule to apply, and the value of zero is overwritten.')
                raise AddBlockOverrideNotDefined(None)

            success_map = dict()
            success_map['codigo'] = 0
            success_map['descricao'] = u'Bloco incluído com sucesso'

            return self.response(dumps_networkapi({'sucesso': success_map}))

        except VipRequestBlockAlreadyInRule, e:
            self.log.error(e.message)
            return self.response_error(361)
        except VipRequestNoBlockInRule, e:
            self.log.error(e.message)
            return self.response_error(362)
        except RequisicaoVipsNotFoundError, e:
            return self.response_error(152)
        except BlockRules.DoesNotExist:
            return self.response_error(359)
        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except AddBlockOverrideNotDefined:
            return self.response_error(371)
        except BaseException, e:
            return self.response_error(1)

    def insert_block_in_rule(self, id_block, rule_applied):
        """
        Insert the specified block in rule.

        @param id_block: Block Identifier to insert.
        @param rule_applied: Rule already appliad in Vip.

        @return: List of dicts with following structure: [{'content_block_id': <block_id>, 'content': <block_content>}].

        @raise VipRequestNoBlockInRule: Rule don't have any block associated.
        @raise VipRequestBlockAlreadyInRule: Block is already in rule.
        """
        block_in_rules = list()
        for content_rule in rule_applied.rulecontent_set.all():

            blocks_envs = BlockRules.objects.filter(
                environment=content_rule.rule.environment)

            is_add = False
            for b in blocks_envs:
                if clear_newline_chr(b.content) == clear_newline_chr(content_rule.content):
                    block_in_rules.append({
                        'content_block_id': b.id,
                        'content': content_rule.content})
                    is_add = True
                    break

            if not is_add:
                block_in_rules.append(
                    {'content_block_id': 0, 'content': content_rule.content})
            # try:
                # content_block = BlockRules.objects.get(content=content_rule.
                # content, environment=content_rule.rule.environment)
                # content_block_id = content_block.id
            # except Exception:
                # Isn't a block, is a custom content
                # pass
            # finally:
                # block_in_rules.append({'content_block_id': content_block_id,
                # 'content': content_rule.content})
        block = BlockRules.objects.get(
            pk=id_block, environment=rule_applied.environment)

        before_block_index = ''
        after_block_index = ''
        for i in range(len(block_in_rules)):
            content_block_id = block_in_rules[i]['content_block_id']

            if block.id == content_block_id:
                raise VipRequestBlockAlreadyInRule(
                    None, 'Block is already in rule')

            if content_block_id != 0:
                # is a block, not a custom content
                if block.id > content_block_id:
                    before_block_index = i
                elif block.id < content_block_id and after_block_index == '':
                    after_block_index = i

        index_to_insert = None

        if before_block_index != '':
            # first block before the new block
            index_to_insert = before_block_index + 1
        elif after_block_index != '':
            # first block after the new block
            index_to_insert = after_block_index

        if index_to_insert is None:
            raise VipRequestNoBlockInRule(
                None, "Rule don't have any block associated.")

        # list.insert(index, object) -- insert object before index
        block_in_rules.insert(
            index_to_insert, {'content_block_id': block.id, 'content': block.content})

        return block_in_rules

    def generate_rule_contents(self, vip, id_block):
        """
        Identifies the blocks in field 'filter applied' of Vip Request and
        generate your rule contents, then insert the new block in the rule.

        @param vip: Vip Request Object
        @param id_block: Block Identifier to insert

        @return: The first param is a list of dicts with following structure: [{'content_block_id': <block_id>, 'content': <block_content>}].
                 The second is the environment.

        @raise VipRequestNoBlockInRule: Rule don't have any block associated.
        @raise VipRequestBlockAlreadyInRule: Block is already in rule.
        """
        has_block_in_filter = False
        filter_applied = vip.filter_applied
        new_rule_content = list()

        if vip.ip is not None:
            environment_v4 = vip.ip.networkipv4.vlan.ambiente
            block_v4 = BlockRules.objects.get(
                pk=id_block, environment=environment_v4)
            blocks_v4 = environment_v4.blockrules_set.all().order_by('order')
            new_rule_content, has_block_in_filter = self.create_rule_by_blocks(
                blocks_v4, filter_applied, block_v4)
            environment = environment_v4

        elif vip.ipv6 is not None:
            environment_v6 = vip.ipv6.networkipv6.vlan.ambiente
            block_v6 = BlockRules.objects.get(
                pk=id_block, environment=environment_v6)
            blocks_v6 = environment_v6.blockrules_set.all().order_by('order')
            new_rule_content, has_block_in_filter = self.create_rule_by_blocks(
                blocks_v6, filter_applied, block_v6)
            environment = environment_v6

        if not has_block_in_filter:
            raise VipRequestNoBlockInRule(
                None, "Rule don't have any block associated.")

        return new_rule_content, environment

    def create_rule_by_blocks(self, blocks, filter_applied, new_block):
        # filter_applied = filter_applied.replace('\n', '')
        # Identifier block in rule_applied and the block to be inserted
        new_blocks_rule = list()
        has_block_in_filter = False
        if clear_newline_chr(new_block.content) in clear_newline_chr(filter_applied):
            raise VipRequestBlockAlreadyInRule(
                None, 'Block is already in rule')
        for block_env in blocks:
            if clear_newline_chr(block_env.content) in clear_newline_chr(filter_applied):
                new_blocks_rule.append(
                    self.create_rule_content_dict(block_env.id, block_env.content))
                has_block_in_filter = True
            elif clear_newline_chr(block_env.content) == clear_newline_chr(new_block.content):
                new_blocks_rule.append(
                    self.create_rule_content_dict(block_env.id, block_env.content))

        if not has_block_in_filter:
            return list(), False

        # Create new rule with your contents
        new_rule_content = list()
        after_index_to_insert_new_rule_content = ''
        after_index_to_insert_old_rule_content = ''
        for i in range(len(new_blocks_rule)):
            # If the block is in rule applied
            if clear_newline_chr(new_blocks_rule[i]['content']) in clear_newline_chr(filter_applied):
                # position of block in filter_applied
                index = filter_applied.index(new_blocks_rule[i]['content'])
                # First block found
                if i == 0:
                    if index == 0:
                        # Do nothing here, it is the first content
                        pass
                    else:
                        # Get all content before it and make a rule content
                        new_rule_content.insert(
                            0, self.create_rule_content_dict(0, filter_applied[0:index]))
                    # Than append the block
                    new_rule_content.append(self.create_rule_content_dict(
                        new_blocks_rule[i]['content_block_id'], new_blocks_rule[i]['content']))
                    # Saves the index to insert the new block after this
                    # content
                    after_index_to_insert_new_rule_content = len(
                        new_rule_content)
                # Last block found
                elif i == (len(new_blocks_rule) - 1):
                    if after_index_to_insert_old_rule_content:
                        # Index to insert the block that already was in
                        # filter_applied after the new block
                        new_rule_content.insert(after_index_to_insert_old_rule_content, self.create_rule_content_dict(
                            new_blocks_rule[i]['content_block_id'], new_blocks_rule[i]['content']))
                    else:
                        # None new block was inserted, just append the block
                        # that already exists
                        new_rule_content.append(self.create_rule_content_dict(
                            new_blocks_rule[i]['content_block_id'], new_blocks_rule[i]['content']))
                    if index + len(new_blocks_rule[i]['content']) == len(filter_applied):
                        # Do nothing, it is the last content
                        pass
                    else:
                        # Get all content after it and make a rule content
                        new_rule_content.append(self.create_rule_content_dict(
                            0, filter_applied[index + len(new_blocks_rule[i]['content']):len(filter_applied)]))
                else:
                    # Than append the block
                    new_rule_content.append(self.create_rule_content_dict(
                        new_blocks_rule[i]['content_block_id'], new_blocks_rule[i]['content']))
                    # Saves the index to insert the new block after this
                    # content
                    after_index_to_insert_new_rule_content = len(
                        new_rule_content)
                    after_index_to_insert_old_rule_content = len(
                        new_rule_content)

            else:
                # if a block was inserted before, then it has the index to
                # insert after
                if after_index_to_insert_new_rule_content:
                    # Insert new block after the last block found
                    new_rule_content.insert(after_index_to_insert_new_rule_content, self.create_rule_content_dict(
                        new_blocks_rule[i]['content_block_id'], new_blocks_rule[i]['content']))
                    # if isn't the last block
                    if i != (len(new_blocks_rule) - 1):
                        # Get all content after the last block and before the
                        # next content block make a rule content
                        start = filter_applied.index(new_rule_content[after_index_to_insert_new_rule_content - 1][
                                                     'content']) + len(new_rule_content[after_index_to_insert_new_rule_content - 1]['content'])
                        end = filter_applied.index(
                            new_blocks_rule[i + 1]['content'])
                        content = filter_applied[start:end]
                        if content.strip():
                            new_rule_content.append(
                                self.create_rule_content_dict(0, content))
                    else:
                        # Get all content after the last block and make a rule
                        # content
                        start = filter_applied.index(new_rule_content[after_index_to_insert_new_rule_content - 1][
                                                     'content']) + len(new_rule_content[after_index_to_insert_new_rule_content - 1]['content'])
                        end = len(filter_applied)
                        new_rule_content.append(
                            self.create_rule_content_dict(0, filter_applied[start:end]))
                else:
                    # if isnt the last block
                    if i != (len(new_blocks_rule) - 1):
                        # Insert new block before the first block found
                        new_rule_content.insert(0, self.create_rule_content_dict(
                            0, filter_applied[0:filter_applied.index(new_blocks_rule[i + 1]['content'])]))
                        new_rule_content.append(self.create_rule_content_dict(
                            new_blocks_rule[i]['content_block_id'], new_blocks_rule[i]['content']))
                        # Index to insert the rule content thas already exists
                        # in rule_applied
                        after_index_to_insert_old_rule_content = len(
                            new_rule_content)

        return new_rule_content, True

    def create_rule_content_dict(self, block_id, block_content):
        # Remove break lines in the beginning and end of string
        block_content = re.sub('\\n$', '', block_content)
        block_content = re.sub('^\\n', '', block_content)
        return {'content_block_id': block_id, 'content': block_content.strip()}
