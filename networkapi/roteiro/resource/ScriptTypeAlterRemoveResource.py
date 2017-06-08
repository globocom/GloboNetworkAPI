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
from networkapi.distributedlock import LOCK_SCRIPT_TYPE
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.roteiro.models import RoteiroError
from networkapi.roteiro.models import TipoRoteiro
from networkapi.roteiro.models import TipoRoteiroHasRoteiroError
from networkapi.roteiro.models import TipoRoteiroNameDuplicatedError
from networkapi.roteiro.models import TipoRoteiroNotFoundError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class ScriptTypeAlterRemoveResource(RestResource):

    log = logging.getLogger('ScriptTypeAlterRemoveResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to edit Script Type.

        URL: scripttype/<id_script_type>/
        """
        try:

            self.log.info('Edit Script Type')

            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_script_type = kwargs.get('id_script_type')

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            script_type_map = networkapi_map.get('script_type')
            if script_type_map is None:
                return self.response_error(3, u'There is no value to the script_type tag  of XML request.')

            # Get XML data
            type = script_type_map.get('type')
            description = script_type_map.get('description')

            # Valid ID Script Type
            if not is_valid_int_greater_zero_param(id_script_type):
                self.log.error(
                    u'The id_script_type parameter is not a valid value: %s.', id_script_type)
                raise InvalidValueError(None, 'id_script_type', id_script_type)

            # Valid type
            if not is_valid_string_minsize(type, 3) or not is_valid_string_maxsize(type, 40):
                self.log.error(u'Parameter type is invalid. Value: %s', type)
                raise InvalidValueError(None, 'type', type)

            # Valid description
            if not is_valid_string_minsize(description, 3) or not is_valid_string_maxsize(description, 100):
                self.log.error(
                    u'Parameter description is invalid. Value: %s', description)
                raise InvalidValueError(None, 'description', description)

            # Find Script Type by ID to check if it exist
            script_type = TipoRoteiro.get_by_pk(id_script_type)

            with distributedlock(LOCK_SCRIPT_TYPE % id_script_type):

                try:
                    if script_type.tipo.lower() != type.lower():
                        TipoRoteiro.get_by_name(type)
                        raise TipoRoteiroNameDuplicatedError(
                            None, u'Já existe um tipo de roteiro com o tipo %s.' % type)
                except TipoRoteiroNotFoundError:
                    pass

                # set variables
                script_type.tipo = type
                script_type.descricao = description

                try:
                    # update Script Type
                    script_type.save()
                except Exception, e:
                    self.log.error(u'Failed to update the Script Type.')
                    raise RoteiroError(e, u'Failed to update the Script Type.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except TipoRoteiroNotFoundError:
            return self.response_error(158, id_script_type)

        except TipoRoteiroNameDuplicatedError:
            return self.response_error(193, type)

        except RoteiroError:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to remove Script Type.

        URL: scripttype/<id_script_type>/
        """
        try:

            self.log.info('Remove Script Type')

            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_script_type = kwargs.get('id_script_type')

            # Valid ID Script Type
            if not is_valid_int_greater_zero_param(id_script_type):
                self.log.error(
                    u'The id_script_type parameter is not a valid value: %s.', id_script_type)
                raise InvalidValueError(None, 'id_script_type', id_script_type)

            # Find Script Type by ID to check if it exist
            script_type = TipoRoteiro.get_by_pk(id_script_type)

            with distributedlock(LOCK_SCRIPT_TYPE % id_script_type):

                try:

                    if script_type.roteiro_set.count() != 0:
                        raise TipoRoteiroHasRoteiroError(
                            None, u'Existe roteiros associado ao tipo de roteiro %d' % script_type.id)

                    # remove Script Type
                    script_type.delete()

                except TipoRoteiroHasRoteiroError, e:
                    raise e
                except Exception, e:
                    self.log.error(u'Failed to remove the Script Type.')
                    raise RoteiroError(e, u'Failed to remove the Script Type.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except TipoRoteiroNotFoundError:
            return self.response_error(158, id_script_type)

        except TipoRoteiroHasRoteiroError:
            return self.response_error(196, id_script_type)

        except RoteiroError:
            return self.response_error(1)
