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

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_PERM
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


class AdministrativePermissionAlterRemoveResource(RestResource):

    log = logging.getLogger('AdministrativePermissionAlterRemoveResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to edit Administrative Permission.

        URL: perms/<id_perm>/
        """
        try:

            self.log.info('Edit Administrative Permission')

            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_perm = kwargs.get('id_perm')

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

            # Valid ID Administrative Permission
            if not is_valid_int_greater_zero_param(id_perm):
                self.log.error(
                    u'The id_perm parameter is not a valid value: %s.', id_perm)
                raise InvalidValueError(None, 'id_perm', id_perm)

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
            adm_perm = PermissaoAdministrativa.get_by_pk(id_perm)

            with distributedlock(LOCK_PERM % id_perm):

                # Find Permission by ID to check if it exist
                permission = Permission.get_by_pk(id_permission)

                # Find UGroup by ID to check if it exist
                ugroup = UGrupo.get_by_pk(id_group)

                try:
                    perm = PermissaoAdministrativa.get_permission_by_permission_ugroup(
                        id_permission, id_group)
                    if perm.id != int(id_perm):
                        raise PermissaoAdministrativaDuplicatedError(
                            None, permission.function)
                except PermissaoAdministrativaNotFoundError:
                    pass

                # set variables
                adm_perm.permission = permission
                adm_perm.ugrupo = ugroup
                adm_perm.leitura = convert_string_or_int_to_boolean(read)
                adm_perm.escrita = convert_string_or_int_to_boolean(write)

                try:
                    # update Administrative Permission
                    adm_perm.save()
                except Exception, e:
                    self.log.error(
                        u'Failed to update the administrative permission.')
                    raise PermissionError(
                        e, u'Failed to update the administrative permission.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except PermissionNotFoundError:
            return self.response_error(350, id_permission)

        except UGrupoNotFoundError:
            return self.response_error(180, id_group)

        except PermissaoAdministrativaNotFoundError:
            return self.response_error(189, id_perm)

        except PermissaoAdministrativaDuplicatedError, e:
            return self.response_error(351, e.message)

        except (GrupoError, PermissionError), e:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to remove Administrative Permission.

        URL: perms/<id_perm>/
        """
        try:

            self.log.info('Remove Administrative Permission')

            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_perm = kwargs.get('id_perm')

            # Valid ID Administrative Permission
            if not is_valid_int_greater_zero_param(id_perm):
                self.log.error(
                    u'The id_perm parameter is not a valid value: %s.', id_perm)
                raise InvalidValueError(None, 'id_perm', id_perm)

            # Find Permission by ID to check if it exist
            adm_perm = PermissaoAdministrativa.get_by_pk(id_perm)

            with distributedlock(LOCK_PERM % id_perm):

                try:
                    # Remove Administrative Permission
                    adm_perm.delete()
                except Exception, e:
                    self.log.error(u'Failed to remove the permission.')
                    raise GrupoError(e, u'Failed to remove the permission.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except PermissaoAdministrativaNotFoundError:
            return self.response_error(189, id_perm)

        except GrupoError, e:
            return self.response_error(1)
