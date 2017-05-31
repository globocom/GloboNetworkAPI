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
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_ENVIRONMENT_VIP
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
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class OptionVipEnvironmentVipAssociationResource(RestResource):

    log = logging.getLogger('OptionVipEnvironmentVipAssociationResource')

    def handle_put(self, request, user, *args, **kwargs):
        """
        Handles PUT requests to create a relationship of OptionVip with EnvironmentVip.

        URL: optionvip/<id_option_vip>/environmentvip/<id_environment_vip>/
        """

        self.log.info('Create a relationship of OptionVip with EnvironmentVip')

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.OPTION_VIP, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid OptionVip ID
            option_vip_id = kwargs.get('id_option_vip')
            if not is_valid_int_greater_zero_param(option_vip_id):
                self.log.error(
                    u'The id_option_vip parameter is not a valid value: %s.', option_vip_id)
                raise InvalidValueError(None, 'id_option_vip', option_vip_id)

            # Valid EnvironmentVip ID
            environment_vip_id = kwargs.get('id_environment_vip')
            if not is_valid_int_greater_zero_param(environment_vip_id):
                self.log.error(
                    u'The id_environment_vip parameter is not a valid value: %s.', environment_vip_id)
                raise InvalidValueError(
                    None, 'id_environment_vip', environment_vip_id)

            # Business Validations

            # Existing OptionVip ID
            option_vip = OptionVip.get_by_pk(option_vip_id)

            # Existing EnvironmentVip ID
            environment_vip = EnvironmentVip.get_by_pk(environment_vip_id)

            with distributedlock(LOCK_ENVIRONMENT_VIP % environment_vip_id):

                # Business Rules

                # Set new values
                opt_vip_env_vip = OptionVipEnvironmentVip()
                opt_vip_env_vip.option = option_vip
                opt_vip_env_vip.environment = environment_vip

                # Existing OptionVipEnvironmentVip
                opt_vip_env_vip.validate()

                # Persist
                opt_vip_env_vip.save()

                # Return XML
                opt_vip_env_vip_map = dict()
                opt_vip_env_vip_map['opcoesvip_ambiente_xref'] = model_to_dict(
                    opt_vip_env_vip, fields=['id'])

                return self.response(dumps_networkapi(opt_vip_env_vip_map))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except OptionVipNotFoundError:
            return self.response_error(289)
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except OptionVipEnvironmentVipDuplicatedError:
            return self.response_error(290)
        except (OptionVipError, EnvironmentVipError, OptionVipEnvironmentVipError):
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """
        Handles DELETE requests to remove a relationship of OptionVip with EnvironmentVip.

        URL: optionvip/<id_option_vip>/environmentvip/<id_environment_vip>/
        """

        self.log.info('Remove a relationship of OptionVip with EnvironmentVip')

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.OPTION_VIP, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid OptionVip ID
            option_vip_id = kwargs.get('id_option_vip')
            if not is_valid_int_greater_zero_param(option_vip_id):
                self.log.error(
                    u'The id_option_vip parameter is not a valid value: %s.', option_vip_id)
                raise InvalidValueError(None, 'id_option_vip', option_vip_id)

            # Valid EnvironmentVip ID
            environment_vip_id = kwargs.get('id_environment_vip')
            if not is_valid_int_greater_zero_param(environment_vip_id):
                self.log.error(
                    u'The id_environment_vip parameter is not a valid value: %s.', environment_vip_id)
                raise InvalidValueError(
                    None, 'id_environment_vip', environment_vip_id)

            # Business Validations

            # Existing OptionVip ID
            option_vip = OptionVip.get_by_pk(option_vip_id)

            # Existing EnvironmentVip ID
            environment_vip = EnvironmentVip.get_by_pk(environment_vip_id)

            # Business Rules

            # Find
            opt_vip_env_vip = OptionVipEnvironmentVip().get_by_option_environment(
                option_vip.id, environment_vip.id)

            # Delete
            opt_vip_env_vip.delete()

            # Return nothing
            return self.response(dumps_networkapi({}))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except OptionVipEnvironmentVipNotFoundError:
            return self.response_error(291)
        except OptionVipNotFoundError:
            return self.response_error(289)
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except (OptionVipError, EnvironmentVipError, OptionVipEnvironmentVipError):
            return self.response_error(1)
