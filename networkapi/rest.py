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


from django.db import transaction
from django.http import HttpResponse
from httplib import *
from networkapi.auth import authenticate
from networkapi.error_message_utils import error_dumps
from networkapi.usuario.models import UsuarioError
from urllib2 import *
from networkapi.log import Log
from _mysql_exceptions import OperationalError
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.distributedlock import LockNotAcquiredError


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

    log = Log('RestResource')

    @transaction.commit_manually
    def handle_request(self, request, *args, **kwargs):
        """Recebe a requisição e redireciona para o método apropriado.

        Antes de redirecionar para o método, é feita a autenticação do usuário.
        """
        response = None
        try:
            self.log.rest(u'INICIO da requisição %s para URL %s. XML: [%s].' % (request.method,
                                                                                request.path,
                                                                                request.raw_post_data))

            username, password, user_ldap = self.read_user_data(request)

            self.log.debug(u'Usuário da requisição: %s.' % username)

            if user_ldap is None:
                user = authenticate(username, password)
            else:
                user = authenticate(username, password, user_ldap)

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

        except (LockNotAcquiredError, OperationalError), e:
            self.log.error(u'Lock wait timeout exceeded.')
            return self.response_error(273)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
        except Exception, e:
            self.log.error(u'Erro não esperado.')
            response = self.response_error(1)
        finally:
            username, password, user_ldap = self.read_user_data(request)
            password = '****'
            if response is not None:
                if response.status_code == 200:
                    transaction.commit()
                    self.log.debug(
                        u'Requisição do usuário %s concluída com sucesso.' % username)
                else:
                    transaction.rollback()
                    self.log.debug(u'Requisição do usuário %s concluída com falha. Conteúdo: [%s].' % (username,
                                                                                                       response.content))
            else:
                transaction.rollback()
                self.log.debug(
                    u'Requisição do usuário %s concluída com falha.' % username)

            self.log.debug(u'FIM da requisição do usuário %s.' % username)

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

    def read_user_data(self, request):
        username = request.META.get('HTTP_NETWORKAPI_USERNAME')
        password = request.META.get('HTTP_NETWORKAPI_PASSWORD')
        user_ldap = request.META.get('HTTP_NETWORKAPI_USERLDAP')
        return username, password, user_ldap

    def not_authenticated(self):
        return HttpResponse(u'401 - Usuário não autenticado. Usuário e/ou senha incorretos.',
                            status=401,
                            content_type='text/plain')

    def not_authorized(self):
        return HttpResponse(u'402 - Usuário não autorizado para executar a operação.',
                            status=402,
                            content_type='text/plain')

    def not_implemented(self):
        """Cria um HttpResponse com o código HTTP 501 - Not implemented."""
        return HttpResponse(u'501 - Chamada não implementada.', status=501,
                            content_type='text/plain')

    def response_error(self, code, *args):
        """Cria um HttpResponse com o XML de erro."""
        return HttpResponse(error_dumps(code, *args), status=500, content_type='text/plain')

    def response(self, content, status=200, content_type='text/plain'):
        """Cria um HttpResponse com os dados informados"""
        return HttpResponse(content, status=status,
                            content_type=content_type)


class RestResponse:

    """Classe básica para respostas dos webservices REST"""

    def __init__(self, exception=None):
        self.exception = exception
