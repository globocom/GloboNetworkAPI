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
from networkapi.exception import EquipmentGroupsNotAuthorizedError
from networkapi.exception import InvalidValueError
from networkapi.exception import RequestVipsNotBeenCreatedError
from networkapi.grupo.models import GrupoError
from networkapi.healthcheckexpect.models import HealthcheckExpectError
from networkapi.healthcheckexpect.models import HealthcheckExpectNotFoundError
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.script_utils import ScriptError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotFoundByEquipAndVipError
from networkapi.requisicaovips.models import InvalidAmbienteValueError
from networkapi.requisicaovips.models import InvalidBalAtivoValueError
from networkapi.requisicaovips.models import InvalidCacheValueError
from networkapi.requisicaovips.models import InvalidClienteValueError
from networkapi.requisicaovips.models import InvalidFinalidadeValueError
from networkapi.requisicaovips.models import InvalidHealthcheckTypeValueError
from networkapi.requisicaovips.models import InvalidHealthcheckValueError
from networkapi.requisicaovips.models import InvalidHostNameError
from networkapi.requisicaovips.models import InvalidMaxConValueError
from networkapi.requisicaovips.models import InvalidMetodoBalValueError
from networkapi.requisicaovips.models import InvalidPersistenciaValueError
from networkapi.requisicaovips.models import InvalidPriorityValueError
from networkapi.requisicaovips.models import InvalidRealValueError
from networkapi.requisicaovips.models import InvalidServicePortValueError
from networkapi.requisicaovips.models import InvalidTimeoutValueError
from networkapi.requisicaovips.models import InvalidTransbordoValueError
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsError
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import clone
from networkapi.util import is_valid_int_greater_zero_param


class RequestPersistenceResource(RestResource):

    log = logging.getLogger(__name__)

    def handle_put(self, request, user, *args, **kwargs):
        """
        Handles PUT requests to change the VIP's persistence.

        URL: vip/<id_vip>/persistence
        """

        self.log.info("Change VIP's persistence")

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Vip ID
            vip_id = kwargs.get('id_vip')
            if not is_valid_int_greater_zero_param(vip_id):
                self.log.error(
                    u'The vip_id parameter is not a valid value: %s.', vip_id)
                raise InvalidValueError(None)

            # Existing Vip ID
            vip = RequisicaoVips.get_by_pk(vip_id)

            with distributedlock(LOCK_VIP % vip_id):

                vip_old = clone(vip)

                # Vip must be created
                if not vip.vip_criado:
                    self.log.error(
                        u'Persistence can not be changed because VIP has not yet been created.')
                    raise RequestVipsNotBeenCreatedError(None)

                # Vip equipments permission
                if vip.ip is not None:
                    for ip_equipment in vip.ip.ipequipamento_set.all():
                        if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT, AdminPermission.WRITE_OPERATION, None, ip_equipment.equipamento_id, AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                            self.log.error(
                                u'Groups of equipment registered with the IP of the  VIP request  is not allowed of acess.')
                            raise EquipmentGroupsNotAuthorizedError(None)

                if vip.ipv6 is not None:
                    for ip_equipment in vip.ipv6.ipv6equipament_set.all():
                        if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT, AdminPermission.WRITE_OPERATION, None, ip_equipment.equipamento_id, AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION):
                            self.log.error(
                                u'Groups of equipment registered with the IP of the  VIP request  is not allowed of acess.')
                            raise EquipmentGroupsNotAuthorizedError(None)

                # Business Validations

                # Load XML data
                xml_map, attrs_map = loads(request.raw_post_data)

                # XML data format
                networkapi_map = xml_map.get('networkapi')
                if networkapi_map is None:
                    return self.response_error(3, u'There is no value to the networkapi tag of XML request.')
                vip_map = networkapi_map.get('vip')
                if vip_map is None:
                    return self.response_error(3, u'There is no value to the vip tag of XML request.')

                # Get variables
                variables_map = vip.variables_to_map()

                # validation of persistence type is doing by set_variables
                persistence = vip_map.get('persistencia', None)
                variables_map['persistencia'] = persistence

                # Set variables
                vip.set_variables(variables_map)

                # Save VIP
                vip.save(user, commit=True)

                # SYNC_VIP
                old_to_new(vip)

                # Executar script

                # gerador_vips -i <ID_REQUISICAO> --healthcheck
                command = 'gerador_vips -i %d --persistence' % vip.id
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
        except EquipmentGroupsNotAuthorizedError:
            return self.response_error(271)
        except RequestVipsNotBeenCreatedError:
            return self.response_error(270, vip_id)
        except InvalidValueError, e:
            return self.response_error(332, e.param, e.value)
        except HealthcheckExpectNotFoundError:
            return self.response_error(124)
        except RequisicaoVipsNotFoundError:
            return self.response_error(152)
        except InvalidFinalidadeValueError:
            return self.response_error(125)
        except InvalidClienteValueError:
            return self.response_error(126)
        except InvalidAmbienteValueError:
            return self.response_error(127)
        except InvalidCacheValueError:
            return self.response_error(128)
        except InvalidMetodoBalValueError:
            return self.response_error(131)
        except InvalidPersistenciaValueError:
            return self.response_error(132)
        except InvalidHealthcheckTypeValueError:
            return self.response_error(133)
        except InvalidPriorityValueError:
            return self.response_error(325)
        except InvalidHealthcheckValueError:
            return self.response_error(134)
        except InvalidTimeoutValueError:
            return self.response_error(135)
        except InvalidHostNameError:
            return self.response_error(136)
        except InvalidMaxConValueError:
            return self.response_error(137)
        except InvalidServicePortValueError, e:
            porta = 'nulo'
            if e.message is not None:
                porta = e.message
            return self.response_error(138, porta)
        except InvalidRealValueError, e:
            real = 'nulo'
            if e.message is not None:
                real = e.message
            return self.response_error(151, real)
        except InvalidBalAtivoValueError:
            return self.response_error(129)
        except InvalidTransbordoValueError, e:
            transbordo = 'nulo'
            if e.message is not None:
                transbordo = e.message
            return self.response_error(130, transbordo)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except IpNotFoundByEquipAndVipError:
            return self.response_error(334, e.message)
        except (RequisicaoVipsError, EquipamentoError, IpError, HealthcheckExpectError, GrupoError), e:
            return self.response_error(1)
