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
from networkapi.ambiente.models import ConfigEnvironmentInvalidError
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.config.models import Configuration
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.ip_subnet_utils import get_prefix_IPV6
from networkapi.infrastructure.ip_subnet_utils import MAX_IPV6_HOSTS
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import Ipv6Equipament
from networkapi.ip.models import NetworkIPv6
from networkapi.ip.models import NetworkIPv6AddressNotAvailableError
from networkapi.ip.models import NetworkIPv6Error
from networkapi.ip.models import NetworkIPv6NotFoundError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.vlan.models import NetworkTypeNotFoundError
from networkapi.vlan.models import TipoRede
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanNotFoundError


class NetworkIPv6AddResource(RestResource):

    log = logging.getLogger('NetworkIPv6AddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """
            Treat requests POST to add a network IPv6
            URL: network/ipv6/add/
        """

        # Commons Validations

        # User permission
        if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
            self.log.error(
                u'User does not have permission to perform the operation.')
            return self.not_authorized()

        # Business Validations

        # Load XML data
        xml_map, _ = loads(request.raw_post_data)

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
        vlan_id = vlan_map.get('id_vlan')
        network_type = vlan_map.get('id_tipo_rede')
        environment_vip = vlan_map.get('id_ambiente_vip')
        prefix = vlan_map.get('prefix')

        # Valid prefix
        if not is_valid_int_greater_zero_param(prefix, False) or (prefix and int(prefix) > 128):
            self.log.error(u'Parameter prefix is invalid. Value: %s.', prefix)
            return self.response_error(269, 'prefix', prefix)

        return self.network_ipv6_add(user, vlan_id, network_type, environment_vip, prefix)

    def handle_put(self, request, user, *args, **kwargs):
        """
            Treat requests PUT to add a network IPv6
            URL: network/ipv6/add/
        """

        # Commons Validations

        # User permission
        if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
            self.log.error(
                u'User does not have permission to perform the operation.')
            return self.not_authorized()

        # Business Validations

        # Load XML data
        xml_map, _ = loads(request.raw_post_data)

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
        vlan_id = vlan_map.get('id_vlan')
        network_type = vlan_map.get('id_tipo_rede')
        environment_vip = vlan_map.get('id_ambiente_vip')
        num_hosts = vlan_map.get('num_hosts')

        # Valid num_hosts
        if not is_valid_int_greater_zero_param(num_hosts) or int(num_hosts) > MAX_IPV6_HOSTS:
            self.log.error(
                u'Parameter num_hosts is invalid. Value: %s.', num_hosts)
            return self.response_error(269, 'num_hosts', num_hosts)

        num_hosts = int(num_hosts)
        # Get configuration
        conf = Configuration.get()

        num_hosts += conf.IPv6_MIN + conf.IPv6_MAX
        prefix = get_prefix_IPV6(num_hosts)
        self.log.info(u'Prefix for %s hosts: %s' % (num_hosts, prefix))

        return self.network_ipv6_add(user, vlan_id, network_type, environment_vip, prefix)

    def network_ipv6_add(self, user, vlan_id, network_type, environment_vip, prefix=None):

        try:
            # Valid vlan ID
            if not is_valid_int_greater_zero_param(vlan_id):
                self.log.error(
                    u'Parameter id_vlan is invalid. Value: %s.', vlan_id)
                raise InvalidValueError(None, 'id_vlan', vlan_id)

            # Network Type

            # Valid network_type ID
            """
            if not is_valid_int_greater_zero_param(network_type):
                self.log.error(
                    u'Parameter id_tipo_rede is invalid. Value: %s.', network_type)
                raise InvalidValueError(None, 'id_tipo_rede', network_type)
            """
            # Find network_type by ID to check if it exist
            net = None
            if network_type:
                net = TipoRede.get_by_pk(network_type)

            # Environment Vip

            if environment_vip is not None:

                # Valid environment_vip ID
                if not is_valid_int_greater_zero_param(environment_vip):
                    self.log.error(
                        u'Parameter id_ambiente_vip is invalid. Value: %s.', environment_vip)
                    raise InvalidValueError(
                        None, 'id_ambiente_vip', environment_vip)

                # Find Environment VIP by ID to check if it exist
                evip = EnvironmentVip.get_by_pk(environment_vip)

            else:
                evip = None

            # Business Rules

            # New NetworkIPv6
            network_ipv6 = NetworkIPv6()
            vlan_map = network_ipv6.add_network_ipv6(user, vlan_id, net, evip, prefix)

            list_equip_routers_ambient = EquipamentoAmbiente.get_routers_by_environment(
                vlan_map['vlan']['id_ambiente'])

            if list_equip_routers_ambient:

                # Add Adds the first available ipv6 on all equipment
                # that is configured as a router for the environment related to
                # network
                ipv6 = Ipv6.get_first_available_ip6(
                    vlan_map['vlan']['id_network'])

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
                ipv6_model.networkipv6_id = vlan_map['vlan']['id_network']

                ipv6_model.save()

                if len(list_equip_routers_ambient) > 1:
                    multiple_ips = True
                else:
                    multiple_ips = False

                if vlan_map.get('vlan').get('vxlan'):
                    logging.debug('vxlan')

                    for equip in list_equip_routers_ambient:
                        Ipv6Equipament().create(user, ipv6_model.id, equip.equipamento.id)

                    if multiple_ips:
                        router_ip = Ipv6.get_first_available_ip6(vlan_map['vlan']['id_network'], True)

                        ipv6s = Ipv6()
                        ipv6s.block1, ipv6s.block2, ipv6s.block3, ipv6s.block4, ipv6s.block5, \
                        ipv6s.block6, ipv6s.block7, ipv6s.block8 = str(router_ip).split(':')
                        ipv6s.networkipv6_id = vlan_map['vlan']['id_network']
                        ipv6s.descricao = "IPv6 alocado para debug"
                        ipv6s.save(user)

                        Ipv6Equipament().create(user,
                                                ipv6s.id,
                                                list_equip_routers_ambient[0].equipamento.id)

                else:

                    for equip in list_equip_routers_ambient:
                        Ipv6Equipament().create(user, ipv6_model.id, equip.equipamento.id)

                        if multiple_ips:
                            router_ip = Ipv6.get_first_available_ip6(vlan_map['vlan']['id_network'], True)
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
                            ipv6_model2.networkipv6_id = vlan_map['vlan']['id_network']
                            ipv6_model2.save(user)
                            Ipv6Equipament().create(user,
                                                    ipv6_model2.id,
                                                    equip.equipamento.id)

            # Return XML
            return self.response(dumps_networkapi(vlan_map))

        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except NetworkTypeNotFoundError, e:
            self.log.error(u'The network_type parameter does not exist.')
            return self.response_error(111)

        except VlanNotFoundError, e:
            self.log.error(u'Vlan not found')
            return self.response_error(116)

        except NetworkTypeNotFoundError, e:
            return self.response_error(111)

        except EnvironmentVipNotFoundError:
            return self.response_error(283)

        except NetworkIPv6AddressNotAvailableError:
            return self.response_error(296)

        except NetworkIPv6NotFoundError:
            return self.response_error(286)

        except ConfigEnvironmentInvalidError:
            return self.response_error(294)

        except IpNotAvailableError, e:
            return self.response_error(150, e.message)

        except (IpError, NetworkIPv6Error, GrupoError, VlanError):
            return self.response_error(1)
