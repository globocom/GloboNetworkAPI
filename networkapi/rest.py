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
from httplib import *
from urllib2 import *

from _mysql_exceptions import OperationalError
from django.db import transaction
from django.http import HttpResponse
from rest_framework.exceptions import AuthenticationFailed

from networkapi.api_rest.authentication import BasicAuthentication
from networkapi.auth import authenticate
from networkapi.distributedlock import LockNotAcquiredError
from networkapi.error_message_utils import error_dumps
from networkapi.extra_logging import local
from networkapi.infrastructure.xml_utils import XMLError
# from networkapi.usuario.models import UsuarioError


class RestError(Exception):

    """Representa um erro ocorrido durante uma requisão REST."""

    def __init__(self, cause, message):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Erro ao realizar requisição REST: Causa: %s, Mensagem: %s' % (
            self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class UserNotAuthorizedError(RestError):

    """Retorna exceção quando o usuário não tem permissão para executar a operação."""

    def __init__(self, cause, message=None):
        RestError.__init__(self, cause, message)


class RestResource(object):

    """
    Representa um recurso acessível via chamadas REST.

    As subclasses de Resource serão responsáveis por expor os serviços de
    forma a serem acessados via requisições HTTP.
    """

    log = logging.getLogger('RestResource')

    @transaction.commit_manually
    def handle_request(self, request, *args, **kwargs):
        """Recebe a requisição e redireciona para o método apropriado.

        Antes de redirecionar para o método, é feita a autenticação do usuário.
        """
        response = None
        try:
            user = RestResource.authenticate_user(request)

            if (user is None):
                response = self.not_authenticated()
            else:
                if request.method == 'GET':
                    response = self.handle_get(request, user, args, **kwargs)
                elif request.method == 'POST':
                    response = self.handle_post(request, user, args, **kwargs)
                elif request.method == 'DELETE':
                    response = self.handle_delete(
                        request, user, args, **kwargs)
                elif request.method == 'PUT':
                    response = self.handle_put(request, user, args, **kwargs)
        except AuthenticationFailed:
            self.log.error(u'Authentication failed.')
            response = self.not_authenticated()
        except (LockNotAcquiredError, OperationalError), e:
            self.log.error(u'Lock wait timeout exceeded.')
            return self.response_error(273)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
        except Exception, e:
            self.log.exception(u'Erro não esperado.')
            response = self.response_error(1)
        finally:
            username, password, user_ldap = RestResource.read_user_data(
                request)
            # password = '****'
            if response is not None:
                if response.status_code == 200:
                    transaction.commit()
                else:
                    transaction.rollback()
            else:
                transaction.rollback()
                self.log.debug(u'Requisição concluída com falha.')

        return response

    def handle_get(self, request, user, *args, **kwargs):
        """Trata uma requisição com o método GET"""
        return self.not_implemented()

    def handle_post(self, request, user, *args, **kwargs):
        """Trata uma requisição com o método POST"""
        return self.not_implemented()

    def handle_delete(self, request, user, *args, **kwargs):
        """Trata uma requisição com o método DELETE"""
        return self.not_implemented()

    def handle_put(self, request, user, *args, **kwargs):
        """Trata uma requisição com o método PUT"""
        return self.not_implemented()

    @classmethod
    def read_user_data(cls, request):
        username = request.META.get('HTTP_NETWORKAPI_USERNAME')
        password = request.META.get('HTTP_NETWORKAPI_PASSWORD')
        user_ldap = request.META.get('HTTP_NETWORKAPI_USERLDAP')
        return username, password, user_ldap

    @classmethod
    def authenticate_user(cls, request):
        if not request.user.is_anonymous():
            return request.user

        user = None
        username, password, user_ldap = RestResource.read_user_data(request)

        if user_ldap is None:
            user = authenticate(username, password)
        else:
            user = authenticate(username, password, user_ldap)

        if user is None:
            credentials = BasicAuthentication().authenticate(request)
            user = credentials[0] if credentials is not None else None

        if user:
            request.user = user

        return user

    def not_authenticated(self):
        http_res = HttpResponse(
            u'401 - Usuário não autenticado. Usuário e/ou senha incorretos.',
            status=401,
            content_type='text/plain')

        http_res['X-Request-Id'] = local.request_id
        http_res['X-Request-Context'] = local.request_context

        return http_res

    def not_authorized(self):
        http_res = HttpResponse(
            u'402 - Usuário não autorizado para executar a operação.',
            status=402,
            content_type='text/plain')

        http_res['X-Request-Id'] = local.request_id
        http_res['X-Request-Context'] = local.request_context

        return http_res

    def not_implemented(self):
        """Cria um HttpResponse com o código HTTP 501 - Not implemented."""
        http_res = HttpResponse(
            u'501 - Chamada não implementada.',
            status=501,
            content_type='text/plain')

        http_res['X-Request-Id'] = local.request_id
        http_res['X-Request-Context'] = local.request_context

        return http_res

    def response_error(self, code, *args):
        """Cria um HttpResponse com o XML de erro."""
        http_res = HttpResponse(
            error_dumps(code, *args),
            status=500,
            content_type='text/plain')

        http_res['X-Request-Id'] = local.request_id
        http_res['X-Request-Context'] = local.request_context

        return http_res

    def not_found(self):
        """Cria um HttpResponse com código HTTP 404 - Not Found."""
        http_res = HttpResponse(
            u'404 - Chamada não encontrada.',
            status=404,
            content_type='text/plain')

        http_res['X-Request-Id'] = local.request_id
        http_res['X-Request-Context'] = local.request_context

        return http_res

    def response(self, content, status=200, content_type='text/plain'):
        """Cria um HttpResponse com os dados informados"""

        http_res = HttpResponse(
            content,
            status=status,
            content_type=content_type)

        http_res['X-Request-Id'] = local.request_id
        http_res['X-Request-Context'] = local.request_context

        return http_res


class RestResponse:

    """Classe básica para respostas dos webservices REST"""

    def __init__(self, exception=None):
        self.exception = exception
