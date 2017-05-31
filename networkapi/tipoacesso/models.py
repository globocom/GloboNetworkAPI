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

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_TYPE_ACCESS
from networkapi.models.BaseModel import BaseModel


class TipoAcessoError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com Tipo de Acesso."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class DuplicateProtocolError(TipoAcessoError):

    """Retorna exceção se houver tentativa de gravação de tipo de acesso com protocolo duplicado."""

    def __init__(self, cause, message=None):
        TipoAcessoError.__init__(self, cause, message)


class AccessTypeUsedByEquipmentError(TipoAcessoError):

    """Retorna exceção se houver tentativa de exclusão de tipo de acesso utilizado por algum equipamento."""

    def __init__(self, cause, message=None):
        TipoAcessoError.__init__(self, cause, message)


class AccessTypeNotFoundError(TipoAcessoError):

    """Retorna exceção para pesquisa de tipo de acesso por chave primária."""

    def __init__(self, cause, message=None):
        TipoAcessoError.__init__(self, cause, message)


class TipoAcesso(BaseModel):

    """Classe que representa a entidade Tipo de Acesso (tabela tipo_acesso)"""

    id = models.AutoField(primary_key=True, db_column='id_tipo_acesso')
    protocolo = models.CharField(unique=True, max_length=45)

    log = logging.getLogger('TipoAcesso')

    class Meta(BaseModel.Meta):
        db_table = u'tipo_acesso'
        managed = True

    @classmethod
    def get_by_pk(cls, pk):
        try:
            return TipoAcesso.objects.get(pk=pk)
        except ObjectDoesNotExist, e:
            raise AccessTypeNotFoundError(
                e, u'Não existe um tipo de acesso com a pk = %s.' % pk)
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar o tipo de acesso.')
            raise TipoAcessoError(e, u'Falha ao pesquisar o tipo de acesso.')
