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
from networkapi.distributedlock import LOCK_EQUIPMENT_ACCESS
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAccessDuplicatedError
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.tipoacesso.models import AccessTypeNotFoundError
from networkapi.tipoacesso.models import TipoAcesso
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class EquipamentoAcessoResource(RestResource):

    """Classe que trata as requisições de PUT,POST,GET e DELETE para a tabela equiptos_acesso."""

    log = logging.getLogger('EquipamentoAcessoResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições GET para consulta de Informações de Acesso a Equipamentos.

        Permite a consulta de Informações de Acesso a Equipamentos existentes.

        URL: /equipamentoacesso/
        """

        try:
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()

            # Efetua a consulta de todos os tipos de acesso
            results = EquipamentoAcesso.search(user.grupos.all())

            if results.count() > 0:
                # Monta lista com dados retornados
                map_list = []
                for item in results:
                    item_map = self.get_equipamento_acesso_map(item)
                    if item_map not in map_list:
                        map_list.append(item_map)

                # Gera response (XML) com resultados
                return self.response(dumps_networkapi({'equipamento_acesso': map_list}))
            else:
                # Gera response (XML) para resultado vazio
                return self.response(dumps_networkapi({}))

        except (EquipamentoError, GrupoError):
            return self.response_error(1)

    def handle_post(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para criar Informações de Acesso a Equipamentos.

        URL: /equipamentoacesso

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

            # Verifica a existência do node "equipamento_acesso"
            equipamento_acesso_map = networkapi_map.get('equipamento_acesso')
            if equipamento_acesso_map is None:
                return self.response_error(3, u'Não existe valor para a tag equipamento_acesso do XML de requisição.')

            # Verifica a existência do valor "id_equipamento"
            id_equipamento = equipamento_acesso_map.get('id_equipamento')

            # Valid ID Equipment
            if not is_valid_int_greater_zero_param(id_equipamento):
                self.log.error(
                    u'The id_equipamento parameter is not a valid value: %s.', id_equipamento)
                raise InvalidValueError(None, 'id_equipamento', id_equipamento)

            try:
                id_equipamento = int(id_equipamento)
            except (TypeError, ValueError):
                self.log.error(
                    u'Valor do id_equipamento inválido: %s.', id_equipamento)
                return self.response_error(117, id_equipamento)

            # Após obtenção do id_equipamento podemos verificar a permissão
            if not has_perm(user,
                            AdminPermission.EQUIPMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION,
                            None,
                            id_equipamento,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                return self.not_authorized()

            # Verifica a existência do valor "fqdn"
            fqdn = equipamento_acesso_map.get('fqdn')

            # Valid fqdn
            if not is_valid_string_maxsize(fqdn, 100) or not is_valid_string_minsize(fqdn, 4):
                self.log.error(u'Parameter fqdn is invalid. Value: %s', fqdn)
                raise InvalidValueError(None, 'fqdn', fqdn)

            # Verifica a existência do valor "user"
            username = equipamento_acesso_map.get('user')

            # Valid username
            if not is_valid_string_maxsize(username, 20) or not is_valid_string_minsize(username, 3):
                self.log.error(
                    u'Parameter username is invalid. Value: %s', username)
                raise InvalidValueError(None, 'username', username)

            # Verifica a existência do valor "pass"
            password = equipamento_acesso_map.get('pass')

            # Valid password
            if not is_valid_string_maxsize(password, 150) or not is_valid_string_minsize(password, 3):
                self.log.error(u'Parameter password is invalid.')
                raise InvalidValueError(None, 'password', '****')

            # Verifica a existência do valor "id_tipo_acesso"
            id_tipo_acesso = equipamento_acesso_map.get('id_tipo_acesso')

            # Valid ID Equipment
            if not is_valid_int_greater_zero_param(id_tipo_acesso):
                self.log.error(
                    u'The id_tipo_acesso parameter is not a valid value: %s.', id_tipo_acesso)
                raise InvalidValueError(None, 'id_tipo_acesso', id_tipo_acesso)

            try:
                id_tipo_acesso = int(id_tipo_acesso)
            except (TypeError, ValueError):
                self.log.error(
                    u'Valor do id_tipo_acesso inválido: %s.', id_tipo_acesso)
                return self.response_error(171, id_tipo_acesso)

            # Obtém o valor de "enable_pass"
            enable_pass = equipamento_acesso_map.get('enable_pass')

            # Valid enable_pass
            if not is_valid_string_maxsize(enable_pass, 150) or not is_valid_string_minsize(enable_pass, 3):
                self.log.error(u'Parameter enable_pass is invalid.')
                raise InvalidValueError(None, 'enable_pass', '****')

            # Cria acesso ao equipamento conforme dados recebidos no XML
            equipamento_acesso = EquipamentoAcesso(
                equipamento=Equipamento(id=id_equipamento),
                fqdn=fqdn,
                user=username,
                password=password,
                tipo_acesso=TipoAcesso(id=id_tipo_acesso),
                enable_pass=enable_pass
            )
            equipamento_acesso.create(user)

            # Monta dict para response
            networkapi_map = dict()
            equipamento_acesso_map = dict()

            equipamento_acesso_map['id'] = equipamento_acesso.id
            networkapi_map['equipamento_acesso'] = equipamento_acesso_map

            return self.response(dumps_networkapi(networkapi_map))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except EquipamentoNotFoundError:
            return self.response_error(117, id_equipamento)
        except TipoAcesso.DoesNotExist:
            return self.response_error(171, id_tipo_acesso)
        except EquipamentoAccessDuplicatedError:
            return self.response_error(242, id_equipamento, id_tipo_acesso)
        except (EquipamentoError, GrupoError):
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Trata uma requisição PUT para alterar informações de acesso a equipamentos.

        URL: /equipamentoacesso/id_equipamento/id_tipo_acesso/

        """

        # Obtém dados do request e verifica acesso
        try:
            # Obtém argumentos passados na URL
            id_equipamento = kwargs.get('id_equipamento')
            if id_equipamento is None:
                return self.response_error(147)

            id_tipo_acesso = kwargs.get('id_tipo_acesso')
            if id_tipo_acesso is None:
                return self.response_error(208)

            # Após obtenção do id_equipamento podemos verificar a permissão
            if not has_perm(user,
                            AdminPermission.EQUIPMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION,
                            None,
                            id_equipamento,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                return self.not_authorized()

            # Obtém dados do XML
            xml_map, attrs_map = loads(request.raw_post_data)

            # Obtém o mapa correspondente ao root node do mapa do XML
            # (networkapi)
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            # Verifica a existência do node "equipamento_acesso"
            equipamento_acesso_map = networkapi_map.get('equipamento_acesso')
            if equipamento_acesso_map is None:
                return self.response_error(3, u'Não existe valor para a tag equipamento_acesso do XML de requisição.')

            # Verifica a existência do valor "fqdn"
            fqdn = equipamento_acesso_map.get('fqdn')
            if fqdn is None:
                return self.response_error(205)

            # Verifica a existência do valor "user"
            username = equipamento_acesso_map.get('user')
            if username is None:
                return self.response_error(206)

            # Verifica a existência do valor "pass"
            password = equipamento_acesso_map.get('pass')
            if password is None:
                return self.response_error(207)

            # Obtém o valor de "enable_pass"
            enable_pass = equipamento_acesso_map.get('enable_pass')

            with distributedlock(LOCK_EQUIPMENT_ACCESS % id_tipo_acesso):

                # Altera a informação de acesso ao equipamentoconforme dados
                # recebidos no XML
                EquipamentoAcesso.update(user,
                                         id_equipamento,
                                         id_tipo_acesso,
                                         fqdn=fqdn,
                                         user=username,
                                         password=password,
                                         enable_pass=enable_pass
                                         )

                # Retorna response vazio em caso de sucesso
                return self.response(dumps_networkapi({}))

        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except EquipamentoNotFoundError:
            return self.response_error(117, id_equipamento)
        except EquipamentoAcesso.DoesNotExist:
            return self.response_error(209, id_equipamento, id_tipo_acesso)
        except (EquipamentoError, GrupoError):
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Trata uma requisição DELETE para excluir uma informação de acesso a equipamento

        URL: /equipamentoacesso/id_equipamento/id_tipo_acesso/

        """

        # Verifica acesso e obtém dados do request
        try:
            # Obtém argumentos passados na URL
            id_equipamento = kwargs.get('id_equipamento')

            # Valid ID Equipment
            if not is_valid_int_greater_zero_param(id_equipamento):
                self.log.error(
                    u'The id_equipamento parameter is not a valid value: %s.', id_equipamento)
                raise InvalidValueError(None, 'id_equipamento', id_equipamento)

            id_tipo_acesso = kwargs.get('id_tipo_acesso')

            # Valid ID Equipment
            if not is_valid_int_greater_zero_param(id_tipo_acesso):
                self.log.error(
                    u'The id_tipo_acesso parameter is not a valid value: %s.', id_tipo_acesso)
                raise InvalidValueError(None, 'id_tipo_acesso', id_tipo_acesso)

            Equipamento.get_by_pk(id_equipamento)

            TipoAcesso.get_by_pk(id_tipo_acesso)

            # Após obtenção do id_equipamento podemos verificar a permissão
            if not has_perm(user,
                            AdminPermission.EQUIPMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION,
                            None,
                            id_equipamento,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                return self.not_authorized()

            with distributedlock(LOCK_EQUIPMENT_ACCESS % id_tipo_acesso):

                # Remove a informação de acesso a equipamento
                EquipamentoAcesso.remove(user, id_equipamento, id_tipo_acesso)

                # Retorna response vazio em caso de sucesso
                return self.response(dumps_networkapi({}))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EquipamentoNotFoundError:
            return self.response_error(117, id_equipamento)
        except AccessTypeNotFoundError:
            return self.response_error(171, id_tipo_acesso)
        except EquipamentoAcesso.DoesNotExist:
            return self.response_error(209, id_equipamento, id_tipo_acesso)
        except (EquipamentoError, GrupoError):
            return self.response_error(1)

    def get_equipamento_acesso_map(self, equipamento_acesso):
        map = dict()
        map['id_equipamento'] = equipamento_acesso.id
        map['fqdn'] = equipamento_acesso.fqdn
        map['user'] = equipamento_acesso.user
        map['pass'] = equipamento_acesso.password
        map['id_tipo_acesso'] = equipamento_acesso.tipo_acesso.id
        map['enable_pass'] = equipamento_acesso.enable_pass
        map['protocolo_tipo_acesso'] = equipamento_acesso.tipo_acesso.protocolo
        return map
