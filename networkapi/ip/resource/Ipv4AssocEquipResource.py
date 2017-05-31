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
from networkapi.distributedlock import LOCK_NETWORK_IPV4
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.equipamento.models import EquipamentoAmbienteDuplicatedError
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.filterequiptype.models import FilterEquipType
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.ipaddr import AddressValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpEquipamento
from networkapi.ip.models import IpEquipmentAlreadyAssociation
from networkapi.ip.models import IpEquipmentNotFoundError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import IpRangeAlreadyAssociation
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv4Error
from networkapi.ip.models import NetworkIPv4NotFoundError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import destroy_cache_function
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.vlan.models import VlanNumberNotAvailableError


class Ipv4AssocEquipResource(RestResource):

    log = logging.getLogger('Ipv4AssocEquipResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to associate and IP to an equipment.

        URL: ipv4/assoc/
        """

        self.log.info('Associate Ip to an Equipment')

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
            ip_id = ip_map.get('id_ip')
            equip_id = ip_map.get('id_equip')
            network_ipv4_id = ip_map.get('id_net')

            # Valid ip_id
            if not is_valid_int_greater_zero_param(ip_id):
                self.log.error(
                    u'Parameter ip_id is invalid. Value: %s.', ip_id)
                raise InvalidValueError(None, 'ip_id', ip_id)

            # Valid equip_id
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'Parameter equip_id is invalid. Value: %s.', equip_id)
                raise InvalidValueError(None, 'equip_id', equip_id)

            # Valid network_ipv4_id
            if not is_valid_int_greater_zero_param(network_ipv4_id):
                self.log.error(
                    u'Parameter network_ipv4_id is invalid. Value: %s.', network_ipv4_id)
                raise InvalidValueError(
                    None, 'network_ipv4_id', network_ipv4_id)

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

            # Get net
            net = NetworkIPv4.get_by_pk(network_ipv4_id)

            with distributedlock(LOCK_NETWORK_IPV4 % network_ipv4_id):

                # Get ip
                ip = Ip.get_by_pk(ip_id)
                # Get equipment
                equip = Equipamento.get_by_pk(equip_id)

                listaVlansDoEquip = []

                for ipequip in equip.ipequipamento_set.all():
                    vlan = ipequip.ip.networkipv4.vlan
                    if vlan not in listaVlansDoEquip:
                        listaVlansDoEquip.append(vlan)

                for ipequip in equip.ipv6equipament_set.all():
                    vlan = ipequip.ip.networkipv6.vlan
                    if vlan not in listaVlansDoEquip:
                        listaVlansDoEquip.append(vlan)

                vlan_atual = net.vlan
                vlan_aux = None
                ambiente_aux = None

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

                                # Equipment type should be in both filters
                                if equip.tipo_equipamento not in tp_equip_list_one or equip.tipo_equipamento not in tp_equip_list_two:
                                    flag_vlan_error = True

                                    # Out of band network is never trunked, it is only in mgmt interface
                                    # allow it - not a good thing to to, but is
                                    # very specific
                                    if vlan.ambiente.divisao_dc.nome == 'OOB-CM' or vlan_atual.ambiente.divisao_dc.nome == 'OOB-CM':
                                        flag_vlan_error = False

                            ## Filter case 3 - end ##

                            if flag_vlan_error:
                                ambiente_aux = vlan.ambiente
                                vlan_aux = vlan
                                nome_ambiente = '%s - %s - %s' % (
                                    vlan.ambiente.divisao_dc.nome, vlan.ambiente.ambiente_logico.nome, vlan.ambiente.grupo_l3.nome)
                                raise VlanNumberNotAvailableError(None,
                                                                  """O ip informado não pode ser cadastrado, pois o equipamento %s, faz parte do ambiente %s (id %s),
                                                                    que possui a Vlan de id %s, que também possui o número %s, e não é permitido que vlans que compartilhem o mesmo ambiente
                                                                    por meio de equipamentos, possuam o mesmo número, edite o número de uma das Vlans ou adicione um filtro no ambiente para efetuar o cadastro desse IP no Equipamento Informado.
                                                                    """ % (equip.nome, nome_ambiente, ambiente_aux.id, vlan_aux.id, vlan_atual.num_vlan))

                # Persist
                try:

                    try:
                        ipEquip = IpEquipamento()
                        ipEquip.get_by_ip_equipment(ip.id, equip_id)

                        # Ip %s.%s.%s.%s already has association with
                        # Equipament %s.' % (self.oct1, self.oct2, self.oct3,
                        # self.oct4,equipment_id)
                        raise IpEquipmentAlreadyAssociation(None, u'Ip %s.%s.%s.%s already has association with Equipament %s.' % (
                            ip.oct1, ip.oct2, ip.oct3, ip.oct4, equip_id))
                    except IpEquipmentNotFoundError, e:
                        pass

                    equipment = Equipamento().get_by_pk(equip_id)
                    ip_equipment = IpEquipamento()
                    ip_equipment.ip = ip

                    ip_equipment.equipamento = equipment

                    # Filter case 2 - Adding new IpEquip for a equip that
                    # already have ip in other network with the same range ##

                    # Get all IpEquipamento related to this equipment
                    ip_equips = IpEquipamento.objects.filter(
                        equipamento=equip_id)

                    for ip_test in [ip_equip.ip for ip_equip in ip_equips]:
                        if ip_test.networkipv4.oct1 == ip.networkipv4.oct1 and \
                                ip_test.networkipv4.oct2 == ip.networkipv4.oct2 and \
                                ip_test.networkipv4.oct3 == ip.networkipv4.oct3 and \
                                ip_test.networkipv4.oct4 == ip.networkipv4.oct4 and \
                                ip_test.networkipv4.block == ip.networkipv4.block and \
                                ip_test.networkipv4 != ip.networkipv4:

                            # Filter testing
                            if ip_test.networkipv4.vlan.ambiente.filter is None or ip.networkipv4.vlan.ambiente.filter is None:
                                raise IpRangeAlreadyAssociation(
                                    None, u'Equipment is already associated with another ip with the same ip range.')
                            else:
                                # Test both environment's filters
                                tp_equip_list_one = list()
                                for fet in FilterEquipType.objects.filter(filter=ip.networkipv4.vlan.ambiente.filter.id):
                                    tp_equip_list_one.append(fet.equiptype)

                                tp_equip_list_two = list()
                                for fet in FilterEquipType.objects.filter(filter=ip_test.networkipv4.vlan.ambiente.filter.id):
                                    tp_equip_list_two.append(fet.equiptype)

                                if equipment.tipo_equipamento not in tp_equip_list_one or equipment.tipo_equipamento not in tp_equip_list_two:
                                    raise IpRangeAlreadyAssociation(
                                        None, u'Equipment is already associated with another ip with the same ip range.')

                    ## Filter case 2 - end ##

                    ip_equipment.save()

                    # Makes Environment Equipment association
                    try:
                        equipment_environment = EquipamentoAmbiente()
                        equipment_environment.equipamento = equipment
                        equipment_environment.ambiente = net.vlan.ambiente
                        equipment_environment.create(user)

                        # Delete vlan's cache
                        destroy_cache_function([net.vlan_id])
                    except EquipamentoAmbienteDuplicatedError, e:
                        # If already exists, OK !
                        pass

                except IpRangeAlreadyAssociation, e:
                    raise IpRangeAlreadyAssociation(None, e.message)
                except IpEquipmentAlreadyAssociation, e:
                    raise IpEquipmentAlreadyAssociation(None, e.message)
                except AddressValueError, e:
                    self.log.error(e)
                    raise IpNotAvailableError(
                        None, u'Ip %s.%s.%s.%s is invalid' % (ip.oct1, ip.oct2, ip.oct3, ip.oct4))
                except IpNotAvailableError, e:
                    raise IpNotAvailableError(None, u'Ip %s.%s.%s.%s not available for network %s.' % (
                        ip.oct1, ip.oct2, ip.oct3, ip.oct4, net.id))
                except (IpError, EquipamentoError), e:
                    self.log.error(
                        u'Error adding new IP or relationship ip-equipment.')
                    raise IpError(
                        e, u'Error adding new IP or relationship ip-equipment.')

                return self.response(dumps_networkapi({}))

        except IpRangeAlreadyAssociation, e:
            return self.response_error(347)
        except VlanNumberNotAvailableError, e:
            return self.response_error(314, e.message)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError, e:
            return self.response_error(150, e.message)
        except NetworkIPv4NotFoundError:
            return self.response_error(281)
        except EquipamentoNotFoundError:
            return self.response_error(117, ip_map.get('id_equipment'))
        except IpNotAvailableError, e:
            return self.response_error(150, e.message)
        except IpEquipmentNotFoundError, e:
            return self.response_error(150, e.message)
        except IpEquipmentAlreadyAssociation, e:
            return self.response_error(150, e.message)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except (IpError, NetworkIPv4Error, EquipamentoError, GrupoError), e:
            self.log.error(e)
            return self.response_error(1)
