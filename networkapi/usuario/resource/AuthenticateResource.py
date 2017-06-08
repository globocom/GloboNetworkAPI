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
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.usuario.models import Usuario
from networkapi.usuario.models import UsuarioError
from networkapi.usuario.models import UsuarioNotFoundError
from networkapi.util import convert_string_or_int_to_boolean
from networkapi.util import is_valid_boolean_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class AuthenticateResource(RestResource):

    log = logging.getLogger('AuthenticateResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to authenticate to user.

        URL: authenticate/
        """

        try:

            self.log.info('Authenticate user')

            # User permission
            if not has_perm(user, AdminPermission.AUTHENTICATE, AdminPermission.WRITE_OPERATION):
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
            username = user_map.get('username')
            password = user_map.get('password')
            is_ldap_user = user_map.get('is_ldap_user')

            # Username can NOT be less 3 and greater than 45
            if not is_valid_string_minsize(username, 3) or not is_valid_string_maxsize(username, 45):
                self.log.error(
                    u'Parameter username is invalid. Value: %s.', username)
                raise InvalidValueError(None, 'username', username)

            if not is_valid_boolean_param(is_ldap_user):
                self.log.error(
                    u'Parameter is_ldap_user is invalid. Value: %s.', is_ldap_user)
                raise InvalidValueError(None, 'is_ldap_user', is_ldap_user)
            else:
                is_ldap_user = convert_string_or_int_to_boolean(is_ldap_user)

            if is_ldap_user:
                user = Usuario().get_by_ldap_user(username, True)
                password = user.pwd
            else:
                # Password can NOT be less 3 and greater than 45
                if not is_valid_string_minsize(password, 3) or not is_valid_string_maxsize(password, 45):
                    self.log.error(
                        u'Parameter password is invalid. Value: %s.', '****')
                    raise InvalidValueError(None, 'password', '****')

                # Find user by username, password to check if it exist
                user = Usuario().get_enabled_user(username.upper(), password)

            # Valid user
            if user is None:
                return self.response(dumps_networkapi({}))

            perms = {}
            for ugroup in user.grupos.all():

                for perm in ugroup.permissaoadministrativa_set.all():

                    function = perm.permission.function

                    if function in perms:

                        write = False
                        read = False

                        if perms.get(function).get('write') is True or perm.escrita is True:
                            write = True

                        if perms.get(function).get('read') is True or perm.leitura is True:
                            read = True

                        perms[function] = {'write': write, 'read': read}

                    else:
                        perms[function] = {
                            'write': perm.escrita, 'read': perm.leitura}

            user_map = {}
            user_dict = model_to_dict(
                user, fields=['id', 'user', 'nome', 'email', 'ativo', 'user_ldap'])
            user_dict['pwd'] = password
            user_dict['permission'] = perms
            user_map['user'] = user_dict

            return self.response(dumps_networkapi(user_map))

        except UsuarioNotFoundError:
            return self.response(dumps_networkapi({}))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except UsuarioError:
            return self.response_error(1)
