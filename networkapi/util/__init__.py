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
from __future__ import absolute_import
from __future__ import unicode_literals

import copy
import functools
import logging
import re
import socket
import sys
import time
import warnings
from hashlib import sha1

from django.core import validators
from django.core.cache import cache
from django.forms.models import model_to_dict

from networkapi.infrastructure.ipaddr import AddressValueError
from networkapi.infrastructure.ipaddr import IPAddress
from networkapi.plugins import exceptions as plugins_exceptions
# from .decorators import deprecated

LOCK = 'LOCK'
PATTERN_XML_PASSWORD = [
    '<password>(.*?)</password>', '<enable_pass>(.*?)</enable_pass>', '<pass>(.*?)</pass>']


def valid_expression(operator, value1, value2):
    if operator == 'eq':
        return value1 == value2
    elif operator == 'ne':
        return value1 != value2
    else:
        return False


def search_hide_password(msg):
    """
    Search and hide password
    """
    for text in PATTERN_XML_PASSWORD:
        r = re.compile(text)
        m = r.search(msg)
        if m:
            password = m.group(1)
            msg = msg.replace(password, '****')

    return msg


def valid_regex(string, regex):
    pattern = re.compile(regex)
    return re.search(pattern, string) is not None


def is_valid_regex(string, regex):
    """Checks if the parameter is a valid value by regex.

    :param param: Value to be validated.

    :return: True if the parameter has a valid vakue, or False otherwise.
    """
    pattern = re.compile(regex)
    return pattern.match(string) is not None


def is_valid_ip(address):
    """Verifica se address é um endereço ip válido."""
    pattern = r'\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    return re.match(pattern, address)


def to_ip(address):
    """Resolve o endereço IP caso address seja um hostname.

    :param address: Hostname ou endereço IP.

    :return: Endereço IP correspondente ao endereço informado.
    """
    if is_valid_ip(address):
        # Se for um ip válido retorna
        return address
    # Se não for um ip válido tenta resolver o ip considerando que address é
    # um hostname
    return socket.gethostbyname(address)


def is_valid_int_param(param, required=True):
    """Checks if the parameter is a valid integer value.

    @param param: Value to be validated.

    @return True if the parameter has a valid integer value, or False otherwise.
    """
    if param is None and not required:
        return True
    elif param is None:
        return False

    try:
        int(param)
    except (TypeError, ValueError):
        return False
    return True


def is_valid_int_greater_zero_param(param, required=True):
    """Checks if the parameter is a valid integer value and greater than zero.

    @param param: Value to be validated.

    @return True if the parameter has a valid integer value, or False otherwise.
    """
    if param is None and not required:
        return True
    elif param is None:
        return False
    try:
        param = int(param)
        if param <= 0:
            return False
    except (TypeError, ValueError):
        return False
    return True


def is_valid_int_greater_equal_zero_param(param):
    """Checks if the parameter is a valid integer value and greater and equal than zero.

    @param param: Value to be validated.

    @return True if the parameter has a valid integer value, or False otherwise.
    """
    if param is None:
        return False
    try:
        param = int(param)
        if param < 0:
            return False
    except (TypeError, ValueError):
        return False
    return True


def is_valid_string_maxsize(param, maxsize=None, required=True):
    """Checks if the parameter is a valid string and his size is less than maxsize.
    If the parameter maxsize is None than the size is ignored
    If the parameter required is True than the string can not be None

    @param param: Value to be validated.
    @param maxsize: Max size of the value to be validated.
    @param required: Check if the value can be None

    @return True if the parameter is valid or False otherwise.
    """

    if required is True and param is None:
        return False

    elif required is False and (param is None or param == ''):
        return True

    if '' == param.strip():
        return False

    if param is not None and not isinstance(param, basestring):
        return False

    if param is not None and maxsize is not None:
        if is_valid_int_greater_zero_param(maxsize):
            if len(param.strip()) > maxsize:
                return False

    return True


def is_valid_string_minsize(param, minsize=None, required=True):
    """Checks if the parameter is a valid string and his size is more than minsize.
    If the parameter minsize is None than the size is ignored
    If the parameter required is True than the string can not be None

    @param param: Value to be validated.
    @param minsize: Min size of the value to be validated.
    @param required: Check if the value can be None

    @return True if the parameter is valid or False otherwise.
    """

    if required is True and param is None:
        return False

    elif required is False and (param is None or param == ''):
        return True

    if '' == param.strip():
        return False

    if param is not None and not isinstance(param, basestring):
        return False

    if param is not None and minsize is not None:
        if is_valid_int_greater_zero_param(minsize):
            if len(param.strip()) < minsize:
                return False

    return True


def is_valid_vlan_name(vlan_name):
    """Checks if the parameter is a valid string for Vlan's name, without special characters and breaklines

    @param vlan_name: Value to be validated.

    @return True if the parameter hasn't a special character, or False otherwise.
    """

    if vlan_name is None or vlan_name == '':
        return False

    regex_for_breakline = re.compile('\r|\n\r|\n')
    regex_for_special_characters = re.compile('[@!#$%^&*()<>?/\\\|}{~:]')

    return False if regex_for_breakline.search(vlan_name) or regex_for_special_characters.search(vlan_name) else True


def is_valid_boolean_param(param, required=True):
    """Checks if the parameter is a valid boolean.

    @param param: Value to be validated.

    @return True if the parameter has a valid boolean value, or False otherwise.
    """

    if param is None and not required:
        return True
    elif param is None:
        return False

    if param in ['0', '1', 'False', 'True', False, True]:
        return True
    else:
        return False


def is_valid_zero_one_param(param, required=True):
    """Checks if the parameter is a valid zero or one string.

    @param param: Value to be validated.

    @return True if the parameter has a valid zero or one value, or False otherwise.
    """
    if param is None and not required:
        return True
    elif param is None:
        return False

    if param == '0':
        return True
    elif param == '1':
        return True
    else:
        return False


def is_valid_yes_no_choice(param):
    """Checks if the parameter is valid 'S' or 'N' char.

    @param param: valid to be validated.

    @return True if the parameter is a valid choice, or False otherwise.
    """

    if param in ('S', 'N'):
        return True
    else:
        return False


def is_valid_uri(param):
    """Checks if the parameter is a valid uri.

    @param param: Value to be validated.

    @return True if the parameter has a valid uri value, or False otherwise.
    """
    pattern = r"^[a-zA-Z0-9\\-_\\\-\\.!\\~\\*'\\(\\);/\\?:\\@\\&=\\{\\}\\#\\\[\\\]\\,]*$"
    return re.match(pattern, param)


def is_valid_text(param, required=True):
    """Checks if the parameter is a valid field text and should follow the format of [A-Za-z]
    and special characters hyphen and underline.

    @param param: Value to be validated.
    @param required: Check if the value can be None

    @return True if the parameter has a valid text value, or False otherwise.

    """
    if required is True and param is None:
        return False

    elif required is False and (param is None or param == ''):
        return True

    pattern = r'^[a-zA-Z0-9\\-_\\\-\\ ]*$'
    return re.match(pattern, param)


def is_valid_pool_identifier_text(param, required=True):
    """Checks if the parameter is a valid field text and should follow the format of [A-Za-z]
    and special characters hyphen and underline.

    @param param: Value to be validated.
    @param required: Check if the value can be None

    @return True if the parameter has a valid text value, or False otherwise.

    """
    if required is True and param is None:
        return False

    elif required is False and (param is None or param == ''):
        return True

    pattern = r'^[a-zA-Z]+[a-zA-Z0-9\._-]*$'
    return re.match(pattern, param)


def is_valid_option(param):
    """Checks if the parameter is a valid field text and 0-9 and should follow the format of [A-Za-z]
    and special characters hyphen, underline and point.

    @param param: Value to be validated.

    @return True if the parameter has a valid text value, or False otherwise.

    """
    pattern = r'^[0-9a-zA-Z\\-_.\\\-\\ ]*$'
    return re.match(pattern, param)


def is_valid_email(param):
    """Checks if the parameter is a valid e-mail.

    @param param: Value to be validated.

    @return True if the parameter has a valid e-mail value, or False otherwise.
    """
    pattern = re.compile(r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
                         r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
                         r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)

    return re.match(pattern, param)


def is_valid_healthcheck_destination(param):
    """Checks if the parameter is a valid healthcheck_destination.

    @param param: Value to be validated.

    @return True if the parameter has a valid healthcheck_destination value, or False otherwise.
    """
    pattern = re.compile(r'^([0-9]+|\*):([0-9]+|\*)$')

    return re.match(pattern, param)


def is_valid_ipv4(param):
    """Checks if the parameter is a valid ipv4.

    @param param: Value to be validated.

    @return True if the parameter has a valid ipv4 value, or False otherwise.
    """
    try:
        IPAddress(param, 4)
        return True
    except AddressValueError:
        return False


def is_valid_ipv6(param):
    """Checks if the parameter is a valid ipv6.

    @param param: Value to be validated.

    @return True if the parameter has a valid ipv6 value, or False otherwise.
    """
    try:
        IPAddress(param, 6)
        return True
    except AddressValueError:
        return False


def is_valid_ip_ipaddr(param):
    """Checks if the parameter is a valid ip is ipv4 or ipv6.

    @param param: Value to be validated.

    @return True if the parameter has a valid ipv6 or ipv4 value, or False otherwise.
    """
    try:
        IPAddress(param)
        return True
    except ValueError:
        return False


def convert_boolean_to_int(param):
    """Convert the parameter of boolean to int.

    @param param: parameter to be converted.

    @return Parameter converted.
    """
    if param is True:
        return int(1)

    elif param is False:
        return int(0)


def convert_string_or_int_to_boolean(param, force=None):
    """Convert the parameter of string or int to boolean.
        @param param: parameter to be converted.
        @return Parameter converted.
    """

    if param == '1' or param == int(1) or param == 'True' or param == 'true':
        return True
    elif param == '0' or param == int(0) or param == 'False' or param == 'false':
        return False
    elif force:
        return False


def clone(obj):
    """Clone the object

    @param obj: object to be cloned

    @return object cloned.
    """
    return copy.copy(obj)


def is_valid_version_ip(param, IP_VERSION):
    """Checks if the parameter is a valid ip version value.

    @param param: Value to be validated.

    @return True if the parameter has a valid ip version value, or False otherwise.
    """
    if param is None:
        return False

    if param == IP_VERSION.IPv4[0] or param == IP_VERSION.IPv6[0]:
        return True

    return False


def mount_ipv4_string(ip):
    return str(str(ip.oct1) + '.' + str(ip.oct2) + '.' + str(ip.oct3) + '.' + str(ip.oct4))


def mount_ipv6_string(ip):
    return str(str(ip.block1) + ':' + str(ip.block2) + ':' + str(ip.block3) + ':' + str(ip.block4) + ':' + str(ip.block5) + ':' + str(ip.block6) + ':' + str(ip.block7) + ':' + str(ip.block8))


def cache_function(length, equipment=False):
    """
    Cache the result of function

    @param length: time in seconds to stay in cache
    """
    def _decorated(func):

        def _cache(*args, **kwargs):

            if equipment is True:
                key = sha1(str(args[0].id) + 'equipment').hexdigest()
                print str(args[0].id) + 'equipment'
            else:
                key = sha1(str(args[0].id)).hexdigest()
                print str(args[0].id)

            # Search in cache if it exists
            if key in cache:

                # Get value in cache
                value = cache.get(key)

                # If was locked
                if value == LOCK:
                    # Try until unlock
                    while value == LOCK:
                        time.sleep(1)
                        value = cache.get(key)
                # Return value of cache
                return value

            # If not exists in cache
            else:
                # Function can be called several times before it finishes and is put into the cache,
                # then lock it to others wait it finishes.
                cache.set(key, LOCK, length)

                # Execute method
                result = func(*args, **kwargs)

                # Set in cache the result of method
                cache.set(key, result, length)

                # If not exists in cache
                # key_list = cache.get(sha1('key_networkapi_vlans').hexdigest())
                # if(key_list is None):
                #    key_list = []

                # Set in cache the keys
                # key_list.append(key)
                # cache.set(sha1('key_networkapi_vlans').hexdigest(), key_list)

                return result

        return _cache
    return _decorated


def destroy_cache_function(key_list, equipment=False):
    for key in key_list:
        key = str(key)
        if equipment is True:
            key = str(key) + 'equipment'
        if sha1(key).hexdigest() in cache:
            cache.delete(sha1(key).hexdigest())


class IP_VERSION:
    IPv6 = ('v6', 'IPv6')
    IPv4 = ('v4', 'IPv4')
    List = (IPv4, IPv6)


def get_environment_map(environment):
    environment_map = dict()
    environment_map['id'] = environment.id
    environment_map['link'] = environment.link
    environment_map['id_divisao'] = environment.divisao_dc.id
    environment_map['nome_divisao'] = environment.divisao_dc.nome
    environment_map['id_ambiente_logico'] = environment.ambiente_logico.id
    environment_map['nome_ambiente_logico'] = environment.ambiente_logico.nome
    environment_map['id_grupo_l3'] = environment.grupo_l3.id
    environment_map['nome_grupo_l3'] = environment.grupo_l3.nome
    environment_map['ambiente_rede'] = environment.divisao_dc.nome + ' - ' + \
        environment.ambiente_logico.nome + ' - ' + \
        environment.grupo_l3.nome

    if environment.filter is not None:
        environment_map['id_filter'] = environment.filter.id
        environment_map['filter_name'] = environment.filter.name

    environment_map['acl_path'] = environment.acl_path
    environment_map['vrf'] = environment.vrf
    environment_map['ipv4_template'] = environment.ipv4_template
    environment_map['ipv6_template'] = environment.ipv6_template

    environment_map['min_num_vlan_1'] = environment.min_num_vlan_1
    environment_map['max_num_vlan_1'] = environment.max_num_vlan_1
    environment_map['min_num_vlan_2'] = environment.min_num_vlan_2
    environment_map['max_num_vlan_2'] = environment.max_num_vlan_2

    return environment_map


def get_vlan_map(vlan, network_ipv4, network_ipv6):

    vlan_map = model_to_dict(vlan)

    if network_ipv4 is not None and len(network_ipv4) > 0:
        net_map = []
        for net in network_ipv4:
            net_dict = model_to_dict(net)
            net_map.append(net_dict)

        vlan_map['redeipv4'] = net_map
    else:
        vlan_map['redeipv4'] = None

    if network_ipv6 is not None and len(network_ipv6) > 0:
        net_map = []
        for net in network_ipv6:
            net_dict = model_to_dict(net)
            net_map.append(net_dict)

        vlan_map['redeipv6'] = net_map
    else:
        vlan_map['redeipv6'] = None

    return vlan_map


def clear_newline_chr(string):
    str_return = string.replace(chr(10), '').replace(chr(13), '')
    return str_return


def is_valid_list_int_greater_zero_param(list_param, required=True):
    """Checks if the parameter list is a valid integer value and greater than zero.

    @param param: Value to be validated.

    @raise ValidationError: If there is validation error in the field
    """
    if required and list_param in validators.EMPTY_VALUES:
        raise ValueError('Field is required.')

    try:
        for param in list_param:

            if param is None and required:
                raise ValueError('Field is required.')

            try:
                param = int(param)

                if param < 1:
                    raise ValueError('Field must be an positive integer.')

            except Exception:
                raise ValueError('Field must be an integer.')

    except Exception:
        raise ValueError('Invalid List Parameter.')

    return True


def is_healthcheck_valid(healthcheck):
    if healthcheck['healthcheck_type'] != 'HTTP' and healthcheck['healthcheck_type'] != 'HTTPS':
        if healthcheck['healthcheck_expect'] != '':
            raise plugins_exceptions.ValueInvalid(
                'healthcheck expect must be empty')
        if healthcheck['healthcheck_request'] != '':
            raise plugins_exceptions.ValueInvalid(
                'healthcheck request must be empty')
    return True
