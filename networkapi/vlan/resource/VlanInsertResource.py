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
import re

from django.core.exceptions import ObjectDoesNotExist

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.ambiente.models import ConfigEnvironmentInvalidError
from networkapi.auth import has_perm
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpEquipamento
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import Ipv6Equipament
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv4AddressNotAvailableError
from networkapi.ip.models import NetworkIPv6
from networkapi.ip.models import NetworkIPv6AddressNotAvailableError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.util import is_valid_vlan_name
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanACLDuplicatedError
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanNameDuplicatedError
from networkapi.vlan.models import VlanNumberEnvironmentNotAvailableError
from networkapi.vlan.models import VlanNumberNotAvailableError


class VlanInsertResource(RestResource):

    log = logging.getLogger('VlanInsertResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST requests to insert vlan

        URL: vlan/insert/
        """

        try:
            # Generic method for v4 and v6
            network_version = kwargs.get('network_version')

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
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
            vlan_map = networkapi_map.get('vlan')
            if vlan_map is None:
                msg = u'There is no value to the vlan tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            environment_id = vlan_map.get('environment_id')
            number = vlan_map.get('number')
            name = vlan_map.get('name')
            acl_file = vlan_map.get('acl_file')
            acl_file_v6 = vlan_map.get('acl_file_v6')
            description = vlan_map.get('description')
            network_ipv4 = vlan_map.get('network_ipv4')
            network_ipv6 = vlan_map.get('network_ipv6')
            vrf = vlan_map.get('vrf')

            # Valid environment_id ID
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'Parameter environment_id is invalid. Value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            # Valid number of Vlan
            if not is_valid_int_greater_zero_param(number):
                self.log.error(
                    u'Parameter number is invalid. Value: %s', number)
                raise InvalidValueError(None, 'number', number)

            # Valid name of Vlan
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 50):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            if not is_valid_vlan_name(name):
                self.log.error(
                    u'Parameter %s is invalid because is using special characters and/or breaklines.', name)
                raise InvalidValueError(None, 'name', name)

            if not network_ipv4 or not str(network_ipv4).isdigit():
                self.log.error(
                    u'Parameter network_ipv4 is invalid. Value: %s.', network_ipv4)
                raise InvalidValueError(None, 'network_ipv4', network_ipv4)

            if not network_ipv6 or not str(network_ipv6).isdigit():
                self.log.error(
                    u'Parameter network_ipv6 is invalid. Value: %s.', network_ipv6)
                raise InvalidValueError(None, 'network_ipv6', network_ipv6)

            # vrf can NOT be greater than 100
            if not is_valid_string_maxsize(vrf, 100, False):
                self.log.error(
                    u'Parameter vrf is invalid. Value: %s.', vrf)
                raise InvalidValueError(None, 'vrf', vrf)

            network_ipv4 = int(network_ipv4)
            network_ipv6 = int(network_ipv6)

            if network_ipv4 not in range(0, 2):
                self.log.error(
                    u'Parameter network_ipv4 is invalid. Value: %s.', network_ipv4)
                raise InvalidValueError(None, 'network_ipv4', network_ipv4)

            if network_ipv6 not in range(0, 2):
                self.log.error(
                    u'Parameter network_ipv6 is invalid. Value: %s.', network_ipv6)
                raise InvalidValueError(None, 'network_ipv6', network_ipv6)

            p = re.compile('^[A-Z0-9-_]+$')
            m = p.match(name)

            if not m:
                name = name.upper()
                m = p.match(name)

                if not m:
                    raise InvalidValueError(None, 'name', name)

            # Valid description of Vlan
            if not is_valid_string_minsize(description, 3, False) or not is_valid_string_maxsize(description, 200, False):
                self.log.error(
                    u'Parameter description is invalid. Value: %s', description)
                raise InvalidValueError(None, 'description', description)

            vlan = Vlan()

            # Valid acl_file Vlan
            if acl_file is not None:
                if not is_valid_string_minsize(acl_file, 3) or not is_valid_string_maxsize(acl_file, 200):
                    self.log.error(
                        u'Parameter acl_file is invalid. Value: %s', acl_file)
                    raise InvalidValueError(None, 'acl_file', acl_file)
                p = re.compile('^[A-Z0-9-_]+$')
                m = p.match(acl_file)
                if not m:
                    raise InvalidValueError(None, 'acl_file', acl_file)

                # VERIFICA SE VLAN COM MESMO ACL JA EXISTE OU NAO
                # commenting acl name check - issue #55
                # vlan.get_vlan_by_acl(acl_file)

            # Valid acl_file_v6 Vlan
            if acl_file_v6 is not None:
                if not is_valid_string_minsize(acl_file_v6, 3) or not is_valid_string_maxsize(acl_file_v6, 200):
                    self.log.error(
                        u'Parameter acl_file_v6 is invalid. Value: %s', acl_file_v6)
                    raise InvalidValueError(None, 'acl_file_v6', acl_file_v6)
                p = re.compile('^[A-Z0-9-_]+$')
                m = p.match(acl_file_v6)
                if not m:
                    raise InvalidValueError(None, 'acl_file_v6', acl_file_v6)

                # VERIFICA SE VLAN COM MESMO ACL JA EXISTE OU NAO
                # commenting acl name check - issue #55
                # vlan.get_vlan_by_acl_v6(acl_file_v6)

            ambiente = Ambiente()
            ambiente = ambiente.get_by_pk(environment_id)

            vlan.acl_file_name = acl_file
            vlan.acl_file_name_v6 = acl_file_v6
            vlan.num_vlan = number
            vlan.nome = name
            vlan.descricao = description
            vlan.ambiente = ambiente
            vlan.ativada = 0
            vlan.acl_valida = 0
            vlan.acl_valida_v6 = 0

            vlan.insert_vlan(user)

            if network_ipv4:
                network_ipv4 = NetworkIPv4()
                vlan_map = network_ipv4.add_network_ipv4(
                    user, vlan.id, None, None, None)
                list_equip_routers_ambient = EquipamentoAmbiente.objects.select_related('equipamento').filter(
                    ambiente=vlan.ambiente.id, is_router=True)

                if list_equip_routers_ambient:

                    # Add Adds the first available ipv4 on all equipment
                    # that is configured as a router for the environment related to
                    # network
                    ip = Ip.get_first_available_ip(network_ipv4.id)

                    ip = str(ip).split('.')

                    ip_model = Ip()
                    ip_model.oct1 = ip[0]
                    ip_model.oct2 = ip[1]
                    ip_model.oct3 = ip[2]
                    ip_model.oct4 = ip[3]
                    ip_model.networkipv4_id = network_ipv4.id

                    ip_model.save(user)

                    if len(list_equip_routers_ambient) > 1 and network_ipv4.block < 30:
                        multiple_ips = True
                    else:
                        multiple_ips = False

                    for equip in list_equip_routers_ambient:
                        IpEquipamento().create(user, ip_model.id, equip.equipamento.id)

                        if multiple_ips:
                            router_ip = Ip.get_first_available_ip(
                                network_ipv4.id, True)
                            router_ip = str(router_ip).split('.')
                            ip_model2 = Ip()
                            ip_model2.oct1 = router_ip[0]
                            ip_model2.oct2 = router_ip[1]
                            ip_model2.oct3 = router_ip[2]
                            ip_model2.oct4 = router_ip[3]
                            ip_model2.networkipv4_id = network_ipv4.id
                            ip_model2.save(user)
                            IpEquipamento().create(user, ip_model2.id, equip.equipamento.id)

            if network_ipv6:
                network_ipv6 = NetworkIPv6()
                vlan_map = network_ipv6.add_network_ipv6(
                    user, vlan.id, None, None, None)

                list_equip_routers_ambient = EquipamentoAmbiente.objects.filter(
                    ambiente=vlan.ambiente.id, is_router=True)

                if list_equip_routers_ambient:

                    # Add Adds the first available ipv6 on all equipment
                    # that is configured as a router for the environment related to
                    # network
                    ipv6 = Ipv6.get_first_available_ip6(network_ipv6.id)

                    ipv6 = str(ipv6).split(':')

                    ipv6_model = Ipv6()
                    ipv6_model.block1 = ipv6[0]
                    ipv6_model.block2 = ipv6[1]
                    ipv6_model.block3 = ipv6[2]
                    ipv6_model.block4 = ipv6[3]
                    ipv6_model.block5 = ipv6[4]
                    ipv6_model.block6 = ipv6[5]
                    ipv6_model.block7 = ipv6[6]
                    ipv6_model.block8 = ipv6[7]
                    ipv6_model.networkipv6_id = network_ipv6.id

                    ipv6_model.save(user)

                    if len(list_equip_routers_ambient) > 1:
                        multiple_ips = True
                    else:
                        multiple_ips = False

                    for equip in list_equip_routers_ambient:

                        Ipv6Equipament().create(
                            user, ipv6_model.id, equip.equipamento.id)

                        if multiple_ips:
                            router_ip = Ipv6.get_first_available_ip6(
                                network_ipv6.id, True)
                            router_ip = str(router_ip).split(':')
                            ipv6_model2 = Ipv6()
                            ipv6_model2.block1 = router_ip[0]
                            ipv6_model2.block2 = router_ip[1]
                            ipv6_model2.block3 = router_ip[2]
                            ipv6_model2.block4 = router_ip[3]
                            ipv6_model2.block5 = router_ip[4]
                            ipv6_model2.block6 = router_ip[5]
                            ipv6_model2.block7 = router_ip[6]
                            ipv6_model2.block8 = router_ip[7]
                            ipv6_model2.networkipv6_id = network_ipv6.id
                            ipv6_model2.save(user)
                            Ipv6Equipament().create(user, ipv6_model2.id, equip.equipamento.id)

            map = dict()
            listaVlan = dict()
            listaVlan['id'] = vlan.id
            listaVlan['nome'] = vlan.nome
            listaVlan['acl_file_name'] = vlan.acl_file_name
            listaVlan['descricao'] = vlan.descricao
            listaVlan['id_ambiente'] = vlan.ambiente.id
            listaVlan['ativada'] = vlan.ativada
            listaVlan['acl_valida'] = vlan.acl_valida
            map['vlan'] = listaVlan

            # Delete vlan's cache
            # destroy_cache_function()

            # Return XML
            return self.response(dumps_networkapi(map))

        except VlanACLDuplicatedError, e:
            return self.response_error(311, acl_file)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except AmbienteNotFoundError, e:
            return self.response_error(112)
        except VlanNameDuplicatedError, e:
            return self.response_error(108)
        except VlanNumberNotAvailableError, e:
            return self.response_error(306, vlan.num_vlan)
        except VlanNumberEnvironmentNotAvailableError, e:
            return self.response_error(315, e.message)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
        except (VlanError, AmbienteError), e:
            return self.response_error(1)
        except ConfigEnvironmentInvalidError, e:
            return self.response_error(294)
        except NetworkIPv4AddressNotAvailableError, e:
            return self.response_error(150, e)

        except NetworkIPv6AddressNotAvailableError, e:
            return self.response_error(150, e)

        except IpNotAvailableError, e:
            return self.response_error(150, e)
        except ObjectDoesNotExist, e:
            return self.response_error(111, e)
