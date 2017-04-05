# -*- coding: utf-8 -*-
import logging

from django.template import Context
from django.template import Template

from networkapi.api_network import exceptions
from networkapi.equipamento import models as eqpt_models
from networkapi.extra_logging import local
from networkapi.extra_logging import NO_REQUEST_ID
from networkapi.plugins.factory import PluginFactory
from networkapi.settings import NETWORK_CONFIG_FILES_PATH
from networkapi.settings import NETWORK_CONFIG_TEMPLATE_PATH
from networkapi.settings import NETWORK_CONFIG_TOAPPLY_REL_PATH
log = logging.getLogger(__name__)

TEMPLATE_NETWORKv4_ACTIVATE = 'ipv4_activate_network_configuration'
TEMPLATE_NETWORKv4_DEACTIVATE = 'ipv4_deactivate_network_configuration'
TEMPLATE_NETWORKv6_ACTIVATE = 'ipv6_activate_network_configuration'
TEMPLATE_NETWORKv6_DEACTIVATE = 'ipv6_deactivate_network_configuration'


def generate_config_file(dict_ips, equipment, template_type):
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
        network_template_file = load_template_file(equipment, template_type)
        key_dict = generate_template_dict(dict_ips, equipment)
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


def load_template_file(equipment, template_type):
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


def has_active_network_in_vlan(vlan):
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


def generate_template_dict(dict_ips, equipment):
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


def remove_svi(equipment, vlan_num):
    """Call function "remove_svi" of Plugin for model of equipment."""

    equip_plugin = PluginFactory.factory(equipment)
    equip_plugin.connect()
    output = equip_plugin.remove_svi(vlan_num)
    equip_plugin.close()

    return output
