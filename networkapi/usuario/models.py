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

import hashlib
import logging
import requests
import socket
import tempfile
import os

import ldap
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.models.BaseModel import BaseModel
from networkapi.system import exceptions
from networkapi.system.facade import get_value
from networkapi.util import convert_string_or_int_to_boolean
from networkapi.util.appcache import get_cache, set_cache
from networkapi.util.encrypt import encrypt_key, generate_key

from base64 import b64encode


class UsuarioError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com usuario."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class UsuarioNotFoundError(UsuarioError):

    """Retorna exceção para pesquisa de Usuario."""

    def __init__(self, cause, message=None):
        UsuarioError.__init__(self, cause, message)


class UsuarioNameDuplicatedError(UsuarioError):

    """Retorna exceção porque já existe um Usuario cadastrado com o mesmo user."""

    def __init__(self, cause, message=None):
        UsuarioError.__init__(self, cause, message)


class UsuarioHasEventOrGrupoError(UsuarioError):

    """Retorna exceção porque existe usuario associado a um event_log ou a um grupo."""

    def __init__(self, cause, message=None):
        UsuarioError.__init__(self, cause, message)


class UsuarioGrupoDuplicatedError(UsuarioError):

    """Retorna exceção quando o usuario_grupo já existe."""

    def __init__(self, cause, message=None):
        UsuarioError.__init__(self, cause, message)


class UserGroupNotFoundError(UsuarioError):

    """returns exception to UserGroup research by primary key."""

    def __init__(self, cause, message=None):
        UsuarioError.__init__(self, cause, message)


class Usuario(BaseModel):

    user = models.CharField(unique=True, max_length=45)
    pwd = models.CharField(max_length=45)
    id = models.AutoField(primary_key=True, db_column='id_user')
    nome = models.CharField(max_length=200)
    ativo = models.BooleanField()
    email = models.CharField(max_length=300)
    grupos = models.ManyToManyField('grupo.UGrupo', through='UsuarioGrupo')
    user_ldap = models.CharField(
        unique=True, max_length=45, null=True, blank=True)

    log = logging.getLogger('Usuario')

    class Meta(BaseModel.Meta):
        db_table = u'usuarios'
        managed = True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return Usuario.objects.filter(
            user=self.user.lower(),
            pwd=self.pwd,
            ativo=1
        )

    @classmethod
    def uniqueUsers(cls):
        userlist = Usuario.objects.all().order_by('user')
        return userlist

    @classmethod
    def encode_password(cls, pwd):
        return hashlib.md5(pwd).hexdigest()

    @classmethod
    def get_by_pk(cls, pk):
        """"Get  User by pk.

        @return: User.

        @raise UsuarioNotFoundError: User is not registered.
        @raise UsuarioError: Failed to search for the User.
        """
        try:
            return Usuario.objects.get(pk=pk)
        except ObjectDoesNotExist, e:
            raise UsuarioNotFoundError(
                e, u'Dont there is a Group L3 by pk = %s.' % pk)
        except Exception, e:
            cls.log.error(u'Failure to search the User.')
            raise UsuarioError(e, u'Failure to search the User.')

    @classmethod
    def get_by_user(cls, name):
        """"Get User by username.

        @return: User.

        @raise UsuarioNotFoundError: User is not registered.
        @raise UsuarioError: Failed to search for the User.
        """
        try:
            return Usuario.objects.get(user__iexact=name)
        except ObjectDoesNotExist, e:
            raise UsuarioNotFoundError(
                e, u'There is no User with username = %s.' % name)
        except Exception, e:
            cls.log.error(u'Failure to search the User.')
            raise UsuarioError(e, u'Failure to search the User.')

    @classmethod
    def get_by_ldap_user(cls, ldap_usr, active=False):
        """Get User by ldap username.

        @return: User.

        @raise UsuarioNotFoundError: User is not registered.
        @raise UsuarioError: Failed to search for the User.
        """
        try:
            if active:
                return Usuario.objects.prefetch_related('grupos').get(user_ldap__iexact=ldap_usr, ativo=1)
            else:
                return Usuario.objects.prefetch_related('grupos').get(user_ldap__iexact=ldap_usr)
        except ObjectDoesNotExist, e:
            raise UsuarioNotFoundError(
                e, u'There is no User with ldap_user = %s.' % ldap_usr)
        except Exception, e:
            cls.log.error(u'Failure to search the User.')
            raise UsuarioError(e, u'Failure to search the User.')

    def get_enabled_user(self, username, password):
        """
        Busca o usuário de acordo com o login e a senha.

        Retorna apenas usuário ativo.
        """
        bypass = 0
        try:
            try:
                use_cache_user = convert_string_or_int_to_boolean(
                    get_value('use_cache_user'))

                if use_cache_user:
                    salt = get_cache('salt_key')

                    if salt:
                        self.log.debug('The encrypt key was taken successfully!')

                        hash_text = str(username + password)
                        encrypted_hash_text = encrypt_key(hash_text, salt)
                        cached_hash_text = get_cache(b64encode(encrypted_hash_text))

                        if cached_hash_text:
                            self.log.debug('This authentication is using cached user')
                            pswd = Usuario.encode_password(password)
                            return Usuario.objects.prefetch_related('grupos').get(user=username, pwd=pswd, ativo=1)

                        else:
                            set_cache(b64encode(encrypted_hash_text), True, int(get_value('time_cache_user')))
                            self.log.debug('The user was cached successfully!')

                    else:
                        salt_key = generate_key()
                        set_cache('salt_key', salt_key, int(get_value('time_cache_salt_key')))
                        self.log.debug('The encrypt token was generated and cached successfully!')

            except Exception as ERROR:
                self.log.error(ERROR)

            # AuthAPI authentication
            try:
                use_authapi = convert_string_or_int_to_boolean(get_value('use_authapi'))

                if use_authapi:

                    pswd_authapi = Usuario.encode_password(password)
                    user = Usuario.objects.prefetch_related('grupos').get(user=username, pwd=pswd_authapi, ativo=1)

                    authapi_info = dict(
                        mail=user.email,
                        password=password,
                        src=socket.gethostbyname(socket.gethostname())
                    )

                    endpoint_ssl_cert = get_value('endpoint_ssl_cert')
                    ssl_cert = requests.get(endpoint_ssl_cert)

                    if ssl_cert.status_code == 200:

                        cert = tempfile.NamedTemporaryFile(delete=False)
                        cert.write(ssl_cert.text)
                        cert.close()

                        response = requests.post(get_value('authapi_url'), json=authapi_info, verify=cert.name)

                        os.unlink(cert.name)

                        if response.status_code == 200:
                            return user
                            self.log.debug('This authentication uses AuthAPI for user \'%s\'' % username)
                        else:
                            self.log.debug('Error getting user from AuthAPI. Trying authentication with LDAP')

                    else:
                        self.log.debug('Error getting SSL certificate from \'%s\'' % endpoint_ssl_cert)

            except Exception as ERROR:
                self.log.error(ERROR)

            try:
                use_ldap = convert_string_or_int_to_boolean(
                    get_value('use_ldap'))
                if use_ldap:
                    ldap_param = get_value('ldap_config')
                    ldap_server = get_value('ldap_server')
                    return_user = self.get_by_ldap_user(username, True)
                else:
                    bypass = 1
            except exceptions.VariableDoesNotExistException, e:
                self.log.error(
                    'Error getting LDAP config variables (use_ldap). Trying local authentication')
                bypass = 1
            except UsuarioNotFoundError, e:
                self.log.debug(
                    "Using local authentication for user \'%s\'" % username)
                bypass = 1

            # local auth
            if bypass:
                password = Usuario.encode_password(password)
                return Usuario.objects.prefetch_related('grupos').get(user=username, pwd=password, ativo=1)

            # ldap auth
            try:
                connect = ldap.open(ldap_server)
                user_dn = 'cn=' + username + ',' + ldap_param
                connect.simple_bind_s(user_dn, password)
                return return_user
            except ldap.INVALID_CREDENTIALS, e:
                self.log.error('LDAP authentication error %s' % e)
            except exceptions.VariableDoesNotExistException, e:
                self.log.error(
                    'Error getting LDAP config variables (ldap_server, ldap_param).')

        except ObjectDoesNotExist:
            self.log.error(u'Usuário não autenticado ou inativo: %s', username)
        except MultipleObjectsReturned:
            self.log.error(
                u'Múltiplos usuários encontrados com o mesmo login e senha: %s', username)
        except Exception, e:
            self.log.error(u'Falha ao pesquisar o usuário.')
            raise UsuarioError(e, u'Falha ao pesquisar o usuário.')
        return None


class UsuarioGrupo(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_usuarios_do_grupo')
    usuario = models.ForeignKey(Usuario, db_column='id_user')
    ugrupo = models.ForeignKey('grupo.UGrupo', db_column='id_grupo')

    log = logging.getLogger('UsuarioGrupo')

    class Meta(BaseModel.Meta):
        db_table = u'usuarios_do_grupo'
        managed = True
        unique_together = ('usuario', 'ugrupo')

    @classmethod
    def list_by_user_id(cls, user_id):
        """"Get UserGroup by user.

        @return: UserGroup.

        @raise UsuarioNotFoundError: UserGroup is not registered.
        @raise UsuarioError: Failed to search for the UserGroup.
        """
        try:
            return UsuarioGrupo.objects.filter(usuario__id=user_id)
        except ObjectDoesNotExist, e:
            raise UsuarioNotFoundError(
                e, u'Dont there is a UserGroup by user = %s.' % user_id)
        except Exception, e:
            cls.log.error(u'Failure to search the UserGroup.')
            raise UsuarioError(e, u'Failure to search the UserGroup.')

    @classmethod
    def get_by_user_group(cls, user_id, group_id):
        """"Get UserGroup by user and Group.

        @return: UserGroup.

        @raise UserGroupNotFoundError: UserGroup is not registered.
        @raise UsuarioError: Failed to search for the UserGroup.
        """
        try:
            return UsuarioGrupo.objects.get(usuario__id=user_id, ugrupo__id=group_id)
        except ObjectDoesNotExist, e:
            raise UserGroupNotFoundError(
                e, u'Dont there is a UserGroup by user = %s and group = %s.' % (user_id, group_id))
        except Exception, e:
            cls.log.error(u'Failure to search the UserGroup.')
            raise UsuarioError(e, u'Failure to search the UserGroup.')
