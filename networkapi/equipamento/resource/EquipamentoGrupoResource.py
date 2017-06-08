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
from networkapi.distributedlock import LOCK_EQUIPMENT_GROUP
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoGrupo
from networkapi.equipamento.models import EquipamentoGrupoDuplicatedError
from networkapi.equipamento.models import EquipamentoGrupoNotFoundError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.equipamento.models import EquipmentDontRemoveError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import EGrupo
from networkapi.grupo.models import EGrupoNotFoundError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class EquipamentoGrupoResource(RestResource):

    """Classe que trata as requisições de PUT,POST,GET e DELETE para a tabela equip_do_grupo."""

    log = logging.getLogger('EquipamentoGrupoResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para inserir um equipamento_grupo.

        URL: equipamentogrupo/
        """

        # verifica parametros
        try:
            xml_map, attrs_map = loads(request.raw_post_data)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)

        self.log.debug('XML_MAP: %s', xml_map)

        networkapi_map = xml_map.get('networkapi')
        if networkapi_map is None:
            return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

        equipment_group_map = networkapi_map.get('equipamento_grupo')
        if equipment_group_map is None:
            return self.response_error(3, u'Não existe valor para a tag equipamento_grupo do XML de requisição.')

        self.log.debug('EGROUP_MAP: %s', equipment_group_map)

        # equip_id = equipment_group_map.get('id_equipamento')
        # if not is_valid_int_greater_zero_param(equip_id):
        #    self.log.error(u'The equip_id parameter is not a valid value: %s.', equip_id)
        #    raise InvalidValueError(None, 'equip_id', equip_id)
        # try:
        #    equip_id = int(equip_id)
        # except (TypeError, ValueError):
        #    self.log.error(u'Valor do id_equipamento inválido: %s.', equip_id)
        #    return self.response_error(117, equip_id)
        #
        # group_id = equipment_group_map.get('id_grupo')
        # if not is_valid_int_greater_zero_param(group_id):
        #    self.log.error(u'The group_id parameter is not a valid value: %s.', group_id)
        #    raise InvalidValueError(None, 'group_id', group_id)
        # try:
        #    group_id = int(group_id)
        # except (TypeError, ValueError):
        #    self.log.error(u'Valor do id_grupo inválido: %s.', group_id)
        #    return self.response_error(102)

        # verifica permissao e se o equipamento está cadastrado
        try:

            equip_id = equipment_group_map.get('id_equipamento')
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'The equip_id parameter is not a valid value: %s.', equip_id)
                raise InvalidValueError(None, 'equip_id', equip_id)
            else:
                equip_id = int(equip_id)

            group_id = equipment_group_map.get('id_grupo')
            if not is_valid_int_greater_zero_param(group_id):
                self.log.error(
                    u'The group_id parameter is not a valid value: %s.', group_id)
                raise InvalidValueError(None, 'group_id', group_id)
            else:
                equip_id = int(equip_id)

            if not has_perm(user,
                            AdminPermission.EQUIPMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION,
                            None,
                            equip_id,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                return self.not_authorized()
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)
        except (EquipamentoError, GrupoError):
            return self.response_error(1)

        return self.insert_equipment_group(equip_id, group_id, user)

    def insert_equipment_group(self, equip_id, group_id, user):

        equipment_group = EquipamentoGrupo()
        equipment_group.egrupo = EGrupo()
        equipment_group.egrupo.id = group_id
        equipment_group.equipamento = Equipamento()
        equipment_group.equipamento.id = equip_id

        try:
            equipment_group.create(user)

            equipment_group_map = dict()
            equipment_group_map['id'] = equipment_group.id
            map = dict()
            map['equipamento_grupo'] = equipment_group_map

            return self.response(dumps_networkapi(map))

        except EGrupoNotFoundError:
            return self.response_error(102)
        except EquipamentoGrupoDuplicatedError:
            return self.response_error(146)
        except (EquipamentoError, GrupoError):
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Trata as requisições de DELETE para remover uma associação entre um Equipamento e um Grupo.

        URL:  /equipamentogrupo/equipamento/<id_equip>/egrupo/<id_egrupo>/
        """
        try:

            equip_id = kwargs.get('id_equip')
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'The equip_id parameter is not a valid value: %s.', equip_id)
                raise InvalidValueError(None, 'equip_id', equip_id)

            egroup_id = kwargs.get('id_egrupo')
            if not is_valid_int_greater_zero_param(egroup_id):
                self.log.error(
                    u'The egroup_id parameter is not a valid value: %s.', egroup_id)
                raise InvalidValueError(None, 'egroup_id', egroup_id)

            Equipamento.get_by_pk(equip_id)
            EGrupo.get_by_pk(egroup_id)

            if not has_perm(user,
                            AdminPermission.EQUIPMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION,
                            None,
                            equip_id,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                return self.not_authorized()

            with distributedlock(LOCK_EQUIPMENT_GROUP % egroup_id):

                EquipamentoGrupo.remove(user, equip_id, egroup_id)
                return self.response(dumps_networkapi({}))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EGrupoNotFoundError:
            return self.response_error(102)
        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)
        except EquipmentDontRemoveError:
            return self.response_error(309)
        except (EquipamentoError, GrupoError):
            return self.response_error(1)
