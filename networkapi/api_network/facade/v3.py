# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context
from django.template import Template

from networkapi.api_deploy.facade import deploy_config_in_equipment_synchronous
from networkapi.api_equipment import exceptions as exceptions_eqpt
from networkapi.api_equipment import facade as facade_eqpt
from networkapi.api_network import exceptions
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import \
    LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT
from networkapi.distributedlock import LOCK_NETWORK_IPV4
from networkapi.distributedlock import LOCK_NETWORK_IPV6
from networkapi.distributedlock import LOCK_VLAN
from networkapi.equipamento import models as eqpt_models
from networkapi.extra_logging import local
from networkapi.extra_logging import NO_REQUEST_ID
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.ip import models as ip_models
from networkapi.plugins.factory import PluginFactory
from networkapi.settings import NETWORK_CONFIG_FILES_PATH
from networkapi.settings import NETWORK_CONFIG_TEMPLATE_PATH
from networkapi.settings import NETWORK_CONFIG_TOAPPLY_REL_PATH

log = logging.getLogger(__name__)

TEMPLATE_NETWORKv4_ACTIVATE = 'ipv4_activate_network_configuration'
TEMPLATE_NETWORKv4_DEACTIVATE = 'ipv4_deactivate_network_configuration'
TEMPLATE_NETWORKv6_ACTIVATE = 'ipv6_activate_network_configuration'
TEMPLATE_NETWORKv6_DEACTIVATE = 'ipv6_deactivate_network_configuration'


###############
# NetworkIPv4 #
###############
def get_networkipv4_by_id(network_id):
    """Get NetworkIPv4."""

    try:
        network = ip_models.NetworkIPv4.get_by_pk(network_id)

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))

    return network


def get_networkipv4_by_ids(network_ids):
    """Get Many NetworkIPv4."""

    net_ids = list()
    for network_id in network_ids:
        try:
            net = get_networkipv4_by_id(network_id)

        except ObjectDoesNotExistException, e:
            raise ObjectDoesNotExistException(e.detail)

        except Exception, e:
            raise NetworkAPIException(str(e))

        else:
            net_ids.append(net.id)

    networks = ip_models.NetworkIPv4.objects.filter(id__in=net_ids)

    return networks


def get_networkipv4_by_search(search=dict()):
    """Get List of NetworkIPv4 by Search."""

    try:
        networks = ip_models.NetworkIPv4.objects.all()
        net_map = build_query_to_datatable_v3(networks, search)

    except FieldError as e:
        raise ValidationAPIException(str(e))

    except Exception as e:
        raise NetworkAPIException(str(e))

    else:
        return net_map


def create_networkipv4(networkv4, user):
    """Creates a NetworkIPv4."""

    try:
        netv4_obj = ip_models.NetworkIPv4()
        netv4_obj.create_v3(networkv4)

    except ip_models.NetworkIPv4ErrorV3, e:
        raise ValidationAPIException(e.message)

    except exceptions.InvalidInputException, e:
        raise ValidationAPIException(e.detail)

    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))

    else:
        return netv4_obj


def update_networkipv4(networkv4, user):
    """Updates a NetworkIPv4."""

    try:
        netv4_obj = get_networkipv4_by_id(networkv4.get('id'))
        netv4_obj.update_v3(networkv4)

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)

    except ip_models.NetworkIPv4ErrorV3, e:
        raise ValidationAPIException(e.message)

    except exceptions.InvalidInputException, e:
        raise ValidationAPIException(e.detail)

    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))

    else:
        return netv4_obj


def delete_networkipv4(network_ids, user):
    """Deletes a list of NetworkIPv4."""

    for network_id in network_ids:
        try:
            netv4_obj = get_networkipv4_by_id(network_id)
            netv4_obj.delete_v3()

        except ObjectDoesNotExistException, e:
            raise ObjectDoesNotExistException(e.detail)

        except ip_models.NetworkIPv4ErrorV3, e:
            raise ValidationAPIException(e.message)

        except ValidationAPIException, e:
            raise ValidationAPIException(e.detail)

        except Exception, e:
            raise NetworkAPIException(str(e))


def undeploy_networkipv4(network_id, user):
    """Loads template for removing Network IPv4 equipment configuration,
    creates file and apply config.

    :param network_id: NetworkIPv4 Id

    Returns: List with status of equipments output
    """

    try:
        netv4_obj = get_networkipv4_by_id(network_id)

        routers = netv4_obj.vlan.ambiente.routers

        if not routers:
            raise exceptions.NoEnvironmentRoutersFoundException()

        if facade_eqpt.all_equipments_are_in_maintenance(routers):
            raise exceptions_eqpt.AllEquipmentsAreInMaintenanceException()

        if user:
            if not facade_eqpt.all_equipments_can_update_config(routers, user):
                raise exceptions_eqpt.UserDoesNotHavePermInAllEqptException(
                    'User does not have permission to update conf in eqpt. '
                    'Verify the permissions of user group with equipment group'
                    '. Network:{}'.format(netv4_obj.id))

        # lock network id to prevent multiple requests to same id
        with distributedlock(LOCK_NETWORK_IPV4 % netv4_obj.id):
            with distributedlock(LOCK_VLAN % netv4_obj.vlan.id):
                if netv4_obj.active == 0:
                    return 'Network already not active. Nothing to do.'

                # load dict with all equipment attributes
                dict_ips = get_dict_v4_to_use_in_configuration_deploy(
                    user, netv4_obj, routers)

                status_deploy = dict()

                # TODO implement threads
                for equipment in routers:

                    # generate config file
                    file_to_deploy = _generate_config_file(
                        dict_ips, equipment, TEMPLATE_NETWORKv4_DEACTIVATE)

                    lockvar = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % (
                        equipment.id)

                    # deploy config file in equipments
                    status_deploy[equipment.id] = \
                        deploy_config_in_equipment_synchronous(
                            file_to_deploy, equipment, lockvar)

                netv4_obj.deactivate_v3()

                # transaction.commit()
                if netv4_obj.vlan.ativada == 1:

                    # if there are no other networks active in vlan, remove int
                    # vlan
                    if not _has_active_network_in_vlan(netv4_obj.vlan):

                        # remove int vlan
                        for equipment in routers:
                            if equipment.maintenance is not True:
                                pass
                                # Delete SVI
                                status_deploy[equipment.id] += _remove_svi(
                                    equipment, netv4_obj.vlan.num_vlan)

                        # Need verify this call
                        netv4_obj.vlan.deactivate_v3()

                return status_deploy

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)

    except ip_models.NetworkIPv4ErrorV3, e:
        raise ValidationAPIException(e.message)

    except exceptions.NoEnvironmentRoutersFoundException, e:
        raise ValidationAPIException(e.detail)

    except exceptions.IncorrectRedundantGatewayRegistryException, e:
        raise ValidationAPIException(e.detail)

    except exceptions_eqpt.AllEquipmentsAreInMaintenanceException, e:
        raise ValidationAPIException(e.detail)

    except exceptions_eqpt.UserDoesNotHavePermInAllEqptException, e:
        raise ValidationAPIException(e.detail)

    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))


def deploy_networkipv4(network_id, user):
    """Loads template for creating Network IPv4 equipment configuration,
    creates file and apply config.

    :param network_id: NetworkIPv4 Id

    Returns: List with status of equipments output
    """

    try:
        netv4_obj = get_networkipv4_by_id(network_id)

        routers = netv4_obj.vlan.ambiente.routers

        if not routers:
            raise exceptions.NoEnvironmentRoutersFoundException()

        if facade_eqpt.all_equipments_are_in_maintenance(routers):
            raise exceptions_eqpt.AllEquipmentsAreInMaintenanceException()

        if user:
            if not facade_eqpt.all_equipments_can_update_config(routers, user):
                raise exceptions_eqpt.UserDoesNotHavePermInAllEqptException(
                    'User does not have permission to update conf in eqpt. '
                    'Verify the permissions of user group with equipment group'
                    '.Network:{}'.format(netv4_obj.id))

        # lock network id to prevent multiple requests to same id
        with distributedlock(LOCK_NETWORK_IPV4 % network_id):
            with distributedlock(LOCK_VLAN % netv4_obj.vlan.id):
                if netv4_obj.active == 1:
                    raise exceptions.NetworkAlreadyActive()

                status_deploy = dict()

                # TODO implement threads
                for equipment in routers:

                    # generate config file
                    file_to_deploy = _generate_config_file(
                        dict_ips, equipment, TEMPLATE_NETWORKv4_ACTIVATE)

                    lockvar = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % (
                        equipment.id)

                    # Apply configuration file on equipment
                    status_deploy[equipment.id] = \
                        deploy_config_in_equipment_synchronous(
                            file_to_deploy, equipment, lockvar)

                netv4_obj.activate_v3()
                # transaction.commit()

                if netv4_obj.vlan.ativada == 0:
                    # Need verify this call
                    netv4_obj.vlan.activate_v3()

                return status_deploy

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)

    except ip_models.NetworkIPv4ErrorV3, e:
        raise ValidationAPIException(e.message)

    except exceptions.NoEnvironmentRoutersFoundException, e:
        raise ValidationAPIException(e.detail)

    except exceptions.IncorrectRedundantGatewayRegistryException, e:
        raise ValidationAPIException(e.detail)

    except exceptions_eqpt.AllEquipmentsAreInMaintenanceException, e:
        raise ValidationAPIException(e.detail)

    except exceptions_eqpt.UserDoesNotHavePermInAllEqptException, e:
        raise ValidationAPIException(e.detail)

    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))


def get_dict_v4_to_use_in_configuration_deploy(user, networkipv4,
                                               equipment_list):
    """Generate dictionary with vlan an IP information to be used to generate
    template dict for equipment configuration

    Args: networkipv4 NetworkIPv4 object
    equipment_list: Equipamento objects list

    Returns: 2-dimension dictionary with equipments information for template
             rendering
    """

    try:
        gateway_ip = ip_models.Ip.get_by_octs_and_net(
            networkipv4.oct1, networkipv4.oct2,
            networkipv4.oct3, networkipv4.oct4 + 1, networkipv4)
    except ip_models.IpNotFoundError:
        log.error('Equipment IPs not correctly registered.'
                  'Router equipments should have first IP of '
                  'network allocated for them.')
        raise exceptions.IncorrectRedundantGatewayRegistryException()

    # Default Vrf of environment
    default_vrf = networkipv4.vlan.ambiente.default_vrf

    for equipment in equipment_list:
        # Verify if equipments have Ip of gateway
        try:
            gateway_ip.ipequipamento_set.get(equipamento=equipment)
        except ObjectDoesNotExist:
            log.error('Equipment IPs not correctly registered.'
                      'Router equipments should have first IP '
                      'of network allocated for them. Equipment: %s' %
                      equipment)
            raise exceptions.IncorrectRedundantGatewayRegistryException()

        # Get internal name of vrf to set in equipment
        # Can be empty, a default value of environment or a
        # value by vlan + equipment
        try:
            vrf_eqpt = equipment.vrfvlanequipment_set.filter(
                vlan=networkipv4.vlan
            ).uniqueResult()
            # Customized vrf
            vrf = vrf_eqpt.vrf
        except ObjectDoesNotExist:
            # Default vrf
            vrf = default_vrf
        finally:
            try:
                # Customized internal name of vrf for this equipment
                vrf_eqpt = equipment.vrfequipment_set.filter(
                    vrf=vrf
                ).uniqueResult()
                vrf_name = vrf_eqpt.internal_name
            except ObjectDoesNotExist:
                vrf_name = vrf.internal_name

    dict_ips = dict()

    if vrf_name:
        dict_ips['vrf'] = vrf_name

    # DHCPRelay list
    dhcprelay_list = networkipv4.dhcprelay

    if dhcprelay_list:

        dict_ips['dhcprelay_list'] = list()
        for dhcprelay in dhcprelay_list:

            ipv4 = dhcprelay.ipv4.ip_formated
            dict_ips['dhcprelay_list'].append(ipv4)

    dict_ips['gateway'] = gateway_ip.ip_formated
    dict_ips['ip_version'] = 'IPV4'
    dict_ips['equipments'] = dict()
    dict_ips['vlan_num'] = networkipv4.vlan.num_vlan
    dict_ips['vlan_name'] = networkipv4.vlan.nome
    dict_ips['cidr_block'] = networkipv4.block
    dict_ips['mask'] = networkipv4.mask_formated
    dict_ips['wildmask'] = networkipv4.wildcard

    has_active = _has_active_network_in_vlan(networkipv4.vlan)
    dict_ips['first_network'] = has_active is False

    # Check IPs for routers when there are multiple gateways
    if len(equipment_list) > 1:
        dict_ips['gateway_redundancy'] = True
        equip_number = 0
        for equipment in equipment_list:

            # Verify if equipment have more ips
            ip_equip = equipment.ipequipamento_set.filter(
                ip__networkipv4=networkipv4
            ).exclude(ip=gateway_ip).select_related('ip')

            if not ip_equip:
                log.error('Equipment IPs not correctly registered. '
                          'In case of multiple gateways, they should '
                          'have an IP other than the gateway registered.'
                          'Equipment: %s' % equipment.id)
                raise exceptions.IncorrectNetworkRouterRegistryException()

            ip = ip_equip[0].ip
            dict_ips[equipment] = dict()
            dict_ips[equipment]['ip'] = ip.ip_formated
            dict_ips[equipment]['prio'] = 100 + equip_number
            equip_number += 1
    else:
        dict_ips['gateway_redundancy'] = False
        dict_ips[equipment_list[0]] = dict()
        dict_ips[equipment_list[0]]['ip'] = dict_ips['gateway']
        dict_ips[equipment_list[0]]['prio'] = 100

    return dict_ips


###############
# NetworkIPv6 #
###############
def get_networkipv6_by_id(network_id):
    """Get NetworkIPv6."""

    try:
        network = ip_models.NetworkIPv6.get_by_pk(network_id)

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))

    return network


def get_networkipv6_by_ids(network_ids):
    """Get Many NetworkIPv6."""

    net_ids = list()
    for network_id in network_ids:
        try:
            net = get_networkipv6_by_id(network_id)

        except ObjectDoesNotExistException, e:
            raise ObjectDoesNotExistException(e.detail)

        except Exception, e:
            raise NetworkAPIException(str(e))

        else:
            net_ids.append(net.id)

    networks = ip_models.NetworkIPv6.objects.filter(id__in=net_ids)

    return networks


def get_networkipv6_by_search(search=dict()):
    """Get List of NetworkIPv6 by Search."""

    try:
        networks = ip_models.NetworkIPv6.objects.all()
        net_map = build_query_to_datatable_v3(networks, search)

    except FieldError as e:
        raise ValidationAPIException(str(e))

    except Exception as e:
        raise NetworkAPIException(str(e))

    else:
        return net_map


def create_networkipv6(networkv6, user):
    """Creates a NetworkIPv6."""

    try:
        netv6_obj = ip_models.NetworkIPv6()
        netv6_obj.create_v3(networkv6)

    except ip_models.NetworkIPv6ErrorV3, e:
        raise ValidationAPIException(e.message)

    except exceptions.InvalidInputException, e:
        raise ValidationAPIException(e.detail)

    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))

    else:
        return netv6_obj


def update_networkipv6(networkv6, user):
    """Updates a NetworkIPv6."""

    try:
        netv6_obj = get_networkipv6_by_id(networkv6.get('id'))
        netv6_obj.update_v3(networkv6)

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)

    except ip_models.NetworkIPv6ErrorV3, e:
        raise ValidationAPIException(e.message)

    except exceptions.InvalidInputException, e:
        raise ValidationAPIException(e.detail)

    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))

    else:
        return netv6_obj


def delete_networkipv6(network_ids, user):
    """Deletes a list of NetworkIPv6."""

    for network_id in network_ids:
        try:
            netv6_obj = get_networkipv6_by_id(network_id)
            netv6_obj.delete_v3()

        except ObjectDoesNotExistException, e:
            raise ObjectDoesNotExistException(e.detail)

        except ip_models.NetworkIPv6ErrorV3, e:
            raise ValidationAPIException(e.message)

        except ValidationAPIException, e:
            raise ValidationAPIException(e.detail)

        except Exception, e:
            raise NetworkAPIException(str(e))


def undeploy_networkipv6(network_id, user):
    """Loads template for removing Network IPv6 equipment configuration,
    creates file and apply config.

    Args: NetworkIPv6 object
    Equipamento objects list

    Returns: List with status of equipments output
    """

    try:
        netv6_obj = get_networkipv6_by_id(network_id)

        routers = netv6_obj.vlan.ambiente.routers

        if not routers:
            raise exceptions.NoEnvironmentRoutersFoundException()

        if facade_eqpt.all_equipments_are_in_maintenance(routers):
            raise exceptions_eqpt.AllEquipmentsAreInMaintenanceException()

        if user:
            if not facade_eqpt.all_equipments_can_update_config(routers, user):
                raise exceptions_eqpt.UserDoesNotHavePermInAllEqptException(
                    'User does not have permission to update conf in eqpt. '
                    'Verify the permissions of user group with equipment group'
                    '. Network:{}'.format(netv6_obj.id))

        # lock network id to prevent multiple requests to same id
        with distributedlock(LOCK_NETWORK_IPV6 % netv6_obj.id):
            with distributedlock(LOCK_VLAN % netv6_obj.vlan.id):
                if netv6_obj.active == 0:
                    return 'Network already not active. Nothing to do.'

                # load dict with all equipment attributes
                dict_ips = get_dict_v6_to_use_in_configuration_deploy(
                    user, netv6_obj, routers)

                status_deploy = dict()

                # TODO implement threads
                for equipment in routers:
                    # generate config file
                    file_to_deploy = _generate_config_file(
                        dict_ips, equipment, TEMPLATE_NETWORKv6_DEACTIVATE)

                    lockvar = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % (
                        equipment.id)

                    # deploy config file in equipments
                    status_deploy[equipment.id] = \
                        deploy_config_in_equipment_synchronous(
                            file_to_deploy, equipment, lockvar)

                netv6_obj.deactivate_v3()

                # transaction.commit()

                if netv6_obj.vlan.ativada == 1:
                    # if there are no other networks active in vlan, remove int
                    # vlan
                    if not _has_active_network_in_vlan(netv6_obj.vlan):
                        # remove int vlan
                        for equipment in routers:
                            if equipment.maintenance is not True:
                                status_deploy[
                                    equipment.id] += _remove_svi(
                                        equipment, netv6_obj.vlan.num_vlan)
                        netv6_obj.vlan.deactivate_v3()

                return status_deploy

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)

    except ip_models.NetworkIPv6ErrorV3, e:
        raise ValidationAPIException(e.message)

    except exceptions.NoEnvironmentRoutersFoundException, e:
        raise ValidationAPIException(e.detail)

    except exceptions.IncorrectRedundantGatewayRegistryException, e:
        raise ValidationAPIException(e.detail)

    except exceptions_eqpt.AllEquipmentsAreInMaintenanceException, e:
        raise ValidationAPIException(e.detail)

    except exceptions_eqpt.UserDoesNotHavePermInAllEqptException, e:
        raise ValidationAPIException(e.detail)

    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))


def deploy_networkipv6(network_id, user):
    """Loads template for creating Network IPv6 equipment configuration,
    creates file and apply config.

    Args: NetworkIPv6 object
    Equipamento objects list

    Returns: List with status of equipments output
    """

    try:

        netv6_obj = get_networkipv6_by_id(network_id)

        routers = netv6_obj.vlan.ambiente.routers

        if not routers:
            raise exceptions.NoEnvironmentRoutersFoundException()

        if facade_eqpt.all_equipments_are_in_maintenance(routers):
            raise exceptions_eqpt.AllEquipmentsAreInMaintenanceException()

        if user:
            if not facade_eqpt.all_equipments_can_update_config(routers, user):
                raise exceptions_eqpt.UserDoesNotHavePermInAllEqptException(
                    'User does not have permission to update conf in eqpt. '
                    'Verify the permissions of user group with equipment group'
                    '. Network:{}'.format(netv6_obj.id))

        # lock network id to prevent multiple requests to same id
        with distributedlock(LOCK_NETWORK_IPV6 % netv6_obj.id):
            with distributedlock(LOCK_VLAN % netv6_obj.vlan.id):
                if netv6_obj.active == 1:
                    raise exceptions.NetworkAlreadyActive()

                # load dict with all equipment attributes
                dict_ips = get_dict_v6_to_use_in_configuration_deploy(
                    user, netv6_obj, routers)

                status_deploy = dict()

                # TODO implement threads
                for equipment in routers:

                    # generate config file
                    file_to_deploy = _generate_config_file(
                        dict_ips, equipment, TEMPLATE_NETWORKv6_ACTIVATE)

                    # deploy config file in equipments
                    lockvar = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % (
                        equipment.id)

                    status_deploy[equipment.id] = \
                        deploy_config_in_equipment_synchronous(
                            file_to_deploy, equipment, lockvar)

                netv6_obj.activate_v3()

                # transaction.commit()

                if netv6_obj.vlan.ativada == 0:
                    netv6_obj.vlan.activate_v3()

                return status_deploy

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)

    except ip_models.NetworkIPv6ErrorV3, e:
        raise ValidationAPIException(e.message)

    except exceptions.NoEnvironmentRoutersFoundException, e:
        raise ValidationAPIException(e.detail)

    except exceptions.IncorrectRedundantGatewayRegistryException, e:
        raise ValidationAPIException(e.detail)

    except exceptions_eqpt.AllEquipmentsAreInMaintenanceException, e:
        raise ValidationAPIException(e.detail)

    except exceptions_eqpt.UserDoesNotHavePermInAllEqptException, e:
        raise ValidationAPIException(e.detail)

    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))


def get_dict_v6_to_use_in_configuration_deploy(user, networkipv6,
                                               equipment_list):
    """Generate dictionary with vlan an IP information to be used to generate
    template dict for equipment configuration

    Args: networkipv4 NetworkIPv4 object
    equipment_list: Equipamento objects list

    Returns: 2-dimension dictionary with equipments information for template
             rendering
    """

    try:
        gateway_ip = ip_models.Ipv6.get_by_blocks_and_net(
            '{0:0{1}x}'.format(int(networkipv6.block1, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block2, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block3, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block4, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block5, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block6, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block7, 16), 4),
            '{0:0{1}x}'.format(int(networkipv6.block8, 16) + 1, 4),
            networkipv6)
    except ip_models.IpNotFoundError:
        log.error('Equipment IPs not correctly registered.'
                  'Router equipments should have first IP of '
                  'network allocated for them.')
        raise exceptions.IncorrectRedundantGatewayRegistryException()

    # Default Vrf of environment
    default_vrf = networkipv6.vlan.ambiente.default_vrf

    for equipment in equipment_list:
        # Verify if equipments have Ip of gateway
        try:
            gateway_ip.ipv6equipament_set.get(equipamento=equipment)
        except ObjectDoesNotExist:
            log.error('Equipment IPs not correctly registered.'
                      'Router equipments should have first IP '
                      'of network allocated for them. Equipment: %s' %
                      equipment)
            raise exceptions.IncorrectRedundantGatewayRegistryException()

        # Get internal name of vrf to set in equipment
        # Can be empty, a default value of environment or a
        # value by vlan + equipment
        try:
            vrf_eqpt = equipment.vrfvlanequipment_set.filter(
                vlan=networkipv6.vlan
            ).uniqueResult()
            # Customized vrf
            vrf = vrf_eqpt.vrf
        except ObjectDoesNotExist:
            # Default vrf
            vrf = default_vrf
        finally:
            try:
                # Customized internal name of vrf for this equipment
                vrf_eqpt = equipment.vrfequipment_set.filter(
                    vrf=vrf
                ).uniqueResult()
                vrf_name = vrf_eqpt.internal_name
            except ObjectDoesNotExist:
                vrf_name = vrf.internal_name

    dict_ips = dict()

    if vrf_name:
        dict_ips['vrf'] = vrf_name

    # DHCPRelay list
    dhcprelay_list = networkipv6.dhcprelay

    if dhcprelay_list:

        dict_ips['dhcprelay_list'] = list()
        for dhcprelay in dhcprelay_list:

            ipv6 = dhcprelay.ipv6.ip_formated
            dict_ips['dhcprelay_list'].append(ipv6)

    dict_ips['gateway'] = gateway_ip.ip_formated
    dict_ips['ip_version'] = 'IPV6'
    dict_ips['equipments'] = dict()
    dict_ips['vlan_num'] = networkipv6.vlan.num_vlan
    dict_ips['vlan_name'] = networkipv6.vlan.nome
    dict_ips['cidr_block'] = networkipv6.block
    dict_ips['mask'] = networkipv6.mask_formated
    dict_ips['wildmask'] = 'Not used'

    has_active = _has_active_network_in_vlan(networkipv6.vlan)
    dict_ips['first_network'] = has_active is False

    # Check IPs for routers when there are multiple gateways
    if len(equipment_list) > 1:
        dict_ips['gateway_redundancy'] = True
        equip_number = 0
        for equipment in equipment_list:

            # Verify if equipment have more ips
            ip_equip = equipment.ipv6equipament_set.filter(
                ip__networkipv6=networkipv6
            ).exclude(ip=gateway_ip).select_related('ip')

            if not ip_equip:
                log.error('Equipment IPs not correctly registered. '
                          'In case of multiple gateways, they should '
                          'have an IP other than the gateway registered.'
                          'Equipment: %s' % equipment.id)
                raise exceptions.IncorrectNetworkRouterRegistryException()

            ip = ip_equip[0].ip
            dict_ips[equipment] = dict()
            dict_ips[equipment]['ip'] = ip.ip_formated
            dict_ips[equipment]['prio'] = 100 + equip_number
            equip_number += 1
    else:
        dict_ips['gateway_redundancy'] = False
        dict_ips[equipment_list[0]] = dict()
        dict_ips[equipment_list[0]]['ip'] = dict_ips['gateway']
        dict_ips[equipment_list[0]]['prio'] = 100

    return dict_ips


###########
# Generic #
###########
def _generate_config_file(dict_ips, equipment, template_type):
    """Load a template and write a file with the rended output.

    Args: 2-dimension dictionary with equipments information for template
          rendering equipment to render template to template type to load.

    Returns: filename with relative path to settings.TFTPBOOT_FILES_PATH
    """

    config_to_be_saved = ''
    request_id = getattr(local, 'request_id', NO_REQUEST_ID)

    filename_out = 'network_equip%s_config_%s' % (equipment.id, request_id)

    filename_to_save = NETWORK_CONFIG_FILES_PATH + filename_out
    rel_file_to_deploy = NETWORK_CONFIG_TOAPPLY_REL_PATH + filename_out

    try:
        network_template_file = _load_template_file(equipment, template_type)
        key_dict = _generate_template_dict(dict_ips, equipment)
        config_to_be_saved += network_template_file.render(Context(key_dict))
    except KeyError, exception:
        log.error('Erro: %s ' % exception)
        raise exceptions.InvalidKeyException(exception)

    # Save new file
    try:
        file_handle = open(filename_to_save, 'w')
        file_handle.write(config_to_be_saved)
        file_handle.close()
    except IOError, e:
        log.error('Error writing to config file: %s' % filename_to_save)
        raise e

    return rel_file_to_deploy


def _load_template_file(equipment, template_type):
    """Load template file with specific type related to equipment.

    Args: equipment: Equipamento object
    template_type: Type of template to be loaded

    Returns: template string
    """

    try:
        equipment_template = (eqpt_models.EquipamentoRoteiro.search(
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
        raise Exception(e)
    except Exception, e:
        log.error('Syntax error when parsing template: %s ' % e)
        raise Exception(e)
        # TemplateSyntaxError

    return template_file


def _has_active_network_in_vlan(vlan):
    """Check if there are any other active network in the vlan this is used
    because some equipments remove all the L3 config when applying some
    commands, so they can only be applyed at the first time or to remove
    interface vlan configuration

    :param vlan: vlan object

    :returns: True of False
    """
    networksv4 = vlan.networkipv4_set.filter(active=True)
    networksv6 = vlan.networkipv6_set.filter(active=True)

    if networksv4 or networksv6:
        return True
    return False


def _generate_template_dict(dict_ips, equipment):
    """Creates a 1-dimension dictionary from a 2 dimension with equipment
    information.

    Args: dict_ips dictionary for template rendering
    equipment to create dictionary to

    Returns: 1-dimension dictionary to use in template rendering for equipment
    """

    key_dict = {}
    # TODO Separate differet vendor support if needed for gateway redundancy
    key_dict['VLAN_NUMBER'] = dict_ips['vlan_num']
    key_dict['VLAN_NAME'] = dict_ips['vlan_name']
    key_dict['IP'] = dict_ips[equipment]['ip']
    key_dict['USE_GW_RED'] = dict_ips['gateway_redundancy']
    key_dict['GW_RED_ADDR'] = dict_ips['gateway']
    key_dict['GW_RED_PRIO'] = dict_ips[equipment]['prio']
    key_dict['CIDR_BLOCK'] = dict_ips['cidr_block']
    key_dict['NETWORK_MASK'] = dict_ips['mask']
    key_dict['NETWORK_WILDMASK'] = dict_ips['wildmask']
    key_dict['IP_VERSION'] = dict_ips['ip_version']
    key_dict['FIRST_NETWORK'] = dict_ips['first_network']
    if 'vrf' in dict_ips.keys():
        key_dict['VRF'] = dict_ips['vrf']

    if 'dhcprelay_list' in dict_ips.keys():
        key_dict['DHCPRELAY_LIST'] = dict_ips['dhcprelay_list']
    else:
        key_dict['DHCPRELAY_LIST'] = []
    # key_dict["ACL_IN"] = ""
    # key_dict["ACL_OUT"] = ""

    return key_dict


def _remove_svi(equipment, vlan_num):
    """Call function "remove_svi" of Plugin for model of equipment."""

    equip_plugin = PluginFactory.factory(equipment)
    equip_plugin.connect()
    output = equip_plugin.remove_svi(vlan_num)
    equip_plugin.close()

    return output
