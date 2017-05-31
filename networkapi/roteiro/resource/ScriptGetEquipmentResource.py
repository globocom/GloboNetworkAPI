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
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class ScriptGetEquipmentResource(RestResource):

    log = logging.getLogger('ScriptGetEquipmentResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Script by Equipment.

        URL: script/equipment/<id_equipment>
        """
        try:

            self.log.info('GET to list all the Script by Equipment')

            id_equipment = kwargs.get('id_equipment')

            # Valid ID Equipment
            if not is_valid_int_greater_zero_param(id_equipment):
                self.log.error(
                    u'The id_equipment parameter is not a valid value: %s.', id_equipment)
                raise InvalidValueError(None, 'id_equipment', id_equipment)

            # Find Equipment by ID to check if it exist
            Equipamento.get_by_pk(id_equipment)

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION, None, id_equipment, AdminPermission.EQUIP_READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            script_list = []
            equipment_scripts = EquipamentoRoteiro.search(None, id_equipment)
            for equipment_script in equipment_scripts:
                script_map = dict()
                script_map['id'] = equipment_script.roteiro.id
                script_map['nome'] = equipment_script.roteiro.roteiro
                script_map['descricao'] = equipment_script.roteiro.descricao
                script_map[
                    'id_tipo_roteiro'] = equipment_script.roteiro.tipo_roteiro.id
                script_map[
                    'nome_tipo_roteiro'] = equipment_script.roteiro.tipo_roteiro.tipo
                script_map[
                    'descricao_tipo_roteiro'] = equipment_script.roteiro.tipo_roteiro.descricao

                script_list.append(script_map)

            return self.response(dumps_networkapi({'script': script_list}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except EquipamentoNotFoundError, e:
            return self.response_error(117, id_equipment)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except EquipamentoError:
            return self.response_error(1)
