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
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_VIP
from networkapi.exception import EquipmentGroupsNotAuthorizedError
from networkapi.exception import InvalidValueError
from networkapi.exception import RequestVipsNotBeenCreatedError
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.script_utils import ScriptError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsError
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import clone
from networkapi.util import is_valid_int_greater_equal_zero_param
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util.decorators import deprecated


class RequestPriorityResource(RestResource):

    log = logging.getLogger('RequestPriorityResource')

    @deprecated(new_uri='use pool features')
    def handle_put(self, request, user, *args, **kwargs):
        """Treat PUT requests to change reals_priority list of VIP.

        URLs: /vip/<id_vip>/priority/
        """

        self.log.info('Change list the reals_priority to VIP')

        try:

            vip_id = kwargs.get('id_vip')

            # Load XML data
            xml_map, attrs_map = loads(
                request.raw_post_data, ['reals_priority'])

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            vip_map = networkapi_map.get('vip')
            if vip_map is None:
                return self.response_error(3, u'There is no value to the vip tag  of XML request.')

            # User permission
            if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Vip ID
            if not is_valid_int_greater_zero_param(vip_id):
                self.log.error(
                    u'The vip_id parameter is not a valid value: %s.', vip_id)
                raise InvalidValueError(None, 'vip_id', vip_id)

            # Valid reals_prioritys
            reals_prioritys_map = vip_map.get('reals_prioritys')
            if (reals_prioritys_map is not None):

                reals_priority_map = reals_prioritys_map.get('reals_priority')
                if (reals_priority_map is not None):

                    # Valid values ​​of reals_priority
                    for reals_priority in reals_priority_map:
                        if not is_valid_int_greater_equal_zero_param(reals_priority):
                            self.log.error(
                                u'The reals_priority parameter is not a valid value: %s.', reals_priority)
                            raise InvalidValueError(
                                None, 'reals_priority', reals_priority)

                    if len(reals_priority_map) > 0:
                        vip_map = RequisicaoVips.is_valid_values_reals_priority(
                            reals_priority_map)
                    else:
                        self.log.error(
                            u'The reals_priority_map parameter is not a valid value: %s.', reals_priority_map)
                        raise InvalidValueError(
                            None, 'reals_priority_map', reals_priority_map)
                else:
                    self.log.error(
                        u'The reals_priority parameter is not a valid value: %s.', reals_priority_map)
                    raise InvalidValueError(
                        None, 'reals_priority', reals_priority_map)
            else:
                self.log.error(
                    u'The reals_prioritys parameter is not a valid value: %s.', reals_prioritys_map)
                raise InvalidValueError(
                    None, 'reals_prioritys', reals_prioritys_map)

            # Existing Vip ID
            vip = RequisicaoVips.get_by_pk(vip_id)

            with distributedlock(LOCK_VIP % vip_id):

                vip_old = clone(vip)

                # Vip must be created
                if not vip.vip_criado:
                    self.log.error(
                        u'Priority can not be changed because VIP has not yet been created.')
                    raise RequestVipsNotBeenCreatedError(None)

                # Vip equipments permission
                for ip_equipment in vip.ip.ipequipamento_set.all():
                    if not has_perm(user, AdminPermission.VIP_CREATE_SCRIPT, AdminPermission.WRITE_OPERATION, None, ip_equipment.equipamento_id, AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                        self.log.error(
                            u'Groups of equipment registered with the IP of the  VIP request  is not allowed of acess.')
                        raise EquipmentGroupsNotAuthorizedError(None)

                variables_map = vip.variables_to_map()

                # Valid list reals_server
                """if len(variables_map.get('reals').get('real')) != len(vip_map.get('reals_prioritys').get('reals_priority')):
                    self.log.error(u'List the Reals_priority is higher or lower than list the real_server.')
                    return self.response_error(272)"""

                variables_map['reals_prioritys'] = vip_map.get(
                    'reals_prioritys')

                vip.set_variables(variables_map)

                vip.save(user, commit=True)

                # gerador_vips -i <ID_REQUISICAO> --priority
                command = 'gerador_vips -i %d --priority' % vip.id
                code, stdout, stderr = exec_script(command)

                if code == 0:
                    success_map = dict()
                    success_map['codigo'] = '%04d' % code
                    success_map['descricao'] = {
                        'stdout': stdout, 'stderr': stderr}

                    map = dict()
                    map['sucesso'] = success_map
                    return self.response(dumps_networkapi(map))
                else:
                    vip_old.save(user, commit=True)
                    return self.response_error(2, stdout + stderr)

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except ScriptError, s:
            return self.response_error(2, s)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except EquipmentGroupsNotAuthorizedError:
            return self.response_error(271)
        except InvalidValueError, e:
            return self.response_error(332, e.param, e.value)
        except RequestVipsNotBeenCreatedError:
            return self.response_error(270, vip_id)
        except RequisicaoVipsNotFoundError:
            return self.response_error(152)
        except RequisicaoVipsError:
            return self.response_error(1)
