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
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.util import get_environment_map
from networkapi.util import is_valid_int_greater_zero_param


class EnvironmentGetByIdResource(RestResource):

    log = logging.getLogger('EnvironmentGetByIdResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handle GET requests to get Environment by id.

            URLs: /environment/id/<environment_id>/,
        """
        try:
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()

            environment_list = []

            environment_id = kwargs.get('environment_id')

            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'Parameter environment_id is invalid. Value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            environment_list.append(
                get_environment_map(Ambiente().get_by_pk(environment_id)))

            return self.response(dumps_networkapi({'ambiente': environment_list}))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except (AmbienteError, GrupoError):
            return self.response_error(1)


if __name__ == '__main__':
    pass
