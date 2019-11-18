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
from string import split

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import ConfigEnvironmentInvalidError
from networkapi.ambiente.models import ConfigEnvironment
from networkapi.ambiente.models import EnvironmentVip
from networkapi.ambiente.models import IP_VERSION
from networkapi.auth import has_perm
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.filterequiptype.models import FilterEquipType
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.ipaddr import IPNetwork
from networkapi.infrastructure.ipaddr import IPv4Network
from networkapi.infrastructure.ipaddr import IPv6Network
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpEquipamento
from networkapi.ip.models import IpError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import Ipv6Equipament
from networkapi.ip.models import NetworkIpAddressNotAvailableError
from networkapi.ip.models import NetworkIPRangeEnvError
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv4AddressNotAvailableError
from networkapi.ip.models import NetworkIPv4Error
from networkapi.ip.models import NetworkEnvironmentError
from networkapi.ip.models import NetworkSubnetRange
from networkapi.ip.models import NetworkIPv6
from networkapi.ip.models import NetworkIPv6AddressNotAvailableError
from networkapi.ip.models import NetworkIPv6Error
from networkapi.rest import RestResource
from networkapi.util import destroy_cache_function
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.vlan.models import NetworkTypeNotFoundError
from networkapi.vlan.models import TipoRede
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanNotFoundError
from networkapi.vlan.resource.VlanFindResource import break_network


class NetworkAddResource(RestResource):
    log = logging.getLogger('NetworkAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST requests to add new Network

        URL: network/add/
        """

        try:

            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            xml_map, attrs_map = loads(request.raw_post_data)

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
            cluster_unit = network_map.get('cluster_unit')

            try:
                net = IPNetwork(network)
            except ValueError:
                raise InvalidValueError(None, 'network', network)

            # Valid vlan ID
            if not is_valid_int_greater_zero_param(id_vlan):
                raise InvalidValueError(None, 'id_vlan', id_vlan)
            if not is_valid_int_greater_zero_param(network_type):
                raise InvalidValueError(None, 'id_network_type', network_type)

            vlan = Vlan().get_by_pk(id_vlan)
            net_type = TipoRede.get_by_pk(network_type)

            if environment_vip is not None:

                if not is_valid_int_greater_zero_param(environment_vip):
                    raise InvalidValueError(None, 'id_environment_vip', environment_vip)

                evips = EnvironmentVip.objects.all()
                evip_list = EnvironmentVip.available_evips(EnvironmentVip(), evips, int(id_vlan))

                # Check if the chose environment is in the same environment
                if any(int(environment_vip) == item['id'] for item in evip_list):
                    # Find Environment VIP by ID to check if it exist
                    env_vip = EnvironmentVip.get_by_pk(environment_vip)
                else:
                    raise InvalidValueError(None, 'id_environment_vip', environment_vip)

            else:
                env_vip = None

            # Check unchecked exception
            blocks, network, version = break_network(network)

            expl = split(net.network.exploded, '.' if version == IP_VERSION.IPv4[0] else ':')
            expl.append(str(net.prefixlen))

            if blocks != expl:
                raise InvalidValueError(None, 'rede', network)

            if version == IP_VERSION.IPv4[0]:

                # Find all networks related to environment
                nets = NetworkIPv4.objects.filter(vlan__ambiente__id=vlan.ambiente.id)

                # Cast to API class
                networks = set([IPv4Network('%d.%d.%d.%d/%d' % (net_ip.oct1, net_ip.oct2, net_ip.oct3, net_ip.oct4,
                                                                net_ip.block)) for net_ip in nets])

                # If network selected not in use
                for network_aux in networks:
                    if net in network_aux or network_aux in net:
                        self.log.debug('Network %s cannot be allocated. It conflicts with %s already '
                                       'in use in this environment.' % (net, network))
                        raise NetworkIPv4AddressNotAvailableError(
                            None, u'Network cannot be allocated. %s already in use in this environment.' % network_aux)

                if env_vip is not None:

                    # Find all networks related to environment vip
                    nets = NetworkIPv4.objects.filter(
                        ambient_vip__id=env_vip.id)

                    # Cast to API class
                    networks = set([IPv4Network('%d.%d.%d.%d/%d' % (net_ip.oct1, net_ip.oct2, net_ip.oct3,
                                                                    net_ip.oct4, net_ip.block)) for net_ip in nets])

                    # If there is already a network with the same  range ip as
                    # related the environment  vip
                    for network_aux in networks:
                        if net in network_aux or network_aux in net:
                            self.log.debug('Network %s cannot be allocated. It conflicts with %s already in use '
                                           'in this environment VIP.' % (net, network))
                            raise NetworkIPv4AddressNotAvailableError(None,
                                                                      u'Network cannot be allocated. %s already in use '
                                                                      u'in this environment VIP.' % network_aux)

                # Check if the new network is in the range of the Environment Network
                try:
                    vlan = Vlan().get_by_pk(id_vlan)
                    vlan_env_id = vlan.ambiente

                    try:
                        config_env = ConfigEnvironment()
                        environment_conf = config_env.get_by_environment(vlan_env_id)

                        if environment_conf:
                            for env_config in environment_conf:

                                ipconfig = env_config.ip_config
                                subnet = ipconfig.subnet

                            env_net = IPNetwork(subnet)

                            try:
                                if net in env_net:
                                    self.log.debug('Network "%s" can be allocated because is in the '
                                                   'environment network(%s) subnets.' % (net, subnet))

                                else:
                                    raise NetworkSubnetRange(None, 'A rede a ser cadastrada (%s) não pertence às '
                                                                   'subredes do ambiente (rede ambiente: %s). '
                                                                   'Cadastre o range desejado no '
                                                                   'ambiente.' % (net, subnet))

                            except NetworkSubnetRange:
                                self.log.error('Network "%s" can not be allocated because is not in the '
                                               'environment network(%s) subnets.' % (net, subnet))
                                return self.response_error(414)

                        else:
                            raise NetworkEnvironmentError(None, 'O ambiente não está configurado. '
                                                                'É necessário efetuar a configuração.')

                    except NetworkEnvironmentError:
                        self.log.error('The environment does not have a registered network')
                        return self.response_error(415)

                except Exception as ERROR:
                    self.log.error(ERROR)

                # # Filter case 1 - Adding new network with same ip range to another network on other environment ##
                # Get environments with networks with the same ip range
                nets = NetworkIPv4.objects.filter(oct1=expl[0], oct2=expl[1], oct3=expl[2],
                                                  oct4=expl[3], block=expl[4])
                env_ids = list()
                for net_ip in nets:
                    env_ids.append(net_ip.vlan.ambiente.id)

                # If other network with same ip range exists
                if len(env_ids) > 0:

                    # Get equipments related to this network's environment
                    env_equips = EquipamentoAmbiente.objects.filter(ambiente=vlan.ambiente.id)

                    # Verify equipments related with all other environments
                    # that contains networks with same ip range
                    for env_id in env_ids:
                        # Equipments related to other environments
                        other_env_equips = EquipamentoAmbiente.objects.filter(ambiente=env_id)
                        # Adjust to equipments
                        equip_list = list()
                        for equip_env in other_env_equips:
                            equip_list.append(equip_env.equipamento.id)

                        for env_equip in env_equips:
                            if env_equip.equipamento.id in equip_list:

                                # Filter testing
                                if other_env_equips[0].ambiente.filter is None or vlan.ambiente.filter is None:
                                    raise NetworkIPRangeEnvError(None,
                                                                 u'Um dos equipamentos associados com o ambiente '
                                                                 u'desta rede também está associado com outro ambiente '
                                                                 u'que tem uma rede com essa mesma faixa, adicione '
                                                                 u'filtros nos ambientes se necessário.')
                                else:
                                    # Test both environment's filters
                                    tp_equip_list_one = list()
                                    for fet in FilterEquipType.objects.filter(filter=vlan.ambiente.filter.id):
                                        tp_equip_list_one.append(fet.equiptype)

                                    tp_equip_list_two = list()
                                    for fet in FilterEquipType.objects.filter(
                                            filter=other_env_equips[0].ambiente.filter.id):
                                        tp_equip_list_two.append(fet.equiptype)

                                    if env_equip.equipamento.tipo_equipamento not in tp_equip_list_one or \
                                            env_equip.equipamento.tipo_equipamento not in tp_equip_list_two:
                                        raise NetworkIPRangeEnvError(None, u'Um dos equipamentos associados com o '
                                                                           u'ambiente desta rede também está associado '
                                                                           u'com outro ambiente que tem uma rede com '
                                                                           u'essa mesma faixa, adicione filtros nos '
                                                                           u'ambientes se necessário.')

                # # Filter case 1 - end ##

                # New NetworkIPv4
                network_ip = NetworkIPv4()

                network_ip.oct1, network_ip.oct2, network_ip.oct3, network_ip.oct4 = str(net.network).split('.')
                network_ip.block = net.prefixlen
                network_ip.mask_oct1, network_ip.mask_oct2, network_ip.mask_oct3, network_ip.mask_oct4 = \
                    str(net.netmask).split('.')
                network_ip.broadcast = net.broadcast.compressed

            else:
                # Find all networks ralated to environment
                nets = NetworkIPv6.objects.filter(vlan__ambiente__id=vlan.ambiente.id)

                networks = set([IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%d' % (net_ip.block1, net_ip.block2,
                                                                            net_ip.block3, net_ip.block4,
                                                                            net_ip.block5, net_ip.block6,
                                                                            net_ip.block7, net_ip.block8,
                                                                            net_ip.block)) for net_ip in nets])

                # If network selected not in use
                for network_aux in networks:
                    if net in network_aux or network_aux in net:
                        self.log.debug('Network %s cannot be allocated. It conflicts with %s already in use '
                                       'in this environment.' % (net, network))
                        raise NetworkIPv4AddressNotAvailableError(None, u'Network cannot be allocated. %s already in '
                                                                        u'use in this environment.' % network_aux)

                if env_vip is not None:

                    # Find all networks related to environment vip
                    nets = NetworkIPv6.objects.filter(
                        ambient_vip__id=env_vip.id)

                    networks = set([IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%d' % (net_ip.block1, net_ip.block2,
                                                                                net_ip.block3, net_ip.block4,
                                                                                net_ip.block5, net_ip.block6,
                                                                                net_ip.block7, net_ip.block8,
                                                                                net_ip.block)) for net_ip in nets])

                    # If there is already a network with the same  range ip as
                    # related the environment  vip
                    for network_aux in networks:
                        if net in network_aux or network_aux in net:
                            self.log.debug('Network %s cannot be allocated. It conflicts with %s already in '
                                           'use in this environment VIP.' % (net, network))
                            raise NetworkIPv4AddressNotAvailableError(None, u'Network cannot be allocated. %s '
                                                                            u'already in use in this environment '
                                                                            u'VIP.' % network_aux)

                # # Filter case 1 - Adding new network with same ip range to another network on other environment ##
                # Get environments with networks with the same ip range
                nets = NetworkIPv6.objects.filter(block1=expl[0], block2=expl[1], block3=expl[2], block4=expl[3],
                                                  block5=expl[4], block6=expl[5], block7=expl[6], block8=expl[7],
                                                  block=expl[8])
                env_ids = list()
                for net_ip in nets:
                    env_ids.append(net_ip.vlan.ambiente.id)

                # If other network with same ip range exists
                if len(env_ids) > 0:

                    # Get equipments related to this network's environment
                    env_equips = EquipamentoAmbiente.objects.filter(ambiente=vlan.ambiente.id)

                    # Verify equipments related with all other environments
                    # that contains networks with same ip range
                    for env_id in env_ids:
                        # Equipments related to other environments
                        other_env_equips = EquipamentoAmbiente.objects.filter(ambiente=env_id)
                        # Adjust to equipments
                        equip_list = list()
                        for equip_env in other_env_equips:
                            equip_list.append(equip_env.equipamento.id)

                        for env_equip in env_equips:
                            if env_equip.equipamento.id in equip_list:

                                # Filter testing
                                if other_env_equips[0].ambiente.filter is None or vlan.ambiente.filter is None:
                                    raise NetworkIPRangeEnvError(None, u'Um dos equipamentos associados com o '
                                                                       u'ambiente desta rede também está associado '
                                                                       u'com outro ambiente que tem uma rede com '
                                                                       u'essa mesma faixa, adicione filtros nos '
                                                                       u'ambientes se necessário.')
                                else:
                                    # Test both environment's filters
                                    tp_equip_list_one = list()
                                    for fet in FilterEquipType.objects.filter(filter=vlan.ambiente.filter.id):
                                        tp_equip_list_one.append(fet.equiptype)

                                    tp_equip_list_two = list()
                                    for fet in FilterEquipType.objects.filter(
                                            filter=other_env_equips[0].ambiente.filter.id):
                                        tp_equip_list_two.append(fet.equiptype)

                                    if env_equip.equipamento.tipo_equipamento not in tp_equip_list_one or \
                                            env_equip.equipamento.tipo_equipamento not in tp_equip_list_two:
                                        raise NetworkIPRangeEnvError(None, u'Um dos equipamentos associados com o '
                                                                           u'ambiente desta rede também está '
                                                                           u'associado com outro ambiente que tem '
                                                                           u'uma rede com essa mesma faixa, adicione '
                                                                           u'filtros nos ambientes se necessário.')

                # # Filter case 1 - end ##

                # New NetworkIPv6
                network_ip = NetworkIPv6()
                network_ip.block1, network_ip.block2, network_ip.block3, network_ip.block4, network_ip.block5, \
                    network_ip.block6, network_ip.block7, network_ip.block8 = str(net.network.exploded).split(':')
                network_ip.block = net.prefixlen
                network_ip.mask1, network_ip.mask2, network_ip.mask3, network_ip.mask4, network_ip.mask5, \
                    network_ip.mask6, network_ip.mask7, network_ip.mask8 = str(net.netmask.exploded).split(':')

            # Get all vlans environments from equipments of the current
            # environment
            ambiente = vlan.ambiente

            equips = list()
            envs = list()

            # equips = all equipments from the environment which this network
            # is about to be allocated on
            for env in ambiente.equipamentoambiente_set.all():
                equips.append(env.equipamento)

            # envs = all environments from all equips above
            # This will be used to test all networks from the environments.
            for equip in equips:
                for env in equip.equipamentoambiente_set.all():
                    if env.ambiente not in envs:
                        envs.append(env.ambiente)

            network_ip_verify = IPNetwork(network)

            # For all vlans in all common environments,
            # check if any network is a subnetwork or supernetwork
            # of the desired network network_ip_verify
            for env in envs:
                for vlan_obj in env.vlan_set.all():

                    is_subnet = verify_subnet(vlan_obj, network_ip_verify, version)

                    if is_subnet:
                        if vlan_obj.ambiente == ambiente:
                            raise NetworkIPRangeEnvError(None)

                        if ambiente.filter_id is None or vlan_obj.ambiente.filter_id is None or \
                                int(vlan_obj.ambiente.filter_id) != int(ambiente.filter_id):
                            raise NetworkIPRangeEnvError(None)

            network_ip.vlan = vlan
            network_ip.network_type = net_type
            network_ip.ambient_vip = env_vip
            network_ip.cluster_unit = cluster_unit

            try:

                destroy_cache_function([id_vlan])
                network_ip.save()

                list_equip_routers_ambient = EquipamentoAmbiente.objects.filter(ambiente=network_ip.vlan.ambiente.id,
                                                                                is_router=True)

                if list_equip_routers_ambient:
                    if version == IP_VERSION.IPv4[0]:
                        if network_ip.block < 31:

                            # Add the first available ipv4 on all equipment
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

                            ip_model.save()

                            if len(list_equip_routers_ambient) > 1 and network_ip.block < 30:
                                multiple_ips = True
                            else:
                                multiple_ips = False

                            logging.debug('vxlan: %s' % vlan.vxlan)

                            if vlan.vxlan:

                                logging.debug('vxlan ok')
                                for equip in list_equip_routers_ambient:
                                    IpEquipamento().create(user, ip_model.id, equip.equipamento.id)

                                if multiple_ips:
                                    debug_ip = Ip.get_first_available_ip(network_ip.id, True)

                                    ips = Ip()
                                    ips.oct1, ips.oct2, ips.oct3, ips.oct4 = str(debug_ip).split('.')
                                    ips.networkipv4_id = network_ip.id
                                    ips.descricao = "IP alocado para debug"
                                    ips.save(user)

                                    IpEquipamento().create(user, ips.id, list_equip_routers_ambient[0].equipamento.id)

                            else:

                                for equip in list_equip_routers_ambient:
                                    IpEquipamento().create(user, ip_model.id, equip.equipamento.id)

                                    if multiple_ips:
                                        router_ip = Ip.get_first_available_ip(network_ip.id, True)
                                        router_ip = str(router_ip).split('.')
                                        ip_model2 = Ip()
                                        ip_model2.oct1 = router_ip[0]
                                        ip_model2.oct2 = router_ip[1]
                                        ip_model2.oct3 = router_ip[2]
                                        ip_model2.oct4 = router_ip[3]
                                        ip_model2.networkipv4_id = network_ip.id
                                        ip_model2.save(user)
                                        IpEquipamento().create(user, ip_model2.id, equip.equipamento.id)

                    else:
                        if network_ip.block < 127:

                            # Add the first available ipv6 on all equipment
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

                            ipv6_model.save()

                            if len(list_equip_routers_ambient) > 1 and network_ip.block < 126:
                                multiple_ips = True
                            else:
                                multiple_ips = False

                            if vlan.vxlan:

                                for equip in list_equip_routers_ambient:
                                    Ipv6Equipament().create(user, ipv6_model.id, equip.equipamento.id)

                                if multiple_ips:
                                    router_ip = Ipv6.get_first_available_ip6(network_ip.id, True)

                                    ipv6s = Ipv6()
                                    ipv6s.block1, ipv6s.block2, ipv6s.block3, ipv6s.block4, ipv6s.block5, \
                                        ipv6s.block6, ipv6s.block7, ipv6s.block8 = str(router_ip).split(':')
                                    ipv6s.networkipv6_id = network_ip.id
                                    ipv6s.descricao = "IPv6 alocado para debug"
                                    ipv6s.save(user)

                                    Ipv6Equipament().create(user, ipv6s.id,
                                                            list_equip_routers_ambient[0].equipamento.id)

                            else:

                                for equip in list_equip_routers_ambient:
                                    Ipv6Equipament().create(user, ipv6_model.id, equip.equipamento.id)

                                    if multiple_ips:
                                        router_ip = Ipv6.get_first_available_ip6(network_ip.id, True)
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
                                        ipv6_model2.networkipv6_id = network_ip.id
                                        ipv6_model2.save(user)
                                        Ipv6Equipament().create(user, ipv6_model2.id, equip.equipamento.id)

            except Exception as e:
                raise IpError(e, u'Error persisting Network.')

            network_map = dict()
            network_map['id'] = network_ip.id
            network_map['rede'] = str(net)
            network_map['broadcast'] = net.broadcast if net.version == 4 else ''
            network_map['mask'] = net.netmask.exploded
            network_map['id_vlan'] = vlan.id
            network_map['id_tipo_rede'] = net_type.id
            network_map['id_ambiente_vip'] = env_vip.id if env_vip is not None else ''
            network_map['active'] = network_ip

            return self.response(dumps_networkapi({'network': network_map}))

        except NetworkIPRangeEnvError:
            return self.response_error(346)
        except InvalidValueError as e:
            self.log.error(u'Parameter %s is invalid. Value: %s.' % (e.param, e.value))
            return self.response_error(269, e.param, e.value)
        except NetworkTypeNotFoundError:
            self.log.error(u'The network_type parameter does not exist.')
            return self.response_error(111)
        except VlanNotFoundError:
            self.log.error(u'Vlan not found')
            return self.response_error(116)
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except NetworkIPv4AddressNotAvailableError:
            return self.response_error(295)
        except NetworkIPv6AddressNotAvailableError:
            return self.response_error(296)
        except ConfigEnvironmentInvalidError:
            return self.response_error(294)
        except NetworkIpAddressNotAvailableError:
            return self.response_error(335)
        except (IpError, NetworkIPv6Error, NetworkIPv4Error, GrupoError, VlanError):
            return self.response_error(1)
        except XMLError as e:
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
            ip = '%s.%s.%s.%s/%s' % (net.oct1,
                                     net.oct2, net.oct3, net.oct4, net.block)
        else:
            ip = '%s:%s:%s:%s:%s:%s:%s:%s/%d' % (net.block1, net.block2, net.block3,
                                                 net.block4, net.block5, net.block6,
                                                 net.block7, net.block8, net.block)

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
