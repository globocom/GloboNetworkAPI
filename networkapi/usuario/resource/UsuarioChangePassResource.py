# -*- coding:utf-8 -*-

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
from networkapi.auth import has_perm
from networkapi.admin_permission import AdminPermission
from networkapi.distributedlock import distributedlock, LOCK_USER
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.grupo.models import GrupoError
import logging
from networkapi.usuario.models import Usuario, UsuarioNotFoundError, UsuarioError
from networkapi.util import is_valid_int_greater_zero_param, is_valid_string_minsize, is_valid_string_maxsize
import hashlib


class UsuarioChangePassResource(RestResource):
    log = logging.getLogger('UsuarioChangePassResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para alterar a senha de um Usuario.

        URL: user-change-pass/
        """

        try:
            xml_map, attrs_map = loads(request.raw_post_data)
            self.log.info('Change user password')

            # User permission
            if not has_perm(user, AdminPermission.AUTHENTICATE, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            user_map = networkapi_map.get('user')
            if user_map is None:
                return self.response_error(3, u'Não existe valor para a tag usuario do XML de requisição.')

            # Get XML data
            id_user = user_map.get('user_id')
            password = user_map.get('password')

            # Valid ID User
            if not is_valid_int_greater_zero_param(id_user):
                self.log.error(
                    u'The id_user parameter is not a valid value: %s.', id_user)
                raise InvalidValueError(None, 'id_user', id_user)

            # Valid pwd
            if not is_valid_string_minsize(password, 3) or not is_valid_string_maxsize(password, 45):
                self.log.error(u'Parameter password is invalid. Value: ****')
                raise InvalidValueError(None, 'password', '****')

            # Find User by ID to check if it exist
            usr = Usuario.get_by_pk(id_user)

            with distributedlock(LOCK_USER % id_user):

                # set variable
                usr.pwd = hashlib.md5(password).hexdigest()

                try:
                    # update User
                    usr.save(user)
                except Exception, e:
                    self.log.error(u'Failed to update the user.')
                    raise UsuarioError(e, u'Failed to update the user.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except UsuarioNotFoundError:
            return self.response_error(177, id_user)

        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)
        except (UsuarioError, GrupoError):
            return self.response_error(1)
