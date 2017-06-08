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
from networkapi.distributedlock import LOCK_SCRIPT
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.roteiro.models import *


class RoteiroResource(RestResource):
    log = logging.getLogger('RoteiroResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições de GET para listar Roteiros.

        URLs: roteiro/$
              roteiro/tiporoteiro/<id_tipo_roteiro>/
              roteiro/equipamento/<id_equip>/
        """

        try:
            map_list = []

            equipment_id = kwargs.get('id_equip')
            if equipment_id is None:
                if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.READ_OPERATION):
                    return self.not_authorized()

                scripts = Roteiro.search(kwargs.get('id_tipo_roteiro'))
                for script in scripts:
                    script_map = dict()
                    script_map['id'] = script.id
                    script_map['nome'] = script.roteiro
                    script_map['descricao'] = script.descricao
                    script_map['id_tipo_roteiro'] = script.tipo_roteiro_id

                    map_list.append(script_map)

            else:
                if not has_perm(user,
                                AdminPermission.EQUIPMENT_MANAGEMENT,
                                AdminPermission.READ_OPERATION,
                                None,
                                equipment_id,
                                AdminPermission.EQUIP_READ_OPERATION):
                    return self.not_authorized()

                equipment_scripts = EquipamentoRoteiro.search(
                    None, equipment_id)
                for equipment_script in equipment_scripts:
                    script_map = dict()
                    script_map['id'] = equipment_script.roteiro.id
                    script_map['nome'] = equipment_script.roteiro.roteiro
                    script_map[
                        'descricao'] = equipment_script.roteiro.descricao
                    script_map[
                        'id_tipo_roteiro'] = equipment_script.roteiro.tipo_roteiro.id
                    script_map[
                        'nome_tipo_roteiro'] = equipment_script.roteiro.tipo_roteiro.tipo
                    script_map[
                        'descricao_tipo_roteiro'] = equipment_script.roteiro.tipo_roteiro.descricao

                    map_list.append(script_map)

            return self.response(dumps_networkapi({'roteiro': map_list}))

        except EquipamentoNotFoundError:
            return self.response_error(117, equipment_id)
        except (RoteiroError, GrupoError, EquipamentoError):
            return self.response_error(1)

    def handle_post(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para inserir um Roteiro.

        URL: roteiro/
        """

        try:
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            xml_map, attrs_map = loads(request.raw_post_data)
            self.log.debug('XML_MAP: %s', xml_map)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            script_map = networkapi_map.get('roteiro')
            if script_map is None:
                return self.response_error(3, u'Não existe valor para a tag roteiro do XML de requisição.')

            script_type_id = script_map.get('id_tipo_roteiro')
            if script_type_id is None:
                return self.response_error(194)

            script_name = script_map.get('nome')
            if script_name is None:
                return self.response_error(195)

            script = Roteiro()

            script.tipo_roteiro = TipoRoteiro()
            try:
                script.tipo_roteiro.id = int(script_type_id)
            except (TypeError, ValueError):
                self.log.error(
                    u'Valor do id_tipo_roteiro inválido: %s.', script_type_id)
                return self.response_error(158, script_type_id)

            script.roteiro = script_name
            script.descricao = script_map.get('descricao')

            script.create(user)

            script_map = dict()
            script_map['id'] = script.id
            networkapi_map = dict()
            networkapi_map['roteiro'] = script_map

            return self.response(dumps_networkapi(networkapi_map))

        except TipoRoteiroNotFoundError:
            return self.response_error(158, script_type_id)
        except RoteiroNameDuplicatedError:
            return self.response_error(250, script_name)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)
        except (RoteiroError, GrupoError):
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Trata as requisições de PUT para alterar um Roteiro.

        URL: roteiro/<id_roteiro>/
        """

        try:
            script_id = kwargs.get('id_roteiro')
            if script_id is None:
                return self.response_error(233)

            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            xml_map, attrs_map = loads(request.raw_post_data)
            self.log.debug('XML_MAP: %s', xml_map)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            script_map = networkapi_map.get('roteiro')
            if script_map is None:
                return self.response_error(3, u'Não existe valor para a tag roteiro do XML de requisição.')

            script_type_id = script_map.get('id_tipo_roteiro')
            if script_type_id is None:
                return self.response_error(194)
            try:
                script_type_id = int(script_type_id)
            except (TypeError, ValueError):
                self.log.error(
                    u'Valor do id_tipo_roteiro inválido: %s.', script_type_id)
                return self.response_error(158, script_type_id)

            script_name = script_map.get('nome')
            if script_name is None:
                return self.response_error(195)

            Roteiro.update(user,
                           script_id,
                           tipo_roteiro_id=script_type_id,
                           roteiro=script_name,
                           descricao=script_map.get('descricao'))

            return self.response(dumps_networkapi({}))

        except RoteiroNotFoundError:
            return self.response_error(165, script_id)
        except TipoRoteiroNotFoundError:
            return self.response_error(158, script_type_id)
        except RoteiroNameDuplicatedError:
            return self.response_error(250, script_name)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)
        except (RoteiroError, GrupoError):
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Trata as requisições de DELETE para remover um Roteiro.

        URL: roteiro/<id_roteiro>/
        """

        try:
            script_id = kwargs.get('id_roteiro')
            if script_id is None:
                return self.response_error(233)

            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            Roteiro.remove(user, script_id)
            return self.response(dumps_networkapi({}))

        except RoteiroNotFoundError:
            return self.response_error(165, script_id)
        except RoteiroHasEquipamentoError:
            return self.response_error(197, script_id)
        except (RoteiroError, GrupoError):
            return self.response_error(1)
