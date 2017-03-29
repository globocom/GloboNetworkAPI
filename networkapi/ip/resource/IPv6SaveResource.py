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

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_NETWORK_IPV6
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.filterequiptype.models import FilterEquipType
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import IpEquipmentAlreadyAssociation
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import IpRangeAlreadyAssociation
from networkapi.ip.models import Ipv6
from networkapi.ip.models import Ipv6Equipament
from networkapi.ip.models import NetworkIPv6
from networkapi.ip.models import NetworkIPv6Error
from networkapi.ip.models import NetworkIPv6NotFoundError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import destroy_cache_function
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.vlan.models import VlanNumberNotAvailableError


class IPv6SaveResource(RestResource):

    log = logging.getLogger('IPv6SaveResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to add an IP6 and associate it to an equipment.

        URL: ipv6/save/
        """

        self.log.info('Add an IP6 and associate it to an equipment')

        try:
            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            ip_map = networkapi_map.get('ip_map')
            if ip_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            equip_id = ip_map.get('id_equip')
            network_ipv6_id = ip_map.get('id_net')
            description = ip_map.get('descricao')
            ip6 = ip_map.get('ip6')

            # Valid equip_id
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'Parameter equip_id is invalid. Value: %s.', equip_id)
                raise InvalidValueError(None, 'equip_id', equip_id)

            # Valid network_ipv4_id
            if not is_valid_int_greater_zero_param(network_ipv6_id):
                self.log.error(
                    u'Parameter network_ipv6_id is invalid. Value: %s.', network_ipv6_id)
                raise InvalidValueError(
                    None, 'network_ipv6_id', network_ipv6_id)

            # Description can NOT be greater than 100
            if not is_valid_string_maxsize(ip6, 39):
                self.log.error(u'Parameter ip6 is invalid. Value: %s.', ip6)
                raise InvalidValueError(None, 'ip6', ip6)

            if description is not None:
                if not is_valid_string_maxsize(description, 100) or not is_valid_string_minsize(description, 3):
                    self.log.error(
                        u'Parameter description is invalid. Value: %s.', description)
                    raise InvalidValueError(None, 'description', description)

            # User permission
            if not has_perm(user,
                            AdminPermission.IPS,
                            AdminPermission.WRITE_OPERATION,
                            None,
                            equip_id,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                raise UserNotAuthorizedError(
                    None, u'User does not have permission to perform the operation.')

            # Business Rules

            # New IP
            ipv6 = Ipv6()

            net = NetworkIPv6.get_by_pk(network_ipv6_id)

            with distributedlock(LOCK_NETWORK_IPV6 % network_ipv6_id):

                # Caso haja erro para retornar o ip corretamente
                ip_error = ip6
                ip6 = ip6.split(':')

                # Ip informado de maneira incorreta
                if len(ip6) is not 8:
                    raise InvalidValueError(None, 'ip6', ip_error)

                ipv6.description = description
                ipv6.block1 = ip6[0]
                ipv6.block2 = ip6[1]
                ipv6.block3 = ip6[2]
                ipv6.block4 = ip6[3]
                ipv6.block5 = ip6[4]
                ipv6.block6 = ip6[5]
                ipv6.block7 = ip6[6]
                ipv6.block8 = ip6[7]
                # Persist

                equip = Equipamento.get_by_pk(equip_id)

                listaVlansDoEquip = []

                for ipequip in equip.ipv6equipament_set.all():
                    vlan = ipequip.ip.networkipv6.vlan
                    if vlan not in listaVlansDoEquip:
                        listaVlansDoEquip.append(vlan)

                for ipequip in equip.ipequipamento_set.all():
                    vlan = ipequip.ip.networkipv4.vlan
                    if vlan not in listaVlansDoEquip:
                        listaVlansDoEquip.append(vlan)

                vlan_atual = net.vlan

                ambiente_aux = None
                vlan_aux = None

                for vlan in listaVlansDoEquip:
                    if vlan.num_vlan == vlan_atual.num_vlan:
                        if vlan.id != vlan_atual.id:

                            # Filter case 3 - Vlans with same number cannot
                            # share equipments ##

                            flag_vlan_error = False
                            # Filter testing
                            if vlan.ambiente.filter is None or vlan_atual.ambiente.filter is None:
                                flag_vlan_error = True
                            else:
                                # Test both environment's filters
                                tp_equip_list_one = list()
                                for fet in FilterEquipType.objects.filter(filter=vlan_atual.ambiente.filter.id):
                                    tp_equip_list_one.append(fet.equiptype)

                                tp_equip_list_two = list()
                                for fet in FilterEquipType.objects.filter(filter=vlan.ambiente.filter.id):
                                    tp_equip_list_two.append(fet.equiptype)

                                if equip.tipo_equipamento not in tp_equip_list_one or equip.tipo_equipamento not in tp_equip_list_two:
                                    flag_vlan_error = True

                            ## Filter case 3 - end ##

                            if flag_vlan_error:

                                vlan_aux = vlan
                                ambiente_aux = vlan.ambiente
                                nome_ambiente = '%s - %s - %s' % (
                                    vlan.ambiente.divisao_dc.nome, vlan.ambiente.ambiente_logico.nome, vlan.ambiente.grupo_l3.nome)
                                raise VlanNumberNotAvailableError(None,
                                                                  """O ip informado não pode ser cadastrado, pois o equipamento %s, faz parte do ambiente %s (id %s),
                                                                    que possui a Vlan de id %s, que também possui o número %s, e não é permitido que vlans que compartilhem o mesmo ambiente,
                                                                    por meio de equipamentos, possuam o mesmo número, edite o número de uma das Vlans ou adicione um filtro no ambiente para efetuar o cadastro desse IP no Equipamento Informado.
                                                                    """ % (equip.nome, nome_ambiente, ambiente_aux.id, vlan_aux.id, vlan_atual.num_vlan))

                ipv6.save_ipv6(equip_id, user, net)

                list_ip = []
                lequips = list()

                if ipv6.id is None:
                    ipv6 = Ipv6.get_by_blocks_and_net(
                        ipv6.block1, ipv6.block2, ipv6.block3, ipv6.block4, ipv6.block5, ipv6.block6, ipv6.block7, ipv6.block8, net.id)

                equips = Ipv6Equipament.list_by_ip6(ipv6.id)
                ip_maps = dict()
                ip_maps['id'] = ipv6.id
                ip_maps['block1'] = ipv6.block1
                ip_maps['block2'] = ipv6.block2
                ip_maps['block3'] = ipv6.block3
                ip_maps['block4'] = ipv6.block4
                ip_maps['block5'] = ipv6.block5
                ip_maps['block6'] = ipv6.block6
                ip_maps['block7'] = ipv6.block7
                ip_maps['block8'] = ipv6.block8
                ip_maps['descricao'] = ipv6.description

                list_id_equip = []

                for equip in equips:
                    list_id_equip.append(equip.equipamento.id)
                    equip = Equipamento.get_by_pk(equip.equipamento.id)
                    lequips.append(model_to_dict(equip))
                ip_maps['equipamento'] = lequips
                list_ip.append(ip_maps)

                network_map = dict()
                network_map['ipv6'] = list_ip

                # Delete vlan's cache
                destroy_cache_function([net.vlan_id])

                # Delete equipment's cache
                destroy_cache_function(list_id_equip, True)

                return self.response(dumps_networkapi(network_map))

        except IpRangeAlreadyAssociation, e:
            return self.response_error(347)
        except VlanNumberNotAvailableError, e:
            return self.response_error(314, e.message)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv6NotFoundError:
            return self.response_error(286)
        except EquipamentoNotFoundError:
            return self.response_error(117, ip_map.get('id_equipment'))
        except IpNotAvailableError, e:
            return self.response_error(150, e.message)
        except IpEquipmentAlreadyAssociation, e:
            return self.response_error(150, e.message)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except (IpError, NetworkIPv6Error, EquipamentoError, GrupoError), e:
            self.log.error(e)
            return self.response_error(1)
