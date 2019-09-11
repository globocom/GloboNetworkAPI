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

from django.db import transaction
from django.template import Context
from django.template import Template

from networkapi.api_deploy.facade import deploy_config_in_equipment_synchronous
from networkapi.api_interface import exceptions as exceptions_interface
from networkapi.api_network import exceptions
from networkapi.api_network.facade.v3 import utils
from networkapi.api_network.models import DHCPRelayIPv4
from networkapi.api_network.models import DHCPRelayIPv6
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_DCHCPv4_NET
from networkapi.distributedlock import LOCK_DCHCPv6_NET
from networkapi.distributedlock import LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT
from networkapi.distributedlock import LOCK_NETWORK_IPV4
from networkapi.distributedlock import LOCK_NETWORK_IPV6
from networkapi.distributedlock import LOCK_VLAN
from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.extra_logging import local
from networkapi.extra_logging import NO_REQUEST_ID
from networkapi.ip.models import Ip
from networkapi.ip.models import IpEquipamento
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import Ipv6Equipament
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv6
from networkapi.plugins.factory import PluginFactory
from networkapi.settings import NETWORK_CONFIG_FILES_PATH
from networkapi.settings import NETWORK_CONFIG_TEMPLATE_PATH
from networkapi.settings import NETWORK_CONFIG_TOAPPLY_REL_PATH


log = logging.getLogger(__name__)

TEMPLATE_NETWORKv4_ACTIVATE = 'ipv4_activate_network_configuration'
TEMPLATE_NETWORKv4_DEACTIVATE = 'ipv4_deactivate_network_configuration'
TEMPLATE_NETWORKv6_ACTIVATE = 'ipv6_activate_network_configuration'
TEMPLATE_NETWORKv6_DEACTIVATE = 'ipv6_deactivate_network_configuration'


def create_dhcprelayIPv4_object(user, ipv4_id, networkipv4_id):

    with distributedlock(LOCK_DCHCPv4_NET % networkipv4_id):
        dhcprelay_obj = DHCPRelayIPv4()
        dhcprelay_obj.create(ipv4_id, networkipv4_id)
        dhcprelay_obj.save()
        return dhcprelay_obj


def create_dhcprelayIPv6_object(user, ipv6_id, networkipv6_id):

    with distributedlock(LOCK_DCHCPv6_NET % networkipv6_id):
        dhcprelay_obj = DHCPRelayIPv6()
        dhcprelay_obj.create(ipv6_id, networkipv6_id)
        dhcprelay_obj.save()
        return dhcprelay_obj


def delete_dhcprelayipv4(user, dhcprelayipv4_id):

    dhcprelayipv4_obj = DHCPRelayIPv4.get_by_pk(id=dhcprelayipv4_id)

    with distributedlock(LOCK_NETWORK_IPV4 % dhcprelayipv4_obj.networkipv4.id):
        if not dhcprelayipv4_obj.networkipv4.active:
            dhcprelayipv4_obj.delete()
            return True
        else:
            raise exceptions.CannotRemoveDHCPRelayFromActiveNetwork()


def delete_dhcprelayipv6(user, dhcprelayipv6_id):

    dhcprelayipv6_obj = DHCPRelayIPv6.get_by_pk(id=dhcprelayipv6_id)

    with distributedlock(LOCK_NETWORK_IPV6 % dhcprelayipv6_obj.networkipv6.id):
        if not dhcprelayipv6_obj.networkipv6.active:
            dhcprelayipv6_obj.delete()
            return True
        else:
            raise exceptions.CannotRemoveDHCPRelayFromActiveNetwork()


def deploy_networkIPv4_configuration(user, networkipv4, equipment_list):
    """Loads template for creating Network IPv4 equipment configuration, creates file and
    apply config.

    Args: equipment_list: NetworkIPv4 object
    equipment_list: Equipamento objects list

    Returns: List with status of equipments output
    """
    log.info("deploy_networkIPv4_configuration")

    data = dict()
    # lock network id to prevent multiple requests to same id
    with distributedlock(LOCK_NETWORK_IPV4 % networkipv4.id):
        with distributedlock(LOCK_VLAN % networkipv4.vlan.id):
            if networkipv4.active == 1:
                data['output'] = 'Network already active. Nothing to do.'
                return data

            # load dict with all equipment attributes
            dict_ips = get_dict_v4_to_use_in_configuration_deploy(
                user, networkipv4, equipment_list)
            status_deploy = dict()
            # TODO implement threads
            for equipment in equipment_list:
                # generate config file
                file_to_deploy = _generate_config_file(
                    dict_ips, equipment, TEMPLATE_NETWORKv4_ACTIVATE)
                # deploy config file in equipments
                lockvar = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % (
                    equipment.id)
                status_deploy[equipment.id] = \
                    deploy_config_in_equipment_synchronous(
                        file_to_deploy, equipment, lockvar)

            networkipv4.activate(user)
            transaction.commit()

            if networkipv4.vlan.ativada == 0:
                networkipv4.vlan.activate(user)

            return status_deploy


def deploy_networkIPv6_configuration(user, networkipv6, equipment_list):
    """Loads template for creating Network IPv6 equipment configuration, creates file and
    apply config.

    Args: NetworkIPv6 object
    Equipamento objects list

    Returns: List with status of equipments output
    """

    data = dict()
    # lock network id to prevent multiple requests to same id
    with distributedlock(LOCK_NETWORK_IPV6 % networkipv6.id):
        with distributedlock(LOCK_VLAN % networkipv6.vlan.id):
            if networkipv6.active == 1:
                data['output'] = 'Network already active. Nothing to do.'
                return data

            # load dict with all equipment attributes
            dict_ips = get_dict_v6_to_use_in_configuration_deploy(
                user, networkipv6, equipment_list)
            status_deploy = dict()
            # TODO implement threads
            for equipment in equipment_list:
                # generate config file
                file_to_deploy = _generate_config_file(
                    dict_ips, equipment, TEMPLATE_NETWORKv6_ACTIVATE)
                # deploy config file in equipments
                lockvar = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % (
                    equipment.id)
                status_deploy[equipment.id] = deploy_config_in_equipment_synchronous(
                    file_to_deploy, equipment, lockvar)

            networkipv6.activate(user)
            transaction.commit()
            if networkipv6.vlan.ativada == 0:
                networkipv6.vlan.activate(user)

            return status_deploy


def remove_deploy_networkIPv4_configuration(user, networkipv4, equipment_list):
    """Loads template for removing Network IPv4 equipment configuration, creates file and
    apply config.

    Args: NetworkIPv4 object
    Equipamento objects list

    Returns: List with status of equipments output
    """

    data = dict()

    # lock network id to prevent multiple requests to same id
    with distributedlock(LOCK_NETWORK_IPV4 % networkipv4.id):
        with distributedlock(LOCK_VLAN % networkipv4.vlan.id):
            if networkipv4.active == 0:
                data['output'] = 'Network already not active. Nothing to do.'
                return data

            # load dict with all equipment attributes
            dict_ips = get_dict_v4_to_use_in_configuration_deploy(
                user, networkipv4, equipment_list)
            status_deploy = dict()
            # TODO implement threads
            for equipment in equipment_list:
                # generate config file
                file_to_deploy = _generate_config_file(
                    dict_ips, equipment, TEMPLATE_NETWORKv4_DEACTIVATE)
                # deploy config file in equipments
                lockvar = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % (
                    equipment.id)
                status_deploy[equipment.id] = deploy_config_in_equipment_synchronous(
                    file_to_deploy, equipment, lockvar)
            networkipv4.deactivate(user)
            transaction.commit()
            if networkipv4.vlan.ativada == 1:
                # if there are no other networks active in vlan, remove int
                # vlan
                if not _has_active_network_in_vlan(networkipv4.vlan):
                    # remove int vlan
                    for equipment in equipment_list:
                        if equipment.maintenance is not True:
                            status_deploy[
                                equipment.id] += _remove_svi(equipment, networkipv4.vlan.num_vlan)
                    networkipv4.vlan.remove(user)

            return status_deploy


def remove_deploy_networkIPv6_configuration(user, networkipv6, equipment_list):
    """Loads template for removing Network IPv6 equipment configuration, creates file and
    apply config.

    Args: NetworkIPv6 object
    Equipamento objects list

    Returns: List with status of equipments output
    """

    data = dict()

    # lock network id to prevent multiple requests to same id
    with distributedlock(LOCK_NETWORK_IPV6 % networkipv6.id):
        with distributedlock(LOCK_VLAN % networkipv6.vlan.id):
            if networkipv6.active == 0:
                data['output'] = 'Network already not active. Nothing to do.'
                return data

            # load dict with all equipment attributes
            dict_ips = get_dict_v6_to_use_in_configuration_deploy(
                user, networkipv6, equipment_list)
            status_deploy = dict()
            # TODO implement threads
            for equipment in equipment_list:
                # generate config file
                file_to_deploy = _generate_config_file(
                    dict_ips, equipment, TEMPLATE_NETWORKv6_DEACTIVATE)
                # deploy config file in equipments
                lockvar = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % (
                    equipment.id)
                status_deploy[equipment.id] = deploy_config_in_equipment_synchronous(
                    file_to_deploy, equipment, lockvar)

            networkipv6.deactivate(user)
            transaction.commit()
            if networkipv6.vlan.ativada == 1:
                # if there are no other networks active in vlan, remove int
                # vlan
                if not _has_active_network_in_vlan(networkipv6.vlan):
                    # remove int vlan
                    for equipment in equipment_list:
                        if equipment.maintenance is not True:
                            status_deploy[
                                equipment.id] += _remove_svi(equipment, networkipv6.vlan.num_vlan)
                    networkipv6.vlan.remove(user)

            return status_deploy


def _generate_config_file(dict_ips, equipment, template_type):
    """Load a template and write a file with the rended output

    Args: 2-dimension dictionary with equipments information for template rendering
    equipment to render template to
    template type to load

    Returns: filename with relative path to settings.TFTPBOOT_FILES_PATH
    """

    config_to_be_saved = ''
    request_id = getattr(local, 'request_id', NO_REQUEST_ID)
    filename_out = 'network_equip' + \
        str(equipment.id) + '_config_' + str(request_id)
    filename_to_save = NETWORK_CONFIG_FILES_PATH + filename_out
    rel_file_to_deploy = NETWORK_CONFIG_TOAPPLY_REL_PATH + filename_out

    try:
        network_template_file = _load_template_file(equipment, template_type)
        key_dict = _generate_template_dict(dict_ips, equipment)
        config_to_be_saved += network_template_file.render(Context(key_dict))
    except KeyError, exception:
        log.error('Erro: %s ' % exception)
        raise exceptions_interface.InvalidKeyException(exception)

    # Save new file
    try:
        file_handle = open(filename_to_save, 'w')
        file_handle.write(config_to_be_saved)
        file_handle.close()
    except IOError, e:
        log.error('Error writing to config file: %s' % filename_to_save)
        raise e

    return rel_file_to_deploy


def _generate_template_dict(dict_ips, equipment):
    """Creates a 1-dimension dictionary from a 2 dimension with equipment information

    Args: dict_ips dictionary for template rendering
    equipment to create dictionary to

    Returns: 1-dimension dictionary to use in template rendering for equipment
    """

    key_dict = dict()

    # TODO Separate differet vendor support if needed for gateway redundancy
    key_dict['VLAN_NUMBER'] = dict_ips['vlan_num']
    key_dict['VLAN_NAME'] = dict_ips['vlan_name']
    key_dict['IP'] = dict_ips[equipment].get('ip')
    key_dict['USE_GW_RED'] = dict_ips['gateway_redundancy']
    key_dict['GW_RED_ADDR'] = dict_ips['gateway']
    key_dict['GW_RED_PRIO'] = dict_ips[equipment].get('prio')
    key_dict['CIDR_BLOCK'] = dict_ips['cidr_block']
    key_dict['NETWORK_MASK'] = dict_ips['mask']
    key_dict['NETWORK_WILDMASK'] = dict_ips['wildmask']
    key_dict['IP_VERSION'] = dict_ips['ip_version']
    key_dict['FIRST_NETWORK'] = dict_ips['first_network']

    if dict_ips['is_vxlan']:
        key_dict['VXLAN'] = dict_ips.get('is_vxlan')
        key_dict['VXLAN_ANYCAST_IP'] = utils.get_local_tunnel_ip(equipment.id)

    if 'vrf' in dict_ips.keys():
        key_dict['VRF'] = dict_ips['vrf']

    if 'dhcprelay_list' in dict_ips.keys():
        key_dict['DHCPRELAY_LIST'] = dict_ips['dhcprelay_list']
    else:
        key_dict['DHCPRELAY_LIST'] = []
    # key_dict["ACL_IN"] = ""
    # key_dict["ACL_OUT"] = ""

    return key_dict


def get_dict_v4_to_use_in_configuration_deploy(user, networkipv4, equipment_list):
    """
    Generate dictionary with vlan an IP information to be used to generate
    template dict for equipment configuration

    Args: networkipv4 NetworkIPv4 object
    equipment_list: Equipamento objects list

    Returns: 2-dimension dictionary with equipments information for template rendering
    """

    log.info("get_dict_v4_to_use_in_configuration_deploy")
    
    try:
        gateway_ip = Ip.get_by_octs_and_net(networkipv4.oct1,
                                            networkipv4.oct2,
                                            networkipv4.oct3,
                                            networkipv4.oct4 + 1,
                                            networkipv4)
    except IpNotFoundError:
        log.error('Equipment IPs not correctly registered. '
                  'Router equipments should have first IP of network allocated for them.')
        raise exceptions.IncorrectRedundantGatewayRegistryException()

    ips = IpEquipamento.objects.filter(ip=gateway_ip,
                                       equipamento__in=equipment_list)

    if len(ips) != len(equipment_list):
        log.error('Equipment IPs not correctly registered. '
                  'Router equipments should have first IP of network allocated for them.')
        raise exceptions.IncorrectRedundantGatewayRegistryException()

    dict_ips = dict()
    if networkipv4.vlan.vrf and networkipv4.vlan.vrf:
        dict_ips['vrf'] = networkipv4.vlan.vrf
    elif networkipv4.vlan.ambiente.vrf and networkipv4.vlan.ambiente.vrf:
        dict_ips['vrf'] = networkipv4.vlan.ambiente.vrf

    # DHCPRelay list
    dhcprelay_list = DHCPRelayIPv4.objects.filter(networkipv4=networkipv4)
    if len(dhcprelay_list) > 0:
        dict_ips['dhcprelay_list'] = []
        for dhcprelay in dhcprelay_list:
            ipv4 = '%s.%s.%s.%s' % (
                dhcprelay.ipv4.oct1, dhcprelay.ipv4.oct2, dhcprelay.ipv4.oct3, dhcprelay.ipv4.oct4)
            dict_ips['dhcprelay_list'].append(ipv4)

    dict_ips['gateway'] = '%d.%d.%d.%d' % (gateway_ip.oct1,
                                           gateway_ip.oct2,
                                           gateway_ip.oct3,
                                           gateway_ip.oct4)
    dict_ips['ip_version'] = 'IPV4'
    dict_ips['equipments'] = dict()
    dict_ips['vlan_num'] = networkipv4.vlan.num_vlan
    dict_ips['vlan_name'] = networkipv4.vlan.nome
    dict_ips['cidr_block'] = networkipv4.block
    dict_ips['mask'] = '%d.%d.%d.%d' % (networkipv4.mask_oct1,
                                        networkipv4.mask_oct2,
                                        networkipv4.mask_oct3,
                                        networkipv4.mask_oct4)
    dict_ips['wildmask'] = '%d.%d.%d.%d' % (255 - networkipv4.mask_oct1,
                                            255 - networkipv4.mask_oct2,
                                            255 - networkipv4.mask_oct3,
                                            255 - networkipv4.mask_oct4)

    if _has_active_network_in_vlan(networkipv4.vlan):
        dict_ips['first_network'] = False
    else:
        dict_ips['first_network'] = True

    is_vxlan = networkipv4.vlan.ambiente.vxlan
    dict_ips['is_vxlan'] = is_vxlan

    log.debug("is_vxlan: %s" % is_vxlan)

    # Check IPs for routers when there are multiple gateways
    if len(equipment_list) > 1 and not is_vxlan:
        dict_ips['gateway_redundancy'] = True
        equip_number = 0
        for equipment in equipment_list:
            ip_equip = IpEquipamento.objects.filter(equipamento=equipment, ip__networkipv4=networkipv4)\
                .exclude(ip=gateway_ip).select_related('ip')
            if not ip_equip:
                log.error('Error: Equipment IPs not correctly registered. '
                          'In case of multiple gateways, they should have an '
                          'IP other than the gateway registered.')
                raise exceptions.IncorrectNetworkRouterRegistryException()
            ip = ip_equip[0].ip
            dict_ips[equipment] = dict()
            dict_ips[equipment]['ip'] = '%s.%s.%s.%s' % (ip.oct1, ip.oct2, ip.oct3, ip.oct4)
            dict_ips[equipment]['prio'] = 100 + equip_number
            equip_number += 1
    elif is_vxlan:
        dict_ips['gateway_redundancy'] = True
        for equipment in equipment_list:
            dict_ips[equipment] = dict()
            dict_ips[equipment]['local_tunnel_ip'] = utils.get_local_tunnel_ip(equipment)
    else:
        dict_ips['gateway_redundancy'] = False
        dict_ips[equipment_list[0]] = dict()
        dict_ips[equipment_list[0]]['ip'] = dict_ips['gateway']
        dict_ips[equipment_list[0]]['prio'] = 100

    return dict_ips


def get_dict_v6_to_use_in_configuration_deploy(user, networkipv6, equipment_list):
    """Generate dictionary with vlan an IP information to be used to generate
    template dict for equipment configuration

    Args: networkipv4 NetworkIPv4 object
    equipment_list: Equipamento objects list

    Returns: 2-dimension dictionary with equipments information for template rendering
    """

    try:
        gateway_ip = Ipv6.get_by_blocks_and_net(
            '{0:0{1}x}'.format(int(networkipv6.block1, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block2, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block3, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block4, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block5, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block6, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block7, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block8, 16) + 1, 4),
            networkipv6)
    except IpNotFoundError:
        log.error('Equipment IPs not correctly registered. \
            Router equipments should have first IP of network allocated for them.')
        raise exceptions.IncorrectRedundantGatewayRegistryException()

    ips = Ipv6Equipament.objects.filter(
        ip=gateway_ip, equipamento__in=equipment_list)
    if len(ips) != len(equipment_list):
        log.error('Equipment IPs not correctly registered. \
            Router equipments should have first IP of network allocated for them.')
        raise exceptions.IncorrectRedundantGatewayRegistryException()

    dict_ips = dict()
    if networkipv6.vlan.vrf is not None and networkipv6.vlan.vrf is not '':
        dict_ips['vrf'] = networkipv6.vlan.vrf
    elif networkipv6.vlan.ambiente.vrf is not None:
        dict_ips['vrf'] = networkipv6.vlan.ambiente.vrf

    dict_ips['gateway'] = '%s:%s:%s:%s:%s:%s:%s:%s' % (gateway_ip.block1, gateway_ip.block2, gateway_ip.block3,
                                                       gateway_ip.block4, gateway_ip.block5, gateway_ip.block6, gateway_ip.block7, gateway_ip.block8)
    dict_ips['ip_version'] = 'IPV6'
    dict_ips['equipments'] = dict()
    dict_ips['vlan_num'] = networkipv6.vlan.num_vlan
    dict_ips['vlan_name'] = networkipv6.vlan.nome
    dict_ips['cidr_block'] = networkipv6.block
    dict_ips['mask'] = '%s:%s:%s:%s:%s:%s:%s:%s' % (networkipv6.mask1, networkipv6.mask2, networkipv6.mask3,
                                                    networkipv6.mask4, networkipv6.mask5, networkipv6.mask6, networkipv6.mask7, networkipv6.mask8)
    dict_ips['wildmask'] = 'Not used'

    if _has_active_network_in_vlan(networkipv6.vlan):
        dict_ips['first_network'] = False
    else:
        dict_ips['first_network'] = True

    is_vxlan = networkipv6.vlan.ambiente.vxlan
    dict_ips['is_vxlan'] = is_vxlan

    log.debug("is_vxlan: %s" % is_vxlan)

    # Check IPs for routers when there are multiple gateways
    if len(equipment_list) > 1 and not is_vxlan:
        dict_ips['gateway_redundancy'] = True
        equip_number = 0
        for equipment in equipment_list:
            ip_equip = Ipv6Equipament.objects.filter(equipamento=equipment, ip__networkipv6=networkipv6).exclude(ip=gateway_ip)\
                .select_related('ip')
            if not ip_equip:
                log.error('Error: Equipment IPs not correctly registered. \
                    In case of multiple gateways, they should have an IP other than the gateway registered.')
                raise exceptions.IncorrectNetworkRouterRegistryException()
            ip = ip_equip[0].ip
            dict_ips[equipment] = dict()
            dict_ips[equipment]['ip'] = '%s:%s:%s:%s:%s:%s:%s:%s' % (
                ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8)
            dict_ips[equipment]['prio'] = 100 + equip_number
            equip_number += 1
    elif is_vxlan:
        dict_ips['gateway_redundancy'] = True
        for equipment in equipment_list:
            dict_ips[equipment] = dict()
            dict_ips[equipment]['local_tunnel_ip'] = utils.get_local_tunnel_ip(equipment)
    else:
        dict_ips['gateway_redundancy'] = False
        dict_ips[equipment_list[0]] = dict()
        dict_ips[equipment_list[0]]['ip'] = dict_ips['gateway']
        dict_ips[equipment_list[0]]['prio'] = 100

    return dict_ips


def _has_active_network_in_vlan(vlan):
    """Check if there are any other active network in the vlan
    this is used because some equipments remove all the L3 config
    when applying some commands, so they can only be applyed at the first time
    or to remove interface vlan configuration

    Args: vlan object

    Returns: True of False
    """
    nets = NetworkIPv4.objects.filter(vlan=vlan)
    for network in nets:
        if network.active is True:
            return True

    netsv6 = NetworkIPv6.objects.filter(vlan=vlan)
    for network in netsv6:
        if network.active is True:
            return True

    return False


def _load_template_file(equipment, template_type):
    """Load template file with specific type related to equipment

    Args: equipment: Equipamento object
    template_type: Type of template to be loaded

    Returns: template string
    """

    try:
        equipment_template = (EquipamentoRoteiro.search(
            None, equipment.id, template_type)).uniqueResult()
    except:
        log.error('Template type %s not found.' % template_type)
        raise exceptions.NetworkTemplateException()

    filename_in = NETWORK_CONFIG_TEMPLATE_PATH + \
        '/' + equipment_template.roteiro.roteiro

    # Read contents from file
    try:
        file_handle = open(filename_in, 'r')
        template_file = Template(file_handle.read())
        file_handle.close()
    except IOError, e:
        log.error('Error opening template file for read: %s' % filename_in)
        raise e
    except Exception, e:
        log.error('Syntax error when parsing template: %s ' % e)
        raise e
        # TemplateSyntaxError

    return template_file


def _remove_svi(equipment, vlan_num):
    equip_plugin = PluginFactory.factory(equipment)
    equip_plugin.connect()
    output = equip_plugin.remove_svi(vlan_num)
    equip_plugin.close()

    return output
