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

from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_SCRIPT
from networkapi.models.BaseModel import BaseModel


class RoteiroError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com Roteiro."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class RoteiroNotFoundError(RoteiroError):

    """Retorna exceção para pesquisa de Roteiro."""

    def __init__(self, cause, message=None):
        RoteiroError.__init__(self, cause, message)


class TipoRoteiroNotFoundError(RoteiroError):

    """Retorna exceção para pesquisa de TipoRoteiro."""

    def __init__(self, cause, message=None):
        RoteiroError.__init__(self, cause, message)


class TipoRoteiroNameDuplicatedError(RoteiroError):

    """Retorna exceção porque já existe um TipoRoteiro cadastrado com o mesmo nome."""

    def __init__(self, cause, message=None):
        RoteiroError.__init__(self, cause, message)


class RoteiroNameDuplicatedError(RoteiroError):

    """Retorna exceção porque já existe um roteiro cadastrado com o mesmo nome."""

    def __init__(self, cause, message=None):
        RoteiroError.__init__(self, cause, message)


class RoteiroHasEquipamentoError(RoteiroError):

    """Retorna exceção porque existe equipamento associado ao roteiro."""

    def __init__(self, cause, message=None):
        RoteiroError.__init__(self, cause, message)


class TipoRoteiroHasRoteiroError(RoteiroError):

    """Retorna exceção porque existe roteiro associado ao tipo de roteiro."""

    def __init__(self, cause, message=None):
        RoteiroError.__init__(self, cause, message)


class TipoRoteiro(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_tipo_roteiro')
    tipo = models.CharField(unique=True, max_length=40, blank=True)
    descricao = models.CharField(max_length=100, blank=True)

    log = logging.getLogger('TipoRoteiro')

    class Meta(BaseModel.Meta):
        db_table = u'tipo_roteiro'
        managed = True

    @classmethod
    def get_by_pk(cls, idt):
        """"Get Script Type by id.

        @return: Script Type.

        @raise TipoRoteiroNotFoundError: Script Type is not registered.
        @raise RoteiroError: Failed to search for the Script Type.
        """
        try:
            return TipoRoteiro.objects.filter(id=idt).uniqueResult()
        except ObjectDoesNotExist, e:
            raise TipoRoteiroNotFoundError(
                e, u'Dont there is a Script Type by pk = %s.' % idt)
        except Exception, e:
            cls.log.error(u'Failure to search the Script Type.')
            raise RoteiroError(e, u'Failure to search the Script Type.')

    @classmethod
    def get_by_name(cls, name):
        """"Get Script Type by name.

        @return: Script Type.

        @raise AmbienteLogicoNotFoundError: Script Type is not registered.
        @raise AmbienteError: Failed to search for the Script Type.
        """
        try:
            return TipoRoteiro.objects.get(tipo__iexact=name)
        except ObjectDoesNotExist, e:
            raise TipoRoteiroNotFoundError(
                e, u'Dont there is a Script Type by name = %s.' % name)
        except Exception, e:
            cls.log.error(u'Failure to search the Script Type.')
            raise RoteiroError(e, u'Failure to search the Script Type.')


class Roteiro(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_roteiros')
    roteiro = models.CharField(max_length=50)
    tipo_roteiro = models.ForeignKey(TipoRoteiro, db_column='id_tipo_roteiro')
    descricao = models.CharField(max_length=100, blank=True)

    log = logging.getLogger('Roteiro')

    class Meta(BaseModel.Meta):
        db_table = u'roteiros'
        managed = True

    @classmethod
    def get_by_pk(cls, idt):
        """"Get Script by id.

        @return: Script.

        @raise RoteiroNotFoundError: Script is not registered.
        @raise RoteiroError: Failed to search for the Script.
        """
        try:
            return Roteiro.objects.filter(id=idt).uniqueResult()
        except ObjectDoesNotExist, e:
            raise RoteiroNotFoundError(
                e, u'Dont there is a Script by pk = %s.' % idt)
        except Exception, e:
            cls.log.error(u'Failure to search the Script.')
            raise RoteiroError(e, u'Failure to search the Script.')

    @classmethod
    def get_by_name(cls, name):
        """"Get Script by Name.

        @return: Script.

        @raise RoteiroNotFoundError: Script is not registered.
        @raise RoteiroError: Failed to search for the Script.
        """
        try:
            return Roteiro.objects.get(roteiro__iexact=name)
        except ObjectDoesNotExist, e:
            raise RoteiroNotFoundError(
                e, u'Dont there is a Script by name = %s.' % name)
        except Exception, e:
            cls.log.error(u'Failure to search the Script.')
            raise RoteiroError(e, u'Failure to search the Script.')

    @classmethod
    def get_by_name_script(cls, name, id_script_type):
        """"Get Script by Name and Script Type.

        @return: Script.

        @raise RoteiroNotFoundError: Script is not registered.
        @raise RoteiroError: Failed to search for the Script.
        """
        try:
            return Roteiro.objects.get(roteiro__iexact=name, tipo_roteiro__id=id_script_type)
        except ObjectDoesNotExist, e:
            raise RoteiroNotFoundError(
                e, u'Dont there is a Script by name = %s and Script Type = %s.' % (name, id_script_type))
        except Exception, e:
            cls.log.error(u'Failure to search the Script.')
            raise RoteiroError(e, u'Failure to search the Script.')
