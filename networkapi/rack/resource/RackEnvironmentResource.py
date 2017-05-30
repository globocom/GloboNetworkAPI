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
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rack.models import EnvironmentRack
from networkapi.rack.models import Rack
from networkapi.rack.models import RackError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError


def get_environment_map(environment):
    environment_map = dict()
    environment_map['id'] = environment.id
    environment_map['divisao_dc_name'] = environment.divisao_dc.nome
    environment_map['ambiente_logico_name'] = environment.ambiente_logico.nome
    environment_map['grupo_l3_name'] = environment.grupo_l3.nome
    if not environment.min_num_vlan_1 is None and not environment.max_num_vlan_1 is None:
        environment_map['range'] = str(
            environment.min_num_vlan_1) + ' - ' + str(environment.max_num_vlan_1)
    else:
        environment_map['range'] = 'Nao definido'

    return environment_map


class RackEnvironmentResource(RestResource):

    log = logging.getLogger('RackEnvironmentResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to find all Racks

        URLs: /rack/list-rack-environment/<rack_id>/
        """

        self.log.info('Find all racks environment')

        try:

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            environment_list = []
            id = kwargs.get('rack_id')
            env = EnvironmentRack()
            environments = env.get_by_rack(id)
            for envs in environments:
                envs = model_to_dict(envs)
                amb = Ambiente()
                ambiente = amb.get_by_pk(envs['ambiente'])
                if 'PROD' in ambiente.ambiente_logico.nome:
                    environment_list.append(get_environment_map(ambiente))

            return self.response(dumps_networkapi({'ambiente': environment_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RackError:
            return self.response_error(397)
