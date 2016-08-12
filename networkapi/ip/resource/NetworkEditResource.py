# -*- coding:utf-8 -*-
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
from networkapi.ambiente.models import EnvironmentVip
from networkapi.ambiente.models import IP_VERSION
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_NETWORK_IPV4
from networkapi.distributedlock import LOCK_NETWORK_IPV6
from networkapi.distributedlock import LOCK_VLAN
from networkapi.equipamento.models import Equipamento
from networkapi.exception import EnvironmentVipError
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.ipaddr import IPNetwork
from networkapi.infrastructure.ipaddr import IPv4Network
from networkapi.infrastructure.ipaddr import IPv6Network
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import NetworkIpAddressNotAvailableError
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv4Error
from networkapi.ip.models import NetworkIPv4NotFoundError
from networkapi.ip.models import NetworkIPv6
from networkapi.ip.models import NetworkIPv6Error
from networkapi.ip.models import NetworkIPv6NotFoundError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.settings import NETWORKIPV4_CREATE
from networkapi.settings import NETWORKIPV6_CREATE
from networkapi.settings import VLAN_CREATE
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_int_param
from networkapi.util import is_valid_version_ip
from networkapi.vlan.models import NetworkTypeNotFoundError
from networkapi.vlan.models import TipoRede
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanNotFoundError


class NetworkEditResource(RestResource):

    log = logging.getLogger('NetworkEditResource')

    def handle_post(self, request, user, *args, **kwargs):
        '''Handles POST requests to edit an Network.

        URL: network/edit/
        '''

        self.log.info('Edit an Network')

        try:
            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            net_map = networkapi_map.get('net')
            if net_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            id_network = net_map.get('id_network')
            ip_type = net_map.get('ip_type')
            id_net_type = net_map.get('id_net_type')
            id_env_vip = net_map.get('id_env_vip')
            cluster_unit = net_map.get('cluster_unit')

            # Valid id_network
            if not is_valid_int_greater_zero_param(id_network):
                self.log.error(
                    u'Parameter id_network is invalid. Value: %s.', id_network)
                raise InvalidValueError(None, 'id_network', id_network)

            # Valid ip_type
            if not is_valid_int_param(ip_type):
                self.log.error(
                    u'Parameter ip_type is invalid. Value: %s.', ip_type)
                raise InvalidValueError(None, 'ip_type', ip_type)

            list_choice = [0, 1]
            # Valid ip_type choice
            if int(ip_type) not in list_choice:
                self.log.error(
                    u'Parameter ip_type is invalid. Value: %s.', ip_type)
                raise InvalidValueError(None, 'ip_type', ip_type)

            # Valid id_net_type
            if not is_valid_int_greater_zero_param(id_net_type):
                self.log.error(
                    u'Parameter id_net_type is invalid. Value: %s.', id_net_type)
                raise InvalidValueError(None, 'id_net_type', id_net_type)

            # Valid id_env_vip
            if id_env_vip is not None:
                if not is_valid_int_greater_zero_param(id_env_vip):
                    self.log.error(
                        u'Parameter id_env_vip is invalid. Value: %s.', id_env_vip)
                    raise InvalidValueError(None, 'id_env_vip', id_env_vip)

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                raise UserNotAuthorizedError(
                    None, u'User does not have permission to perform the operation.')

            # Business Rules

            if (id_env_vip is not None):
                id_env_vip = EnvironmentVip.get_by_pk(id_env_vip)
            id_net_type = TipoRede.get_by_pk(id_net_type)

            # New network_tyoe

            # EDIT NETWORK IP4
            if int(ip_type) == 0:
                net = NetworkIPv4.get_by_pk(id_network)

                with distributedlock(LOCK_NETWORK_IPV4 % id_network):

                    if id_env_vip is not None:

                        if net.ambient_vip is None or net.ambient_vip.id != id_env_vip.id:

                            network = IPNetwork(
                                '%d.%d.%d.%d/%d' % (net.oct1, net.oct2, net.oct3, net.oct4, net.block))

                            # Find all networks related to environment vip
                            nets = NetworkIPv4.objects.select_related().filter(
                                ambient_vip__id=id_env_vip.id)

                            # Cast to API class
                            networks = set([IPv4Network(
                                '%d.%d.%d.%d/%d' % (net_ip.oct1, net_ip.oct2, net_ip.oct3, net_ip.oct4, net_ip.block)) for net_ip in nets])

                            # If there is already a network with the same ip
                            # range as related the environment vip
                            if network in networks:
                                raise NetworkIpAddressNotAvailableError(
                                    None, u'Unavailable address to create a NetworkIPv4.')

                    net.edit_network_ipv4(user, id_net_type, id_env_vip, cluster_unit)

            # EDIT NETWORK IP6
            else:
                net = NetworkIPv6.get_by_pk(id_network)

                with distributedlock(LOCK_NETWORK_IPV6 % id_network):

                    if id_env_vip is not None:

                        if net.ambient_vip is None or net.ambient_vip.id != id_env_vip.id:

                            network = IPNetwork('%s:%s:%s:%s:%s:%s:%s:%s/%d' % (
                                net.block1, net.block2, net.block3, net.block4, net.block5, net.block6, net.block7, net.block8, net.block))

                            # Find all networks related to environment vip
                            nets = NetworkIPv6.objects.select_related().filter(
                                ambient_vip__id=id_env_vip.id)

                            # Cast to API class
                            networks = set([IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%d' % (net_ip.block1, net_ip.block2, net_ip.block3,
                                                                                        net_ip.block4, net_ip.block5, net_ip.block6, net_ip.block7, net_ip.block8, net_ip.block)) for net_ip in nets])

                            # If there is already a network with the same
                            # range ip as related the environment  vip
                            if net in networks:
                                raise NetworkIpAddressNotAvailableError(
                                    None, u'Unavailable address to create a NetworkIPv6.')

                    net.edit_network_ipv6(user, id_net_type, id_env_vip)

            # Delete vlan's cache
            # destroy_cache_function()

            return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv4NotFoundError:
            return self.response_error(281)
        except NetworkIPv6NotFoundError:
            return self.response_error(286)
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except NetworkTypeNotFoundError:
            return self.response_error(111)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except NetworkIpAddressNotAvailableError, e:
            return self.response_error(335)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except (NetworkIPv4Error, NetworkIPv6Error, GrupoError, EnvironmentVipError, VlanError), e:
            self.log.error(e)
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        '''Handles PUT requests to create Network and Vlan.

        URL: network/create/
        '''

        try:

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            network_map = networkapi_map.get('network')
            ids = network_map.get('ids')
            id_vlan = network_map.get('id_vlan')

            if not is_valid_int_greater_zero_param(id_vlan):
                self.log.error(
                    u'The id network parameter is invalid. Value: %s.', id_vlan)
                raise InvalidValueError(None, 'id_network', id_vlan)

            vlan = Vlan()
            vlan = vlan.get_by_pk(id_vlan)

            # Check permission group equipments
            equips_from_ipv4 = Equipamento.objects.filter(
                ipequipamento__ip__networkipv4__vlan=id_vlan, equipamentoambiente__is_router=1).distinct()
            equips_from_ipv6 = Equipamento.objects.filter(
                ipv6equipament__ip__networkipv6__vlan=id_vlan, equipamentoambiente__is_router=1).distinct()
            for equip in equips_from_ipv4:
                # User permission
                if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
                    self.log.error(
                        u'User does not have permission to perform the operation.')
                    return self.not_authorized()
            for equip in equips_from_ipv6:
                # User permission
                if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
                    self.log.error(
                        u'User does not have permission to perform the operation.')
                    return self.not_authorized()

            with distributedlock(LOCK_VLAN % id_vlan):
                if vlan.ativada == 0:
                    # Make command - VLAN'
                    vlan_command = VLAN_CREATE % int(id_vlan)

                    # Execute command
                    code, stdout, stderr = exec_script(vlan_command)

                    # code = 0 means OK
                    if code == 0:
                        vlan.activate(user)
                    else:
                        return self.response_error(2, stdout + stderr)

                # if 'ids' is a list
                if isinstance(ids, list):
                    for id in ids:
                        code, stdout, stderr = self.activate_network(user, id)
                else:
                    code, stdout, stderr = self.activate_network(user, ids)

                if code != 0:
                    return self.response_error(2, stdout + stderr)

                return self.response(dumps_networkapi({'network': network_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except VlanNotFoundError, e:
            return self.response_error(116)

    def activate_network(self, user, id):
        # id => ex: '55-v4' or '55-v6'
        value = id.split('-')

        if len(value) != 2:
            self.log.error(
                u'The id network parameter is invalid format: %s.', value)
            raise InvalidValueError(None, 'id_network', value)

        id_net = value[0]
        network_type = value[1]

        if not is_valid_int_greater_zero_param(id_net):
            self.log.error(
                u'The id network parameter is invalid. Value: %s.', id_net)
            raise InvalidValueError(None, 'id_network', id_net)

        if not is_valid_version_ip(network_type, IP_VERSION):
            self.log.error(
                u'The type network parameter is invalid value: %s.', network_type)
            raise InvalidValueError(None, 'network_type', network_type)

        if network_type == 'v4':
            # network_type = 'v4'

            # Make command
            command = NETWORKIPV4_CREATE % int(id_net)
            code, stdout, stderr = exec_script(command)
            if code == 0:
                # Change column 'active = 1'
                net = NetworkIPv4.get_by_pk(id_net)
                net.activate(user)
        else:
            # network_type = 'v6'

            # Make command
            command = NETWORKIPV6_CREATE % int(id_net)
            code, stdout, stderr = exec_script(command)
            if code == 0:
                # Change column 'active = 1'
                net = NetworkIPv6.get_by_pk(id_net)
                net.activate(user)

        return code, stdout, stderr
