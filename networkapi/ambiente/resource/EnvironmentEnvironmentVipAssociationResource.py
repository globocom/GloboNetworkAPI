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
from __future__ import with_statement

import logging

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import EnvironmentEnvironmentVip
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_ENVIRONMENT_VIP
from networkapi.exception import EnvironmentEnvironmentServerPoolLinked
from networkapi.exception import EnvironmentEnvironmentVipDuplicatedError
from networkapi.exception import EnvironmentEnvironmentVipError
from networkapi.exception import EnvironmentEnvironmentVipNotFoundError
from networkapi.exception import EnvironmentNotFoundError
from networkapi.exception import EnvironmentVipError
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.exception import OptionVipEnvironmentVipDuplicatedError
from networkapi.exception import OptionVipEnvironmentVipError
from networkapi.exception import OptionVipEnvironmentVipNotFoundError
from networkapi.exception import OptionVipError
from networkapi.exception import OptionVipNotFoundError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.requisicaovips.models import OptionVip
from networkapi.requisicaovips.models import OptionVipEnvironmentVip
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class EnvironmentEnvironmentVipAssociationResource(RestResource):

    log = logging.getLogger('EnvironmentEnvironmentVipAssociationResource')

    def handle_put(self, request, user, *args, **kwargs):
        """
        Handles PUT requests to create a relationship of Environment with EnvironmentVip.

        URL: environment/<environment_id>/environmentvip/<environment_vip_id>/
        """

        self.log.info(
            'Create a relationship of Environment with EnvironmentVip')

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Environment
            environment_id = kwargs.get('environment_id')
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'The environment_id parameter is not a valid value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            # Valid EnvironmentVip ID
            environment_vip_id = kwargs.get('environment_vip_id')
            if not is_valid_int_greater_zero_param(environment_vip_id):
                self.log.error(
                    u'The id_environment_vip parameter is not a valid value: %s.', environment_vip_id)
                raise InvalidValueError(
                    None, 'environment_vip_id', environment_vip_id)

            # Business Validations

            # Existing Environment ID
            environment = Ambiente.get_by_pk(environment_id)

            # Existing EnvironmentVip ID
            environment_vip = EnvironmentVip.get_by_pk(environment_vip_id)

            with distributedlock(LOCK_ENVIRONMENT_VIP % environment_vip_id):

                # Business Rules
                # Set new values
                environment_environment_vip = EnvironmentEnvironmentVip()
                environment_environment_vip.environment = environment
                environment_environment_vip.environment_vip = environment_vip

                # Existing EnvironmentEnvironmentVip
                environment_environment_vip.validate()

                # Persist
                environment_environment_vip.save()

                # Return XML
                environment_environment_vip_map = {}
                environment_environment_vip_map['environment_environment_vip'] = model_to_dict(
                    environment_environment_vip, fields=['id'])

                return self.response(dumps_networkapi(environment_environment_vip_map))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EnvironmentNotFoundError:
            return self.response_error(112)
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except EnvironmentEnvironmentVipDuplicatedError:
            return self.response_error(392)
        except Exception, error:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """
        Handles DELETE requests to create a relationship of Environment with EnvironmentVip.

        URL: environment/<environment_id>/environmentvip/<environment_vip_id>/
        """

        self.log.info(
            'Remove a relationship of Environment with EnvironmentVip')

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Environment
            environment_id = kwargs.get('environment_id')
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'The environment_id parameter is not a valid value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            # Valid EnvironmentVip ID
            environment_vip_id = kwargs.get('environment_vip_id')
            if not is_valid_int_greater_zero_param(environment_vip_id):
                self.log.error(
                    u'The id_environment_vip parameter is not a valid value: %s.', environment_vip_id)
                raise InvalidValueError(
                    None, 'environment_vip_id', environment_vip_id)

            # Business Validations

            # Existing Environment ID
            environment = Ambiente.get_by_pk(environment_id)
            # Existing EnvironmentVip ID
            environment_vip = EnvironmentVip.get_by_pk(environment_vip_id)
            # Business Rules
            environment_environment_vip = EnvironmentEnvironmentVip(
            ).get_by_environment_environment_vip(environment.id, environment_vip.id)
            server_pool_list = EnvironmentEnvironmentVip.get_server_pool_by_environment_environment_vip(
                environment_environment_vip)

            # Check if there are any pool from this environment used in any vip
            # of this environment vip
            if server_pool_list:
                raise EnvironmentEnvironmentServerPoolLinked(
                    {'environment': environment.name})

            # Delete
            environment_environment_vip.delete()

            # Return nothing
            return self.response(dumps_networkapi({}))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EnvironmentEnvironmentVipNotFoundError:
            return self.response_error(393)
        except EnvironmentNotFoundError:
            return self.response_error(112)
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except EnvironmentEnvironmentServerPoolLinked, error:
            return self.response_error(394, error.cause.get('environment'))
        except Exception, error:
            return self.response_error(1)
