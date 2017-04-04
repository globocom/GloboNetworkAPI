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
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_EQUIPMENT_ENVIRONMENT
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.equipamento.models import EquipamentoAmbienteNotFoundError
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.ip.models import IpCantBeRemovedFromVip
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotFoundError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class EquipmentEnvironmentDeallocateResource(RestResource):

    log = logging.getLogger('EquipmentEnvironmentDeallocateResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat Delete requests to remove related Equipment and  Environment

        URL: equipment/<id_equip>/environment/<id_amb>/
        """

        self.log.info('Remove EquipmentEnvironment by id')

        try:

            # Business Validations

            id_equipment = kwargs.get('id_equipment')
            id_environment = kwargs.get('id_environment')

            if not is_valid_int_greater_zero_param(id_equipment):
                self.log.error(
                    u'Parameter id_equipment is invalid. Value: %s.', id_equipment)
                raise InvalidValueError(None, 'id_equipment', id_equipment)

            if not is_valid_int_greater_zero_param(id_environment):
                self.log.error(
                    u'Parameter id_environment is invalid. Value: %s.', id_environment)
                raise InvalidValueError(None, 'id_environment', id_environment)

            # Find Equipment by ID to check if it exist
            Equipamento.get_by_pk(id_equipment)

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, id_equipment, AdminPermission.EQUIP_WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Find Environment by ID to check if it exist
            environment = Ambiente.get_by_pk(id_environment)

            with distributedlock(LOCK_EQUIPMENT_ENVIRONMENT % id_environment):
                """
                equip_env = EquipamentoAmbiente().get_by_equipment_environment(
                    id_equipment, id_environment)

                is_error = False
                ipv4_error = ""
                ipv6_error = ""

                for ipequip in equip_env.equipamento.ipequipamento_set.all():

                    if ipequip.ip.networkipv4.vlan.ambiente.id == int(id_environment):
                        try:
                            ip = ipequip.ip
                            ipequip.remove(user, ip.id, ipequip.equipamento.id)
                        except IpCantBeRemovedFromVip, e:
                            is_error = True
                            ipv4_error += " %s.%s.%s.%s - Vip %s ," % (
                                ip.oct1, ip.oct2, ip.oct3, ip.oct4, e.cause)

                for ipequip in equip_env.equipamento.ipv6equipament_set.all():

                    if ipequip.ip.networkipv6.vlan.ambiente.id == int(id_environment):
                        try:
                            ip = ipequip.ip
                            ipequip.remove(user, ip.id, ipequip.equipamento.id)
                        except IpCantBeRemovedFromVip, e:
                            is_error = True
                            ipv6_error += " %s:%s:%s:%s:%s:%s:%s:%s - Vip %s ," % (
                                ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8, e.cause)

                if is_error:
                    return self.response_error(336, environment.show_environment(), ipv4_error, ipv6_error)

                # Remove Equipment - Environment
                """
                EquipamentoAmbiente.remove(user, id_equipment, id_environment)

                return self.response(dumps_networkapi({}))

        except EquipamentoNotFoundError, e:
            return self.response_error(117, id_equipment)

        except AmbienteNotFoundError, e:
            return self.response_error(112)

        except EquipamentoAmbienteNotFoundError, e:
            return self.response_error(320)

        except IpNotFoundError, e:
            return self.response_error(119)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except (EquipamentoError, AmbienteError, IpError), e:
            return self.response_error(1)
