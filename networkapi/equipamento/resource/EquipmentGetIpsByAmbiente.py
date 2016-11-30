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
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import EnvironmentEnvironmentVip
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource


class EquipmentGetIpsByAmbiente(RestResource):

    log = logging.getLogger('EquipmentFindResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles POST requests to find all Equipments by search parameters.

        URLs: /equipment/find/
        """

        self.log.info('Find all Equipments')

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Get data from URL GET parameters
            equip_name = kwargs.get('equip_name').strip()
            id_ambiente = kwargs.get('id_ambiente')

            # Business Rules

            # Start with alls
            ambiente = Ambiente.get_by_pk(id_ambiente)
            # Get Equipment
            equip = Equipamento.get_by_name(equip_name)

            lista_ips_equip = set()
            lista_ipsv6_equip = set()

            environment_vip_list = EnvironmentVip.get_environment_vips_by_environment_id(
                id_ambiente)
            environment_list_related = EnvironmentEnvironmentVip.get_environment_list_by_environment_vip_list(
                environment_vip_list)

            # # Get all IPV4's Equipment
            for environment in environment_list_related:
                for ipequip in equip.ipequipamento_set.select_related('ip', 'networkipv4', 'vlan').all():
                    network_ipv4 = ipequip.ip.networkipv4
                    if network_ipv4.vlan.ambiente == environment:
                        lista_ips_equip.add(ipequip.ip)

            # # Get all IPV6's Equipment
            for environment in environment_list_related:
                for ipequip in equip.ipv6equipament_set.select_related('ip', 'networkipv6', 'vlan').all():
                    network_ipv6 = ipequip.ip.networkipv6
                    if network_ipv6.vlan.ambiente == environment:
                        lista_ipsv6_equip.add(ipequip.ip)

            # lists and dicts for return
            lista_ip_entregue = list()
            lista_ip6_entregue = list()

            for ip in lista_ips_equip:
                dict_ips4 = dict()
                dict_network = dict()

                dict_ips4['id'] = ip.id
                dict_ips4['ip'] = '%s.%s.%s.%s' % (
                    ip.oct1, ip.oct2, ip.oct3, ip.oct4)

                dict_network['id'] = ip.networkipv4_id
                dict_network['network'] = '%s.%s.%s.%s' % (
                    ip.networkipv4.oct1, ip.networkipv4.oct2, ip.networkipv4.oct3, ip.networkipv4.oct4)
                dict_network['mask'] = '%s.%s.%s.%s' % (
                    ip.networkipv4.mask_oct1, ip.networkipv4.mask_oct2, ip.networkipv4.mask_oct3, ip.networkipv4.mask_oct4)

                dict_ips4['network'] = dict_network

                lista_ip_entregue.append(dict_ips4)

            for ip in lista_ipsv6_equip:
                dict_ips6 = dict()
                dict_network = dict()

                dict_ips6['id'] = ip.id
                dict_ips6['ip'] = '%s:%s:%s:%s:%s:%s:%s:%s' % (
                    ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8)

                dict_network['id'] = ip.networkipv6.id
                dict_network['network'] = '%s:%s:%s:%s:%s:%s:%s:%s' % (
                    ip.networkipv6.block1, ip.networkipv6.block2, ip.networkipv6.block3, ip.networkipv6.block4, ip.networkipv6.block5, ip.networkipv6.block6, ip.networkipv6.block7, ip.networkipv6.block8)
                dict_network['mask'] = '%s:%s:%s:%s:%s:%s:%s:%s' % (
                    ip.networkipv6.block1, ip.networkipv6.block2, ip.networkipv6.block3, ip.networkipv6.block4, ip.networkipv6.block5, ip.networkipv6.block6, ip.networkipv6.block7, ip.networkipv6.block8)

                dict_ips6['network'] = dict_network

                lista_ip6_entregue.append(dict_ips6)

            lista_ip_entregue = lista_ip_entregue if len(
                lista_ip_entregue) > 0 else None
            lista_ip6_entregue = lista_ip6_entregue if len(
                lista_ip6_entregue) > 0 else None

            return self.response(dumps_networkapi({'list_ipv4': lista_ip_entregue, 'list_ipv6': lista_ip6_entregue}))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except (EquipamentoError, GrupoError):
            return self.response_error(1)
        except BaseException, e:
            return self.response_error(1)
