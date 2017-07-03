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

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpEquipamento
from networkapi.ip.models import IpEquipmentNotFoundError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import Ipv6Equipament
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class IPGetByEquipResource(RestResource):

    log = logging.getLogger('IPGetByEquipResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to get a ipv4 and ipv6 of determined Equip.

        URLs: ip/getbyequip/id_equip
        """

        try:
            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Valid id access
            id_equip = kwargs.get('id_equip')

            if not is_valid_int_greater_zero_param(id_equip):
                raise InvalidValueError(None, 'id_equip', id_equip)

            # Business Rules
            listadeIps6 = []
            listaDeIps4 = []

            equip = Equipamento.get_by_pk(id_equip)

            ipEquip = IpEquipamento()
            ips = ipEquip.list_by_equip(equip.id)

            for ip4 in ips:
                listaDeIps4.append(Ip.get_by_pk(ip4.ip.id))

            ips = Ipv6Equipament.list_by_equip(equip.id)

            for ip6 in ips:
                listadeIps6.append(Ipv6.get_by_pk(ip6.ip.id))

            network_map = dict()

            list_ips = []
            list_ip4 = []
            list_ip6 = []

            dict_ips = dict()
            ip4_maps = dict()
            ip6_maps = dict()

            for ip4 in listaDeIps4:

                ip4_maps['id'] = ip4.id
                ip4_maps['oct1'] = ip4.oct1
                ip4_maps['oct2'] = ip4.oct2
                ip4_maps['oct3'] = ip4.oct3
                ip4_maps['oct4'] = ip4.oct4
                ip4_maps['descricao'] = ip4.descricao
                ip4_maps['id_rede'] = ip4.networkipv4_id
                list_ip4.append(ip4_maps)
                ip4_maps = dict()

            for ip6 in listadeIps6:

                ip6_maps['id'] = ip6.id
                ip6_maps['block1'] = ip6.block1
                ip6_maps['block2'] = ip6.block2
                ip6_maps['block3'] = ip6.block3
                ip6_maps['block4'] = ip6.block4
                ip6_maps['block5'] = ip6.block5
                ip6_maps['block6'] = ip6.block6
                ip6_maps['block7'] = ip6.block7
                ip6_maps['block8'] = ip6.block8
                ip6_maps['descricao'] = ip6.description
                ip6_maps['id_rede'] = ip6.networkipv6_id
                list_ip6.append(ip6_maps)
                ip6_maps = dict()

            dict_ips['ipv4'] = list_ip4
            dict_ips['ipv6'] = list_ip6
            list_ips.append(dict_ips)

            network_map['ips'] = list_ips

            # Return XML
            return self.response(dumps_networkapi(network_map))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError:
            return self.response_error(150, 'IP %s not registered ' % id_equip)
        except EquipamentoNotFoundError:
            return self.response_error(117)
        except IpEquipmentNotFoundError, e:
            return self.response_error(150, e.message)
        except (IpError, EquipamentoError):
            return self.response_error(1)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
