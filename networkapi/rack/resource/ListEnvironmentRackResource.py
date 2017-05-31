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
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rack.models import EnvironmentRack
from networkapi.rack.models import Rack
from networkapi.rest import RestResource


def get_prod_envs(ambientes):

    lista = []
    for item in ambientes:
        if item['ambiente_logico_name'] == 'PRODUCAO':
            lista.append(item)

    return lista


def get_envs(ambientes, no_blocks=False):

    lists = []

    for env in ambientes:
        if env.blockrules_set.count() == 0 or not no_blocks:
            env_map = model_to_dict(env)
            env_map['grupo_l3_name'] = env.grupo_l3.nome
            env_map['ambiente_logico_name'] = env.ambiente_logico.nome
            env_map['divisao_dc_name'] = env.divisao_dc.nome
            if env.filter is not None:
                env_map['filter_name'] = env.filter.name
            lists.append(env_map)

    return lists


class ListEnvironmentRackResource(RestResource):

    log = logging.getLogger('ListEnvironmentRackResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests POST to list all Environments.
        URL: rack/list-rack-environment/<nome_rack>/
        """

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()

            id_rack = kwargs.get('nome_rack')
            lista_ambiente = []

            ambientes = EnvironmentRack.get_by_rack(id_rack)

            for amb in ambientes:
                lista_ambiente.append(amb.ambiente)

            lists = get_envs(lista_ambiente)
            lists = get_prod_envs(lists)

            # Return XML
            environment_list = dict()
            environment_list['ambiente'] = lists
            return self.response(dumps_networkapi(environment_list))

        except GrupoError:
            return self.response_error(1)
