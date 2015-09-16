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


from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.ip.models import NetworkIPv4, NetworkIPv4AddressNotAvailableError, NetworkIPv6, IpError, NetworkIPv6Error, NetworkIPv4Error, NetworkIPv6AddressNotAvailableError, NetworkIpAddressNotAvailableError, NetworkIPRangeEnvError
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param, \
    destroy_cache_function
from networkapi.vlan.models import TipoRede, NetworkTypeNotFoundError, VlanNotFoundError, Vlan, VlanError
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.exception import InvalidValueError, EnvironmentVipNotFoundError
from networkapi.ambiente.models import EnvironmentVip, ConfigEnvironmentInvalidError, IP_VERSION, \
    Ambiente
from networkapi.infrastructure.ipaddr import IPNetwork, IPv6Network, IPv4Network
from networkapi.vlan.resource.VlanFindResource import break_network
from string import split
from networkapi.filterequiptype.models import FilterEquipType
from django.forms.models import model_to_dict
from networkapi.ip.models import Ip, Ipv6, IpEquipamento, Ipv6Equipament


class NetworkAddResource(RestResource):

    log = Log('NetworkAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST requests to add new Network

        URL: network/add/
        """

        try:

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
            network_map = networkapi_map.get('network')
            if network_map is None:
                msg = u'There is no value to the vlan tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            network = network_map.get('network')
            id_vlan = network_map.get('id_vlan')
            network_type = network_map.get('id_network_type')
            environment_vip = network_map.get('id_environment_vip')

            # Valid Network
            try:
                net = IPNetwork(network)
            except ValueError, e:
                raise InvalidValueError(None, 'network', network)

            # VLAN

            # Valid vlan ID
            if not is_valid_int_greater_zero_param(id_vlan):
                raise InvalidValueError(None, 'id_vlan', id_vlan)

            # Find vlan by ID to check if it exist
            vlan = Vlan().get_by_pk(id_vlan)

            # Network Type

            # Valid network_type ID
            if not is_valid_int_greater_zero_param(network_type):
                raise InvalidValueError(None, 'id_network_type', network_type)

            # Find network_type by ID to check if it exist
            net_type = TipoRede.get_by_pk(network_type)

            # Environment Vip

            if environment_vip is not None:

                # Valid environment_vip ID
                if not is_valid_int_greater_zero_param(environment_vip):
                    raise InvalidValueError(
                        None, 'id_environment_vip', environment_vip)

                evips = EnvironmentVip.objects.all()

                evip_list = EnvironmentVip.available_evips(
                    EnvironmentVip(), evips, int(id_vlan))

                # Check if the chose environment is in the same environment
                if any(int(environment_vip) == item['id'] for item in evip_list):
                    # Find Environment VIP by ID to check if it exist
                    env_vip = EnvironmentVip.get_by_pk(environment_vip)
                else:
                    raise InvalidValueError(
                        None, 'id_environment_vip', environment_vip)

            else:
                env_vip = None

            # Check unchecked exception
            blocks, network, version = break_network(network)

            expl = split(
                net.network.exploded, "." if version == IP_VERSION.IPv4[0] else ":")
            expl.append(str(net.prefixlen))

            if blocks != expl:
                raise InvalidValueError(None, 'rede', network)

            # Business Rules

            if version == IP_VERSION.IPv4[0]:

                # Find all networks related to environment
                nets = NetworkIPv4.objects.select_related().filter(
                    vlan__ambiente__id=vlan.ambiente.id)

                # Cast to API class
                networks = set([IPv4Network(
                    '%d.%d.%d.%d/%d' % (net_ip.oct1, net_ip.oct2, net_ip.oct3, net_ip.oct4, net_ip.block)) for net_ip in nets])

                # If network selected not in use
                if net in networks:
                    raise NetworkIPv4AddressNotAvailableError(
                        None, u'Unavailable address to create a NetworkIPv4.')

                if env_vip is not None:

                    # Find all networks related to environment vip
                    nets = NetworkIPv4.objects.select_related().filter(
                        ambient_vip__id=env_vip.id)

                    # Cast to API class
                    networks = set([IPv4Network(
                        '%d.%d.%d.%d/%d' % (net_ip.oct1, net_ip.oct2, net_ip.oct3, net_ip.oct4, net_ip.block)) for net_ip in nets])

                    # If there is already a network with the same  range ip as
                    # related the environment  vip
                    if net in networks:
                        raise NetworkIpAddressNotAvailableError(
                            None, u'Unavailable address to create a NetworkIPv4.')

                # # Filter case 1 - Adding new network with same ip range to another network on other environment ##
                # Get environments with networks with the same ip range
                nets = NetworkIPv4.objects.filter(
                    oct1=expl[0], oct2=expl[1], oct3=expl[2], oct4=expl[3], block=expl[4])
                env_ids = list()
                for net_ip in nets:
                    env_ids.append(net_ip.vlan.ambiente.id)

                # If other network with same ip range exists
                if len(env_ids) > 0:

                    # Get equipments related to this network's environment
                    env_equips = EquipamentoAmbiente.objects.filter(
                        ambiente=vlan.ambiente.id)

                    # Verify equipments related with all other environments
                    # that contains networks with same ip range
                    for env_id in env_ids:
                        # Equipments related to other environments
                        other_env_equips = EquipamentoAmbiente.objects.filter(
                            ambiente=env_id)
                        # Adjust to equipments
                        equip_list = list()
                        for equip_env in other_env_equips:
                            equip_list.append(equip_env.equipamento.id)

                        for env_equip in env_equips:
                            if env_equip.equipamento.id in equip_list:

                                # Filter testing
                                if other_env_equips[0].ambiente.filter is None or vlan.ambiente.filter is None:
                                    raise NetworkIPRangeEnvError(
                                        None, u'Um dos equipamentos associados com o ambiente desta rede também está associado com outro ambiente que tem uma rede com essa mesma faixa, adicione filtros nos ambientes se necessário.')
                                else:
                                    # Test both environment's filters
                                    tp_equip_list_one = list()
                                    for fet in FilterEquipType.objects.filter(filter=vlan.ambiente.filter.id):
                                        tp_equip_list_one.append(fet.equiptype)

                                    tp_equip_list_two = list()
                                    for fet in FilterEquipType.objects.filter(filter=other_env_equips[0].ambiente.filter.id):
                                        tp_equip_list_two.append(fet.equiptype)

                                    if env_equip.equipamento.tipo_equipamento not in tp_equip_list_one or env_equip.equipamento.tipo_equipamento not in tp_equip_list_two:
                                        raise NetworkIPRangeEnvError(
                                            None, u'Um dos equipamentos associados com o ambiente desta rede também está associado com outro ambiente que tem uma rede com essa mesma faixa, adicione filtros nos ambientes se necessário.')

                # # Filter case 1 - end ##

                # New NetworkIPv4
                network_ip = NetworkIPv4()

                # Set octs by network generated
                network_ip.oct1, network_ip.oct2, network_ip.oct3, network_ip.oct4 = str(
                    net.network).split('.')
                # Set block by network generated
                network_ip.block = net.prefixlen
                # Set mask by network generated
                network_ip.mask_oct1, network_ip.mask_oct2, network_ip.mask_oct3, network_ip.mask_oct4 = str(
                    net.netmask).split('.')
                # Set broadcast by network generated
                network_ip.broadcast = net.broadcast

            else:
                # Find all networks ralated to environment
                nets = NetworkIPv6.objects.select_related().filter(
                    vlan__ambiente__id=vlan.ambiente.id)

                # Cast to API class
                networks = set([IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%d' % (net_ip.block1, net_ip.block2, net_ip.block3,
                                                                            net_ip.block4, net_ip.block5, net_ip.block6, net_ip.block7, net_ip.block8, net_ip.block)) for net_ip in nets])

                # If network selected not in use
                if net in networks:
                    raise NetworkIPv6AddressNotAvailableError(
                        None, u'Unavailable address to create a NetworkIPv6.')

                if env_vip is not None:

                    # Find all networks related to environment vip
                    nets = NetworkIPv6.objects.select_related().filter(
                        ambient_vip__id=env_vip.id)

                    # Cast to API class
                    networks = set([IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%d' % (net_ip.block1, net_ip.block2, net_ip.block3,
                                                                                net_ip.block4, net_ip.block5, net_ip.block6, net_ip.block7, net_ip.block8, net_ip.block)) for net_ip in nets])

                    # If there is already a network with the same  range ip as
                    # related the environment  vip
                    if net in networks:
                        raise NetworkIpAddressNotAvailableError(
                            None, u'Unavailable address to create a NetworkIPv6.')

                # # Filter case 1 - Adding new network with same ip range to another network on other environment ##
                # Get environments with networks with the same ip range
                nets = NetworkIPv6.objects.filter(block1=expl[0], block2=expl[1], block3=expl[2], block4=expl[
                                                  3], block5=expl[4], block6=expl[5], block7=expl[6], block8=expl[7], block=expl[8])
                env_ids = list()
                for net_ip in nets:
                    env_ids.append(net_ip.vlan.ambiente.id)

                # If other network with same ip range exists
                if len(env_ids) > 0:

                    # Get equipments related to this network's environment
                    env_equips = EquipamentoAmbiente.objects.filter(
                        ambiente=vlan.ambiente.id)

                    # Verify equipments related with all other environments
                    # that contains networks with same ip range
                    for env_id in env_ids:
                        # Equipments related to other environments
                        other_env_equips = EquipamentoAmbiente.objects.filter(
                            ambiente=env_id)
                        # Adjust to equipments
                        equip_list = list()
                        for equip_env in other_env_equips:
                            equip_list.append(equip_env.equipamento.id)

                        for env_equip in env_equips:
                            if env_equip.equipamento.id in equip_list:

                                # Filter testing
                                if other_env_equips[0].ambiente.filter is None or vlan.ambiente.filter is None:
                                    raise NetworkIPRangeEnvError(
                                        None, u'Um dos equipamentos associados com o ambiente desta rede também está associado com outro ambiente que tem uma rede com essa mesma faixa, adicione filtros nos ambientes se necessário.')
                                else:
                                    # Test both environment's filters
                                    tp_equip_list_one = list()
                                    for fet in FilterEquipType.objects.filter(filter=vlan.ambiente.filter.id):
                                        tp_equip_list_one.append(fet.equiptype)

                                    tp_equip_list_two = list()
                                    for fet in FilterEquipType.objects.filter(filter=other_env_equips[0].ambiente.filter.id):
                                        tp_equip_list_two.append(fet.equiptype)

                                    if env_equip.equipamento.tipo_equipamento not in tp_equip_list_one or env_equip.equipamento.tipo_equipamento not in tp_equip_list_two:
                                        raise NetworkIPRangeEnvError(
                                            None, u'Um dos equipamentos associados com o ambiente desta rede também está associado com outro ambiente que tem uma rede com essa mesma faixa, adicione filtros nos ambientes se necessário.')

                # # Filter case 1 - end ##

                # New NetworkIPv6
                network_ip = NetworkIPv6()

                # Set block by network generated
                network_ip.block1, network_ip.block2, network_ip.block3, network_ip.block4, network_ip.block5, network_ip.block6, network_ip.block7, network_ip.block8 = str(
                    net.network.exploded).split(':')
                # Set block by network generated
                network_ip.block = net.prefixlen
                # Set mask by network generated
                network_ip.mask1, network_ip.mask2, network_ip.mask3, network_ip.mask4, network_ip.mask5, network_ip.mask6, network_ip.mask7, network_ip.mask8 = str(
                    net.netmask.exploded).split(':')

            # Get all vlans environments from equipments of the current
            # environment
            ambiente = vlan.ambiente

            equips = list()
            envs = list()
            envs_aux = list()

            for env in ambiente.equipamentoambiente_set.all():
                equips.append(env.equipamento)

            for equip in equips:
                for env in equip.equipamentoambiente_set.all():
                    if not env.ambiente_id in envs_aux:
                        envs.append(env.ambiente)
                        envs_aux.append(env.ambiente_id)

            # Check subnet's
            if version == IP_VERSION.IPv4[0]:
                expl = split(net.network.exploded, ".")
            else:
                expl = split(net.network.exploded, ":")

            expl.append(str(net.prefixlen))

            ids_exclude = []
            ids_all = []

            network_ip_verify = IPNetwork(network)
            for env in envs:
                for vlan_obj in env.vlan_set.all():
                    ids_all.append(vlan_obj.id)
                    is_subnet = verify_subnet(
                        vlan_obj, network_ip_verify, version)

                    if not is_subnet:
                        ids_exclude.append(vlan_obj.id)
                    else:
                        if ambiente.filter_id == None or vlan_obj.ambiente.filter_id == None or int(vlan_obj.ambiente.filter_id) != int(ambiente.filter_id):
                            pass
                        else:
                            ids_exclude.append(vlan_obj.id)

            # Ignore actual vlan
            if envs != [] and long(id_vlan) not in ids_exclude:
                ids_exclude.append(id_vlan)

            # Check if have duplicated vlan's with same net range in an
            # environment with shared equipment
            if len(ids_all) != len(ids_exclude):
                raise NetworkIPRangeEnvError(None)

            # Set Vlan
            network_ip.vlan = vlan

            # Set Network Type
            network_ip.network_type = net_type

            # Set Environment VIP
            network_ip.ambient_vip = env_vip

            # Persist
            try:

                # Delete vlan's cache
                destroy_cache_function([id_vlan])
                network_ip.save(user)

                list_equip_routers_ambient = EquipamentoAmbiente.objects.filter(
                    ambiente=network_ip.vlan.ambiente.id, is_router=True)

                if list_equip_routers_ambient:

                    if version == IP_VERSION.IPv4[0]:

                        if network_ip.block < 31:

                            # Add Adds the first available ipv4 on all equipment
                            # that is configured as a router for the environment
                            # related to network
                            ip = Ip.get_first_available_ip(network_ip.id)

                            ip = str(ip).split('.')

                            ip_model = Ip()
                            ip_model.oct1 = ip[0]
                            ip_model.oct2 = ip[1]
                            ip_model.oct3 = ip[2]
                            ip_model.oct4 = ip[3]
                            ip_model.networkipv4_id = network_ip.id

                            ip_model.save(user)

                            for equip in list_equip_routers_ambient:

                                IpEquipamento().create(
                                    user, ip_model.id, equip.equipamento.id)

                    else:
                        if network_ip.block < 127:

                            # Add Adds the first available ipv6 on all equipment
                            # that is configured as a router for the environment
                            # related to network
                            ipv6 = Ipv6.get_first_available_ip6(network_ip.id)

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
                            ipv6_model.networkipv6_id = network_ip.id

                            ipv6_model.save(user)

                            for equip in list_equip_routers_ambient:

                                Ipv6Equipament().create(
                                    user, ipv6_model.id, equip.equipamento.id)

            except Exception, e:
                raise IpError(e, u'Error persisting Network.')

            network_map = dict()
            network_map['id'] = network_ip.id
            network_map['rede'] = str(net)
            network_map[
                'broadcast'] = net.broadcast if net.version == 4 else ''
            network_map['mask'] = net.netmask.exploded
            network_map['id_vlan'] = vlan.id
            network_map['id_tipo_rede'] = net_type.id
            network_map[
                'id_ambiente_vip'] = env_vip.id if env_vip != None else ''
            network_map['active'] = network_ip

            # Return XML
            return self.response(dumps_networkapi({'network': network_map}))

        except NetworkIPRangeEnvError, e:
            return self.response_error(346)
        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.' % (e.param, e.value))
            return self.response_error(269, e.param, e.value)
        except NetworkTypeNotFoundError, e:
            self.log.error(u'The network_type parameter does not exist.')
            return self.response_error(111)
        except VlanNotFoundError, e:
            self.log.error(u'Vlan not found')
            return self.response_error(116)
        except EnvironmentVipNotFoundError, e:
            return self.response_error(283)
        except NetworkIPv4AddressNotAvailableError, e:
            return self.response_error(295)
        except NetworkIPv6AddressNotAvailableError, e:
            return self.response_error(296)
        except ConfigEnvironmentInvalidError, e:
            return self.response_error(294)
        except NetworkIpAddressNotAvailableError, e:
            return self.response_error(335)
        except (IpError, NetworkIPv6Error, NetworkIPv4Error, GrupoError, VlanError), e:
            return self.response_error(1)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)


def verify_subnet(vlan, network_ip, version):
    if version == IP_VERSION.IPv4[0]:
        vlan_net = vlan.networkipv4_set.all()
    else:
        vlan_net = vlan.networkipv6_set.all()

    # One vlan may have many networks, iterate over it
    for net in vlan_net:

        if version == IP_VERSION.IPv4[0]:
            ip = "%s.%s.%s.%s/%s" % (net.oct1,
                                     net.oct2, net.oct3, net.oct4, net.block)
        else:
            ip = "%s:%s:%s:%s:%s:%s:%s:%s/%d" % (net.block1, net.block2, net.block3,
                                                 net.block4, net.block5, net.block6, net.block7, net.block8, net.block)

        ip_net = IPNetwork(ip)
        # If some network, inside this vlan, is subnet of network search param
        if ip_net in network_ip:
            # This vlan must be in vlans founded, dont need to continue
            # checking
            return True
        # If some network, inside this vlan, is supernet of network search
        # param
        if network_ip in ip_net:
            # This vlan must be in vlans founded, dont need to continue
            # checking
            return True

    # If dont found any subnet return None
    return False
