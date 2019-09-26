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
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.config.models import Configuration
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.ip_subnet_utils import get_prefix_IPV4
from networkapi.infrastructure.ip_subnet_utils import MAX_IPV4_HOSTS
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpEquipamento
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv4AddressNotAvailableError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.vlan.models import NetworkTypeNotFoundError
from networkapi.vlan.models import TipoRede
from networkapi.vlan.models import VlanNotFoundError


class NetworkIPv4AddResource(RestResource):

    log = logging.getLogger('NetworkIPv4AddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """
            Treat requests POST to add a network IPv4
            URL: network/ipv4/add/
        """

        if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
            self.log.error(
                u'User does not have permission to perform the operation.')
            return self.not_authorized()

        xml_map, _ = loads(request.raw_post_data)
        networkapi_map = xml_map.get('networkapi')

        if networkapi_map is None:
            msg = "There is no value to the networkapi tag of XML request."
            self.log.error(msg)
            return self.response_error(3, msg)

        vlan_map = networkapi_map.get('vlan')
        if vlan_map is None:
            msg = "There is no value to the vlan tag of XML request."
            self.log.error(msg)
            return self.response_error(3, msg)

        # Get XML data
        vlan_id = vlan_map.get('id_vlan')
        network_type = vlan_map.get('id_tipo_rede')
        environment_vip = vlan_map.get('id_ambiente_vip')
        prefix = vlan_map.get('prefix')

        # Valid prefix
        if not is_valid_int_greater_zero_param(prefix, False) or (prefix and int(prefix) > 32):
            msg = "CIDR prefix is invalid. It must be between 1 and 32  Value: {}".format(prefix)
            self.log.error(msg)
            return self.response_error(150, msg)

        return self.network_ipv4_add(user, vlan_id, network_type, environment_vip, prefix)

    def handle_put(self, request, user, *args, **kwargs):
        """
            Treat requests PUT to add a network IPv4 with num hosts param
            URL: network/ipv4/add/
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
        if not is_valid_int_greater_zero_param(num_hosts) or int(num_hosts) > MAX_IPV4_HOSTS:
            self.log.error(
                u'Parameter num_hosts is invalid. Value: %s.', num_hosts)
            return self.response_error(269, 'num_hosts', num_hosts)

        num_hosts = int(num_hosts)
        # Get configuration
        conf = Configuration.get()

        num_hosts += conf.IPv4_MIN + conf.IPv4_MAX
        prefix = get_prefix_IPV4(num_hosts)
        self.log.info(u'Prefix for %s hosts: %s' % (num_hosts, prefix))

        return self.network_ipv4_add(user, vlan_id, network_type, environment_vip, prefix)

    def network_ipv4_add(self, user, vlan_id, network_type, environment_vip, prefix=None):

        try:

            if not is_valid_int_greater_zero_param(vlan_id):
                msg = "The Vlan number is invalid. Value: {}".format(prefix)
                self.log.error(msg)
                return self.response_error(150, msg)

            net = None
            if network_type:
                net = TipoRede.get_by_pk(network_type)

            if environment_vip is not None:
                # Valid environment_vip ID
                if not is_valid_int_greater_zero_param(environment_vip):
                    msg = "The VIP Environment id is invalid. Value: {}".format(prefix)
                    self.log.error(msg)
                    return self.response_error(150, msg)
                # Find Environment VIP by ID to check if it exist
                evip = EnvironmentVip.get_by_pk(environment_vip)

            else:
                evip = None

            # Business Rules

            # New NetworkIPv4
            network_ipv4 = NetworkIPv4()
            vlan_map = network_ipv4.add_network_ipv4(user, vlan_id, net, evip, prefix)

            list_equip_routers_ambient = EquipamentoAmbiente.get_routers_by_environment(
                vlan_map['vlan']['id_ambiente'])

            if list_equip_routers_ambient:

                # Add the first available ipv4 on all equipment
                # that is configured as a router for the environment related to
                # network
                ip = Ip.get_first_available_ip(vlan_map['vlan']['id_network'])

                ip = str(ip).split('.')

                ip_model = Ip()
                ip_model.oct1 = ip[0]
                ip_model.oct2 = ip[1]
                ip_model.oct3 = ip[2]
                ip_model.oct4 = ip[3]
                ip_model.networkipv4_id = network_ipv4.id

                ip_model.save()

                if len(list_equip_routers_ambient) > 1:
                    multiple_ips = True
                else:
                    multiple_ips = False

                if vlan_map.get('vlan').get('vxlan'):

                    logging.debug('vxlan')
                    for equip in list_equip_routers_ambient:
                        IpEquipamento().create(user, ip_model.id, equip.equipamento.id)

                    if multiple_ips:
                        debug_ip = Ip.get_first_available_ip(network_ipv4.id, True)

                        ips = Ip()
                        ips.oct1, ips.oct2, ips.oct3, ips.oct4 = str(debug_ip).split('.')
                        ips.networkipv4_id = network_ipv4.id
                        ips.descricao = "IP alocado para debug"
                        ips.save(user)

                        IpEquipamento().create(user, ips.id, list_equip_routers_ambient[0].equipamento.id)

                else:

                    for equip in list_equip_routers_ambient:
                        IpEquipamento().create(user, ip_model.id, equip.equipamento.id)

                        if multiple_ips:
                            router_ip = Ip.get_first_available_ip(network_ipv4.id, True)
                            router_ip = str(router_ip).split('.')
                            ip_model2 = Ip()
                            ip_model2.oct1 = router_ip[0]
                            ip_model2.oct2 = router_ip[1]
                            ip_model2.oct3 = router_ip[2]
                            ip_model2.oct4 = router_ip[3]
                            ip_model2.networkipv4_id = network_ipv4.id
                            ip_model2.save(user)
                            IpEquipamento().create(user, ip_model2.id, equip.equipamento.id)

            # Return XML
            return self.response(dumps_networkapi(vlan_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkTypeNotFoundError, e:
            self.log.error(u'The network_type parameter does not exist.')
            return self.response_error(111)
        except VlanNotFoundError, e:
            self.log.error(u'Vlan not found')
            return self.response_error(116)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
        except GrupoError, e:
            return self.response_error(1)
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except NetworkIPv4AddressNotAvailableError:
            return self.response_error(295)
        except ConfigEnvironmentInvalidError:
            return self.response_error(294)
        except IpNotAvailableError, e:
            return self.response_error(150, e)
        except NetworkAPIException as e:
            return self.response_error(150, e)
