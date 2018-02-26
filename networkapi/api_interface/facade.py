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
import ast
import logging
import re

from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context
from django.template import Template

from networkapi.api_deploy.facade import deploy_config_in_equipment_synchronous
from networkapi.api_interface import exceptions
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.distributedlock import LOCK_EQUIPMENT
from networkapi.distributedlock import LOCK_INTERFACE_DEPLOY_CONFIG
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.exception import InvalidValueError
from networkapi.extra_logging import local
from networkapi.extra_logging import NO_REQUEST_ID
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.interface.models import EnvironmentInterface
from networkapi.interface.models import Interface
from networkapi.interface.models import PortChannel
from networkapi.interface import models
from networkapi.system import exceptions as var_exceptions
from networkapi.system.facade import get_value as get_variable
from networkapi.util import is_valid_int_greater_zero_param


log = logging.getLogger(__name__)

# register = template.Library()

# @register.filter
# def get(dictionary, key):
#    return dictionary.get(key)

def create_interface(interface):

    try:
        interface_obj = Interface()
        interface_obj.create_v3(interface)
    except models.InterfaceError, e:
        raise ValidationAPIException(e.message)
    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)
    except Exception, e:
        raise NetworkAPIException(str(e))

    return interface_obj

def get_interface_by_search(search=dict()):
    """Return a list of interface by dict."""

    try:
        interfaces = Interface.objects.filter()
        interface_map = build_query_to_datatable_v3(interfaces, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return interface_map

def get_interface_by_ids(interface_ids):
    try:
        interfaces_obj = list()
        for i in interface_ids:
            interface = Interface.objects.get(id=int(i))
            interfaces_obj.append(interface)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except ObjectDoesNotExist, e:
        raise Exception(u'There is no interface with id = %s. %s' % (id, e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return interfaces_obj

def generate_delete_file(user, equip_id, interface_list, channel):
    try:
        INTERFACE_CONFIG_TOAPPLY_REL_PATH = get_variable(
            'interface_config_toapply_rel_path')
        INTERFACE_CONFIG_FILES_PATH = get_variable(
            'interface_config_files_path')
        TEMPLATE_REMOVE_CHANNEL = get_variable('template_remove_channel')
        TEMPLATE_REMOVE_INTERFACE = get_variable('template_remove_interface')
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável INTERFACE_CONFIG_TEMPLATE_PATH,'
            'TEMPLATE_REMOVE_CHANNEL ou TEMPLATE_REMOVE_INTERFACE.')

    key_dict = dict()
    config_to_be_saved = ''
    request_id = getattr(local, 'request_id', NO_REQUEST_ID)
    extension = '.py' if interface_list[0].equipamento.modelo.marca.nome == "HP" else ''
    filename_out = 'equip_' + str(equip_id) + '_channel_' + str(channel.id) + '_remove_' + str(request_id) + extension
    log.debug(filename_out)
    filename_to_save = INTERFACE_CONFIG_FILES_PATH + filename_out
    rel_file_to_deploy = INTERFACE_CONFIG_TOAPPLY_REL_PATH + filename_out

    key_dict['PORTCHANNEL_NAME'] = channel.nome

    for i in interface_list:
        key_dict['INTERFACE_NAME'] = i.interface
        try:
            interface_template_file = _load_template_file(
                int(equip_id), TEMPLATE_REMOVE_INTERFACE)
            config_to_be_saved += interface_template_file.render(
                Context(key_dict))
        except exceptions.InterfaceTemplateException, e:
            log.error(e)
            raise exceptions.InterfaceTemplateException()
        except KeyError, exception:
            log.error('Erro: %s ' % exception)
            raise exceptions.InvalidKeyException(exception)
        log.info('facade ' + str(i.interface))

    try:
        channel_template_file = _load_template_file(
            int(equip_id), TEMPLATE_REMOVE_CHANNEL)
        config_to_be_saved += channel_template_file.render(Context(key_dict))
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

def delete_channel(user, equip_id, interface_list, channel):

    file_to_deploy = generate_delete_file(
        user, equip_id, interface_list, channel)

    # TODO Deploy config file
    try:
        lockvar = LOCK_EQUIPMENT % (equip_id)
        status_deploy = deploy_config_in_equipment_synchronous(
            file_to_deploy, int(equip_id), lockvar)
        log.info('Status: %s' % status_deploy)
    except exceptions.InterfaceException, exception:
        log.error(exception)
        raise exceptions.InterfaceException(exception)

    return status_deploy

def generate_and_deploy_interface_config_sync(user, id_interface):

    if not is_valid_int_greater_zero_param(id_interface):
        raise exceptions.InvalidIdInterfaceException()

    interface = Interface.get_by_pk(id_interface)
    interfaces = [interface]

    file_to_deploy = _generate_config_file(interfaces)

    # TODO Deploy config file
    lockvar = LOCK_INTERFACE_DEPLOY_CONFIG % (interface.equipamento.id)
    status_deploy = deploy_config_in_equipment_synchronous(
        file_to_deploy, interface.equipamento, lockvar)

    return status_deploy

def generate_and_deploy_channel_config_sync(user, id_channel):

    if not is_valid_int_greater_zero_param(id_channel):
        raise exceptions.InvalidIdInterfaceException()

    channel = PortChannel.get_by_pk(id_channel)

    interfaces = channel.list_interfaces()

    # group interfaces by equipment
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

    # TODO Deploy config file
    # make separate threads
    for equipment_id in files_to_deploy.keys():
        lockvar = LOCK_INTERFACE_DEPLOY_CONFIG % (equipment_id)
        equipamento = Equipamento.get_by_pk(equipment_id)
        status_deploy = deploy_config_in_equipment_synchronous(
            files_to_deploy[equipment_id], equipamento, lockvar)

    return status_deploy

def _generate_config_file(interfaces_list):
    log.info("_generate_config_file")

    try:
        INTERFACE_CONFIG_TOAPPLY_REL_PATH = get_variable(
            'interface_config_toapply_rel_path')
        INTERFACE_CONFIG_FILES_PATH = get_variable(
            'interface_config_files_path')
        TEMPLATE_TYPE_INT = get_variable('template_type_int')
        TEMPLATE_TYPE_CHANNEL = get_variable('template_type_channel')
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável INTERFACE_CONFIG'
            '<TOAPPLY,TEMPLATE,FILES>_PATH.')

    # check if all interfaces are configuring same equipment
    # raises error if not
    equipment_interfaces = dict()
    equipment_interfaces[interfaces_list[0].equipamento.nome] = 1
    for interface in interfaces_list:
        if interface.equipamento.nome not in equipment_interfaces:
            log.error(
                'Error trying to configure multiple interfaces in '
                'different equipments in same call.')
            raise exceptions.InvalidIdInterfaceException

    config_to_be_saved = ''
    equipment_id = interfaces_list[0].equipamento.id

    request_id = getattr(local, 'request_id', NO_REQUEST_ID)
    extension = '.py' if interfaces_list[0].equipamento.modelo.marca.nome == "HP" else ''
    filename_out = 'int-d_' + str(interfaces_list[0].id) + '_config_' + str(request_id) + extension
    log.debug(filename_out)
    filename_to_save = INTERFACE_CONFIG_FILES_PATH + filename_out
    rel_file_to_deploy = INTERFACE_CONFIG_TOAPPLY_REL_PATH + filename_out

    int_template_file = _load_template_file(equipment_id, TEMPLATE_TYPE_INT)
    channels_configured = {}

    for interface in interfaces_list:
        key_dict = _generate_dict(interface)

        # If Interface is in channel, render the template for channel,
        # only once for each channel
        try:
            if interface.channel is not None:
                if interface.channel.id is not None and \
                        interface.channel.id not in channels_configured.keys():
                    channel_template_file = _load_template_file(
                        equipment_id, TEMPLATE_TYPE_CHANNEL)
                    config_to_be_saved += channel_template_file.render(
                        Context(key_dict))
                    channels_configured[interface.channel.id] = 1

            # Render the template for interface
            config_to_be_saved += int_template_file.render(Context(key_dict))
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

def _load_template_file(equipment_id, template_type):
    log.info("_load_template_file")

    try:
        INTERFACE_CONFIG_TEMPLATE_PATH = get_variable(
            'interface_config_template_path')
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável INTERFACE_CONFIG'
            '<TOAPPLY,TEMPLATE,FILES>_PATH.')

    try:
        equipment_template = (EquipamentoRoteiro.search(
            None, equipment_id, template_type)).uniqueResult()
    except:
        log.error('Template type %s not found. Equip: %s' %
                  (template_type, equipment_id))
        raise exceptions.InterfaceTemplateException()

    filename_in = INTERFACE_CONFIG_TEMPLATE_PATH + \
        equipment_template.roteiro.roteiro

    # Read contents from file
    try:
        file_handle = open(filename_in, 'r')
        template_file = Template(file_handle.read())
        file_handle.close()
    except IOError, e:
        log.error('Error opening template file for read: %s. Equip: %s' %
                  (filename_in, equipment_id))
        raise e
    except Exception, e:
        log.error('Syntax error when parsing template: %s ' % e)
        raise e
        # TemplateSyntaxError

    return template_file

def _generate_dict(interface):
    log.info("_generate_dict")

    try:
        supported_string = get_variable('supported_equipment_brands')
        SUPPORTED_EQUIPMENT_BRANDS = ast.literal_eval(supported_string)
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável supported_equipment_brands.')
    except ValueError:
        raise var_exceptions.VariableDoesNotExistException(
            'Erro buscando a variável supported_equipment_brands. '
            'Formato invalido. Deve ser uma string no formato de lista.')

    # Check if it is a supported equipment interface

    if interface.equipamento.modelo.marca.nome not in \
            SUPPORTED_EQUIPMENT_BRANDS:
        raise exceptions.UnsupportedEquipmentException()

    key_dict = {}
    # TODO Separate differet vendor support
    # Cisco Nexus 6001 dict
    key_dict['NATIVE_VLAN'] = interface.vlan_nativa
    key_dict['USE_MCLAG'] = 1
    key_dict['INTERFACE_NAME'] = interface.interface
    key_dict['INTERFACE_DESCRIPTION'] = str(
        interface.ligacao_front.equipamento.nome
    ) + ' ' + str(interface.ligacao_front.interface)
    key_dict['INTERFACE_TYPE'] = interface.tipo.tipo
    if key_dict['INTERFACE_TYPE'] in 'trunk':
        vlan_range_results = get_vlan_range(interface)
        key_dict['VLAN_RANGE'] = vlan_range_results[0]
        key_dict['VLAN_RANGE_LIST'] = vlan_range_results[1]

    if interface.channel is not None:
        key_dict['BOOL_INTERFACE_IN_CHANNEL'] = 1
        key_dict['PORTCHANNEL_NAME'] = interface.channel.nome
        try:
            key_dict['MCLAG_IDENTIFIER'] = int(
                re.sub(r'[a-zA\-]', '', interface.channel.nome))
        except ValueError, e:
            log.error('Error: invalid channel name')
            raise e
        if interface.channel.lacp:
            key_dict['CHANNEL_LACP_MODE'] = 'active'
        else:
            key_dict['CHANNEL_LACP_MODE'] = 'on'

    else:
        key_dict['BOOL_INTERFACE_IN_CHANNEL'] = 0

    return key_dict

def get_vlan_range(interface):
    log.info("get_vlan_range")

    # TODO Generate vlan range
    env_ints = EnvironmentInterface.get_by_interface(interface.id)
    vlan_range = ''
    vlan_range_list = []
    for env_int in env_ints:
        #This test is not good. Has to be treated elsewhere with plugins
        if interface.equipamento.modelo.marca.nome == "HP":
            separator = ' to '
            range_list_separator = ' '
        else:
            separator = '-'
            range_list_separator = ','

        if env_int.vlans:
            vlan_range_temp = env_int.vlans
            vlan_range_temp = vlan_range_temp.replace('-', separator)
            vlan_range_list_temp = [vlan_range_temp]
        else:

            vlan_range_1 = str(env_int.ambiente.min_num_vlan_1) + \
                           separator + str(env_int.ambiente.max_num_vlan_1)
            vlan_range_2 = str(env_int.ambiente.min_num_vlan_2) + \
                           separator + str(env_int.ambiente.max_num_vlan_2)

            if vlan_range_1 is not vlan_range_2:
                vlan_range_temp = vlan_range_1 + range_list_separator + vlan_range_2
                vlan_range_list_temp = [vlan_range_1, vlan_range_2]
            else:
                vlan_range_temp = vlan_range_1
                vlan_range_list_temp = [vlan_range_1]

        if vlan_range is '':
            vlan_range = vlan_range_temp
            vlan_range_list.extend(vlan_range_list_temp)
        elif vlan_range_temp not in vlan_range:
            vlan_range += range_list_separator + vlan_range_temp
            vlan_range_list.extend(vlan_range_list_temp)

    if vlan_range == '':
        raise exceptions.InterfaceTrunkAllowedVlanException()

    return [vlan_range, vlan_range_list]

def verificar_vlan_range(amb, vlans):
    log.info("verificar_vlan_range")

    for intervalo in vlans.split(';'):
        for i in re.split('\W+', intervalo.replace('to', '-')):
            try:
                i = int(i)
            except:
                raise InvalidValueError(None, None, 'Numero da Vlan')
            if amb.min_num_vlan_1:
                if not (i >= amb.min_num_vlan_1 and i <= amb.max_num_vlan_1):
                    if not (i >= amb.min_num_vlan_2 and i <= amb.max_num_vlan_2):
                        raise exceptions.InterfaceException(
                            u'Numero de vlan fora do range '
                            'definido para o ambiente')

def verificar_vlan_nativa(vlan_nativa):
    log.info("verificar_vlan_nativa")

    if vlan_nativa is not None:
        if int(vlan_nativa) < 1 or 3967 < int(vlan_nativa) < 4048 or int(vlan_nativa) >= 4096:
            raise InvalidValueError(None, 'Vlan Nativa', 'Range valido: 1-3967, 4048-4095.')

def check_channel_name_on_equipment(nome, interfaces):
    log.info("check_channel_name_on_equipment")

    for i in interfaces:

        interface = Interface.objects.get(id=int(i))

        interface_obj = Interface.objects.filter(
            channel__nome=nome,
            equipamento__id=interface.equipamento.id)

        if interface_obj:
            raise Exception ("Channel name %s already exist on the equipment %s" % (nome, interface.equipamento.nome))

        front_interface_obj = Interface.objects.filter(
            channel__nome=nome,
            equipamento__id=interface.ligacao_front.equipamento.id)

        if front_interface_obj:
            raise Exception ("Channel name %s already exist on the equipment %s" % (nome, interface.ligacao_front.equipamento.nome))

    log.info("passei")

def available_channel_number(channel_name, interface_ids):
    log.info("available channel")

    interface_obj = Interface()

    for interface_id in interface_ids:

        interface = interface_obj.get_by_pk(interface_id)

        if not interface:
            raise Exception("Do not exist interface with id: %s" % interface_id)

        equipment_id = interface.equipamento.id

        if not interface.ligacao_front:
            raise Exception("Interface is not connected.")

        front_equipment_id = interface.ligacao_front.equipamento.id

        if Interface.objects.filter(equipamento=equipment_id, channel__nome=channel_name):
            raise Exception("Channel name already exist on the equipment: %s" % channel_name)
        if Interface.objects.filter(equipamento=front_equipment_id, channel__nome=channel_name):
            raise Exception("Channel name already exist on the equipment: %s" % channel_name)