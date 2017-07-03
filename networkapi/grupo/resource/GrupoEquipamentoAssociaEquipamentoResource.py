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
import re

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import *
from networkapi.auth import has_perm
from networkapi.equipamento.models import *
from networkapi.grupo.models import EGrupoNotFoundError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.roteiro.models import *
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_minsize


class GrupoEquipamentoAssociaEquipamentoResource(RestResource):

    log = logging.getLogger('EquipamentoGrupoAssociaEquipamentoResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Trata uma requisicao POST para inserir um associao entre grupo de equipamento e equipamento.

        URL: equipmentogrupo/associa
        """

        try:
            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            equip_map = networkapi_map.get('equipamento_grupo')
            if equip_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            equip_id = equip_map.get('id_equipamento')
            id_grupo = equip_map.get('id_grupo')

            # Valid equip_id
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'Parameter equip_id is invalid. Value: %s.', equip_id)
                raise InvalidValueError(None, 'equip_id', equip_id)

            # Valid id_modelo
            if not is_valid_int_greater_zero_param(id_grupo):
                self.log.error(
                    u'Parameter id_grupo is invalid. Value: %s.', id_grupo)
                raise InvalidValueError(None, 'id_modelo', id_grupo)

            if not has_perm(user,
                            AdminPermission.EQUIPMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION,
                            id_grupo,
                            equip_id,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                raise UserNotAuthorizedError(
                    None, u'User does not have permission to perform the operation.')

            # Business Rules

            # New IP
            equip = Equipamento()
            equip = equip.get_by_pk(equip_id)
            egrupo = EGrupo.get_by_pk(id_grupo)
            tipo_equipamento = TipoEquipamento()

            try:
                if ((int(egrupo.GRUPO_EQUIPAMENTO_ORQUESTRACAO) == int(id_grupo)) and (int(equip.tipo_equipamento.id) != int(tipo_equipamento.TIPO_EQUIPAMENTO_SERVIDOR_VIRTUAL))):
                    raise EquipamentoError(
                        None, "Equipamentos que não sejam do tipo 'Servidor Virtual' não podem fazer parte do grupo 'Equipamentos Orquestração'.")
            except EquipamentoError, e:
                return self.response_error(150, e.message)

            equipamento_grupo = EquipamentoGrupo()
            equipamento_grupo.egrupo = egrupo
            equipamento_grupo.equipamento = equip
            equipamento_grupo.create(user)

            map = dict()
            map['id'] = equipamento_grupo.id
            map_return = dict()
            lista = []
            lista.append(map)
            map_return['grupo'] = lista

            return self.response(dumps_networkapi(map_return))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except TipoEquipamentoNotFoundError, e:
            return self.response_error(150, e.message)
        except ModeloNotFoundError, e:
            return self.response_error(150, e.message)
        except EquipamentoNotFoundError, e:
            return self.response_error(117, equip_id)
        except EquipamentoNameDuplicatedError, e:
            return self.response_error(e.message)
        except EquipamentoError, e:
            return self.response_error(150, e.message)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
