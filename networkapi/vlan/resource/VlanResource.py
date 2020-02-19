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

from django.conf import settings

from networkapi import error_message_utils
from networkapi import settings
from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.script_utils import ScriptError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.interface.models import Interface
from networkapi.interface.models import InterfaceError
from networkapi.interface.models import InterfaceNotFoundError
from networkapi.interface.models import InterfaceProtectedError
from networkapi.ip.models import ConfigEnvironmentInvalidError
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv4AddressNotAvailableError
from networkapi.ip.models import NetworkIPv4NotFoundError
from networkapi.ip.models import NetworkIPvXNotFoundError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.util import is_valid_vlan_name
from networkapi.vlan.models import NetworkTypeNotFoundError
from networkapi.vlan.models import TipoRede
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanNameDuplicatedError
from networkapi.vlan.models import VlanNetworkAddressNotAvailableError
from networkapi.vlan.models import VlanNotFoundError
from networkapi.vlan.models import VlanNumberNotAvailableError


class VlanResource(RestResource):

    """Class to treat GET, POST, PUT and DELETE requests for Vlan."""

    log = logging.getLogger('VlanResource')

    def handle_post(self, request, user, *args, **kwargs):
        """
        Handles POST requests to allocate a new VLAN.

        URL: vlan/
        """

        self.log.info('Allocate new VLAN')

        try:

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
            environment = vlan_map.get('id_ambiente')
            network_type = vlan_map.get('id_tipo_rede')
            name = vlan_map.get('nome')
            description = vlan_map.get('descricao')
            environment_vip = vlan_map.get('id_ambiente_vip')
            vrf = vlan_map.get('vrf')

            # Name must NOT be none and 50 is the maxsize
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 50):
                self.log.error(u'Parameter nome is invalid. Value: %s.', name)
                raise InvalidValueError(None, 'nome', name)

            if not is_valid_vlan_name(name):
                self.log.error(
                    u'Parameter %s is invalid because is using special characters and/or breaklines.', name)
                raise InvalidValueError(None, 'name', name)

            # Description can NOT be greater than 200
            if not is_valid_string_minsize(description, 3, False) or not is_valid_string_maxsize(description, 200, False):
                self.log.error(
                    u'Parameter descricao is invalid. Value: %s.', description)
                raise InvalidValueError(None, 'descricao', description)

            # vrf can NOT be greater than 100
            if not is_valid_string_maxsize(vrf, 100, False):
                self.log.error(
                    u'Parameter vrf is invalid. Value: %s.', vrf)
                raise InvalidValueError(None, 'vrf', vrf)

            # Environment
            # Valid environment ID
            if not is_valid_int_greater_zero_param(environment):
                self.log.error(
                    u'Parameter id_ambiente is invalid. Value: %s.', environment)
                raise InvalidValueError(None, 'id_ambiente', environment)

            # Find environment by ID to check if it exist
            env = Ambiente.get_by_pk(environment)

            # Environment Vip
            if environment_vip is not None:

                # Valid environment_vip ID
                if not is_valid_int_greater_zero_param(environment_vip):
                    self.log.error(
                        u'Parameter id_ambiente_vip is invalid. Value: %s.', environment_vip)
                    raise InvalidValueError(
                        None, 'id_ambiente_vip', environment_vip)

                # Find Environment VIP by ID to check if it exist
                evip = EnvironmentVip.get_by_pk(environment_vip)

            else:
                evip = None

            # Network Type
            # Valid network_type ID
            if not is_valid_int_greater_zero_param(network_type):
                self.log.error(
                    u'Parameter id_tipo_rede is invalid. Value: %s.', network_type)
                raise InvalidValueError(None, 'id_tipo_rede', network_type)

            # Find network_type by ID to check if it exist
            net = TipoRede.get_by_pk(network_type)

            # Business Rules

            # New Vlan
            vlan = Vlan()
            vlan.nome = name
            vlan.descricao = description
            vlan.ambiente = env

            # Check if environment has min/max num_vlan value or use the value
            # thas was configured in settings
            if (vlan.ambiente.min_num_vlan_1 and vlan.ambiente.max_num_vlan_1) or (vlan.ambiente.min_num_vlan_2 and vlan.ambiente.max_num_vlan_2):
                min_num_01 = vlan.ambiente.min_num_vlan_1 if vlan.ambiente.min_num_vlan_1 and vlan.ambiente.max_num_vlan_1 else vlan.ambiente.min_num_vlan_2
                max_num_01 = vlan.ambiente.max_num_vlan_1 if vlan.ambiente.min_num_vlan_1 and vlan.ambiente.max_num_vlan_1 else vlan.ambiente.max_num_vlan_2
                min_num_02 = vlan.ambiente.min_num_vlan_2 if vlan.ambiente.min_num_vlan_2 and vlan.ambiente.max_num_vlan_2 else vlan.ambiente.min_num_vlan_1
                max_num_02 = vlan.ambiente.max_num_vlan_2 if vlan.ambiente.min_num_vlan_2 and vlan.ambiente.max_num_vlan_2 else vlan.ambiente.max_num_vlan_1
            else:
                min_num_01 = settings.MIN_VLAN_NUMBER_01
                max_num_01 = settings.MAX_VLAN_NUMBER_01
                min_num_02 = settings.MIN_VLAN_NUMBER_02
                max_num_02 = settings.MAX_VLAN_NUMBER_02

            # Persist
            vlan.create_new(user,
                            min_num_01,
                            max_num_01,
                            min_num_02,
                            max_num_02
                            )

            # New NetworkIPv4
            network_ipv4 = NetworkIPv4()
            vlan_map = network_ipv4.add_network_ipv4(user, vlan.id, net, evip)

            # Return XML
            return self.response(dumps_networkapi(vlan_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except GrupoError:
            return self.response_error(1)
        except NetworkTypeNotFoundError:
            return self.response_error(111)
        except EnvironmentVipNotFoundError, e:
            return self.response_error(283)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except VlanNotFoundError:
            return self.response_error(116)
        except VlanNameDuplicatedError:
            return self.response_error(108)
        except VlanNumberNotAvailableError:
            return self.response_error(109, min_num_01, max_num_01, min_num_02, max_num_02)
        except VlanNetworkAddressNotAvailableError:
            return self.response_error(150)
        except ConfigEnvironmentInvalidError:
            return self.response_error(294)
        except NetworkIPv4AddressNotAvailableError:
            return self.response_error(295)
        except (VlanError, AmbienteError, VlanError):
            return self.response_error(1)

    def get_vlan_map_shared(self, vlan):
        vlan_map = dict()
        vlan_map['id'] = vlan.id
        vlan_map['nome'] = vlan.nome
        vlan_map['num_vlan'] = vlan.num_vlan
        vlan_map['id_ambiente'] = vlan.ambiente.id
        vlan_map['descricao'] = vlan.descricao
        vlan_map['acl_file_name'] = vlan.acl_file_name
        vlan_map['acl_valida'] = '1' if vlan.acl_valida else '0'
        vlan_map['acl_file_name_v6'] = vlan.acl_file_name_v6
        vlan_map['acl_valida_v6'] = '1' if vlan.acl_valida_v6 else '0'
        vlan_map['ativada'] = '1' if vlan.ativada else '0'
        return vlan_map

    def get_vlan_map(self, vlan, network_ipv4):
        vlan_map = self.get_vlan_map_shared(vlan)
        vlan_map['id_tipo_rede'] = network_ipv4.network_type.id
        vlan_map['rede_oct1'] = network_ipv4.oct1
        vlan_map['rede_oct2'] = network_ipv4.oct2
        vlan_map['rede_oct3'] = network_ipv4.oct3
        vlan_map['rede_oct4'] = network_ipv4.oct4
        vlan_map['bloco'] = network_ipv4.block
        vlan_map['mascara_oct1'] = network_ipv4.mask_oct1
        vlan_map['mascara_oct2'] = network_ipv4.mask_oct2
        vlan_map['mascara_oct3'] = network_ipv4.mask_oct3
        vlan_map['mascara_oct4'] = network_ipv4.mask_oct4
        vlan_map['broadcast'] = network_ipv4.broadcast
        return vlan_map

    def get_vlan_map_ipv6(self, vlan, network_ipv6):
        vlan_map = self.get_vlan_map_shared(vlan)
        vlan_map['id_tipo_rede'] = network_ipv6.network_type.id
        vlan_map['bloco1'] = network_ipv6.block1
        vlan_map['bloco2'] = network_ipv6.block2
        vlan_map['bloco3'] = network_ipv6.block3
        vlan_map['bloco4'] = network_ipv6.block4
        vlan_map['bloco5'] = network_ipv6.block5
        vlan_map['bloco6'] = network_ipv6.block6
        vlan_map['bloco7'] = network_ipv6.block7
        vlan_map['bloco8'] = network_ipv6.block8
        vlan_map['bloco'] = network_ipv6.block
        vlan_map['mask_bloco1'] = network_ipv6.mask1
        vlan_map['mask_bloco2'] = network_ipv6.mask2
        vlan_map['mask_bloco3'] = network_ipv6.mask3
        vlan_map['mask_bloco4'] = network_ipv6.mask4
        vlan_map['mask_bloco5'] = network_ipv6.mask5
        vlan_map['mask_bloco6'] = network_ipv6.mask6
        vlan_map['mask_bloco7'] = network_ipv6.mask7
        vlan_map['mask_bloco8'] = network_ipv6.mask8
        return vlan_map

    def handle_get(self, request, user, *args, **kwargs):
        """Treat GET requests to find VLAN by id.

        URLs: /vlan/<id_vlan>/
        """

        try:
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()

            id_vlan = kwargs.get('id_vlan')

            # Get vlan by id
            if id_vlan is not None:
                self.log.debug('id_vlan = %s', kwargs['id_vlan'])

                # Valid environment_vip ID
                if not is_valid_int_greater_zero_param(id_vlan):
                    self.log.error(
                        u'Parameter id_vlan is invalid. Value: %s.', id_vlan)
                    raise InvalidValueError(None, 'id_vlan', id_vlan)

                vlan = Vlan().get_by_pk(id_vlan)

                # Get first network_ipv4 or network_ipv6 related to vlan
                try:
                    network_ipv4 = vlan.networkipv4_set.order_by('id')[0]
                    vlan_map = self.get_vlan_map(vlan, network_ipv4)
                except IndexError, e:
                    self.log.error(
                        u'Error finding the first network_ipv4 from vlan, trying network_ipv6.')
                    try:
                        network_ipv6 = vlan.networkipv6_set.order_by('id')[0]
                        vlan_map = self.get_vlan_map_ipv6(vlan, network_ipv6)
                    except IndexError, e:
                        self.log.error(
                            u'Error findind the first network_ipv6, raising exception.')
                        raise NetworkIPvXNotFoundError(
                            e, u'Error finding the first network_ipv4 and network_ipv6 from vlan.')

                map = dict()
                map['vlan'] = vlan_map

                return self.response(dumps_networkapi(map))
            else:
                return super(VlanResource, self).handle_get(request, user, *args, **kwargs)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except VlanNotFoundError:
            return self.response_error(116)
        except NetworkIPvXNotFoundError:
            return self.response_error(281)
        except (VlanError, GrupoError):
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Treat PUT requests to create, add, validate, remove or check VLAN to trunk.

        URLs: /vlan/<id_vlan>/criar/, /vlan/<id_vlan>/add/, /vlan/<id_vlan>/del/, /vlan/<id_vlan>/check/,
              /vlan/list/, /vlanl2/<id_vlan>/criar/
        """
        operation = kwargs.get('operacao')
        if operation is None:
            return super(VlanResource, self).handle_put(request, user, *args, **kwargs)

        vlan_id = kwargs.get('id_vlan')
        if (vlan_id is None) and (operation != 'list'):
            return self.response_error(115)

        try:
            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Valid vlan id
            if (operation != 'list') and not is_valid_int_greater_zero_param(kwargs.get('id_vlan')):
                self.log.error(
                    u'Parameter id_vlan is invalid. Value: %s.', kwargs.get('id_vlan'))
                raise InvalidValueError(None, 'id_vlan', kwargs.get('id_vlan'))

            # XML operations
            else:
                xml_map, attrs_map = loads(
                    request.raw_post_data, ['id_equipamento'])
                networkapi_map = xml_map.get('networkapi')
                if networkapi_map is None:
                    return self.response_error(3, u'There is no value to the networkapi tag of XML request.')

                if (operation == 'criar'):
                    return self.create_vlan(user, kwargs.get('id_vlan'))
                else:
                    return self.add_remove_check_list_vlan_trunk(user,
                                                                 networkapi_map,
                                                                 kwargs.get(
                                                                     'id_vlan'),
                                                                 operation)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except VlanNotFoundError:
            return self.response_error(116)
        except NetworkIPv4NotFoundError:
            return self.response_error(281)
        except (VlanError, GrupoError, EquipamentoError, InterfaceError):
            return self.response_error(1)
        except ScriptError, s:
            return self.response_error(2, s)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)

    def create_vlan(self, user, vlan_id):

        if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
            return self.not_authorized()

        vlan = Vlan().get_by_pk(vlan_id)

        # Check permission group equipments
        equips_from_ipv4 = Equipamento.objects.filter(
            ipequipamento__ip__networkipv4__vlan=vlan_id, equipamentoambiente__is_router=1)
        equips_from_ipv6 = Equipamento.objects.filter(
            ipv6equipament__ip__networkipv6__vlan=vlan_id, equipamentoambiente__is_router=1)
        for equip in equips_from_ipv4:
            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()
        for equip in equips_from_ipv6:
            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

        if vlan.ativada:
            return self.response_error(122)

        command = settings.VLAN_CREATE % (vlan.id)

        code, stdout, stderr = exec_script(command)
        if code == 0:
            vlan.activate(user)

            success_map = dict()
            success_map['codigo'] = '%04d' % code
            success_map['descricao'] = {'stdout': stdout, 'stderr': stderr}

            map = dict()
            map['sucesso'] = success_map

            return self.response(dumps_networkapi(map))
        else:
            return self.response_error(2, stdout + stderr)

    def add_remove_check_list_vlan_trunk(self, user, networkapi_map, vlan_id, operation):

        equipment_map = networkapi_map.get('equipamento')
        if equipment_map is None:
            return self.response_error(105)

        try:
            name = equipment_map.get('nome')
            if name is None or name == '':
                self.log.error(u'Parameter nome is invalid. Value: %s.', name)
                raise InvalidValueError(None, 'nome', name)

            interface_name = equipment_map.get('nome_interface')
            if interface_name is None or interface_name == '':
                self.log.error(
                    u'Parameter nome_interface is invalid. Value: %s.', interface_name)
                raise InvalidValueError(None, 'nome_interface', interface_name)

            if operation != 'list':
                vlan = Vlan().get_by_pk(vlan_id)

            # Check existence
            equipment = Equipamento().get_by_name(name)

            equip_permission = AdminPermission.EQUIP_UPDATE_CONFIG_OPERATION
            admin_permission = AdminPermission.WRITE_OPERATION
            if operation in ['check', 'list']:
                equip_permission = AdminPermission.EQUIP_READ_OPERATION
                admin_permission = AdminPermission.READ_OPERATION

            if not has_perm(user,
                            AdminPermission.VLAN_ALTER_SCRIPT,
                            admin_permission,
                            None,
                            equipment.id,
                            equip_permission):
                return self.not_authorized()

            interface = Interface.get_by_interface_equipment(
                interface_name, equipment.id)

            if interface.ligacao_front is None:
                return self.response_error(139)

            protected = None
            if operation not in ['check', 'list']:
                protected = 0

            try:
                switch_interface = interface.get_switch_interface_from_host_interface(
                    protected)
            except InterfaceNotFoundError:
                return self.response_error(144)

            if not has_perm(user,
                            AdminPermission.VLAN_ALTER_SCRIPT,
                            admin_permission,
                            None,
                            switch_interface.equipamento_id,
                            equip_permission):
                return self.not_authorized()

            # configurador -T snmp_vlans_trunk -i <nomequip> -A “'int=<interface> add=<numvlan>'”
            # configurador -T snmp_vlans_trunk -i <nomequip> -A “'int=<interface> del=<numvlan>'”
            # configurador -T snmp_vlans_trunk -i <nomequip> -A “'int=<interface> check=<numvlan>'"
            # configurador -T snmp_vlans_trunk -i <nomequip> -A
            # “'int=<interface> list'"
            command = 'configurador -T snmp_vlans_trunk -i %s -A "\'int=%s %s' % (switch_interface.equipamento.nome,
                                                                                  switch_interface.interface,
                                                                                  operation)
            if operation != 'list':
                command = command + '=%d' % vlan.num_vlan

            command = command + '\'"'

            code, stdout, stderr = exec_script(command)
            if code == 0:
                map = dict()
                success_map = dict()
                success_map['codigo'] = '%04d' % code
                success_map['descricao'] = {'stdout': stdout, 'stderr': stderr}
                map['sucesso'] = success_map

                return self.response(dumps_networkapi(map))
            else:
                return self.response_error(2, stdout + stderr)

        except EquipamentoNotFoundError:
            return self.response_error(117, name)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except InterfaceNotFoundError:
            return self.response_error(141)
        except InterfaceProtectedError:
            return self.response_error(143)
        except EquipamentoNotFoundError:
            return self.response_error(117, switch_interface.equipamento_id)
