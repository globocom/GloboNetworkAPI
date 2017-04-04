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
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.exception import EnvironmentVipError
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.exception import OptionVipError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class EnvironmentAllGetByEnvironmentVipResource(RestResource):

    log = logging.getLogger('EnvironmentAllGetByEnvironmentVipResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Environment by Environment Vip.

        URL: environment/environmentvip/<environment_vip_id>'
        """

        try:

            self.log.info(
                'GET to list all the Environment by Environment Vip.')

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            environment_vip_id = kwargs.get('environment_vip_id')

            # Valid Environment VIP ID
            if not is_valid_int_greater_zero_param(environment_vip_id):
                self.log.error(
                    u'The id_environment_vip parameter is not a valid value: %s.', environment_vip_id)
                raise InvalidValueError(
                    None, 'environment_vip_id', environment_vip_id)

            # Find Environment VIP by ID to check if it exist
            environment_vip = EnvironmentVip.get_by_pk(environment_vip_id)

            environment_related_list = []

            for env_env_vip in environment_vip.environmentenvironmentvip_set.all():
                environment_map = {}
                environment_map['environment_id'] = env_env_vip.environment.id
                environment_map[
                    'environment_vip_id'] = env_env_vip.environment_vip.id
                environment_map[
                    'environment'] = env_env_vip.environment.grupo_l3.nome
                environment_map[
                    'ambiente_logico_name'] = env_env_vip.environment.ambiente_logico.nome
                environment_map[
                    'divisao_dc_name'] = env_env_vip.environment.divisao_dc.nome

                environment_related_list.append(environment_map)

            return self.response(dumps_networkapi({'environment_related_list': environment_related_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except EnvironmentVipNotFoundError:
            return self.response_error(283)

        except Exception, error:
            return self.response_error(1)
