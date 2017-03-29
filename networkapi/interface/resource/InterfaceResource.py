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

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_INTERFACE
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.interface.models import BackLinkNotFoundError
from networkapi.interface.models import EnvironmentInterface
from networkapi.interface.models import FrontLinkNotFoundError
from networkapi.interface.models import Interface
from networkapi.interface.models import InterfaceError
from networkapi.interface.models import InterfaceForEquipmentDuplicatedError
from networkapi.interface.models import InterfaceNotFoundError
from networkapi.interface.models import InterfaceUsedByOtherInterfaceError
from networkapi.interface.models import TipoInterface
from networkapi.rest import RestResource
from networkapi.util import convert_string_or_int_to_boolean
from networkapi.util import is_valid_boolean_param
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class InterfaceResource(RestResource):

    """Classe responsável por tratar as requisições relacionadas com a tabela "interfaces"."""

    log = logging.getLogger('InterfaceResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Método responsável por tratar as requisições GET para consultar as interfaces.

        URL: /interface/<nome_interface>/equipamento/<id_equipamento>
        URL: /interface/equipamento/<id_equipamento>
        """

        # Get url parameters
        equipment_id = kwargs.get('id_equipamento')
        interface_name = kwargs.get('nome_interface')

        # Temporário, remover. Fazer de outra forma.
        if isinstance(interface_name, basestring):
            interface_name = interface_name.replace('s2it_replace', '/')

        is_new = kwargs.get('new')

        try:
            # Valid id_equipamento value
            if not is_valid_int_greater_zero_param(equipment_id):
                self.log.error(
                    u'Parameter equipment_id is invalid. Value: %s', equipment_id)
                raise InvalidValueError(None, 'equipment_id', equipment_id)

            # Valid interface_name value
            if not is_valid_string_minsize(interface_name, 1, required=False) or not is_valid_string_maxsize(interface_name, 20, required=False):
                self.log.error(
                    u'Parameter interface_name is invalid. Value: %s', interface_name)
                raise InvalidValueError(None, 'interface_name', interface_name)

            # Check permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION, None,
                            equipment_id, AdminPermission.EQUIP_READ_OPERATION):
                return self.not_authorized()

            # Check interface and call search method
            if interface_name is None:
                return self.search_interface_of_equipment(equipment_id, is_new)
            else:
                return self.search_interface_by_name_and_equipment(equipment_id, interface_name, is_new)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EquipamentoNotFoundError:
            return self.response_error(117, equipment_id)
        except InterfaceNotFoundError:
            return self.response_error(141)
        except (EquipamentoError, GrupoError, InterfaceError):
            return self.response_error(1)

    def handle_post(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para criar uma nova interface para o equipamento

        URL: /interface/

        """
        # Obtém dados do request e verifica acesso
        try:

            # Obtém os dados do xml do request
            xml_map, attrs_map = loads(request.raw_post_data)

            # Obtém o mapa correspondente ao root node do mapa do XML
            # (networkapi)
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            # Verifica a existência do node "interface"
            interface_map = networkapi_map.get('interface')
            if interface_map is None:
                return self.response_error(3, u'Não existe valor para a tag interface do XML de requisição.')

            # Valid id_equipamento value
            id_equipamento = interface_map.get('id_equipamento')
            if not is_valid_int_greater_zero_param(id_equipamento):
                self.log.error(
                    u'Parameter id_equipamento is invalid. Value: %s', id_equipamento)
                raise InvalidValueError(None, 'id_equipamento', id_equipamento)
            else:
                id_equipamento = int(id_equipamento)

            # Check existence
            Equipamento.get_by_pk(id_equipamento)

            # Verify permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None,
                            id_equipamento, AdminPermission.EQUIP_WRITE_OPERATION):
                return self.not_authorized()

            # Valid name value
            nome = interface_map.get('nome')
            if not is_valid_string_minsize(nome, 1) or not is_valid_string_maxsize(nome, 20):
                self.log.error(u'Parameter nome is invalid. Value: %s', nome)
                raise InvalidValueError(None, 'nome', nome)

            # Valid protegida value
            protegida = interface_map.get('protegida')
            if not is_valid_boolean_param(protegida):
                self.log.error(
                    u'Parameter protegida is invalid. Value: %s', protegida)
                raise InvalidValueError(None, 'protegida', protegida)
            else:
                protegida = convert_string_or_int_to_boolean(protegida)

            # Valid descricao value
            descricao = interface_map.get('descricao')
            if descricao is not None:
                if not is_valid_string_minsize(descricao, 3) or not is_valid_string_maxsize(descricao, 200):
                    self.log.error(
                        u'Parameter descricao is invalid. Value: %s', descricao)
                    raise InvalidValueError(None, 'descricao', descricao)

            # Valid "id_ligacao_front" value
            id_ligacao_front = interface_map.get('id_ligacao_front')
            if id_ligacao_front is not None:
                if not is_valid_int_greater_zero_param(id_ligacao_front):
                    self.log.error(
                        u'The id_ligacao_front parameter is not a valid value: %s.', id_ligacao_front)
                    raise InvalidValueError(
                        None, 'id_ligacao_front', id_ligacao_front)
                else:
                    id_ligacao_front = int(id_ligacao_front)
                    ligacao_front = Interface(id=id_ligacao_front)
            else:
                ligacao_front = None

            # Valid "id_ligacao_back" value
            id_ligacao_back = interface_map.get('id_ligacao_back')
            if id_ligacao_back is not None:
                if not is_valid_int_greater_zero_param(id_ligacao_back):
                    self.log.error(
                        u'The id_ligacao_back parameter is not a valid value: %s.', id_ligacao_back)
                    raise InvalidValueError(
                        None, 'id_ligacao_back', id_ligacao_back)
                else:
                    id_ligacao_back = int(id_ligacao_back)
                    ligacao_back = Interface(id=id_ligacao_back)
            else:
                ligacao_back = None

            tipo_interface = interface_map.get('tipo')
            if tipo_interface is None:
                tipo_interface = 'Access'
            tipo_interface = TipoInterface.get_by_name(tipo_interface)

            vlan = interface_map.get('vlan')

            # Cria a interface conforme dados recebidos no XML
            interface = Interface(
                interface=nome,
                protegida=protegida,
                descricao=descricao,
                ligacao_front=ligacao_front,
                ligacao_back=ligacao_back,
                equipamento=Equipamento(id=id_equipamento),
                tipo=tipo_interface,
                vlan_nativa=vlan
            )

            interface.create(user)

            networkapi_map = dict()
            interface_map = dict()

            interface_map['id'] = interface.id
            networkapi_map['interface'] = interface_map

            return self.response(dumps_networkapi(networkapi_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except EquipamentoNotFoundError:
            return self.response_error(117, id_equipamento)
        except FrontLinkNotFoundError:
            return self.response_error(212)
        except BackLinkNotFoundError:
            return self.response_error(213)
        except InterfaceForEquipmentDuplicatedError:
            return self.response_error(187, nome, id_equipamento)
        except (InterfaceError, GrupoError, EquipamentoError):
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Trata uma requisição PUT para alterar informações de uma interface.

        URL: /interface/<id_interface>/
        """

        # Get request data and check permission
        try:
            # Valid Interface ID
            id_interface = kwargs.get('id_interface')
            if not is_valid_int_greater_zero_param(id_interface):
                self.log.error(
                    u'The id_interface parameter is not a valid value: %s.', id_interface)
                raise InvalidValueError(None, 'id_interface', id_interface)

            # Get interface and equipment to check permission
            interface = Interface.get_by_pk(id_interface)
            id_equipamento = interface.equipamento_id

            # Check permission
            if not has_perm(user,
                            AdminPermission.EQUIPMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION,
                            None,
                            id_equipamento,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                return self.not_authorized()

            # Get XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no networkapi tag in XML request.')

            interface_map = networkapi_map.get('interface')
            if interface_map is None:
                return self.response_error(3, u'There is no interface tag in XML request.')

            # Valid name value
            nome = interface_map.get('nome')
            if not is_valid_string_minsize(nome, 1) or not is_valid_string_maxsize(nome, 20):
                self.log.error(u'Parameter nome is invalid. Value: %s', nome)
                raise InvalidValueError(None, 'nome', nome)

            # Valid protegida value
            protegida = interface_map.get('protegida')
            if not is_valid_boolean_param(protegida):
                self.log.error(
                    u'Parameter protegida is invalid. Value: %s', protegida)
                raise InvalidValueError(None, 'protegida', protegida)
            else:
                protegida = convert_string_or_int_to_boolean(protegida)

            # Valid descricao value
            descricao = interface_map.get('descricao')
            if descricao is not None:
                if not is_valid_string_minsize(descricao, 3) or not is_valid_string_maxsize(descricao, 200):
                    self.log.error(
                        u'Parameter descricao is invalid. Value: %s', descricao)
                    raise InvalidValueError(None, 'descricao', descricao)

            # Valid "id_ligacao_front" value
            id_ligacao_front = interface_map.get('id_ligacao_front')
            if id_ligacao_front is not None:
                if not is_valid_int_greater_zero_param(id_ligacao_front):
                    self.log.error(
                        u'The id_ligacao_front parameter is not a valid value: %s.', id_ligacao_front)
                    raise InvalidValueError(
                        None, 'id_ligacao_front', id_ligacao_front)
                else:
                    id_ligacao_front = int(id_ligacao_front)

            # Valid "id_ligacao_back" value
            id_ligacao_back = interface_map.get('id_ligacao_back')
            if id_ligacao_back is not None:
                if not is_valid_int_greater_zero_param(id_ligacao_back):
                    self.log.error(
                        u'The id_ligacao_back parameter is not a valid value: %s.', id_ligacao_back)
                    raise InvalidValueError(
                        None, 'id_ligacao_back', id_ligacao_back)
                else:
                    id_ligacao_back = int(id_ligacao_back)

            tipo = interface_map.get('tipo')
            if tipo is not None:
                tipo = TipoInterface.get_by_name(tipo)

            vlan = interface_map.get('vlan')
            with distributedlock(LOCK_INTERFACE % id_interface):

                # Update interface
                Interface.update(user,
                                 id_interface,
                                 interface=nome,
                                 protegida=protegida,
                                 descricao=descricao,
                                 ligacao_front_id=id_ligacao_front,
                                 ligacao_back_id=id_ligacao_back,
                                 tipo=tipo,
                                 vlan_nativa=vlan)

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except InterfaceNotFoundError:
            return self.response_error(141)
        except FrontLinkNotFoundError:
            return self.response_error(212)
        except BackLinkNotFoundError:
            return self.response_error(213)
        except InterfaceForEquipmentDuplicatedError:
            return self.response_error(187, nome, id_equipamento)
        except (InterfaceError, GrupoError, EquipamentoError):
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Trata uma requisição DELETE para excluir uma interface

        URL: /interface/<id_interface>/

        """
        # Get request data and check permission
        try:
            # Valid Interface ID
            id_interface = kwargs.get('id_interface')
            if not is_valid_int_greater_zero_param(id_interface):
                self.log.error(
                    u'The id_interface parameter is not a valid value: %s.', id_interface)
                raise InvalidValueError(None, 'id_interface', id_interface)

            # Get interface and equipment to check permission
            interface = Interface.get_by_pk(id_interface)
            id_equipamento = interface.equipamento_id

            # Check permission
            if not has_perm(user,
                            AdminPermission.EQUIPMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION,
                            None,
                            id_equipamento,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                return self.not_authorized()

            with distributedlock(LOCK_INTERFACE % id_interface):

                # Remove interface
                Interface.remove(user, id_interface)

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

    def search_interface_of_equipment(self, equipment_id, is_new):
        """Obtém as interfaces do equipamento"""

        # Efetua a consulta das interfaces do equipamento
        results = Interface.search(equipment_id)

        if results.count() > 0:
            # Monta lista com dados retornados
            map_list = []
            for item in results:
                if is_new:
                    map_list.append(self.get_new_interface_map(item))
                else:
                    map_list.append(self.get_interface_map(item))

            # Gera response (XML) com resultados
            if is_new:
                return self.response(dumps_networkapi({'interfaces': map_list}))
            else:
                return self.response(dumps_networkapi({'interface': map_list}))

        else:
            # Gera response (XML) para resultado vazio
            return self.response(dumps_networkapi({}))

    def search_interface_by_name_and_equipment(self, equipment_id, interface_name, is_new):
        """Obtém a interface do equipamento e retorna todas as interfaces ligadas no front e no back. """

        interface = Interface.get_by_interface_equipment(
            interface_name, equipment_id)
        interfaces = interface.search_front_back_interfaces()

        map_list = []
        for interface in interfaces:
            if is_new:
                map_list.append(self.get_new_interface_map(interface))
            else:
                map_list.append(self.get_interface_map(interface))

        if is_new:
            return self.response(dumps_networkapi({'interfaces': map_list}))
        else:
            return self.response(dumps_networkapi({'interface': map_list}))

    def get_interface_map(self, interface):
        """Gera o mapa para renderização do XML com os atributos de uma interface"""
        map = dict()
        map['id'] = interface.id
        map['nome'] = interface.interface
        map['protegida'] = interface.protegida
        map['descricao'] = interface.descricao
        map['tipo'] = interface.tipo.tipo
        map['id_equipamento'] = interface.equipamento_id
        map['equipamento_nome'] = interface.equipamento.nome
        map['vlan'] = interface.vlan_nativa
        map['sw_router'] = None
        if interface.channel is not None:
            map['channel'] = interface.channel.nome
            map['lacp'] = interface.channel.lacp
            map['id_channel'] = interface.channel.id
            map['sw_router'] = True
        elif interface.ligacao_front is not None:
            try:
                sw_router = interface.get_switch_and_router_interface_from_host_interface(
                    None)
                if sw_router.channel is not None:
                    map['channel'] = sw_router.channel.nome
                    map['lacp'] = sw_router.channel.lacp
                    map['id_channel'] = sw_router.channel.id
            except:
                pass
        if interface.ligacao_front is None:
            map['id_ligacao_front'] = ''
        else:
            map['id_ligacao_front'] = interface.ligacao_front_id
        if interface.ligacao_back is None:
            map['id_ligacao_back'] = ''
        else:
            map['id_ligacao_back'] = interface.ligacao_back_id
        return map

    def get_new_interface_map(self, interface):
        int_map = model_to_dict(interface)
        int_map['nome'] = interface.interface
        int_map['tipo_equip'] = interface.equipamento.tipo_equipamento_id
        int_map['equipamento_nome'] = interface.equipamento.nome
        int_map['marca'] = interface.equipamento.modelo.marca_id
        int_map['tipo'] = interface.tipo.tipo
        int_map['vlan'] = interface.vlan_nativa
        int_map['sw_router'] = None
        if interface.channel is not None:
            int_map['channel'] = interface.channel.nome
            int_map['lacp'] = interface.channel.lacp
            int_map['id_channel'] = interface.channel.id
            int_map['sw_router'] = True
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
        if interface.ligacao_back is not None:
            int_map['nome_ligacao_back'] = interface.ligacao_back.interface
            int_map['nome_equip_l_back'] = interface.ligacao_back.equipamento.nome

        return int_map
