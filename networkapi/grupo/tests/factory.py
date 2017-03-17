# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

import factory

LOG = logging.getLogger(__name__)

from networkapi.grupo import models


class UGrupoFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.UGrupo

    nome = factory.Sequence(lambda n: 'grupo-{0}'.format(n))
    leitura = 'S'
    escrita = 'S'
    edicao = 'S'
    exclusao = 'S'
