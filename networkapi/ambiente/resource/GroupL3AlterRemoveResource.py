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
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import GroupL3NotFoundError
from networkapi.ambiente.models import GrupoL3
from networkapi.ambiente.models import GrupoL3NameDuplicatedError
from networkapi.ambiente.models import GrupoL3UsedByEnvironmentError
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_GROUP_L3
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_regex
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class GroupL3AlterRemoveResource(RestResource):

    log = logging.getLogger('GroupL3AlterRemoveResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to edit Group l3.

        URL: groupl3/<id_groupl3>/
        """
        try:

            self.log.info('Edit Group l3')

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_groupl3 = kwargs.get('id_groupl3')

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            group_l3_map = networkapi_map.get('group_l3')
            if group_l3_map is None:
                return self.response_error(3, u'There is no value to the group_l3 tag  of XML request.')

            # Get XML data
            name = group_l3_map.get('name')

            # Valid ID Group L3
            if not is_valid_int_greater_zero_param(id_groupl3):
                self.log.error(
                    u'The id_groupl3 parameter is not a valid value: %s.', id_groupl3)
                raise InvalidValueError(None, 'id_groupl3', id_groupl3)

            # Valid name
            if not is_valid_string_minsize(name, 2) or not is_valid_string_maxsize(name, 80):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            # Find GroupL3 by ID to check if it exist
            groupl3 = GrupoL3.get_by_pk(id_groupl3)

            with distributedlock(LOCK_GROUP_L3 % id_groupl3):

                try:
                    if groupl3.nome.lower() != name.lower():
                        GrupoL3.get_by_name(name)
                        raise GrupoL3NameDuplicatedError(
                            None, u'Já existe um grupo l3 com o valor name %s.' % name)
                except GroupL3NotFoundError:
                    pass

                # set variables
                groupl3.nome = name

                try:
                    # update Group l3
                    groupl3.save()
                except Exception, e:
                    self.log.error(u'Failed to update the Group l3.')
                    raise AmbienteError(e, u'Failed to update the Group l3.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except GroupL3NotFoundError:
            return self.response_error(160, id_groupl3)

        except GrupoL3NameDuplicatedError:
            return self.response_error(169, name)

        except AmbienteError:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to remove Group l3.

        URL: groupl3/<id_groupl3>/
        """
        try:

            self.log.info('Remove Group l3')

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_groupl3 = kwargs.get('id_groupl3')

            # Valid ID Group L3
            if not is_valid_int_greater_zero_param(id_groupl3):
                self.log.error(
                    u'The id_groupl3 parameter is not a valid value: %s.', id_groupl3)
                raise InvalidValueError(None, 'id_groupl3', id_groupl3)

            # Find GroupL3 by ID to check if it exist
            groupl3 = GrupoL3.get_by_pk(id_groupl3)

            with distributedlock(LOCK_GROUP_L3 % id_groupl3):

                try:

                    if groupl3.ambiente_set.count() > 0:
                        raise GrupoL3UsedByEnvironmentError(
                            None, u'O GrupoL3 %s tem ambiente associado.' % groupl3.id)

                    # remove Group l3
                    groupl3.delete()

                except GrupoL3UsedByEnvironmentError, e:
                    raise e
                except Exception, e:
                    self.log.error(u'Failed to remove the Group l3.')
                    raise GrupoError(e, u'Failed to remove the Group l3.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except GroupL3NotFoundError:
            return self.response_error(160, id_groupl3)

        except GrupoL3UsedByEnvironmentError:
            return self.response_error(218, id_groupl3)

        except AmbienteError:
            return self.response_error(1)
