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
import logging

from django.db.models import Q

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.blockrules.models import Rule
from networkapi.exception import EnvironmentVipError
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.exception import OptionVipError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.requisicaovips.models import OptionVip
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class RequestVipGetRulesByEVipResource(RestResource):

    log = logging.getLogger('RequestVipGetRulesByEVipResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all rules by Environment Vip.

        URL: environment-vip/get/rules/<id_evip>
        """

        try:

            self.log.info('GET to list all the Rules by Environment Vip.')

            # User permission
            if not has_perm(user, AdminPermission.VIPS_REQUEST, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_environment_vip = kwargs.get('id_evip')
            id_vip = kwargs.get('id_vip')

            # Valid Environment VIP ID
            if not is_valid_int_greater_zero_param(id_environment_vip):
                self.log.error(
                    u'The id_environment_vip parameter is not a valid value: %s.', id_environment_vip)
                raise InvalidValueError(
                    None, 'id_environment_vip', id_environment_vip)

            # Find Environment VIP by ID to check if it exist
            environment_vip = EnvironmentVip.get_by_pk(id_environment_vip)

            envs = list()

            for net4 in environment_vip.networkipv4_set.all():
                if net4.vlan.ambiente.id not in envs:
                    envs.append(net4.vlan.ambiente.id)

            for net6 in environment_vip.networkipv6_set.all():
                if net6.vlan.ambiente.id not in envs:
                    envs.append(net6.vlan.ambiente.id)

            if id_vip:
                if not is_valid_int_greater_zero_param(id_vip):
                    self.log.error(
                        u'Parameter id_vip is invalid. Value: %s.', id_vip)
                    raise InvalidValueError(None, 'id_vip', id_vip)

                vip = RequisicaoVips.get_by_pk(id_vip)
                rules = Rule.objects.filter(environment__id__in=envs).filter(
                    Q(vip=vip) | Q(vip=None))
            else:
                rules = Rule.objects.filter(environment__id__in=envs, vip=None)

            rules_dict = dict()
            rules_list = []

            rules_list.append({'id': u'', 'name_rule_opt': u''})

            for rule in rules:
                rules_dict['name_rule_opt'] = rule.name
                rules_dict['id'] = rule.id
                rules_list.append(rules_dict)
                rules_dict = dict()

            return self.response(dumps_networkapi({'name_rule_opt': rules_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except EnvironmentVipNotFoundError:
            return self.response_error(283)

        except (OptionVipError, EnvironmentVipError):
            return self.response_error(1)
