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

from django.conf import settings

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_IPV6
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import *
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import *
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import *


class Ipv6AssociateResource(RestResource):

    log = logging.getLogger('Ipv6AssociateResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests  PUT to insert the relationship between IPv6 and equipment.

        URL: ipv6/<id_ipv6>/equipment/<id_equip>/$
        """
        self.log.info('Associates an IPv6 to a equipament.')

        try:

            ipv6_id = kwargs.get('id_ipv6')
            equip_id = kwargs.get('id_equip')

            # Valid Ipv6 ID
            if not is_valid_int_greater_zero_param(ipv6_id):
                self.log.error(
                    u'The id_ipv6 parameter is not a valid value: %s.', ipv6_id)
                raise InvalidValueError(None, 'id_ipv6', ipv6_id)

            # Valid Ipv6 ID
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'The id_equip parameter is not a valid value: %s.', equip_id)
                raise InvalidValueError(None, 'id_equip', equip_id)

            # Existing Ipv6Equipament ID
            ipv6_equipment = Ipv6Equipament()
            ipv6_equipment.equipamento = Equipamento().get_by_pk(equip_id)

            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.WRITE_OPERATION, None, equip_id, AdminPermission.EQUIP_WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Existing IPv6 ID
            ipv6_equipment.ip = Ipv6().get_by_pk(ipv6_id)

            with distributedlock(LOCK_IPV6 % ipv6_id):

                # Existing IPv6 ID
                ipv6_equipment.validate_ip()

                try:
                    # Existing EquipmentEnvironment
                    if ipv6_equipment.equipamento not in [ea.equipamento
                                                          for ea in ipv6_equipment.ip.networkipv6.vlan.ambiente.equipamentoambiente_set.all()]:
                        ea = EquipamentoAmbiente(
                            ambiente=ipv6_equipment.ip.networkipv6.vlan.ambiente, equipamento=ipv6_equipment.equipamento)
                        ea.save()

                    ipv6_equipment.save()
                except Exception, e:
                    self.log.error(u'Failed to insert a ip_equipamento.')
                    raise IpError(e, u'Failed to insert a ip_equipamento.')

                ipequipamento_map = dict()
                ipequipamento_map['id'] = ipv6_equipment.id
                map = dict()
                map['ip_equipamento'] = ipequipamento_map

                return self.response(dumps_networkapi(map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except IpNotFoundError:
            return self.response_error(119)

        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)

        except IpEquipamentoDuplicatedError:
            return self.response_error(120)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except (IpError, EquipamentoError, GrupoError):
            return self.response_error(1)
