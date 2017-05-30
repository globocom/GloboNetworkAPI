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
"""
"""
import logging

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource


def get_envs(self, user, no_blocks=False):
    try:

        # Commons Validations

        # User permission
        if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
            return self.not_authorized()

        # Business Rules

        # Get all environments in DB
        environments = Ambiente.objects.all().order_by('divisao_dc__nome', 'ambiente_logico__nome',
                                                       'grupo_l3__nome').select_related('grupo_l3', 'ambiente_logico', 'divisao_dc', 'filter')

        lists = []

        if not no_blocks:
            use_env = 1
        else:
            use_env = 0

        for env in environments:
            if no_blocks:
                if env.blockrules_set.count() != 0:
                    use_env = 0
            if use_env:
                env_map = model_to_dict(env)
                env_map['grupo_l3_name'] = env.grupo_l3.nome
                env_map['ambiente_logico_name'] = env.ambiente_logico.nome
                env_map['divisao_dc_name'] = env.divisao_dc.nome
                if not env.min_num_vlan_1 is None and not env.max_num_vlan_2 is None:
                    env_map['range'] = str(
                        env.min_num_vlan_1) + ' - ' + str(env.max_num_vlan_2)
                else:
                    env_map['range'] = 'Nao definido'
                if env.filter is not None:
                    env_map['filter_name'] = env.filter.name
                lists.append(env_map)
                if not env.min_num_vlan_1 is None and not env.max_num_vlan_2 is None:
                    env_map['range'] = str(
                        env.min_num_vlan_1) + ' - ' + str(env.max_num_vlan_2)
                else:
                    env_map['range'] = 'Nao definido'

        # Return XML
        environment_list = dict()
        environment_list['ambiente'] = lists
        return self.response(dumps_networkapi(environment_list))

    except GrupoError:
        return self.response_error(1)


class EnvironmentListResource(RestResource):

    log = logging.getLogger('EnvironmentListResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests POST to list all Environments.

        URL: /ambiente/list/
        """

        return get_envs(self, user)

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to list all Environments without blocks.

        URL: /ambiente/list_no_blocks/
        """

        return get_envs(self, user, True)
