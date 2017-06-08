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
from networkapi.ambiente.models import Ambiente
from networkapi.api_interface import exceptions as api_interface_exceptions
from networkapi.api_interface import facade as api_interface_facade
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.interface.models import EnvironmentInterface
from networkapi.interface.models import Interface
from networkapi.interface.models import InterfaceError
from networkapi.interface.models import InterfaceNotFoundError
from networkapi.interface.models import PortChannel
from networkapi.interface.models import TipoInterface
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.system import exceptions as var_exceptions
from networkapi.util import convert_string_or_int_to_boolean
from networkapi.util import is_valid_int_greater_zero_param


logger = logging.getLogger(__name__)


def alterar_interface(var, interface, port_channel, int_type, vlan_nativa, user, envs_vlans, amb):

    cont = []

    var = interface.get_by_pk(int(var))

    if var.channel is None:
        var.channel = port_channel
    elif not var.channel.id == port_channel.id:
        raise InterfaceError(
            'Interface %s já está em um Channel' % var.interface)

    if cont is []:
        cont.append(int(var.equipamento.id))
    elif not var.equipamento.id in cont:
        cont.append(int(var.equipamento.id))
        if len(cont) > 2:
            raise InterfaceError(
                'Mais de dois equipamentos foram selecionados')

    var.tipo = int_type
    var.vlan_nativa = vlan_nativa
    var.save()

    interface_list = EnvironmentInterface.objects.all().filter(interface=var.id)
    for int_env in interface_list:
        int_env.delete()

    if 'trunk' in int_type.tipo:
        if type(envs_vlans) is not list:
            d = envs_vlans
            envs_vlans = []
            envs_vlans.append(d)
        for i in envs_vlans:
            amb = amb.get_by_pk(int(i.get('env')))
            amb_int = EnvironmentInterface()
            amb_int.interface = var
            amb_int.ambiente = amb
            try:
                range_vlans = i.get('vlans')
            except:
                range_vlans = None
                pass
            if range_vlans:
                api_interface_facade.verificar_vlan_range(amb, range_vlans)
                amb_int.vlans = range_vlans
            try:
                amb_int.create(user)
            except Exception, e:
                logger.error(e)
                pass


class InterfaceChannelResource(RestResource):

    log = logging.getLogger('InterfaceChannelResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Rack.
        URL: channel/inserir/
        """
        try:
            self.log.info('Inserir novo Channel')

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            channel_map = networkapi_map.get('channel')
            if channel_map is None:
                return self.response_error(3, u'There is no value to the channel tag  of XML request.')

            # Get XML data
            interfaces = channel_map.get('interfaces')
            nome = channel_map.get('nome')
            lacp = channel_map.get('lacp')
            int_type = channel_map.get('int_type')
            vlan_nativa = channel_map.get('vlan')
            envs_vlans = channel_map.get('envs')

            port_channel = PortChannel()
            interface = Interface()
            amb = Ambiente()
            cont = []

            api_interface_facade.verificar_vlan_nativa(vlan_nativa)

            # verifica se o nome do port channel já existe no equipamento
            interfaces = str(interfaces).split('-')
            api_interface_facade.verificar_nome_channel(nome, interfaces)

            # cria o port channel
            port_channel.nome = str(nome)
            port_channel.lacp = convert_string_or_int_to_boolean(lacp)
            port_channel.create(user)

            int_type = TipoInterface.get_by_name(str(int_type))

            for var in interfaces:
                if not var == '' and not var is None:
                    interf = interface.get_by_pk(int(var))

                    try:
                        sw_router = interf.get_switch_and_router_interface_from_host_interface(
                            interf.protegida)
                    except:
                        raise InterfaceError('Interface não conectada')

                    if sw_router.channel is not None:
                        raise InterfaceError(
                            'Interface %s já está em um Channel' % sw_router.interface)

                    if cont is []:
                        cont.append(int(sw_router.equipamento.id))
                    elif not sw_router.equipamento.id in cont:
                        cont.append(int(sw_router.equipamento.id))
                        if len(cont) > 2:
                            raise InterfaceError(
                                'Mais de dois equipamentos foram selecionados')

                    if sw_router.ligacao_front is not None:
                        ligacao_front_id = sw_router.ligacao_front.id
                    else:
                        ligacao_front_id = None
                    if sw_router.ligacao_back is not None:
                        ligacao_back_id = sw_router.ligacao_back.id
                    else:
                        ligacao_back_id = None

                    Interface.update(user,
                                     sw_router.id,
                                     interface=sw_router.interface,
                                     protegida=sw_router.protegida,
                                     descricao=sw_router.descricao,
                                     ligacao_front_id=ligacao_front_id,
                                     ligacao_back_id=ligacao_back_id,
                                     tipo=int_type,
                                     vlan_nativa=vlan_nativa,
                                     channel=port_channel)

                    if 'trunk' in int_type.tipo:
                        interface_list = EnvironmentInterface.objects.all().filter(interface=sw_router.id)
                        for int_env in interface_list:
                            int_env.delete()
                        if type(envs_vlans) is not list:
                            d = envs_vlans
                            envs_vlans = []
                            envs_vlans.append(d)
                        for i in envs_vlans:
                            amb = amb.get_by_pk(int(i.get('env')))
                            amb_int = EnvironmentInterface()
                            amb_int.interface = sw_router
                            amb_int.ambiente = amb
                            try:
                                range_vlans = i.get('vlans')
                            except:
                                range_vlans = None
                                pass
                            if range_vlans:
                                api_interface_facade.verificar_vlan_range(
                                    amb, range_vlans)
                                amb_int.vlans = range_vlans
                            amb_int.create(user)

            port_channel_map = dict()
            port_channel_map['port_channel'] = port_channel

            return self.response(dumps_networkapi({'port_channel': port_channel_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except InterfaceError, e:
            return self.response_error(405, e)
        except api_interface_exceptions.InterfaceException, e:
            return self.response_error(405, e)

    def handle_get(self, request, user, *args, **kwargs):
        """Trata uma requisição PUT para alterar informações de um channel.
        URL: channel/get-by-name/
        """
        # Get request data and check permission

        try:
            self.log.info('Get Channel')

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Get XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no networkapi tag in XML request.')

            channel_name = kwargs.get('channel_name')

            channel = PortChannel.get_by_name(channel_name)

            try:
                for ch in channel:
                    channel = model_to_dict(ch)
            except:
                channel = model_to_dict(channel)
                pass

            return self.response(dumps_networkapi({'channel': channel}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except InterfaceError:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Trata uma requisição DELETE para excluir um port channel
            URL: /channel/delete/<channel_name>/<interface_id>
        """
        try:
            self.log.info('Delete Channel')

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            interface_id = kwargs.get('channel_name')
            interface = Interface.get_by_pk(int(interface_id))
            equip_list = []

            try:
                interface.channel.id
                channel = interface.channel
            except:
                channel = interface.ligacao_front.channel
                pass
            try:
                interfaces = Interface.objects.all().filter(channel__id=channel.id)
            except:
                return self.response(dumps_networkapi({}))

            for i in interfaces:
                equip_list.append(i.equipamento.id)
            equip_list = set(equip_list)
            equip_dict = dict()
            for e in equip_list:
                equip_dict[str(e)] = interfaces.filter(equipamento__id=e)

            tipo = TipoInterface()
            tipo = tipo.get_by_name('access')

            for e in equip_dict:
                for i in equip_dict.get(e):
                    try:
                        front = i.ligacao_front.id
                    except:
                        front = None
                        pass
                    try:
                        back = i.ligacao_back.id
                    except:
                        back = None
                        pass
                    i.update(user,
                             i.id,
                             interface=i.interface,
                             protegida=i.protegida,
                             descricao=i.descricao,
                             ligacao_front_id=front,
                             ligacao_back_id=back,
                             tipo=tipo,
                             vlan_nativa='1')

                status = api_interface_facade.delete_channel(
                    user, e, equip_dict.get(e), channel)

            channel.delete(user)

            return self.response(dumps_networkapi({}))

        except api_interface_exceptions.InterfaceException, e:
            return self.response_error(410, e)
        except api_interface_exceptions.InvalidKeyException, e:
            return self.response_error(410, e)
        except var_exceptions.VariableDoesNotExistException, e:
            return self.response_error(410, e)
        except api_interface_exceptions.InterfaceTemplateException, e:
            return self.response_error(410, e)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests POST to add Rack.

        URL: channel/editar/
        """
        try:
            self.log.info('Editar Channel')

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            channel_map = networkapi_map.get('channel')
            if channel_map is None:
                return self.response_error(3, u'There is no value to the channel tag  of XML request.')

            # Get XML data
            id_channel = channel_map.get('id_channel')
            nome = channel_map.get('nome')
            if not is_valid_int_greater_zero_param(nome):
                raise InvalidValueError(
                    None, 'Numero do Channel', 'Deve ser um numero inteiro.')
            lacp = channel_map.get('lacp')
            int_type = channel_map.get('int_type')
            vlan_nativa = channel_map.get('vlan')
            envs_vlans = channel_map.get('envs')
            ids_interface = channel_map.get('ids_interface')
            if ids_interface is None:
                raise InterfaceError('Nenhuma interface selecionada')

            if type(ids_interface) == list:
                interfaces_list = ids_interface
            else:
                interfaces_list = str(ids_interface).split('-')

            port_channel = PortChannel()
            interface = Interface()
            amb = Ambiente()

            api_interface_facade.verificar_vlan_nativa(vlan_nativa)

            # verifica se o nome do port channel já existe no equipamento
            channel = port_channel.get_by_pk(int(id_channel))
            if not nome == channel.nome:
                api_interface_facade.verificar_nome_channel(
                    nome, interfaces_list)

            # buscar interfaces do channel
            interfaces = Interface.objects.all().filter(channel__id=id_channel)
            ids_list = []
            for i in interfaces:
                ids_list.append(i.id)

            ids_list = [int(y) for y in ids_list]
            if type(ids_interface) is list:
                ids_interface = [int(x) for x in ids_interface]
                desassociar = set(ids_list) - set(ids_interface)
                for item in desassociar:
                    item = interface.get_by_pk(int(item))
                    item.channel = None
                    item.save()
            else:
                if ids_interface is not None:
                    ids_interface = int(ids_interface)
                    if ids_interface is not None:
                        for item in ids_list:
                            item = interface.get_by_pk(int(item))
                            item.channel = None
                            item.save()
                    else:
                        for item in ids_list:
                            if not item == ids_interface:
                                item = interface.get_by_pk(int(item))
                                item.channel = None
                                item.save()

            # update channel
            channel.nome = str(nome)
            channel.lacp = convert_string_or_int_to_boolean(lacp)
            channel.save()

            int_type = TipoInterface.get_by_name(str(int_type))

            # update interfaces
            if type(ids_interface) is not list:
                i = ids_interface
                ids_interface = []
                ids_interface.append(i)
            for var in ids_interface:
                alterar_interface(var, interface, channel,
                                  int_type, vlan_nativa, user, envs_vlans, amb)
                interface = Interface()
                server_obj = Interface()
                interface_sw = interface.get_by_pk(int(var))
                interface_server = server_obj.get_by_pk(
                    interface_sw.ligacao_front.id)
                try:
                    front = interface_server.ligacao_front.id
                except:
                    front = None
                    pass
                try:
                    back = interface_server.ligacao_back.id
                except:
                    back = None
                    pass
                server_obj.update(user,
                                  interface_server.id,
                                  interface=interface_server.interface,
                                  protegida=interface_server.protegida,
                                  descricao=interface_server.descricao,
                                  ligacao_front_id=front,
                                  ligacao_back_id=back,
                                  tipo=int_type,
                                  vlan_nativa=int(vlan_nativa))

            port_channel_map = dict()
            port_channel_map['port_channel'] = port_channel

            return self.response(dumps_networkapi({'port_channel': port_channel_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except InterfaceError, e:
            return self.response_error(406, e)
