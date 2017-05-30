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
import hashlib
import logging

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.usuario.models import Usuario
from networkapi.usuario.models import UsuarioError
from networkapi.usuario.models import UsuarioNameDuplicatedError
from networkapi.usuario.models import UsuarioNotFoundError
from networkapi.util import is_valid_email
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class UserAddResource(RestResource):

    log = logging.getLogger('UserAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add user.

        URL: user/
        """

        try:

            self.log.info('Add User')

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

            user_map = networkapi_map.get('user')
            if user_map is None:
                return self.response_error(3, u'There is no value to the user tag  of XML request.')

            # Get XML data
            username = user_map.get('user')
            password = user_map.get('password')
            name = user_map.get('name')
            email = user_map.get('email')
            user_ldap = user_map.get('user_ldap')

            # Valid username
            if not is_valid_string_minsize(username, 3) or not is_valid_string_maxsize(username, 45):
                self.log.error(
                    u'Parameter user is invalid. Value: %s', username)
                raise InvalidValueError(None, 'user', username)

            # Valid pwd
            if not is_valid_string_minsize(password, 3) or not is_valid_string_maxsize(password, 45):
                self.log.error(u'Parameter password is invalid. Value: ****')
                raise InvalidValueError(None, 'password', '****')

            # Valid name
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 200):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            # Valid email
            if not is_valid_string_minsize(email, 3) or not is_valid_string_maxsize(email, 200) or not is_valid_email(email):
                self.log.error(u'Parameter email is invalid. Value: %s', email)
                raise InvalidValueError(None, 'email', email)

            # Valid LDAP username
            if user_ldap is not None:
                if not is_valid_string_minsize(user_ldap, 3) or not is_valid_string_maxsize(user_ldap, 45):
                    self.log.error(
                        u'Parameter user_ldap is invalid. Value: %s', user_ldap)
                    raise InvalidValueError(None, 'user_ldap', user_ldap)

            try:
                Usuario.get_by_user(username)
                raise UsuarioNameDuplicatedError(
                    None, u'Já existe um usuário com o valor user %s.' % username)
            except UsuarioNotFoundError:
                pass

            usr = Usuario()

            # set variables
            usr.user = username
            usr.pwd = Usuario.encode_password(password)
            usr.nome = name
            usr.email = email
            usr.ativo = True
            usr.user_ldap = user_ldap

            try:
                # save User
                usr.save()
            except Exception, e:
                self.log.error(u'Failed to save the user.')
                raise UsuarioError(e, u'Failed to save the user.')

            perm_map = dict()
            perm_map['usuario'] = model_to_dict(
                usr, exclude=['user', 'nome', 'pwd', 'name', 'email'])

            return self.response(dumps_networkapi(perm_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UsuarioNameDuplicatedError:
            return self.response_error(179, username)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except (GrupoError, UsuarioError):
            return self.response_error(1)
