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
from __future__ import with_statement

import logging
import re

from networkapi import error_message_utils
from networkapi import settings
from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_VLAN
from networkapi.equipamento.models import Equipamento
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.util import destroy_cache_function
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.util import is_valid_vlan_name
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanACLDuplicatedError
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanNameDuplicatedError
from networkapi.vlan.models import VlanNotFoundError
from networkapi.vlan.models import VlanNumberEnvironmentNotAvailableError
from networkapi.vlan.models import VlanNumberNotAvailableError


class VlanEditResource(RestResource):

    log = logging.getLogger('VlanEditResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST requests to edit a vlan

        URL: vlan/edit/
        """

        try:

            network_version = kwargs.get('network_version')

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            vlan_map = networkapi_map.get('vlan')
            if vlan_map is None:
                msg = u'There is no value to the vlan tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            environment_id = vlan_map.get('environment_id')
            number = vlan_map.get('number')
            name = vlan_map.get('name')
            acl_file = vlan_map.get('acl_file')
            acl_file_v6 = vlan_map.get('acl_file_v6')
            description = vlan_map.get('description')
            id_vlan = vlan_map.get('vlan_id')

            # Valid vlan ID
            if not is_valid_int_greater_zero_param(id_vlan):
                self.log.error(
                    u'Parameter id_vlan is invalid. Value: %s.', id_vlan)
                raise InvalidValueError(None, 'id_vlan', id_vlan)

            # Valid environment_id ID
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'Parameter environment_id is invalid. Value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            # Valid number of Vlan
            if not is_valid_int_greater_zero_param(number):
                self.log.error(
                    u'Parameter number is invalid. Value: %s', number)
                raise InvalidValueError(None, 'number', number)

            # Valid name of Vlan
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 50):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            if not is_valid_vlan_name(name):
                self.log.error(
                    u'Parameter %s is invalid because is using special characters and/or breaklines.', name)
                raise InvalidValueError(None, 'name', name)

            p = re.compile('^[A-Z0-9-_]+$')
            m = p.match(name)

            if not m:
                name = name.upper()
                m = p.match(name)

                if not m:
                    raise InvalidValueError(None, 'name', name)

            # Valid description of Vlan
            if not is_valid_string_minsize(description, 3, False) or not is_valid_string_maxsize(description, 200, False):
                self.log.error(
                    u'Parameter description is invalid. Value: %s', description)
                raise InvalidValueError(None, 'description', description)

            vlan = Vlan()
            vlan = vlan.get_by_pk(id_vlan)

            with distributedlock(LOCK_VLAN % id_vlan):

                # Valid acl_file Vlan
                if acl_file is not None:
                    if not is_valid_string_minsize(acl_file, 3) or not is_valid_string_maxsize(acl_file, 200):
                        self.log.error(
                            u'Parameter acl_file is invalid. Value: %s', acl_file)
                        raise InvalidValueError(None, 'acl_file', acl_file)
                    p = re.compile('^[A-Z0-9-_]+$')
                    m = p.match(acl_file)
                    if not m:
                        raise InvalidValueError(None, 'acl_file', acl_file)

                    # VERIFICA SE VLAN COM MESMO ACL JA EXISTE OU NAO
                    # commenting acl name check - issue #55
                    # vlan.get_vlan_by_acl(acl_file)

                # Valid acl_file_v6 Vlan
                if acl_file_v6 is not None:
                    if not is_valid_string_minsize(acl_file_v6, 3) or not is_valid_string_maxsize(acl_file_v6, 200):
                        self.log.error(
                            u'Parameter acl_file_v6 is invalid. Value: %s', acl_file_v6)
                        raise InvalidValueError(
                            None, 'acl_file_v6', acl_file_v6)
                    p = re.compile('^[A-Z0-9-_]+$')
                    m = p.match(acl_file_v6)
                    if not m:
                        raise InvalidValueError(
                            None, 'acl_file_v6', acl_file_v6)

                    # VERIFICA SE VLAN COM MESMO ACL JA EXISTE OU NAO
                    # commenting acl name check - issue #55
                    # vlan.get_vlan_by_acl_v6(acl_file_v6)

                ambiente = Ambiente()
                ambiente = ambiente.get_by_pk(environment_id)

                change_name = False
                change_number_environment = False

                redes4 = vlan.networkipv4_set.all()
                redes6 = vlan.networkipv6_set.all()

                listaIpsv4 = []
                listaIpsv6 = []

                listaEquips4 = []
                listaEquips6 = []

                for rede in redes4:
                    for ip in rede.ip_set.all():
                        listaIpsv4.append(ip)

                for rede in redes6:
                    for ip in rede.ipv6_set.all():
                        listaIpsv6.append(ip)

                for ip in listaIpsv4:
                    for ipequip in ip.ipequipamento_set.all():
                        listaEquips4.append(ipequip.equipamento)

                for ip in listaIpsv6:
                    for ipequip in ip.ipv6equipament_set.all():
                        listaEquips6.append(ipequip.equipamento)

                listaDeIps4DoEquip = []
                listaDeIps6DoEquip = []
                listaDeVlansDoEquip = []

                for equip in listaEquips4:
                    for ipequip in equip.ipequipamento_set.all():
                        ip_aux = ipequip.ip
                        if ip_aux not in listaDeIps4DoEquip:
                            listaDeIps4DoEquip.append(ip_aux)

                for equip in listaEquips6:
                    for ipequip in equip.ipv6equipament_set.all():
                        ip_aux = ipequip.ip
                        if ip_aux not in listaDeIps4DoEquip:
                            listaDeIps6DoEquip.append(ip_aux)

                for ip in listaDeIps4DoEquip:
                    vlan_aux = ip.networkipv4.vlan
                    if vlan_aux not in listaDeVlansDoEquip:
                        listaDeVlansDoEquip.append(vlan_aux)

                for ip in listaDeIps6DoEquip:
                    vlan_aux = ip.networkipv6.vlan
                    if vlan_aux not in listaDeVlansDoEquip:
                        listaDeVlansDoEquip.append(vlan_aux)

                if vlan.nome != name:
                    change_name = True
                    vlan.nome = name
                if int(vlan.num_vlan) != int(number) or int(vlan.ambiente.id) != int(environment_id):
                    change_number_environment = True
                    vlan.num_vlan = number
                    vlan.ambiente = ambiente

                vlan.acl_file_name = acl_file
                vlan.acl_file_name_v6 = acl_file_v6
                vlan.descricao = description

                vlan_id_cache = [id_vlan]
                # Delete vlan's cache
                destroy_cache_function(vlan_id_cache)

                # Delete equipment's cache
                equip_id_list = []

                for netv4 in vlan.networkipv4_set.all():
                    for ip in netv4.ip_set.all():
                        for ip_equip in ip.ipequipamento_set.all():
                            equip_id_list.append(ip_equip.equipamento_id)

                for netv6 in vlan.networkipv6_set.all():
                    for ip in netv6.ipv6_set.all():
                        for ip_equip in ip.ipv6equipament_set.all():
                            equip_id_list.append(ip_equip.equipamento_id)

                destroy_cache_function(equip_id_list, True)

                vlan.edit_vlan(user, change_name, change_number_environment)
                # Return XML

                return self.response(dumps_networkapi({}))

        except VlanACLDuplicatedError, e:
            return self.response_error(311, acl_file)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except AmbienteNotFoundError, e:
            return self.response_error(112)
        except VlanNameDuplicatedError, e:
            return self.response_error(108)
        except VlanNumberNotAvailableError, e:
            return self.response_error(306, vlan.num_vlan)
        except VlanNumberEnvironmentNotAvailableError, e:
            return self.response_error(315, e.message)
        except VlanNotFoundError, e:
            return self.response_error(150, e.message)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
        except (VlanError, AmbienteError), e:
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Treat PUT requests to activate a vlan
           Set column ativada = 1

        URL: vlan/create/
        """

        try:

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            vlan_map = networkapi_map.get('vlan')

            id_vlan = vlan_map.get('vlan_id')

            vlan = Vlan()
            vlan = vlan.get_by_pk(id_vlan)

            # Check permission group equipments
            equips_from_ipv4 = Equipamento.objects.filter(
                ipequipamento__ip__networkipv4__vlan=id_vlan, equipamentoambiente__is_router=1)
            equips_from_ipv6 = Equipamento.objects.filter(
                ipv6equipament__ip__networkipv6__vlan=id_vlan, equipamentoambiente__is_router=1)

            for equip in equips_from_ipv4:
                # User permission
                if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None,
                                equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
                    self.log.error(
                        u'User does not have permission to perform the operation.')
                    return self.not_authorized()
            for equip in equips_from_ipv6:
                # User permission
                if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None,
                                equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
                    self.log.error(
                        u'User does not have permission to perform the operation.')
                    return self.not_authorized()

            if vlan.ativada:
                return self.response(dumps_networkapi({}))

            # Make command
            vlan_command = settings.VLAN_CREATE % int(id_vlan)

            # Execute command
            code, stdout, stderr = exec_script(vlan_command)

            # if command was successfully executed
            if code == 0:

                # After execute script, change to activated
                vlan.activate(user)
            else:
                return self.response_error(2, stdout + stderr)

            return self.response(dumps_networkapi({}))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)
        except AmbienteNotFoundError as e:
            return self.response_error(112)
        except VlanNameDuplicatedError as e:
            return self.response_error(108)
        except VlanNumberNotAvailableError as e:
            return self.response_error(306, vlan.num_vlan)
        except VlanNumberEnvironmentNotAvailableError as e:
            return self.response_error(315, e.message)
        except VlanNotFoundError as e:
            return self.response_error(150, e.message)
        except XMLError as e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
        except (VlanError, AmbienteError) as e:
            return self.response_error(1)
