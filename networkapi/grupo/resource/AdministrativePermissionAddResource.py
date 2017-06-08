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
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.grupo.models import PermissaoAdministrativa
from networkapi.grupo.models import PermissaoAdministrativaDuplicatedError
from networkapi.grupo.models import PermissaoAdministrativaNotFoundError
from networkapi.grupo.models import Permission
from networkapi.grupo.models import PermissionError
from networkapi.grupo.models import PermissionNotFoundError
from networkapi.grupo.models import UGrupo
from networkapi.grupo.models import UGrupoNotFoundError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import convert_string_or_int_to_boolean
from networkapi.util import is_valid_boolean_param
from networkapi.util import is_valid_int_greater_zero_param


class AdministrativePermissionAddResource(RestResource):

    log = logging.getLogger('AdministrativePermissionAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Administrative Permission.

        URL: aperms/
        """

        try:

            self.log.info('Add Administrative Permission')

            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            perm_map = networkapi_map.get('administrative_permission')
            if perm_map is None:
                return self.response_error(3, u'There is no value to the administrative_permission tag  of XML request.')

            # Get XML data
            id_permission = perm_map.get('id_permission')
            id_group = perm_map.get('id_group')
            read = perm_map.get('read')
            write = perm_map.get('write')

            # Valid ID Permission
            if not is_valid_int_greater_zero_param(id_permission):
                self.log.error(
                    u'The id_permission parameter is not a valid value: %s.', id_permission)
                raise InvalidValueError(None, 'id_permission', id_permission)

            # Valid ID Group
            if not is_valid_int_greater_zero_param(id_group):
                self.log.error(
                    u'The id_group parameter is not a valid value: %s.', id_group)
                raise InvalidValueError(None, 'id_group', id_group)

            # Valid Read
            if not is_valid_boolean_param(read):
                self.log.error(
                    u'The read parameter is not a valid value: %s.', read)
                raise InvalidValueError(None, 'read', read)

            # Valid Read
            if not is_valid_boolean_param(write):
                self.log.error(
                    u'The write parameter is not a valid value: %s.', write)
                raise InvalidValueError(None, 'write', write)

            # Find Permission by ID to check if it exist
            permission = Permission.get_by_pk(id_permission)

            # Find UGroup by ID to check if it exist
            ugroup = UGrupo.get_by_pk(id_group)

            try:
                PermissaoAdministrativa.get_permission_by_permission_ugroup(
                    id_permission, id_group)
                raise PermissaoAdministrativaDuplicatedError(
                    None, permission.function)
            except PermissaoAdministrativaNotFoundError:
                pass

            adm_perm = PermissaoAdministrativa()

            # set variables
            adm_perm.permission = permission
            adm_perm.ugrupo = ugroup
            adm_perm.leitura = convert_string_or_int_to_boolean(read)
            adm_perm.escrita = convert_string_or_int_to_boolean(write)

            try:
                # save Administrative Permission
                adm_perm.save()
            except Exception, e:
                self.log.error(
                    u'Failed to save the administrative permission.')
                raise GrupoError(
                    e, u'Failed to save the administrative permission.')

            perm_map = dict()
            perm_map['perm'] = model_to_dict(
                adm_perm, exclude=['permission', 'leitura', 'escrita', 'ugrupo'])

            return self.response(dumps_networkapi(perm_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except PermissionNotFoundError:
            return self.response_error(350, id_permission)

        except UGrupoNotFoundError:
            return self.response_error(180, id_group)

        except PermissaoAdministrativaDuplicatedError, e:
            return self.response_error(351, e.message)

        except (GrupoError, PermissionError), e:
            return self.response_error(1)
