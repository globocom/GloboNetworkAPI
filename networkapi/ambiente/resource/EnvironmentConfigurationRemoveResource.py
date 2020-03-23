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
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.ambiente.models import IPConfig
from networkapi.ambiente.models import IPConfigError
from networkapi.ambiente.models import IPConfigNotFoundError
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import PermissionError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class EnvironmentConfigurationRemoveResource(RestResource):

    log = logging.getLogger('EnvironmentConfigurationRemoveResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests GET to Remove Prefix Configuration.

        URL: /environment/configuration/remove/environment_id/configuration_id/
        """
        try:

            configuration_id = kwargs.get('configuration_id')

            environment_id = kwargs.get('environment_id')

            self._validate_permission(user)

            self._validate_configuration_id(configuration_id)

            self._validate_environment_id(environment_id)

            ip_config = IPConfig.remove(
                self, user, environment_id, configuration_id)

            # remove from cidr table
            logging.debug("Remove config from cidr table.")
            Ambiente().delete_cidr([configuration_id])

            return self.response(dumps_networkapi({'ip_config': ip_config}))

        except PermissionError:
            return self.not_authorized()

        except IPConfigNotFoundError, e:
            self.log.error(u'IpCofig not registred')
            return self.response_error(301)

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)

        except AmbienteNotFoundError, e:
            self.log.error(u'Environment not registred')
            return self.response_error(112)

        except IPConfigError:
            return self.response_error(1)

    """Validations"""

    def _validate_permission(self, user):

        if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.ENVIRONMENT_MANAGEMENT):
            self.log.error(
                u'User does not have permission to perform the operation.')
            raise PermissionError(None, None)

    def _validate_configuration_id(self, id_configuration):

        if not is_valid_int_greater_zero_param(id_configuration):
            self.log.error(
                u'The id_configuration parameter is invalid value: %s.', id_configuration)
            raise InvalidValueError(None, 'id_configuration', id_configuration)

        """ Check if exists"""
        IPConfig().get_by_pk(id_configuration)

    def _validate_environment_id(self, id_environment):

        if not is_valid_int_greater_zero_param(id_environment):
            self.log.error(
                u'The id_environment parameter is invalid value: %s.', id_environment)
            raise InvalidValueError(None, 'id_environment', id_environment)

        """ Check if exists"""
        Ambiente().get_by_pk(id_environment)
