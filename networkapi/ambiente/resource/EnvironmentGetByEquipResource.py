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

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.auth import has_perm
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class EnvironmentGetByEquipResource(RestResource):

    log = logging.getLogger('EnvironmentGetByEquipResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all Environments.

        URL: /ambiente/equip/id_equip
        """

        try:
        
            # Commons Validations
        
            # User permission
        
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()
        
            id_equip = kwargs.get('id_equip')
        
            if not is_valid_int_greater_zero_param(id_equip):
                raise InvalidValueError(None, 'id_equip', id_equip)
        
            # Business Rules
            equip = Equipamento.get_by_pk(id_equip)
            environments_list = EquipamentoAmbiente.get_by_equipment(equip.id)
        
            # Get all environments in DB
            lists_aux = []
            for environment in environments_list:
                env = Ambiente.get_by_pk(environment.ambiente.id)
                env_map = model_to_dict(env)
                env_map['grupo_l3_name'] = env.grupo_l3.nome
                env_map['ambiente_logico_name'] = env.ambiente_logico.nome
                env_map['divisao_dc_name'] = env.divisao_dc.nome
                env_map['is_router'] = environment.is_router
        
                try:
                    env_map['range'] = str(
                        env.min_num_vlan_1) + ' - ' + str(env.max_num_vlan_1)
                    if env.min_num_vlan_1 != env.min_num_vlan_2:
                        env_map['range'] = env_map[
                            'range'] + '; ' + str(env.min_num_vlan_2) + ' - ' + str(env.max_num_vlan_2)
                except:
                    env_map['range'] = 'Nao definido'
        
                if env.filter is not None:
                    env_map['filter_name'] = env.filter.name
        
                lists_aux.append(env_map)
            # Return XML
            environment_list = dict()
            environment_list['ambiente'] = lists_aux
            return self.response(dumps_networkapi(environment_list))
        
        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except EquipamentoNotFoundError, e:
            return self.response_error(117, id_equip)
        except GrupoError:
            return self.response_error(1)
