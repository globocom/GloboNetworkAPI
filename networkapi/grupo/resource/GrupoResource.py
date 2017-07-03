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
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_GROUP_EQUIPMENT
from networkapi.distributedlock import LOCK_GROUP_RIGHTS
from networkapi.distributedlock import LOCK_GROUP_USER
from networkapi.distributedlock import LOCK_PERM
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import *
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.util import destroy_cache_function
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize


class GrupoEquipamentoResource(RestResource):

    log = logging.getLogger('GrupoEquipamentoResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições de GET para listar todos os grupos de equipamento.

        URL: egrupo/$
        """
        try:
            if not has_perm(user, AdminPermission.EQUIPMENT_GROUP_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()

            egroups = EGrupo.search()

            map_list = []
            for egroup in egroups:
                egroup_map = dict()
                egroup_map['id'] = egroup.id
                egroup_map['nome'] = egroup.nome

                map_list.append(egroup_map)

            return self.response(dumps_networkapi({'grupo': map_list}))

        except (GrupoError):
            return self.response_error(1)

    def handle_post(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para inserir um grupo de equipamento.

        URL: egrupo/
        """
        try:
            if not has_perm(user, AdminPermission.EQUIPMENT_GROUP_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            xml_map, attrs_map = loads(request.raw_post_data)
            self.log.debug('XML_MAP: %s', xml_map)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            egroup_map = networkapi_map.get('grupo')
            if egroup_map is None:
                return self.response_error(3, u'Não existe valor para a tag grupo do XML de requisição.')

            name = egroup_map.get('nome')
            if not is_valid_string_maxsize(name, 100):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            egroup = EGrupo()
            egroup.nome = name
            egroup.create(user)

            return self.response(dumps_networkapi({'grupo': {'id': egroup.id}}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EGrupoNameDuplicatedError:
            return self.response_error(254, name)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)
        except GrupoError:
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Trata as requisições de PUT para alterar um grupo de equipamento.

        URL: egrupo/<id_grupo>/
        """
        try:
            egroup_id = kwargs.get('id_grupo')
            if not is_valid_int_greater_zero_param(egroup_id):
                self.log.error(
                    u'The egroup_id parameter is not a valid value: %s.', egroup_id)
                raise InvalidValueError(None, 'egroup_id', egroup_id)

            egrp = EGrupo.get_by_pk(egroup_id)

            if not has_perm(user, AdminPermission.EQUIPMENT_GROUP_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            xml_map, attrs_map = loads(request.raw_post_data)
            self.log.debug('XML_MAP: %s', xml_map)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            egroup_map = networkapi_map.get('grupo')
            if egroup_map is None:
                return self.response_error(3, u'Não existe valor para a tag grupo do XML de requisição.')

            name = egroup_map.get('nome')
            if not is_valid_string_maxsize(name, 100):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            with distributedlock(LOCK_GROUP_EQUIPMENT % egroup_id):

                # Destroy equipment's cache
                equip_id_list = []
                for equipament in egrp.equipamento_set.all():
                    equip_id_list.append(equipament.id)
                destroy_cache_function(equip_id_list, True)

                EGrupo.update(user, egroup_id, nome=name)

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EGrupoNotFoundError:
            return self.response_error(102)
        except EGrupoNameDuplicatedError:
            return self.response_error(254, name)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)
        except GrupoError:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Trata as requisições de DELETE para remover um grupo de equipamento.

        URL: egrupo/<id_grupo>/
        """

        try:
            egroup_id = kwargs.get('id_grupo')
            if not is_valid_int_greater_zero_param(egroup_id):
                self.log.error(
                    u'The egroup_id parameter is not a valid value: %s.', egroup_id)
                raise InvalidValueError(None, 'egroup_id', egroup_id)

            egrp = EGrupo.get_by_pk(egroup_id)

            if not has_perm(user, AdminPermission.EQUIPMENT_GROUP_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            with distributedlock(LOCK_GROUP_EQUIPMENT % egroup_id):
                EGrupo.remove(user, egroup_id)
                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except GroupDontRemoveError, e:
            return self.response_error(310, e.cause, e.message)
        except EGrupoNotFoundError:
            return self.response_error(102)
        except GrupoError:
            return self.response_error(1)


class DireitoGrupoEquipamentoResource(RestResource):
    log = logging.getLogger('DireitoGrupoEquipamentoResource')

    def __get_direito_map(self, direito):
        direito_map = dict()
        direito_map['id'] = direito.id
        direito_map['id_grupo_usuario'] = direito.ugrupo_id
        direito_map['nome_grupo_usuario'] = direito.ugrupo.nome
        direito_map['id_grupo_equipamento'] = direito.egrupo_id
        direito_map['nome_grupo_equipamento'] = direito.egrupo.nome
        direito_map['leitura'] = direito.leitura
        direito_map['escrita'] = direito.escrita
        direito_map['alterar_config'] = direito.alterar_config
        direito_map['exclusao'] = direito.exclusao
        return direito_map

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições de GET para listar os direitos de grupo de usuários em grupo de equipamentos.

        URLs: direitosgrupoequipamento/$
              direitosgrupoequipamento/ugrupo/<id_grupo_usuario>/$
              direitosgrupoequipamento/egrupo/<id_grupo_equipamento>/$
              direitosgrupoequipamento/<id_direito>/$
        """

        try:
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.READ_OPERATION):
                return self.not_authorized()

            map_list = []

            right_id = kwargs.get('id_direito')

            if not is_valid_int_greater_zero_param(right_id, False):
                self.log.error(
                    u'The right_id parameter is not a valid value: %s.', right_id)
                raise InvalidValueError(None, 'right_id', right_id)

            if right_id is not None:
                map_list.append(
                    self.__get_direito_map(DireitosGrupoEquipamento.get_by_pk(right_id)))
            else:

                ugroup = kwargs.get('id_grupo_usuario')
                egroup = kwargs.get('id_grupo_equipamento')

                if not is_valid_int_greater_zero_param(ugroup, False):
                    self.log.error(
                        u'The ugroup_id parameter is not a valid value: %s.', ugroup)
                    raise InvalidValueError(None, 'ugroup_id', ugroup)

                if not is_valid_int_greater_zero_param(egroup, False):
                    self.log.error(
                        u'The egroup_id parameter is not a valid value: %s.', egroup)
                    raise InvalidValueError(None, 'egroup_id', egroup)

                if ugroup is not None:
                    UGrupo.get_by_pk(ugroup)

                if egroup is not None:
                    EGrupo.get_by_pk(egroup)

                rights = DireitosGrupoEquipamento.search(ugroup, None, egroup)
                for right in rights:
                    map_list.append(self.__get_direito_map(right))

            return self.response(dumps_networkapi({'direito_grupo_equipamento': map_list}))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except DireitosGrupoEquipamento.DoesNotExist:
            return self.response_error(258, right_id)
        except EGrupoNotFoundError:
            return self.response_error(102)
        except UGrupoNotFoundError:
            return self.response_error(180, ugroup)
        except (GrupoError):
            return self.response_error(1)

    def __valida_id_ugrupo(self, id_grupo):
        if id_grupo is None:
            return self.response_error(235)
        try:
            id_grupo = int(id_grupo)
        except (TypeError, ValueError):
            self.log.error(
                u'Valor do id_grupo_usuario inválido: %s.', id_grupo)
            return self.response_error(180, id_grupo)

        return None

    def __valida_id_egrupo(self, id_grupo):
        if id_grupo is None:
            return self.response_error(106)
        try:
            id_grupo = int(id_grupo)
        except (TypeError, ValueError):
            self.log.error(
                u'Valor do id_grupo_equipamento inválido: %s.', id_grupo)
            return self.response_error(102)

        return None

    def __valida_request(self, direito_map, handle_post=True):

        if handle_post:
            id_ugrupo = direito_map.get('id_grupo_usuario')
            response = self.__valida_id_ugrupo(id_ugrupo)
            if response is not None:
                return response

            id_egrupo = direito_map.get('id_grupo_equipamento')
            response = self.__valida_id_egrupo(id_egrupo)
            if response is not None:
                return response

        read = direito_map.get('leitura')
        if read is None:
            raise InvalidValueError(None, 'leitura', read)
        elif (read == '0'):
            direito_map['leitura'] = False
        elif (read == '1'):
            direito_map['leitura'] = True
        else:
            raise InvalidValueError(None, 'leitura', read)

        write = direito_map.get('escrita')
        if write is None:
            raise InvalidValueError(None, 'escrita', write)
        elif (write == '0'):
            direito_map['escrita'] = False
        elif (write == '1'):
            direito_map['escrita'] = True
        else:
            raise InvalidValueError(None, 'escrita', write)

        update_config = direito_map.get('alterar_config')
        if update_config is None:
            raise InvalidValueError(None, 'alterar_config', update_config)
        elif (update_config == '0'):
            direito_map['alterar_config'] = False
        elif (update_config == '1'):
            direito_map['alterar_config'] = True
        else:
            raise InvalidValueError(None, 'alterar_config', update_config)

        delete = direito_map.get('exclusao')
        if delete is None:
            raise InvalidValueError(None, 'exclusao', delete)
        elif (delete == '0'):
            direito_map['exclusao'] = False
        elif (delete == '1'):
            direito_map['exclusao'] = True
        else:
            raise InvalidValueError(None, 'exclusao', delete)

        return None

    def handle_post(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para inserir direitos de um grupo de usuário em um grupo de equipamento.

        URL: direitosgrupoequipamento/
        """
        try:
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            try:
                xml_map, attrs_map = loads(request.raw_post_data)
                self.log.debug('XML_MAP: %s', xml_map)
            except XMLError, x:
                self.log.error(u'Erro ao ler o XML da requisicao.')
                return self.response_error(3, x)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            direito_map = networkapi_map.get('direito_grupo_equipamento')
            if direito_map is None:
                return self.response_error(3, u'Não existe valor para a tag direito_grupo_equipamento do XML de requisição.')

            response = self.__valida_request(direito_map)
            if response is not None:
                return response

            direito = DireitosGrupoEquipamento()
            direito.egrupo = EGrupo(id=direito_map.get('id_grupo_equipamento'))
            direito.ugrupo = UGrupo(id=direito_map.get('id_grupo_usuario'))
            direito.leitura = direito_map.get('leitura')
            direito.escrita = direito_map.get('escrita')
            direito.alterar_config = direito_map.get('alterar_config')
            direito.exclusao = direito_map.get('exclusao')

            direito.create(user)

            return self.response(dumps_networkapi({'direito_grupo_equipamento': {'id': direito.id}}))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except UGrupo.DoesNotExist:
            return self.response_error(180, direito_map.get('id_grupo_usuario'))
        except EGrupoNotFoundError:
            return self.response_error(102)
        except DireitoGrupoEquipamentoDuplicatedError:
            return self.response_error(267, direito_map.get('id_grupo_usuario'), direito_map.get('id_grupo_equipamento'))
        except (GrupoError):
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Trata as requisições de PUT para alterar direitos de um grupo de usuário em um grupo de equipamento.

        URL: direitosgrupoequipamento/<id_direito>/
        """
        try:
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            right_id = kwargs.get('id_direito')
            if not is_valid_int_greater_zero_param(right_id):
                self.log.error(
                    u'The right_id parameter is not a valid value: %s.', right_id)
                raise InvalidValueError(None, 'right_id', right_id)

            try:
                xml_map, attrs_map = loads(request.raw_post_data)
                self.log.debug('XML_MAP: %s', xml_map)
            except XMLError, x:
                self.log.error(u'Erro ao ler o XML da requisicao.')
                return self.response_error(3, x)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            direito_map = networkapi_map.get('direito_grupo_equipamento')
            if direito_map is None:
                return self.response_error(3, u'Não existe valor para a tag direito_grupo_equipamento do XML de requisição.')

            response = self.__valida_request(direito_map, False)
            if response is not None:
                return response

            with distributedlock(LOCK_GROUP_RIGHTS % right_id):

                DireitosGrupoEquipamento.update(user,
                                                right_id,
                                                leitura=direito_map.get(
                                                    'leitura'),
                                                escrita=direito_map.get(
                                                    'escrita'),
                                                alterar_config=direito_map.get(
                                                    'alterar_config'),
                                                exclusao=direito_map.get('exclusao'))

                return self.response(dumps_networkapi({}))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except DireitosGrupoEquipamento.DoesNotExist:
            return self.response_error(258, right_id)
        except (GrupoError):
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Trata as requisições de DELETE para remover direitos de um grupo de usuário em um grupo de equipamento.

        URL: direitosgrupoequipamento/<id_direito>/
        """
        try:
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            right_id = kwargs.get('id_direito')
            if not is_valid_int_greater_zero_param(right_id, False):
                self.log.error(
                    u'The right_id parameter is not a valid value: %s.', right_id)
                raise InvalidValueError(None, 'right_id', right_id)

            DireitosGrupoEquipamento.get_by_pk(right_id)

            with distributedlock(LOCK_GROUP_RIGHTS % right_id):

                DireitosGrupoEquipamento.remove(user, right_id)

                return self.response(dumps_networkapi({}))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except DireitosGrupoEquipamento.DoesNotExist:
            return self.response_error(258, right_id)
        except (GrupoError):
            return self.response_error(1)
