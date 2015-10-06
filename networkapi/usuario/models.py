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
import hashlib
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import logging
from networkapi.models.BaseModel import BaseModel
from networkapi.distributedlock import distributedlock, LOCK_USER_GROUP


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
        """"Get User by ldap username.

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
        '''
        Busca o usuário de acordo com o login e a senha.

        Retorna apenas usuário ativo.
        '''
        try:
            password = Usuario.encode_password(password)
            return Usuario.objects.prefetch_related('grupos').get(user=username, pwd=password, ativo=1)
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
    def list_by_user_id(self, user_id):
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
            self.log.error(u'Failure to search the UserGroup.')
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
