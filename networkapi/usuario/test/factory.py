# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import factory
import datetime

from .. import models

class UGrupoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.UGrupo

    nome = factory.Sequence(lambda n: 'grupo-{0}'.format(n))
    leitura = 'S'
    escrita = 'S'
    edicao = 'S'
    exclusao = 'S'

class UsuarioFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Usuario

    user = factory.Sequence(lambda n: 'user-{0}'.format(n))
    pwd = factory.Sequence(lambda n: 'user-{0}-pwd'.format(n))
    nome = factory.Sequence(lambda n: 'user-{0}-nome'.format(n))
    ativo = True
    email = factory.Sequence(lambda n: 'user-{0}@email.com'.format(n))
    user_ldap = factory.Sequence(lambda n: 'user-{0}-ldap'.format(n))

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