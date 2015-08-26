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

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi, XMLError, loads
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.interface.models import PortChannel, Interface, InterfaceError, TipoInterface, EnvironmentInterface
from networkapi.exception import InvalidValueError
from networkapi.util import convert_string_or_int_to_boolean
from networkapi.ambiente.models import Ambiente
from django.forms.models import model_to_dict

class InterfaceChannelResource(RestResource):

    log = Log('InterfaceChannelResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Rack.

        URL: channel/inserir/
        """
        try:
            self.log.info("Inserir novo Channel")

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
            vlan = channel_map.get('vlan')
            envs = channel_map.get('envs')
            port_channel = PortChannel()
            interface = Interface()
            amb = Ambiente()

            port_channel.nome = str(nome)
            port_channel.lacp = convert_string_or_int_to_boolean(lacp)
            port_channel.create(user)

            interfaces = str(interfaces).split('-')

            int_type = TipoInterface.get_by_name(str(int_type))
            for var in interfaces:
                if not var==("" or None):
                    interf = interface.get_by_pk(int(var))
                    try:
                        sw_router = interf.get_switch_and_router_interface_from_host_interface(interf.protegida)
                    except:
                        raise Exception("Interface não conectada.")
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
                                     vlan_nativa=vlan,
                                     channel=port_channel)

                    if "trunk" in int_type.tipo:
                        interface_list = EnvironmentInterface.objects.all().filter(interface=sw_router.id)
                        for int_env in interface_list:
                            int_env.delete(user)
                        if envs is not None:
                            if not type(envs)==unicode:
                                for env in envs:
                                    amb_int = EnvironmentInterface()
                                    amb_int.interface = sw_router
                                    amb_int.ambiente = amb.get_by_pk(int(env))
                                    amb_int.create(user)
                            else:
                                amb_int = EnvironmentInterface()
                                amb_int.interface = sw_router
                                amb_int.ambiente = amb.get_by_pk(int(envs))
                                amb_int.create(user)

            port_channel_map = dict()
            port_channel_map['port_channel'] = port_channel

            return self.response(dumps_networkapi({'port_channel': port_channel_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except InterfaceError:
           return self.response_error(1)

    def handle_get(self, request, user, *args, **kwargs):
        """Trata uma requisição PUT para alterar informações de um channel.
        URL: channel/get-by-name/
        """
        # Get request data and check permission

        try:
            self.log.info("Get Channel")

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
            channel = model_to_dict(channel)

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

        URL: /channel/delete/<channel_name>/

        """
        # Get request data and check permission
        try:
            self.log.info("Delete Channel")

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            channel_name = kwargs.get('channel_name')

            channel = PortChannel.get_by_name(str(channel_name))

            channel.delete(user)

            return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except InterfaceNotFoundError:
            return self.response_error(141)
        except InterfaceUsedByOtherInterfaceError:
            return self.response_error(214, id_interface)
        except (InterfaceError, GrupoError, EquipamentoError):
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests POST to add Rack.

        URL: channel/editar/
        """
        try:
            self.log.info("Editar Channel")

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
            lacp = channel_map.get('lacp')
            int_type = channel_map.get('int_type')
            vlan = channel_map.get('vlan')
            envs = channel_map.get('envs')
            ids_interface = channel_map.get('ids_interface')

            port_channel = PortChannel()
            interface = Interface()
            amb = Ambiente()

            #buscar interfaces do channel
            interfaces = Interface.objects.all().filter(channel__id=id_channel)
            ids_list = []
            for i in interfaces:
                ids_list.append(i.id)


            ids_interface = [ int(x) for x in ids_interface ]
            ids_list = [ int(y) for y in ids_list ]
            desassociar = set(ids_list) - set(ids_interface)
            for item in desassociar:
                item = interface.get_by_pk(int(item))
                item.channel = None
                item.save(user)

            #update channel
            port_channel = port_channel.get_by_pk(id_channel)
            port_channel.nome = str(nome)
            port_channel.lacp = convert_string_or_int_to_boolean(lacp)
            port_channel.save(user)

            int_type = TipoInterface.get_by_name(str(int_type))

            #update interfaces
            for var in ids_interface:
                var = interface.get_by_pk(int(var))
                if var.channel is None:
                    var.channel = port_channel
                var.tipo = int_type
                var.vlan_nativa = vlan
                var.save(user)

                if "trunk" in int_type.tipo:
                    interface_list = EnvironmentInterface.objects.all().filter(interface=var.id)
                    for int_env in interface_list:
                        int_env.delete(user)
                    if envs is not None:
                        if not type(envs)==unicode:
                            for env in envs:
                                amb_int = EnvironmentInterface()
                                amb_int.interface = var
                                amb_int.ambiente = amb.get_by_pk(int(env))
                                amb_int.create(user)
                        else:
                            amb_int = EnvironmentInterface()
                            amb_int.interface = var
                            amb_int.ambiente = amb.get_by_pk(int(envs))
                            amb_int.create(user)

            port_channel_map = dict()
            port_channel_map['port_channel'] = port_channel

            return self.response(dumps_networkapi({'port_channel': port_channel_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except InterfaceError:
           return self.response_error(1)