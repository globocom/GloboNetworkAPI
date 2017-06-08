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
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteLogico
from networkapi.ambiente.models import AmbienteLogicoNameDuplicatedError
from networkapi.ambiente.models import AmbienteLogicoNotFoundError
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_regex
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class LogicalEnvironmentAddResource(RestResource):

    log = logging.getLogger('LogicalEnvironmentAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Logical Environment.

        URL: logicalenvironment/
        """

        try:

            self.log.info('Add Logical Environment')

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            logical_environment_map = networkapi_map.get('logical_environment')
            if logical_environment_map is None:
                return self.response_error(3, u'There is no value to the logical_environment tag  of XML request.')

            # Get XML data
            name = logical_environment_map.get('name')

            try:
                AmbienteLogico.get_by_name(name)
                raise AmbienteLogicoNameDuplicatedError(
                    None, u'Já existe um Ambiente Lógico com o valor name %s.' % name)
            except AmbienteLogicoNotFoundError:
                pass

            log_env = AmbienteLogico()

            # set variables
            log_env.nome = name

            try:
                # save Logical Environment
                log_env.save()
            except Exception, e:
                self.log.error(u'Failed to save the Logical Environment.')
                raise AmbienteError(
                    e, u'Failed to save the Logical Environment.')

            log_env_map = dict()
            log_env_map['logical_environment'] = model_to_dict(
                log_env, exclude=['nome'])

            return self.response(dumps_networkapi(log_env_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except AmbienteLogicoNameDuplicatedError:
            return self.response_error(173, name)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except (AmbienteError):
            return self.response_error(1)
