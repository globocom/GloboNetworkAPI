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
import commands
import logging
import re

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import EquipmentGroupsNotAuthorizedError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource

logger = logging.getLogger('VlanApplyAcl')


class Enum(set):

    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError


EXTENTION_FILE = '.txt'

DIVISON_DC = Enum(['FE', 'BE', 'DEV_QA_FE', 'DEV_QA',
                   'BORDA', 'BE_POP_SP', 'FE_POP_SP', 'BORDA_POP_SP'])

ENVIRONMENT_LOGICAL = Enum(
    ['APLICATIVOS', 'PORTAL', 'HOMOLOGACAO', 'PRODUCAO', 'BORDA'])

NETWORK_TYPES = Enum(['v4', 'v6'])


def hexa(x): return hex(x)[2:]


class VlanApplyAcl(RestResource):

    log = logging.getLogger('VlanApplyAcl')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST requests to APPLY ACL in a vlan

        URL: vlan/apply/acl
        """

        self.log.info('Apply ACL Vlan')
        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.ACL_APPLY, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(
                request.raw_post_data, ['searchable_columns', 'asorting_cols'])

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            vlan_map = networkapi_map.get('vlan')
            if vlan_map is None:
                msg = u'There is no value to the vlan tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            equipments = vlan_map.get('equipments')
            vlan = vlan_map.get('vlan')
            environment = vlan_map.get('environment')
            network = vlan_map.get('network')

            key_acl = 'acl_file_name' if network == NETWORK_TYPES.v4 else 'acl_file_name_v6'

            acl = self.check_name_file(vlan[key_acl])

            path = self.path_acl(environment['nome_ambiente_logico'], environment['nome_divisao'],
                                 environment['acl_path'])

            if path == DIVISON_DC.BORDA:
                path = 'Borda'

            name_equipaments = ''
            for equip in equipments:

                if not isinstance(equipments, list):
                    equip = equipments

                # User permission
                if not has_perm(user, AdminPermission.ACL_APPLY, AdminPermission.WRITE_OPERATION, None, equip.get('equipamento').get('id'), AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                    self.log.error(
                        u'Groups of equipment registered with the IP of the  VIP request  is not allowed of acess.')
                    raise EquipmentGroupsNotAuthorizedError(None)

                equip = equip.get('equipamento').get('nome')

                if not equip in name_equipaments:

                    if not isinstance(equipments, list):
                        name_equipaments += '%s' % equip
                    else:
                        if equip == equipments[0].get('equipamento').get('nome'):
                            name_equipaments += '%s' % equip
                        else:
                            name_equipaments += ',%s' % equip

            # Script
            (erro, result) = commands.getstatusoutput(
                '/usr/bin/backuper -T acl -b %s/%s -e -i %s -w 300' % (path, acl, name_equipaments))

            if erro:
                logger.error('Erro quando o usuário %s tentou aplicar ACL %s no equipamentos: %s erro: %s' % (
                    user.nome, acl, equipments, result))
                erro = False

            for equip in equipments:
                logger.info('%s aplicou a ACL %s no Equipamento:%s' %
                            (user.nome, acl, equip))

            vlan_map = dict()
            vlan_map['is_apply'] = erro
            vlan_map['result'] = result

            return self.response(dumps_networkapi(vlan_map))

        except EquipmentGroupsNotAuthorizedError:
            return self.response_error(271)
        except Exception, e:
            logger.error('Erro quando o usuário %s tentou aplicar ACL %s no equipamentos: %s' % (
                user.nome, acl, equipments))
            logger.error(e)
            raise Exception(e)
        except BaseException, e:
            return self.response_error(1)

    def check_name_file(self, acl_file_name, extention=True):
        """Validates the filename do acl has point and space and adds extension

        @param acl_file_name: name is validaded
        @param extention: True case add extention
        """
        acl = ''
        for caracter in acl_file_name:
            if ((caracter == '.') or (caracter == ' ')):
                pass
            else:
                acl += caracter

        if extention is True:
            acl = acl + EXTENTION_FILE

        return acl

    def path_acl(self, environment_logical, divison_dc, acl_path=None):
        """Creates the path depending on the parameters of environment

        @param environment_logical: environment logical
        @param divison_dc: divison dc
        """
        path = divison_dc

        if environment_logical == ENVIRONMENT_LOGICAL.HOMOLOGACAO:

            if divison_dc == DIVISON_DC.FE:
                path = DIVISON_DC.DEV_QA_FE

            else:
                path = DIVISON_DC.DEV_QA

        elif environment_logical == ENVIRONMENT_LOGICAL.PRODUCAO:

            if divison_dc == self.replace_to_correct(DIVISON_DC.BE_POP_SP):
                path = self.replace_to_correct(DIVISON_DC.BE_POP_SP)

            elif divison_dc == self.replace_to_correct(DIVISON_DC.FE_POP_SP):
                path = self.replace_to_correct(DIVISON_DC.FE_POP_SP)

        elif environment_logical == ENVIRONMENT_LOGICAL.BORDA:

            if divison_dc == self.replace_to_correct(DIVISON_DC.BORDA_POP_SP):
                path = self.replace_to_correct(DIVISON_DC.BORDA_POP_SP)
            else:
                path = divison_dc

        if path == DIVISON_DC.BORDA:
            path = 'Borda'

        if acl_path:
            path = acl_path

        return path

    def replace_to_correct(self, value):
        return value.replace('_', '-')
