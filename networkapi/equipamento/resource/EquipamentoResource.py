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

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import *
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_BRAND
from networkapi.distributedlock import LOCK_EQUIPMENT
from networkapi.distributedlock import LOCK_EQUIPMENT_ENVIRONMENT
from networkapi.distributedlock import LOCK_EQUIPMENT_SCRIPT
from networkapi.distributedlock import LOCK_MODEL
from networkapi.equipamento.models import *
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import EGrupoNotFoundError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import IpCantBeRemovedFromVip
from networkapi.ip.models import IpEquipamento
from networkapi.ip.models import Ipv6Equipament
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.roteiro.models import *
from networkapi.util import convert_string_or_int_to_boolean
from networkapi.util import destroy_cache_function
from networkapi.util import is_valid_boolean_param
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


def add_script(user, equipamento):
    try:
        modelo_roteiro = ModeloRoteiro.objects.filter(
            modelo__id=equipamento.modelo.id)
        for rot in modelo_roteiro:
            equip_roteiro = EquipamentoRoteiro()
            equip_roteiro.roteiro = rot.roteiro
            equip_roteiro.equipamento = equipamento
            equip_roteiro.create(user)
    except:
        pass


def remove_equipment(equipment_id, user):
    """Remove um equipamento e todos os seus relacionamentos.

    @return: Nothing.

    @raise EquipamentoNotFoundError: Equipamento não cadastrado.

    @raise EquipamentoError, GrupoError: Falha no banco de dados.

    @raise UserNotAuthorizedError: Usuário sem autorização para executar a operação.
    """
    if not has_perm(user,
                    AdminPermission.EQUIPMENT_MANAGEMENT,
                    AdminPermission.WRITE_OPERATION,
                    None,
                    equipment_id,
                    AdminPermission.EQUIP_WRITE_OPERATION):
        raise UserNotAuthorizedError(
            None, u'Usuário não tem permissão para executar a operação.')

    Equipamento().remove(user, equipment_id)
    return


def insert_equipment(equipment_map, user):
    """
    Insere um equipamento e o relacionamento entre equipamento e o grupo.

    @param equipment_map: Map com as chaves: id_grupo, id_tipo_equipamento, id_modelo e nome
    @param user: Usuário autenticado na API.

    @return Em caso de erro retorna a tupla: (código da mensagem de erro, argumento01, argumento02, ...)
            Em caso de sucesso retorna a tupla: (0, <identificador do equipamento_grupo>, <equipamento>)

    @raise InvalidGroupToEquipmentTypeError: Equipamento do grupo “Equipamentos Orquestração” somente poderá ser criado com tipo igual a “Servidor Virtual”.

    @raise EGrupoNotFoundError: Grupo não cadastrado.

    @raise GrupoError: Falha ao pesquisar o Grupo.

    @raise TipoEquipamentoNotFoundError: Tipo de equipamento nao cadastrado.

    @raise ModeloNotFoundError: Modelo nao cadastrado.

    @raise EquipamentoNameDuplicatedError: Nome do equipamento duplicado.

    @raise EquipamentoError: Falha ou inserir o equipamento.

    @raise UserNotAuthorizedError: Usuário sem autorização para executar a operação.

    """
    log = logging.getLogger('insert_equipment')

    log.debug('EQUIPAMENTO_MAP: %s', equipment_map)

    equipment = Equipamento()
    equipment.tipo_equipamento = TipoEquipamento()
    equipment.modelo = Modelo()

    group_id = equipment_map.get('id_grupo')
    if not is_valid_int_greater_zero_param(group_id):
        log.error(
            u'The group_id parameter is not a valid value: %s.', group_id)
        raise InvalidValueError(None, 'group_id', group_id)
    else:
        group_id = int(group_id)

    if not has_perm(user,
                    AdminPermission.EQUIPMENT_MANAGEMENT,
                    AdminPermission.WRITE_OPERATION,
                    group_id,
                    None,
                    AdminPermission.EQUIP_WRITE_OPERATION):
        raise UserNotAuthorizedError(
            None, u'Usuário não tem permissão para executar a operação.')

    equipment_type_id = equipment_map.get('id_tipo_equipamento')
    if not is_valid_int_greater_zero_param(equipment_type_id):
        log.error(
            u'The equipment_type_id parameter is not a valid value: %s.', equipment_type_id)
        raise InvalidValueError(None, 'equipment_type_id', equipment_type_id)
    else:
        equipment.tipo_equipamento.id = int(equipment_type_id)

    model_id = equipment_map.get('id_modelo')
    if not is_valid_int_greater_zero_param(model_id):
        log.error(
            u'The model_id parameter is not a valid value: %s.', model_id)
        raise InvalidValueError(None, 'model_id', model_id)
    else:
        equipment.modelo.id = int(model_id)

    name = equipment_map.get('nome')
    if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 50):
        log.error(u'The name parameter is not a valid value: %s.', name)
        raise InvalidValueError(None, 'name', name)
    else:
        equipment.nome = name

    # maintenance is a new feature. Check existing value if not defined in request
    # Old calls does not send this field
    maintenance = equipment_map.get('maintenance')
    if maintenance is None:
        maintenance = False
    if not is_valid_boolean_param(maintenance):
        log.error(
            u'The maintenance parameter is not a valid value: %s.', maintenance)
        raise InvalidValueError(None, 'maintenance', maintenance)
    else:
        equipment.maintenance = convert_string_or_int_to_boolean(maintenance)

    equipment_group_id = equipment.create(user, group_id)

    return 0, equipment_group_id, equipment


class EquipamentoResource(RestResource):

    """Classe que trata as requisicoes de PUT,POST,GET e DELETE para a tabela equipamentos."""

    log = logging.getLogger('EquipamentoResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Trata uma requisicao POST para inserir um equipamento.

        URL: equipamento/
        """

        try:
            xml_map, attrs_map = loads(request.raw_post_data)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)

        self.log.debug('XML_MAP: %s', xml_map)

        networkapi_map = xml_map.get('networkapi')
        if networkapi_map is None:
            return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

        equipment_map = networkapi_map.get('equipamento')
        if equipment_map is None:
            return self.response_error(3, u'Não existe valor para a tag equipamento do XML de requisição.')

        try:
            response = insert_equipment(equipment_map, user)
            if response[0] == 0:
                networkapi_map = dict()

                equipment_map = dict()
                equipment_map['id'] = response[2].id

                equipment_group_map = dict()
                equipment_group_map['id'] = response[1]

                networkapi_map['equipamento'] = equipment_map
                networkapi_map['equipamento_grupo'] = equipment_group_map

                add_script(user, response[2])

                return self.response(dumps_networkapi(networkapi_map))
            else:
                if len(response) > 1:
                    return self.response_error(response[0], response[1:len(response)])
                return self.response_error(response[0])

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except InvalidGroupToEquipmentTypeError:
            return self.response_error(107)
        except TipoEquipamentoNotFoundError:
            return self.response_error(100)
        except ModeloNotFoundError:
            return self.response_error(101)
        except EquipamentoNameDuplicatedError:
            return self.response_error(149)
        except EGrupoNotFoundError:
            return self.response_error(102)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except (EquipamentoError, GrupoError):
            return self.response_error(1)

    def handle_get(self, request, user, *args, **kwargs):
        """Trata requisições GET para consulta de equipamentos.

        Permite a consulta de equipamento filtrado por nome,
        equipamentos filtrados por tipo de equipamento e ambiente

        URLs: /equipamento/nome/<nome_equip>/
              /equipamento/id/<id_equip>/
              /equipamento/tipoequipamento/<id_tipo_equip>/ambiente/<id_ambiente>/
        """
        try:
            equipment_name = kwargs.get('nome_equip')
            equipment_id = kwargs.get('id_equip')
            equipment_type_id = kwargs.get('id_tipo_equip')
            environment_id = kwargs.get('id_ambiente')

            if (equipment_id is None) and (equipment_name is None) and (equipment_type_id is None or environment_id is None):
                return super(EquipamentoResource, self).handle_get(request, user, *args, **kwargs)

            equipments = []
            if equipment_id is not None:

                if not is_valid_int_greater_zero_param(equipment_id):
                    self.log.error(
                        u'The equipment_id parameter is not a valid value: %s.', equipment_id)
                    raise InvalidValueError(None, 'equipment_id', equipment_id)

                equipment = Equipamento.get_by_pk(int(equipment_id))

                if not has_perm(user,
                                AdminPermission.EQUIPMENT_MANAGEMENT,
                                AdminPermission.READ_OPERATION,
                                None,
                                equipment.id,
                                AdminPermission.EQUIP_READ_OPERATION):
                    return self.not_authorized()

                equipments.append(equipment)

            elif equipment_name is not None:

                equipment = Equipamento.get_by_name(equipment_name)

                if not has_perm(user,
                                AdminPermission.EQUIPMENT_MANAGEMENT,
                                AdminPermission.READ_OPERATION,
                                None,
                                equipment.id,
                                AdminPermission.EQUIP_READ_OPERATION):
                    return self.not_authorized()

                equipments.append(equipment)

            else:
                if not has_perm(user,
                                AdminPermission.EQUIPMENT_MANAGEMENT,
                                AdminPermission.READ_OPERATION):
                    return self.not_authorized()

                if not is_valid_int_greater_zero_param(environment_id):
                    self.log.error(
                        u'The environment_id parameter is not a valid value: %s.', environment_id)
                    raise InvalidValueError(
                        None, 'environment_id', environment_id)

                if not is_valid_int_greater_zero_param(equipment_type_id):
                    self.log.error(
                        u'The equipment_type_id parameter is not a valid value: %s.', equipment_type_id)
                    raise InvalidValueError(
                        None, 'equipment_type_id', equipment_type_id)

                Ambiente.get_by_pk(environment_id)
                TipoEquipamento.get_by_pk(equipment_type_id)

                equipments = Equipamento().search(
                    None, equipment_type_id, environment_id, user.grupos.all())

            map_list = []
            for equipment in equipments:
                equip_map = dict()
                equip_map['id'] = equipment.id
                equip_map['nome'] = equipment.nome
                equip_map[
                    'id_tipo_equipamento'] = equipment.tipo_equipamento.id
                equip_map[
                    'nome_tipo_equipamento'] = equipment.tipo_equipamento.tipo_equipamento
                equip_map['id_modelo'] = equipment.modelo.id
                equip_map['nome_modelo'] = equipment.modelo.nome
                equip_map['id_marca'] = equipment.modelo.marca.id
                equip_map['nome_marca'] = equipment.modelo.marca.nome
                equip_map['maintenance'] = equipment.maintenance
                map_list.append(equip_map)

            return self.response(dumps_networkapi({'equipamento': map_list}))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EquipamentoNotFoundError:
            return self.response_error(117, equipment_name)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except TipoEquipamentoNotFoundError:
            return self.response_error(100)
        except (EquipamentoError, GrupoError):
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Trata requisições de DELETE para remover um equipamento.

        URL: /equipamento/id/
        """

        try:

            equipment_id = kwargs.get('id_equip')
            if not is_valid_int_greater_zero_param(equipment_id):
                self.log.error(
                    u'The equipment_id parameter is not a valid value: %s.', equipment_id)
                raise InvalidValueError(None, 'equipment_id', equipment_id)

            equip = Equipamento.get_by_pk(equipment_id)

            with distributedlock(LOCK_EQUIPMENT % equipment_id):

                ip_equipamento_list = IpEquipamento.objects.filter(
                    equipamento=equipment_id)
                ip6_equipamento_list = Ipv6Equipament.objects.filter(
                    equipamento=equipment_id)

                # Delete vlan's cache
                key_list = []
                for eq in ip_equipamento_list:
                    vlan = eq.ip.networkipv4.vlan
                    vlan_id = vlan.id
                    key_list.append(vlan_id)

                for eq in ip6_equipamento_list:
                    vlan = eq.ip.networkipv6.vlan
                    vlan_id = vlan.id
                    key_list.append(vlan_id)

                destroy_cache_function(key_list)

                remove_equipment(equipment_id, user)
                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EquipamentoNotFoundError:
            return self.response_error(117, equipment_id)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except IpCantBeRemovedFromVip, e:
            return self.response_error(345, equip.nome, e.cause, e.message)
        except (EquipamentoError, GrupoError), e:
            return self.response_error(e)
        except Exception, e:
            return self.response_error(1)


class EquipamentoAmbienteResource(RestResource):
    log = logging.getLogger('EquipamentoAmbienteResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para inserir uma associação entre um Equipamento e um Ambiente.

        URL: equipamentoambiente/$
        """

        try:
            xml_map, attrs_map = loads(request.raw_post_data)
            self.log.debug('XML_MAP: %s', xml_map)

            networkapi_map = xml_map.get('networkapi')

            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            equipenviron_map = networkapi_map.get('equipamento_ambiente')
            if equipenviron_map is None:
                return self.response_error(3, u'Não existe valor para a tag equipamento_ambiente do XML de requisição.')

            equip_id = equipenviron_map.get('id_equipamento')

            # Valid ID Equipment
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'The equip_id parameter is not a valid value: %s.', equip_id)
                raise InvalidValueError(None, 'equip_id', equip_id)

            environment_id = equipenviron_map.get('id_ambiente')

            # Valid ID Environment
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'The environment_id parameter is not a valid value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            is_router = int(equipenviron_map.get('is_router', 0))

            if not has_perm(user,
                            AdminPermission.EQUIPMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION,
                            None,
                            equip_id,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                return self.not_authorized()

            equip_environment = EquipamentoAmbiente(equipamento=Equipamento(id=equip_id),
                                                    ambiente=Ambiente(
                                                        id=environment_id),
                                                    is_router=is_router)

            equip_environment.create(user)

            equip_environment_map = dict()
            equip_environment_map['id'] = equip_environment.id
            networkapi_map = dict()
            networkapi_map['equipamento_ambiente'] = equip_environment_map

            return self.response(dumps_networkapi(networkapi_map))

        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EquipamentoAmbienteDuplicatedError:
            return self.response_error(156, equip_id, environment_id)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)
        except (EquipamentoError, RoteiroError, GrupoError):
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para inserir uma associação entre um Equipamento e um Ambiente.

        URL: equipamentoambiente/update/$
        """

        try:
            xml_map, attrs_map = loads(request.raw_post_data)
            self.log.debug('XML_MAP: %s', xml_map)

            networkapi_map = xml_map.get('networkapi')

            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            equipenviron_map = networkapi_map.get('equipamento_ambiente')
            if equipenviron_map is None:
                return self.response_error(3, u'Não existe valor para a tag equipamento_ambiente do XML de requisição.')

            equip_id = equipenviron_map.get('id_equipamento')

            # Valid ID Equipment
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'The equip_id parameter is not a valid value: %s.', equip_id)
                raise InvalidValueError(None, 'equip_id', equip_id)

            environment_id = equipenviron_map.get('id_ambiente')

            # Valid ID Environment
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'The environment_id parameter is not a valid value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            is_router = int(equipenviron_map.get('is_router', 0))

            if not has_perm(user,
                            AdminPermission.EQUIPMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION,
                            None,
                            equip_id,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                return self.not_authorized()

            try:
                equip_environment = EquipamentoAmbiente().get_by_equipment_environment(
                    equip_id, environment_id)
                equip_environment.is_router = is_router
                equip_environment.save()

            except EquipamentoAmbienteNotFoundError:
                self.log.warning(
                    u'Falha ao alterar a associação equipamento/ambiente, associação não existe %s/%s.' % (equip_id, environment_id))
                pass
            except Exception, e:
                self.log.error(
                    u'Falha ao alterar a associação equipamento/ambiente: %s/%s.' % (equip_id, environment_id))
                raise EquipamentoError(
                    e, u'Falha ao alterar a associação equipamento/ambiente: %s/%s.' % (equip_id, environment_id))

            equip_environment_map = dict()
            equip_environment_map['id'] = equip_id

            networkapi_map = dict()
            networkapi_map['equipamento_ambiente'] = equip_environment_map

            return self.response(dumps_networkapi(networkapi_map))

        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EquipamentoAmbienteDuplicatedError:
            return self.response_error(156, equip_id, environment_id)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)
        except (EquipamentoError, RoteiroError, GrupoError):
            return self.response_error(1)


if __name__ == '__main__':
    pass
