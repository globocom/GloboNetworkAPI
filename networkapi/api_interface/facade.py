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

from networkapi.extra_logging import local
from networkapi.settings import INTERFACE_TOAPPLY_PATH, INTERFACE_CONFIG_TEMPLATE_PATH
from networkapi.distributedlock import LOCK_INTERFACE_EQUIP_CONFIG
from networkapi.log import Log

from networkapi.interface.models import Interface
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.api_interface import exceptions
from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.roteiro.models import TipoRoteiro
from networkapi.api_deploy.facade import deploy_config_in_equipment_synchronous

SUPPORTED_EQUIPMENT_BRANDS = ["Cisco"]
TEMPLATE_TYPE = "interface_configuration"

log = Log(__name__)

def generate_and_deploy_interface_config(user, id_interface):

    if not is_valid_int_greater_zero_param(id_interface):
        raise exceptions.InvalidIdInterfaceException()

    interface = Interface.get_by_pk(id_interface)

    file_to_deploy = _generate_config_file(interface)

    #TODO Deploy config file
    lockvar = LOCK_INTERFACE_EQUIP_CONFIG % (interface.equipamento.id)
    status_deploy = deploy_config_in_equipment_synchronous(file_to_deploy, interface.equipamento, lockvar)

    return status_deploy

def _generate_config_file(interface):

    #TODO
    equipment_id = interface.equipamento.id
    equipment_template = EquipamentoRoteiro.search(None, equipment_id, TEMPLATE_TYPE)
    if len(equipment_template) != 1:
        raise exceptions.InterfaceTemplateException()

    filename_in = INTERFACE_CONFIG_TEMPLATE_PATH+"/"+equipment_template.roteiro.roteiro

    request_id = getattr(local, 'request_id', NO_REQUEST_ID)
    filename_out = "int_id_"+interface.id+"_config_"+request_id

    # Read contents from file
    try:
        file_handle = open(filein, 'r')
        template_file = Template ( file_handle.read() )
        file_handle.close()
    except IOError, e:
        log.error("Error opening template file for read: %s" % filein)
        raise e

    key_dict = _generate_dict(interface)

    #Render the template
    try:
        config_to_be_saved = template_file.render( Context(key_dict) )
    except KeyError, exception:
        raise InvalidKeyException(exception)

    #Save new file
    try:
        file_handle = open(filename_out, 'w')
        file_handle.write(config_to_be_saved)
        file_handle.close()
    except IOError, e:
        log.error("Error writing to config file: %s" % fileout)
        raise e

    rel_file_to_deploy = INTERFACE_TOAPPLY_PATH+filename_out

    return rel_file_to_deploy

def _generate_dict(interface):

    #Check if it is a supported equipment interface
    if interface.equipamento.modelo.marca not in SUPPORTED_EQUIPMENT_BRANDS:
        raise exceptions.UnsupportedEquipmentException()

    key_dict = {}

    #TODO Separate differet vendor support
    #Cisco Nexus 6001 dict
    key_dict["NATIVE_VLAN"] = interface.vlan_nativa
    key_dict["VLAN_RANGE"] = get_vlan_range(interface)
    key_dict["USE_MCLAG"] = 1
    key_dict["MCLAG_IDENTIFIER"] = int ( re.sub(r"[a-zA\-]", "", interface.channel.name) )
    key_dict["INTERFACE_NAME"] = interface.interface
    key_dict["INTERFACE_DESCRIPTION"] = "description to be defined"
    key_dict["INTERFACE_TYPE"] = interface.tipo.tipo
    if interface.channel is not None:
        key_dict["BOOL_INTERFACE_IN_CHANNEL"] = 1
        key_dict["PORTCHANNEL_NAME"] = interface.channel.name
        if interface.channel.lacp:
            key_dict["CHANNEL_LACP_MODE"] = "active"
        else:
            key_dict["CHANNEL_LACP_MODE"] = "on"

    else:
        key_dict["BOOL_INTERFACE_IN_CHANNEL"] = 0


    return key_dict

