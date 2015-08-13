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
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi, XMLError, loads
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.interface.models import PortChannel, Interface, InterfaceError, TipoInterface
from networkapi.equipamento.models import Equipamento
from django.forms.models import model_to_dict
from networkapi.exception import InvalidValueError
from networkapi.util import convert_string_or_int_to_boolean




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

            port_channel = PortChannel()
            interface = Interface()

            port_channel.nome = str(nome)
            port_channel.lacp = convert_string_or_int_to_boolean(lacp)
            port_channel.create(user)

            interfaces = str(interfaces).split('-')

            for var in interfaces:
                if not var=="":
                    interf = interface.get_by_pk(int(var))

                    if interf.ligacao_front is not None:
                        ligacao_front_id = interf.ligacao_front.id
                    else:
                        ligacao_front_id = None
                    if interf.ligacao_back is not None:
                        ligacao_back_id = interf.ligacao_back.id
                    else:
                        ligacao_back_id = None

                    Interface.update(user,
                                     interf.id,
                                     interface=interf.interface,
                                     protegida=interf.protegida,
                                     descricao=interf.descricao,
                                     ligacao_front_id=ligacao_front_id,
                                     ligacao_back_id=ligacao_back_id,
                                     tipo=interf.tipo,
                                     vlan_nativa=interf.vlan_nativa,
                                     channel=port_channel)

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