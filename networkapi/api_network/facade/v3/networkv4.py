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
from networkapi.distributedlock import LOCK_NETWORK_IPV4
from networkapi.distributedlock import LOCK_VLAN
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.ip import models as ip_models
from networkapi.util.geral import create_lock_with_blocking
from networkapi.util.geral import destroy_lock

log = logging.getLogger(__name__)

TEMPLATE_NETWORKv4_ACTIVATE = 'ipv4_activate_network_configuration'
TEMPLATE_NETWORKv4_DEACTIVATE = 'ipv4_deactivate_network_configuration'


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


def create_networkipv4(networkv4, user=None, force=False):
    """Creates a NetworkIPv4."""

    try:
        netv4_obj = ip_models.NetworkIPv4()
        netv4_obj.create_v3(networkv4, force=force)

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


def update_networkipv4(networkv4, user, force=False):
    """Updates a NetworkIPv4."""

    try:
        netv4_obj = get_networkipv4_by_id(networkv4.get('id'))
        netv4_obj.update_v3(networkv4, force=force)

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


def delete_networkipv4(network_ids, user, force=False):
    """Deletes a list of NetworkIPv4."""

    for network_id in network_ids:
        try:
            netv4_obj = get_networkipv4_by_id(network_id)
            netv4_obj.delete_v3(force=force)

        except ObjectDoesNotExistException, e:
            raise ObjectDoesNotExistException(e.detail)

        except ip_models.NetworkIPv4ErrorV3, e:
            raise ValidationAPIException(e.message)

        except ValidationAPIException, e:
            raise ValidationAPIException(e.detail)

        except Exception, e:
            raise NetworkAPIException(str(e))


def undeploy_networkipv4(network_id, user, force=False):
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
        locks_name.append(LOCK_NETWORK_IPV4 % netv4_obj.id)
        locks_name.append(LOCK_VLAN % netv4_obj.vlan.id)
        for equipment in routers:
            lock_name = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % \
                (equipment.id)
            locks_name.append(lock_name)

        locks_list = create_lock_with_blocking(locks_name)

    try:
        if netv4_obj.active == 0:
            return 'Network already not active. Nothing to do.'

        # load dict with all equipment attributes
        dict_ips = get_dict_v4_to_use_in_configuration_deploy(
            user, netv4_obj, routers)

        status_deploy = dict()

        # TODO implement threads
        for equipment in routers:

            # generate config file
            file_to_deploy = utils.generate_config_file(
                dict_ips, equipment, TEMPLATE_NETWORKv4_DEACTIVATE)

            # deploy config file in equipments
            status_deploy[equipment.id] = \
                deploy_config_in_equipment(file_to_deploy, equipment)

        netv4_obj.deactivate_v3()

        # transaction.commit()
        if netv4_obj.vlan.ativada == 1:

            # if there are no other networks active in vlan, remove int
            # vlan
            if not utils.has_active_network_in_vlan(netv4_obj.vlan):

                # remove int vlan
                for equipment in routers:
                    if equipment.maintenance is not True:
                        pass
                        # Delete SVI
                        status_deploy[equipment.id] += utils.remove_svi(
                            equipment, netv4_obj.vlan.num_vlan)

                # Need verify this call
                netv4_obj.vlan.deactivate_v3(locks_name)

        return status_deploy

    except ip_models.NetworkIPv4ErrorV3 as e:
        raise ValidationAPIException(e.message)

    except ObjectDoesNotExistException as e:
        raise ObjectDoesNotExistException(e.detail)

    except exceptions_eqpt.AllEquipmentsAreInMaintenanceException as e:
        raise ValidationAPIException(e.detail)

    except exceptions.IncorrectRedundantGatewayRegistryException as e:
        raise ValidationAPIException(e.detail)

    except exceptions.NetworkAlreadyActive as e:
        raise ValidationAPIException(e.detail)

    except ValidationAPIException as e:
        raise ValidationAPIException(e.detail)

    except Exception as e:
        raise NetworkAPIException(str(e))

    finally:
        destroy_lock(locks_list)


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
        locks_name.append(LOCK_NETWORK_IPV4 % network_id)
        locks_name.append(LOCK_VLAN % netv4_obj.vlan.id)
        for equipment in routers:
            lock_name = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % \
                (equipment.id)
            locks_name.append(lock_name)

        locks_list = create_lock_with_blocking(locks_name)

    try:
        if netv4_obj.active == 1:
            raise exceptions.NetworkAlreadyActive()

        status_deploy = dict()

        # load dict with all equipment attributes
        dict_ips = get_dict_v4_to_use_in_configuration_deploy(
            user, netv4_obj, routers)

        # TODO implement threads
        for equipment in routers:

            # generate config file
            file_to_deploy = utils.generate_config_file(
                dict_ips, equipment, TEMPLATE_NETWORKv4_ACTIVATE)

            # Apply configuration file on equipment
            status_deploy[equipment.id] = \
                deploy_config_in_equipment(file_to_deploy, equipment)

        netv4_obj.activate_v3()
        # transaction.commit()

        if netv4_obj.vlan.ativada == 0:
            # Need verify this call
            netv4_obj.vlan.activate_v3(locks_name)

        return status_deploy

    except ip_models.NetworkIPv4ErrorV3, e:
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

    has_active = utils.has_active_network_in_vlan(networkipv4.vlan)
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

    dict_ips['is_vxlan'] = networkipv4.vlan.vxlan

    return dict_ips
