# -*- coding:utf-8 -*-

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

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.ambiente.models import Ambiente
from django.forms.models import model_to_dict


def get_environment_related_with_environment_vip(self, user, no_blocks=False):

    try:

        # Commons Validations
        # User permission
        if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
            return self.not_authorized()

        environment_list = []

        env_list_net_v4_related = Ambiente.objects.filter(vlan__networkipv4__ambient_vip__id__isnull=False)\
            .order_by('divisao_dc__nome', 'ambiente_logico__nome', 'grupo_l3__nome')\
            .select_related('grupo_l3', 'ambiente_logico', 'divisao_dc', 'filter')\
            .distinct()

        env_list_net_v6_related = Ambiente.objects.filter(vlan__networkipv6__ambient_vip__id__isnull=False)\
            .order_by('divisao_dc__nome', 'ambiente_logico__nome', 'grupo_l3__nome')\
            .select_related('grupo_l3', 'ambiente_logico', 'divisao_dc', 'filter')\
            .distinct()

        environment_list.extend(env_list_net_v4_related)
        environment_list.extend(env_list_net_v6_related)

        environment_list_dict = []

        for environment in environment_list:
            if environment.blockrules_set.count() == 0 or not no_blocks:
                env_map = model_to_dict(environment)
                env_map["grupo_l3_name"] = environment.grupo_l3.nome
                env_map["ambiente_logico_name"] = environment.ambiente_logico.nome
                env_map["divisao_dc_name"] = environment.divisao_dc.nome
                if environment.filter is not None:
                        env_map["filter_name"] = environment.filter.name

                environment_list_dict.append(env_map)

        response = {'ambiente': environment_list_dict}

        return self.response(dumps_networkapi(response))

    except Exception as error:
        return self.response_error(1)


class EnvironmentListResource(RestResource):

    log = Log('EnvironmentListResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests POST to list all Environments.

        URL: /ambiente/list/
        """

        return get_environment_related_with_environment_vip(self, user)

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to list all Environments without blocks.

        URL: /ambiente/list_no_blocks/
        """

        return get_environment_related_with_environment_vip(self, user, True)
