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


class CacheUser(object):

    log = logging.getLogger('CacheUser')

    def _generate_salt_key(self):
        """"Generate salt_key for encrypt process in cache user.
        @return: salt_key.
        @raise VariableDoesNotExistException: time_cache_salt_key is not registered.
        @raise Exception: Any different errors catch.
        """
        try:
            salt = get_cache('salt_key')

            if not salt:
                salt_key = generate_key()
                set_cache('salt_key', salt_key, int(get_value('time_cache_salt_key')))
                self.log.debug('The encrypt token was generated and cached successfully!')
                return salt_key

            return salt

        except exceptions.VariableDoesNotExistException:
            self.log.error(u'Error getting time_cache_salt_key variable.')
        except Exception as ERROR:
            self.log.error(ERROR)

    def _mount_hash(self, username, password):
        """"Generate hash of username + password, then encrypt it for caching.
        @return: hash encrypted.
        @raise Exception: Any different errors catch.
        """
        try:
            salt = self._generate_salt_key()

            if salt:
                self.log.debug('The encrypt key was taken successfully!')
                hash_text = str(username + password)
                encrypted_hash_text = encrypt_key(hash_text, salt)
                self.log.debug('The encrypted_hash_text was generate successfully!')

                return encrypted_hash_text

            else:
                self.log.error('Problems to take salt_key')

        except Exception as ERROR:
            self.log.error(u'Error on mount hash for cache user: %s' % ERROR)

    def get(self, username, password):
        """"Get the cached user.
        @return: Hash of user cached.
        @raise Exception: Any different errors catch.
        """
        try:
            encrypted_hash_text = self._mount_hash(username, password)

            if encrypted_hash_text:
                self.log.debug('The encrypted_hash_text was taken successfully!')
                cached_hash_text = get_cache(b64encode(encrypted_hash_text))

                return cached_hash_text

            else:
                self.log.error('Problems to take encrypted_hash_text')

        except Exception as ERROR:
            self.log.error(u'Error on get cached user: %s' % ERROR)

    def set(self, username, password):
        """"Set the cached user.
        @raise VariableDoesNotExistException: time_cache_user is not registered.
        @raise Exception: Any different errors catch.
        """
        try:
            encrypted_hash_text = self._mount_hash(username, password)

            if encrypted_hash_text:
                set_cache(b64encode(encrypted_hash_text), True, int(get_value('time_cache_user')))
                self.log.debug('The user was cached successfully!')

            else:
                self.log.error('Problems to take encrypted_hash_text')

        except exceptions.VariableDoesNotExistException:
            self.log.error(u'Error getting time_cache_user variable.')
        except Exception as ERROR:
            self.log.error(ERROR)


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

    cache_user = CacheUser()

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
    def get_by_authapi(cls, username, password):
        """"Get User in AuthAPI by username and password.
        @return: AuthAPI response.
        @raise UsuarioNotFoundError: User is not registered
        @raise VariableDoesNotExist: Feature Flag not found.
        @raise Exception: For any different problem found.
        """
        try:
            user = Usuario.objects.prefetch_related('grupos').get(user=username, ativo=1)
            authapi_info = dict(
                mail=user.email,
                password=password,
                src=socket.gethostbyname(socket.gethostname())
            )

            try:
                ssl_cert = open(get_value('path_ssl_cert'))

                try:
                    response = requests.post(get_value('authapi_url'), json=authapi_info, verify=ssl_cert.name)
                    ssl_cert.close()
                    return response

                except exceptions.VariableDoesNotExistException:
                    cls.log.error(u'Error getting authapi_url variable.')
                except Exception as ERROR:
                    raise Exception('Error uses AuthAPI. %s' % ERROR)

            except exceptions.VariableDoesNotExistException:
                cls.log.error(u'Error getting path_ssl_cert variable.')
            except Exception as ERROR:
                raise Exception('Error to get SSL certificate. %s' % ERROR)

        except ObjectDoesNotExist as ERROR:
            raise UsuarioNotFoundError(ERROR, u'There is no User with username = %s in AuthAPI.' % username)
        except Exception as ERROR:
            cls.log.error(u'Failure to search the User. Error: %s' % ERROR)

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
            # Cached User authentication
            try:
                if convert_string_or_int_to_boolean(get_value('use_cache_user')):
                    cached_hash_text = self.cache_user.get(username, password)

                    if cached_hash_text:
                        self.log.debug('This authentication is using cached user')
                        return Usuario.objects.prefetch_related('grupos').get(user=username, ativo=1)

                    else:
                        raise Exception('No cached user found with this credentials')

            except exceptions.VariableDoesNotExistException:
                self.log.error(
                    u'Error getting cache user variable. Trying AuthAPI authentication')
            except Exception as ERROR:
                self.log.error(u'Error to get cached user. %s. Trying AuthAPI authentication. ' % ERROR)

            # AuthAPI authentication
            try:
                if convert_string_or_int_to_boolean(get_value('use_authapi')):
                    response = self.get_by_authapi(username, password)

                    if response.status_code == 200:
                        self.log.debug('This authentication uses AuthAPI for user \'%s\'' % username)

                        try:
                            if convert_string_or_int_to_boolean(get_value('use_cache_user')):
                                self.cache_user.set(username, password)
                        except exceptions.VariableDoesNotExistException:
                            self.log.debug(u'User will not be cached because cached user is disabled')

                        return Usuario.objects.prefetch_related('grupos').get(user=username, ativo=1)

                    elif response.status_code == 400:
                        raise Exception('No user founds in AuthAPI with this credentials')

                    elif response.status_code == 500:
                        raise Exception('Error to connect with AuthAPI')

            except exceptions.VariableDoesNotExistException:
                self.log.error(
                    u'Error getting AuthAPI variable. Trying ldap authentication')
            except Exception as ERROR:
                self.log.error(u'Error to get user from AuthAPI. %s. Trying ldap authentication. ' % ERROR)

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

                try:
                    if convert_string_or_int_to_boolean(get_value('use_cache_user')):
                        self.cache_user.set(username, password)
                except exceptions.VariableDoesNotExistException:
                    self.log.debug(u'User will not be cached because cached user is disabled')

                password = Usuario.encode_password(password)
                return Usuario.objects.prefetch_related('grupos').get(user=username, pwd=password, ativo=1)

            # ldap auth
            try:
                connect = ldap.open(ldap_server)
                user_dn = 'cn=' + username + ',' + ldap_param
                connect.simple_bind_s(user_dn, password)

                try:
                    if convert_string_or_int_to_boolean(get_value('use_cache_user')):
                        self.cache_user.set(username, password)
                except exceptions.VariableDoesNotExistException:
                    self.log.debug(u'User will not be cached because cached user is disabled')

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
