# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

import factory

from networkapi.grupo.tests.factory import UGrupoFactory
from networkapi.usuario import models

LOG = logging.getLogger(__name__)


class UsuarioFactory(factory.DjangoModelFactory):

    """
    usr = Usuario()

    # set variables
    usr.user = username
    usr.pwd = hashlib.md5(password).hexdigest()
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
    """

    # class Meta:
    #     model = models.Usuario
    FACTORY_FOR = models.Usuario

    user = factory.Sequence(lambda n: 'user-{0}'.format(n))
    pwd = factory.Sequence(lambda n: 'user-{0}-pwd'.format(n))
    nome = factory.Sequence(lambda n: 'user-{0}-nome'.format(n))
    ativo = True
    email = factory.Sequence(lambda n: 'user-{0}@email.com'.format(n))
    user_ldap = None


class UsuarioGrupoFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = models.UsuarioGrupo

    usuario = factory.SubFactory(UsuarioFactory)
    ugrupo = factory.SubFactory(UGrupoFactory)


class UserWithGroupFactory(UsuarioFactory):
    group = factory.RelatedFactory(UsuarioGrupoFactory, 'usuario')
