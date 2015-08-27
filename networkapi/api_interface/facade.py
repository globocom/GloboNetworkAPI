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

from django.template import Context, Template
#from jinja2 import Template
import thread
import re

from networkapi.extra_logging import local, NO_REQUEST_ID
from networkapi.settings import INTERFACE_TOAPPLY_REL_PATH, INTERFACE_CONFIG_TEMPLATE_PATH, INTERFACE_CONFIG_FILES_PATH
from networkapi.distributedlock import LOCK_INTERFACE_EQUIP_CONFIG
from networkapi.log import Log

from networkapi.interface.models import Interface, PortChannel
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.api_interface import exceptions
from networkapi.equipamento.models import Equipamento, EquipamentoRoteiro
from networkapi.roteiro.models import TipoRoteiro
from networkapi.api_deploy.facade import deploy_config_in_equipment_synchronous

SUPPORTED_EQUIPMENT_BRANDS = ["Cisco"]
TEMPLATE_TYPE_INT = "interface_configuration"
TEMPLATE_TYPE_CHANNEL = "interface_channel_configuration"

log = Log(__name__)

#register = template.Library()

#@register.filter
#def get(dictionary, key):
#    return dictionary.get(key)


def generate_and_deploy_interface_config_sync(user, id_interface):

    if not is_valid_int_greater_zero_param(id_interface):
        raise exceptions.InvalidIdInterfaceException()

    interface = Interface.get_by_pk(id_interface)
    interfaces = [interface]

    file_to_deploy = _generate_config_file(interfaces)

    #TODO Deploy config file
    lockvar = LOCK_INTERFACE_EQUIP_CONFIG % (interface.equipamento.id)
    status_deploy = deploy_config_in_equipment_synchronous(file_to_deploy, interface.equipamento, lockvar)

    return status_deploy

def generate_and_deploy_channel_config_sync(user, id_channel):

    if not is_valid_int_greater_zero_param(id_channel):
        raise exceptions.InvalidIdInterfaceException()

    channel = PortChannel.get_by_pk(id_channel)

    interfaces = channel.list_interfaces()

    #group interfaces by equipment
    equipment_interfaces = dict()
    for interface in interfaces:
        if interface.equipamento.id not in equipment_interfaces:
            equipment_interfaces[interface.equipamento.id] = []
        equipment_interfaces[interface.equipamento.id].append(interface)

    files_to_deploy = {}
    for equipment_id in equipment_interfaces.keys():
        grouped_interfaces = equipment_interfaces[equipment_id]
        file_to_deploy = _generate_config_file(grouped_interfaces)
        files_to_deploy[equipment_id] = file_to_deploy

    #TODO Deploy config file
    #make separate threads
    for equipment_id in files_to_deploy.keys():
        lockvar = LOCK_INTERFACE_EQUIP_CONFIG % (equipment_id)
        equipamento = Equipamento.get_by_pk(equipment_id)
        status_deploy = deploy_config_in_equipment_synchronous(files_to_deploy[equipment_id], equipamento, lockvar)

    return status_deploy

def _generate_config_file(interfaces_list):

    #check if all interfaces are configuring same equipment
    #raises error if not
    equipment_interfaces = dict()
    equipment_interfaces[interfaces_list[0].equipamento.nome] = 1
    for interface in interfaces_list:
        if interface.equipamento.nome not in equipment_interfaces:
            log.error("Error trying to configure multiple interfaces in different equipments in same call.")
            raise exceptions.InvalidIdInterfaceException

    config_to_be_saved = ""
    equipment_id = interfaces_list[0].equipamento.id

    request_id = getattr(local, 'request_id', NO_REQUEST_ID)
    filename_out = "int-d_"+str(interfaces_list[0].id)+"_config_"+str(request_id)
    filename_to_save = INTERFACE_CONFIG_FILES_PATH+filename_out
    rel_file_to_deploy = INTERFACE_TOAPPLY_REL_PATH+filename_out

    int_template_file = _load_template_file(equipment_id, TEMPLATE_TYPE_INT)
    channels_configured = {}

    for interface in interfaces_list:
        key_dict = _generate_dict(interface)

        #If Interface is in channel, render the template for channel, only once
        #for each channel
        if interface.channel is not None:
            try:
                if interface.channel.id is not None and interface.channel.id not in channels_configured.keys():
                    channel_template_file = _load_template_file(equipment_id, TEMPLATE_TYPE_CHANNEL)
                    config_to_be_saved += channel_template_file.render( Context(key_dict) )
                    channels_configured[interface.channel.id] = 1

            #Render the template for interface
                config_to_be_saved += int_template_file.render( Context(key_dict) )
            except KeyError, exception:
                log.error("Erro: %s " % exception)
                raise exceptions.InvalidKeyException(exception)

    #Save new file
    try:
        log.info("saving file %s" % filename_to_save)
        file_handle = open(filename_to_save, 'w')
        file_handle.write(config_to_be_saved)
        file_handle.close()
    except IOError, e:
        log.error("Error writing to config file: %s" % filename_to_save)
        raise e

    return rel_file_to_deploy

def _load_template_file(equipment_id, template_type):
    try:
        equipment_template = (EquipamentoRoteiro.search(None, equipment_id, template_type)).uniqueResult()
    except:
        log.error("Template type %s not found." % template_type)
        raise exceptions.InterfaceTemplateException()

    filename_in = INTERFACE_CONFIG_TEMPLATE_PATH+"/"+equipment_template.roteiro.roteiro

    # Read contents from file
    try:
        file_handle = open(filename_in, 'r')
        template_file = Template ( file_handle.read() )
        file_handle.close()
    except IOError, e:
        log.error("Error opening template file for read: %s" % filename_in)
        raise e
    except Exception, e:
        log.error("Syntax error when parsing template: %s " % e)
        raise e
        #TemplateSyntaxError

    return template_file

def _generate_dict(interface):

    #Check if it is a supported equipment interface
    if interface.equipamento.modelo.marca.nome not in SUPPORTED_EQUIPMENT_BRANDS:
        log.info("%s" % interface.equipamento.modelo.marca.nome) 
        raise exceptions.UnsupportedEquipmentException()

    key_dict = {}
    #TODO Separate differet vendor support
    #Cisco Nexus 6001 dict
    key_dict["NATIVE_VLAN"] = interface.vlan_nativa
    log.info ("%s" % interface)
    log.info("%s" % interface.vlan_nativa)
    key_dict["VLAN_RANGE"] = get_vlan_range(interface)
    key_dict["USE_MCLAG"] = 1
    key_dict["INTERFACE_NAME"] = interface.interface
    key_dict["INTERFACE_DESCRIPTION"] = "description to be defined"
    key_dict["INTERFACE_TYPE"] = interface.tipo.tipo
    if interface.channel is not None:
        key_dict["BOOL_INTERFACE_IN_CHANNEL"] = 1
        key_dict["PORTCHANNEL_NAME"] = interface.channel.nome
        try:
            key_dict["MCLAG_IDENTIFIER"] = int ( re.sub(r"[a-zA\-]", "", interface.channel.nome) )
        except ValueError, e:
            log.error("Error: invalid channel name")
            raise e
        if interface.channel.lacp:
            key_dict["CHANNEL_LACP_MODE"] = "active"
        else:
            key_dict["CHANNEL_LACP_MODE"] = "on"

    else:
        key_dict["BOOL_INTERFACE_IN_CHANNEL"] = 0


    return key_dict

def get_vlan_range(interface):
    #TODO Generate vlan range
    return "1-200"

