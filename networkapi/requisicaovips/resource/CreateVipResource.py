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
from __future__ import with_statement

import logging

from networkapi.admin_permission import AdminPermission
from networkapi.api_vip_request.syncs import old_to_new
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_VIP
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.healthcheckexpect.models import HealthcheckExpectError
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.script_utils import ScriptError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import IpError
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsError
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.requisicaovips.models import ServerPool
from networkapi.rest import RestResource
from networkapi.settings import VIP_CREATE
from networkapi.util import is_valid_int_greater_zero_param


class CreateVipResource(RestResource):

    log = logging.getLogger('CreateVipResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST requests to run script creation for vip

        URL: vip/create/
        """

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VIP_CREATE_SCRIPT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            vip_map = networkapi_map.get('vip')
            if vip_map is None:
                msg = u'There is no value to the vip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            vip_id = vip_map.get('id_vip')

            return self.__create_vip(vip_id, user)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EquipamentoNotFoundError, e:
            return self.response_error(117)
        except RequisicaoVipsNotFoundError, e:
            return self.response_error(152)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
        except ScriptError, s:
            return self.response_error(2, s)
        except (RequisicaoVipsError, GrupoError, HealthcheckExpectError, EquipamentoError, IpError):
            return self.response_error(1)

    def __create_vip(self, vip_id, user):

                # Valid vip ID
        if not is_valid_int_greater_zero_param(vip_id):
            self.log.error(u'Parameter id_vip is invalid. Value: %s.', vip_id)
            raise InvalidValueError(None, 'id_vip', vip_id)

        with distributedlock(LOCK_VIP % vip_id):

            # Vip must exists in database
            vip = RequisicaoVips.get_by_pk(vip_id)

            # Equipment permissions
            if vip.ip is not None:
                for ip_equipment in vip.ip.ipequipamento_set.all():
                    if not has_perm(user, AdminPermission.VIP_CREATE_SCRIPT, AdminPermission.WRITE_OPERATION, None, ip_equipment.equipamento_id, AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                        return self.not_authorized()

            if vip.ipv6 is not None:
                for ip_equipment in vip.ipv6.ipv6equipament_set.all():
                    if not has_perm(user, AdminPermission.VIP_CREATE_SCRIPT, AdminPermission.WRITE_OPERATION, None, ip_equipment.equipamento_id, AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                        return self.not_authorized()

            # Must be validated
            if not vip.validado:
                return self.response_error(191, vip_id)

            # Must be created
            if vip.vip_criado:
                return self.response_error(192, vip_id)

            # Business Rules

            # Make command
            command = VIP_CREATE % (vip.id)

            # Execute command
            code, stdout, stderr = exec_script(command)
            if code == 0:

                success_map = dict()
                success_map['codigo'] = '%04d' % code
                success_map['descricao'] = {'stdout': stdout, 'stderr': stderr}

                vip.rule_applied = vip.rule
                vip.filter_applied = vip.l7_filter

                vip.l7_filter = None
                vip.rule = None
                vip.filter_valid = False

                vip.vip_criado = 1
                vip.save()

                # SYNC_VIP
                old_to_new(vip)

                server_pools = ServerPool.objects.filter(
                    vipporttopool__requisicao_vip=vip.id)

                for server_pool in server_pools:
                    if not server_pool.pool_created:
                        server_pool.pool_created = 1
                        server_pool.save()

                map = dict()
                map['sucesso'] = success_map

            else:
                return self.response_error(2, stdout + stderr)

            # Return XML
            return self.response(dumps_networkapi(map))

    def handle_put(self, request, user, *args, **kwargs):
        """Trata as requisições de PUT para atualizar/criar uma requisição de VIP.

        URLs: vip/<id_vip>/, vip/<id_vip>/criar/
        """
        try:
            vip_id = kwargs.get('id_vip')

            if vip_id is None:
                return self.response_error(243)

            return self.__create_vip(vip_id, user)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except (RequisicaoVipsNotFoundError):
            return self.response_error(152)
        except (RequisicaoVipsError, GrupoError, HealthcheckExpectError, EquipamentoError, IpError):
            return self.response_error(1)
