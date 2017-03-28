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

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.interface.models import EnvironmentInterface
from networkapi.interface.models import Interface
from networkapi.interface.models import InterfaceError
from networkapi.interface.models import InterfaceNotFoundError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


def get_new_interface_map(interface):
    int_map = model_to_dict(interface)
    int_map['id'] = interface.id
    int_map['nome'] = interface.interface
    int_map['descricao'] = interface.descricao
    int_map['tipo_equip'] = interface.equipamento.tipo_equipamento_id
    int_map['equipamento_nome'] = interface.equipamento.nome
    int_map['marca'] = interface.equipamento.modelo.marca_id
    int_map['protegida'] = interface.protegida
    int_map['tipo'] = interface.tipo.tipo
    int_map['vlan'] = interface.vlan_nativa
    int_map['sw_router'] = None
    if interface.channel is not None:
        int_map['channel'] = interface.channel.nome
        int_map['lacp'] = interface.channel.lacp
        int_map['id_channel'] = interface.channel.id
        int_map['sw_router'] = True
        try:
            vlans = EnvironmentInterface.objects.filter(
                interface=interface.id).uniqueResult()
            int_map['vlans'] = vlans.vlans
        except:
            int_map['vlans'] = None
            pass
    elif interface.ligacao_front is not None:
        try:
            sw_router = interface.get_switch_and_router_interface_from_host_interface(
                None)
            if sw_router.channel is not None:
                int_map['channel'] = sw_router.channel.nome
                int_map['lacp'] = sw_router.channel.lacp
                int_map['id_channel'] = sw_router.channel.id
        except:
            pass
    if interface.ligacao_front is not None:
        int_map['nome_ligacao_front'] = interface.ligacao_front.interface
        int_map['nome_equip_l_front'] = interface.ligacao_front.equipamento.nome
        int_map['id_ligacao_front'] = interface.ligacao_front.id
    if interface.ligacao_back is not None:
        int_map['nome_ligacao_back'] = interface.ligacao_back.interface
        int_map['nome_equip_l_back'] = interface.ligacao_back.equipamento.nome
        int_map['id_ligacao_back'] = interface.ligacao_back.id

    return int_map


class InterfaceGetResource(RestResource):

    log = logging.getLogger('InterfaceGetResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat GET requests to list interface by ID or by channel

        URL: interface/<id_interface>/get/
             interface/get-by-channel/<channel_name>/equip-name/
             interface/get/<channel_name>/<id_equip>
        """

        try:

            self.log.info('GET Interface')

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Get id_interface param
            interface = kwargs.get('id_interface')
            channel = kwargs.get('channel_name')
            equipamento = kwargs.get('id_equipamento')
            equip_name = kwargs.get('equip_name')

            equipInterface_list = []
            interface_list = []

            # Valid Interface ID
            if interface is not None:
                if not is_valid_int_greater_zero_param(interface):
                    self.log.error(
                        u'The id_interface parameter is not a valid value: %s.', interface)
                    raise InvalidValueError(None, 'id_interface', interface)
                id_interface = interface
                # Checks if interface exists in database
                interface = Interface.get_by_pk(id_interface)
                int_map = get_new_interface_map(interface)
                # Return interface map
                return self.response(dumps_networkapi({'interface': int_map}))

            if channel is not None:
                if equip_name is not None:
                    interfaces = Interface.objects.all().filter(channel__nome=channel)
                    channel_id = None
                    for interf in interfaces:
                        if interf.equipamento.nome == equip_name or interf.ligacao_front.equipamento.nome == equip_name:
                            channel_id = interf.channel.id
                    for interf in interfaces:
                        if interf.channel.id == channel_id:
                            equipInterface_list.append(
                                get_new_interface_map(interf))
                    return self.response(dumps_networkapi({'interfaces': equipInterface_list}))
                if equipamento is not None:
                    interfaces = Interface.objects.all().filter(channel__nome=channel)
                    for interf in interfaces:
                        if interf.equipamento.id == int(equipamento):
                            int_server = interf.get_server_switch_or_router_interface_from_host_interface()
                            equipamento = int_server.equipamento.id
                    interfaces_equip = Interface.objects.all().filter(
                        equipamento__id=int(equipamento))
                    for interf in interfaces_equip:
                        try:
                            i = interf.get_switch_and_router_interface_from_host_interface()
                            interface_list.append(get_new_interface_map(i))
                        except:
                            pass
                    return self.response(dumps_networkapi({'interfaces': interface_list}))

            return self.response(dumps_networkapi({}))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except InterfaceNotFoundError:
            return self.response_error(141)
        except (InterfaceError, GrupoError, EquipamentoError):
            return self.response_error(1)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
