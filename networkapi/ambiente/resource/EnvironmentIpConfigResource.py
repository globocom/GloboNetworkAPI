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
from networkapi.ambiente.models import ConfigEnvironment
from networkapi.ambiente.models import ConfigEnvironmentDuplicateError
from networkapi.ambiente.models import IPConfig
from networkapi.ambiente.models import IPConfigNotFoundError
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class EnvironmentIpConfigResource(RestResource):

    log = logging.getLogger('EnvironmentIpConfigResource')

    CODE_MESSAGE_CONFIG_ENVIRONMENT_ALREADY_EXISTS = 302

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests associate environment to ip config

        URL: ipconfig/
        """

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')
            environment_map = networkapi_map.get('ambiente')
            if environment_map is None:
                return self.response_error(3, u'Não existe valor para a tag ambiente do XML de requisição.')

            # Get XML data
            id_environment = environment_map.get('id_environment')
            id_ip_config = environment_map.get('id_ip_config')

            # Valid environment
            if not is_valid_int_greater_zero_param(id_environment):
                raise InvalidValueError(None, 'id_environment', id_environment)

            # Valid ip config
            if not is_valid_int_greater_zero_param(id_ip_config):
                raise InvalidValueError(None, 'id_ip_config', id_ip_config)

            # Environment must exists
            environment = Ambiente().get_by_pk(id_environment)

            # Ip config must exists
            ip_conf = IPConfig().get_by_pk(id_ip_config)

            # Makes the relationship
            config = ConfigEnvironment()
            config.ip_config = ip_conf
            config.environment = environment

            config.save()

            # Make return xml
            conf_env_map = dict()
            conf_env_map['id_config_do_ambiente'] = config.id

            return self.response(dumps_networkapi({'config_do_ambiente': conf_env_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except ConfigEnvironmentDuplicateError, e:
            return self.response_error(self.CODE_MESSAGE_CONFIG_ENVIRONMENT_ALREADY_EXISTS)

        except IPConfigNotFoundError, e:
            return self.response_error(301)

        except AmbienteNotFoundError, e:
            return self.response_error(112)

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)

        except (AmbienteError, GrupoError, Exception), e:
            return self.response_error(1)
