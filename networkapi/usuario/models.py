# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
import hashlib
from django.db import models
from networkapi.grupo.models import UGrupo
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from networkapi.log import Log
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
    grupos = models.ManyToManyField(UGrupo, through='UsuarioGrupo')
    user_ldap = models.CharField(
        unique=True,
        max_length=45,
        null=True,
        blank=True)

    log = Log('Usuario')

    class Meta(BaseModel.Meta):
        db_table = u'usuarios'
        managed = True

    @classmethod
    def get_by_pk(cls, pk):
        """"Get  User by pk.

        @return: User.

        @raise UsuarioNotFoundError: User is not registered.
        @raise UsuarioError: Failed to search for the User.
        """
        try:
            return Usuario.objects.get(pk=pk)
        except ObjectDoesNotExist as e:
            raise UsuarioNotFoundError(
                e,
                u'Dont there is a Group L3 by pk = %s.' %
                pk)
        except Exception as e:
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
        except ObjectDoesNotExist as e:
            raise UsuarioNotFoundError(
                e,
                u'There is no User with username = %s.' %
                name)
        except Exception as e:
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
                return Usuario.objects.get(user_ldap__iexact=ldap_usr, ativo=1)
            else:
                return Usuario.objects.get(user_ldap__iexact=ldap_usr)
        except ObjectDoesNotExist as e:
            raise UsuarioNotFoundError(
                e,
                u'There is no User with ldap_user = %s.' %
                ldap_usr)
        except Exception as e:
            cls.log.error(u'Failure to search the User.')
            raise UsuarioError(e, u'Failure to search the User.')

    def get_enabled_user(self, username, password):
        '''
        Busca o usuário de acordo com o login e a senha.

        Retorna apenas usuário ativo.
        '''
        try:
            password = hashlib.md5(password).hexdigest()
            return Usuario.objects.get(user=username, pwd=password, ativo=1)
        except ObjectDoesNotExist:
            self.log.error(u'Usuário não autenticado ou inativo: %s', username)
        except MultipleObjectsReturned:
            self.log.error(
                u'Múltiplos usuários encontrados com o mesmo login e senha: %s',
                username)
        except Exception as e:
            self.log.error(u'Falha ao pesquisar o usuário.')
            raise UsuarioError(e, u'Falha ao pesquisar o usuário.')
        return None


class UsuarioGrupo(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_usuarios_do_grupo')
    usuario = models.ForeignKey(Usuario, db_column='id_user')
    ugrupo = models.ForeignKey(UGrupo, db_column='id_grupo')

    log = Log('UsuarioGrupo')

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
        except ObjectDoesNotExist as e:
            raise UsuarioNotFoundError(
                e,
                u'Dont there is a UserGroup by user = %s.' %
                user_id)
        except Exception as e:
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
            return UsuarioGrupo.objects.get(
                usuario__id=user_id,
                ugrupo__id=group_id)
        except ObjectDoesNotExist as e:
            raise UserGroupNotFoundError(
                e, u'Dont there is a UserGroup by user = %s and group = %s.' %
                (user_id, group_id))
        except Exception as e:
            cls.log.error(u'Failure to search the UserGroup.')
            raise UsuarioError(e, u'Failure to search the UserGroup.')
