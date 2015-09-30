# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import factory
import logging

LOG = logging.getLogger(__name__)

from networkapi.usuario import models

class UGrupoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.UGrupo

    nome = factory.Sequence(lambda n: 'grupo-{0}'.format(n))
    leitura = 'S'
    escrita = 'S'
    edicao = 'S'
    exclusao = 'S'

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
        usr.save(user)
    except Exception, e:
        self.log.error(u'Failed to save the user.')
        raise UsuarioError(e, u'Failed to save the user.')
    """
    FACTORY_FOR = models.Usuario

    user = factory.Sequence(lambda n: 'user-{0}'.format(n))
    pwd = factory.Sequence(lambda n: 'user-{0}-pwd'.format(n))
    nome = factory.Sequence(lambda n: 'user-{0}-nome'.format(n))
    ativo = True
    email = factory.Sequence(lambda n: 'user-{0}@email.com'.format(n))
    user_ldap = None

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        manager = cls._get_manager(target_class)

        if cls.FACTORY_DJANGO_GET_OR_CREATE:
            return cls._get_or_create(target_class, *args, **kwargs)

        usr = models.Usuario()

        # set variables
        usr.user = kwargs.get('user')
        usr.pwd = kwargs.get('pwd')
        usr.nome = kwargs.get('nome')
        usr.email = kwargs.get('email')
        usr.ativo = kwargs.get('ativo')
        usr.user_ldap = kwargs.get('user_ldap')

        try:
            # save User
            usr.save(None)
        except Exception, e:
            LOG.exception(u"Failed to save the user {0}.".format(usr))

    @factory.post_generation
    def grupos(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for grupo in extracted:
                self.grupos.add(grupo)
        else:
            self.grupos.add(UGrupoFactory())