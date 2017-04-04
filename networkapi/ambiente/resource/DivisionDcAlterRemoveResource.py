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
from networkapi.ambiente.models import DivisaoDc
from networkapi.ambiente.models import DivisaoDcNameDuplicatedError
from networkapi.ambiente.models import DivisaoDcNotFoundError
from networkapi.ambiente.models import DivisaoDcUsedByEnvironmentError
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_DC_DIVISION
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_regex
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class DivisionDcAlterRemoveResource(RestResource):

    log = logging.getLogger('DivisionDcAlterRemoveResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to edit Division Dc.

        URL: divisiondc/<id_divisiondc>/
        """
        try:

            self.log.info('Edit Division Dc')

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_divisiondc = kwargs.get('id_divisiondc')

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            division_dc_map = networkapi_map.get('division_dc')
            if division_dc_map is None:
                return self.response_error(3, u'There is no value to the division_dc tag  of XML request.')

            # Get XML data
            name = division_dc_map.get('name')

            # Valid ID Division Dc
            if not is_valid_int_greater_zero_param(id_divisiondc):
                self.log.error(
                    u'The id_divisiondc parameter is not a valid value: %s.', id_divisiondc)
                raise InvalidValueError(None, 'id_divisiondc', id_divisiondc)

            # Valid name
            if not is_valid_string_minsize(name, 2) or not is_valid_string_maxsize(name, 80):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            # Find Division Dc by ID to check if it exist
            division_dc = DivisaoDc.get_by_pk(id_divisiondc)

            with distributedlock(LOCK_DC_DIVISION % id_divisiondc):

                try:
                    if division_dc.nome.lower() != name.lower():
                        DivisaoDc.get_by_name(name)
                        raise DivisaoDcNameDuplicatedError(
                            None, u'Já existe um Divisão Dc com o valor name %s.' % name)
                except DivisaoDcNotFoundError:
                    pass

                # set variables
                division_dc.nome = name

                try:
                    # update Division Dc
                    division_dc.save()
                except Exception, e:
                    self.log.error(u'Failed to update the Division Dc.')
                    raise AmbienteError(
                        e, u'Failed to update the Division Dc.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except DivisaoDcNameDuplicatedError:
            return self.response_error(175, name)

        except DivisaoDcNotFoundError:
            return self.response_error(164, id_divisiondc)

        except AmbienteError:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to remove Division Dc.

        URL: divisiondc/<id_divisiondc>/
        """
        try:

            self.log.info('Remove Division Dc')

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_divisiondc = kwargs.get('id_divisiondc')

            # Valid ID Division Dc
            if not is_valid_int_greater_zero_param(id_divisiondc):
                self.log.error(
                    u'The id_divisiondc parameter is not a valid value: %s.', id_divisiondc)
                raise InvalidValueError(None, 'id_divisiondc', id_divisiondc)

            # Find Division Dc by ID to check if it exist
            division_dc = DivisaoDc.get_by_pk(id_divisiondc)

            with distributedlock(LOCK_DC_DIVISION % id_divisiondc):

                try:

                    if division_dc.ambiente_set.count() > 0:
                        raise DivisaoDcUsedByEnvironmentError(
                            None, u'A Divisão DC %s tem ambiente associado.' % division_dc.id)

                    # remove Division Dc
                    division_dc.delete()

                except DivisaoDcUsedByEnvironmentError, e:
                    raise e
                except Exception, e:
                    self.log.error(u'Failed to remove the Division Dc.')
                    raise AmbienteError(
                        e, u'Failed to remove the Division Dc.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except DivisaoDcNotFoundError:
            return self.response_error(164, id_divisiondc)

        except DivisaoDcUsedByEnvironmentError:
            return self.response_error(216, id_divisiondc)

        except AmbienteError:
            return self.response_error(1)
