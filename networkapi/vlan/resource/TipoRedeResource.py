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

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.vlan.models import TipoRede
from networkapi.vlan.models import TipoRedeNameDuplicatedError
from networkapi.vlan.models import TipoRedeNotFoundError
from networkapi.vlan.models import TipoRedeUsedByVlanError
from networkapi.vlan.models import VlanError


class TipoRedeResource(RestResource):

    """Classe que trata as requisições de PUT,POST,GET e DELETE para a tabela tipo_rede."""

    log = logging.getLogger('TipoRedeResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições GET para consulta de tipos de rede.

        Permite a consulta de tipos de rede existentes.

        URL: /tiporede/
        """

        try:
            if not has_perm(user, AdminPermission.NETWORK_TYPE_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()

            # Efetua a consulta de todos os tipos de rede
            results = TipoRede.search()

            if results.count() > 0:
                # Monta lista com dados retornados
                map_list = []
                for item in results:
                    item_map = self.get_tipo_rede_map(item)
                    map_list.append(item_map)

                # Gera response (XML) com resultados
                return self.response(dumps_networkapi({'tipo_rede': map_list}))
            else:
                # Gera response (XML) para resultado vazio
                return self.response(dumps_networkapi({}))

        except (VlanError, GrupoError):
            return self.response_error(1)

    def handle_post(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para criar tipos de rede.

        URL: /tiporede/

        """

        # Obtém dados do request e verifica acesso
        try:
            # Verificar a permissão
            if not has_perm(user, AdminPermission.NETWORK_TYPE_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            # Obtém os dados do xml do request
            xml_map, attrs_map = loads(request.raw_post_data)

            # Obtém o mapa correspondente ao root node do mapa do XML
            # (networkapi)
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            # Verifica a existência do node "tipo_rede"
            tipo_rede_map = networkapi_map.get('tipo_rede')
            if tipo_rede_map is None:
                return self.response_error(3, u'Não existe valor para a tag tipo_rede do XML de requisição.')

            # Verifica a existência do valor "fqdn"
            nome = tipo_rede_map.get('nome')
            if nome is None:
                return self.response_error(176)

            # Cria acesso ao equipamento conforme dados recebidos no XML
            tipo_rede = TipoRede(tipo_rede=nome)
            tipo_rede.create(user)

            # Monta dict para response
            networkapi_map = dict()
            tipo_rede_map = dict()

            tipo_rede_map['id'] = tipo_rede.id
            networkapi_map['tipo_rede'] = tipo_rede_map

            return self.response(dumps_networkapi(networkapi_map))
        except TipoRedeNameDuplicatedError:
            return self.response_error(253, nome)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except (GrupoError, VlanError):
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Trata uma requisição PUT para alterar tipos de rede.

        URL: /tiporede/<id_tipo_rede>/

        """

        # Obtém dados do request e verifica acesso
        try:
            # Verificar a permissão
            if not has_perm(user, AdminPermission.NETWORK_TYPE_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            # Obtém argumentos passados na URL
            id_tipo_rede = kwargs.get('id_tipo_rede')
            if id_tipo_rede is None:
                return self.response_error(256)

            # Obtém dados do XML
            xml_map, attrs_map = loads(request.raw_post_data)

            # Obtém o mapa correspondente ao root node do mapa do XML
            # (networkapi)
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            # Verifica a existência do node "tipo_rede"
            tipo_rede_map = networkapi_map.get('tipo_rede')
            if tipo_rede_map is None:
                return self.response_error(3, u'Não existe valor para a tag tipo_rede do XML de requisição.')

            # Verifica a existência do valor "fqdn"
            nome = tipo_rede_map.get('nome')
            if nome is None:
                return self.response_error(176)

            # Altera o tipo de redeconforme dados recebidos no XML
            TipoRede.update(user,
                            id_tipo_rede,
                            tipo_rede=nome
                            )

            # Retorna response vazio em caso de sucesso
            return self.response(dumps_networkapi({}))
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except TipoRedeNotFoundError:
            return self.response_error(111)
        except TipoRedeNameDuplicatedError:
            return self.response_error(253, nome)
        except (GrupoError, VlanError):
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Trata uma requisição DELETE para excluir um tipo de rede

        URL: /tiporede/<id_tipo_rede>/

        """

        # Verifica acesso e obtém dados do request
        try:
            # Verificar a permissão
            if not has_perm(user, AdminPermission.NETWORK_TYPE_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            # Obtém argumentos passados na URL
            id_tipo_rede = kwargs.get('id_tipo_rede')
            if id_tipo_rede is None:
                return self.response_error(256)

            # Remove a informação de acesso a equipamento
            TipoRede.remove(user, id_tipo_rede)

            # Retorna response vazio em caso de sucesso
            return self.response(dumps_networkapi({}))
        except TipoRedeNotFoundError:
            return self.response_error(111)
        except TipoRedeUsedByVlanError:
            return self.response_error(215, id_tipo_rede)
        except (GrupoError, VlanError):
            return self.response_error(1)

    def get_tipo_rede_map(self, tipo_rede):
        map = dict()
        map['id'] = tipo_rede.id
        map['nome'] = tipo_rede.tipo_rede
        return map
