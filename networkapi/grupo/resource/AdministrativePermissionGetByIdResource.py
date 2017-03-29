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
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.grupo.models import PermissaoAdministrativa
from networkapi.grupo.models import PermissaoAdministrativaNotFoundError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class AdministrativePermissionGetByIdResource(RestResource):

    log = logging.getLogger('AdministrativePermissionGetByIdResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to get Administrative Permission by the identifier.

        URL: aperms/get/<id_perm>/
        """

        try:

            self.log.info('Get Administrative Permission by the identifier')

            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_perm = kwargs.get('id_perm')

            # Valid Administrative Permission ID
            if not is_valid_int_greater_zero_param(id_perm):
                self.log.error(
                    u'The id_perm parameter is not a valid value: %s.', id_perm)
                raise InvalidValueError(None, 'id_perm', id_perm)

            # Find Administrative Permission by ID to check if it exist
            perm = PermissaoAdministrativa.get_by_pk(id_perm)

            perms_map = dict()
            perms_map['perm'] = model_to_dict(perm)

            return self.response(dumps_networkapi(perms_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except PermissaoAdministrativaNotFoundError:
            return self.response_error(189, id_perm)

        except GrupoError, e:
            return self.response_error(1)
