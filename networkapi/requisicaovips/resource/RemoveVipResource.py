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
from networkapi.requisicaovips.models import VipPortToPool
from networkapi.rest import RestResource
from networkapi.settings import VIP_REMOVE
from networkapi.util import is_valid_int_greater_zero_param


class RemoveVipResource(RestResource):

    log = logging.getLogger('RemoveVipResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST requests to run remove script for vip

        URL: vip/remove/
        """

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VIP_REMOVE_SCRIPT, AdminPermission.WRITE_OPERATION):
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
                msg = u'There is no value to the vlan tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            vip_id = vip_map.get('id_vip')

            # Valid vip ID
            if not is_valid_int_greater_zero_param(vip_id):
                self.log.error(
                    u'Parameter id_vip is invalid. Value: %s.', vip_id)
                raise InvalidValueError(None, 'id_vip', vip_id)

            map = dict()

            # Vip must exists in database
            vip = RequisicaoVips.get_by_pk(vip_id)

            with distributedlock(LOCK_VIP % vip_id):

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
                if not vip.vip_criado:
                    return self.response_error(322, vip_id)

                # Business Rules

                # Make command
                command = VIP_REMOVE % (vip.id)

                # Execute command
                code, stdout, stderr = exec_script(command)
                if code == 0:

                    success_map = dict()
                    success_map['codigo'] = '%04d' % code
                    success_map['descricao'] = {
                        'stdout': stdout, 'stderr': stderr}

                    vip.vip_criado = 0
                    vip.save()

                    # SYNC_VIP
                    old_to_new(vip)

                    # Marks the server pool as not created if the
                    # server pool is not used in another already created vip
                    # request
                    server_pools = ServerPool.objects.filter(
                        vipporttopool__requisicao_vip=vip.id)

                    for server_pool in server_pools:
                        # Checks if server pool is still used in another
                        # created vip request
                        server_pools_still_used = VipPortToPool.objects.filter(
                            server_pool=server_pool).exclude(requisicao_vip=vip.id)
                        vip_with_server_pool_is_created = 0
                        for server_pool_still_used in server_pools_still_used:
                            if server_pool_still_used.requisicao_vip.vip_criado:
                                vip_with_server_pool_is_created = 1

                        if not vip_with_server_pool_is_created and server_pool.pool_created:
                            server_pool.pool_created = 0
                            server_pool.save()

                        map['sucesso'] = success_map

                else:
                    return self.response_error(2, stdout + stderr)

                # Return XML
                return self.response(dumps_networkapi(map))

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
