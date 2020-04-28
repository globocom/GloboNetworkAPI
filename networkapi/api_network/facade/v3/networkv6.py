# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist

from networkapi.api_deploy.facade import deploy_config_in_equipment
from networkapi.api_equipment import exceptions as exceptions_eqpt
from networkapi.api_equipment import facade as facade_eqpt
from networkapi.api_network import exceptions
from networkapi.api_network.facade.v3 import utils
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.distributedlock import \
    LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT
from networkapi.distributedlock import LOCK_NETWORK_IPV6
from networkapi.distributedlock import LOCK_VLAN
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.ip import models as ip_models
from networkapi.util.geral import create_lock_with_blocking
from networkapi.util.geral import destroy_lock

log = logging.getLogger(__name__)

TEMPLATE_NETWORKv6_ACTIVATE = 'ipv6_activate_network_configuration'
TEMPLATE_NETWORKv6_DEACTIVATE = 'ipv6_deactivate_network_configuration'


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


def create_networkipv6(networkv6, user=None, force=False):
    """Creates a NetworkIPv6."""

    try:
        netv6_obj = ip_models.NetworkIPv6()
        netv6_obj.create_v3(networkv6, force=force)

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


def update_networkipv6(networkv6, user, force=False):
    """Updates a NetworkIPv6."""

    try:
        netv6_obj = get_networkipv6_by_id(networkv6.get('id'))
        netv6_obj.update_v3(networkv6, force=force)

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


def delete_networkipv6(network_ids, user, force=False):
    """Deletes a list of NetworkIPv6."""

    for network_id in network_ids:
        try:
            netv6_obj = get_networkipv6_by_id(network_id)
            netv6_obj.delete_v3(force=force)

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

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)

    except exceptions.NoEnvironmentRoutersFoundException, e:
        raise ValidationAPIException(e.detail)

    except exceptions_eqpt.AllEquipmentsAreInMaintenanceException, e:
        raise ValidationAPIException(e.detail)

    except exceptions_eqpt.UserDoesNotHavePermInAllEqptException, e:
        raise ValidationAPIException(e.detail)

    except exceptions.NetworkAlreadyActive, e:
        raise ValidationAPIException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))

    else:
        # lock network id to prevent multiple requests to same id
        locks_name = list()
        locks_name.append(LOCK_NETWORK_IPV6 % netv6_obj.id)
        locks_name.append(LOCK_VLAN % netv6_obj.vlan.id)
        for equipment in routers:
            lock_name = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % \
                (equipment.id)
            locks_name.append(lock_name)

        locks_list = create_lock_with_blocking(locks_name)

    try:
        if netv6_obj.active == 0:
            return 'Network already not active. Nothing to do.'

        # load dict with all equipment attributes
        dict_ips = get_dict_v6_to_use_in_configuration_deploy(
            user, netv6_obj, routers)

        status_deploy = dict()

        # TODO implement threads
        for equipment in routers:
            # generate config file
            file_to_deploy = utils.generate_config_file(
                dict_ips, equipment, TEMPLATE_NETWORKv6_DEACTIVATE)

            # deploy config file in equipments
            status_deploy[equipment.id] = \
                deploy_config_in_equipment(file_to_deploy, equipment)

        netv6_obj.deactivate_v3()

        if netv6_obj.vlan.ativada == 1:

            # if there are no other networks active in vlan, remove int
            # vlan
            if not utils.has_active_network_in_vlan(netv6_obj.vlan):

                # remove int vlan
                for equipment in routers:
                    if equipment.maintenance is not True:
                        status_deploy[
                            equipment.id] += utils.remove_svi(
                                equipment, netv6_obj.vlan.num_vlan)

                netv6_obj.vlan.deactivate_v3(locks_name)

        return status_deploy

    except ip_models.NetworkIPv6ErrorV3, e:
        raise ValidationAPIException(e.message)

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)

    except exceptions_eqpt.AllEquipmentsAreInMaintenanceException, e:
        raise ValidationAPIException(e.detail)

    except exceptions.IncorrectRedundantGatewayRegistryException, e:
        raise ValidationAPIException(e.detail)

    except exceptions.NetworkAlreadyActive, e:
        raise ValidationAPIException(e.detail)

    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))

    finally:
        destroy_lock(locks_list)


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

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)

    except exceptions.NoEnvironmentRoutersFoundException, e:
        raise ValidationAPIException(e.detail)

    except exceptions_eqpt.AllEquipmentsAreInMaintenanceException, e:
        raise ValidationAPIException(e.detail)

    except exceptions_eqpt.UserDoesNotHavePermInAllEqptException, e:
        raise ValidationAPIException(e.detail)

    except exceptions.NetworkAlreadyActive, e:
        raise ValidationAPIException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))

    else:
        # lock network id to prevent multiple requests to same id
        locks_name = list()
        locks_name.append(LOCK_NETWORK_IPV6 % netv6_obj.id)
        locks_name.append(LOCK_VLAN % netv6_obj.vlan.id)
        for equipment in routers:
            lock_name = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % \
                (equipment.id)
            locks_name.append(lock_name)

        locks_list = create_lock_with_blocking(locks_name)

    try:

        if netv6_obj.active == 1:
            raise exceptions.NetworkAlreadyActive()

        # load dict with all equipment attributes
        dict_ips = get_dict_v6_to_use_in_configuration_deploy(
            user, netv6_obj, routers)

        status_deploy = dict()

        # TODO implement threads
        for equipment in routers:

            # generate config file
            file_to_deploy = utils.generate_config_file(
                dict_ips, equipment, TEMPLATE_NETWORKv6_ACTIVATE)

            status_deploy[equipment.id] = \
                deploy_config_in_equipment(file_to_deploy, equipment)

        netv6_obj.activate_v3()

        # transaction.commit()

        if netv6_obj.vlan.ativada == 0:
            netv6_obj.vlan.activate_v3(locks_name)

        return status_deploy

    except ip_models.NetworkIPv6ErrorV3, e:
        raise ValidationAPIException(e.message)

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)

    except exceptions_eqpt.AllEquipmentsAreInMaintenanceException, e:
        raise ValidationAPIException(e.detail)

    except exceptions.IncorrectRedundantGatewayRegistryException, e:
        raise ValidationAPIException(e.detail)

    except exceptions.NetworkAlreadyActive, e:
        raise ValidationAPIException(e.detail)

    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)

    except Exception, e:
        raise NetworkAPIException(str(e))

    finally:
        destroy_lock(locks_list)


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

    has_active = utils.has_active_network_in_vlan(networkipv6.vlan)
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

    dict_ips['is_vxlan'] = networkipv6.vlan.vxlan

    return dict_ips
