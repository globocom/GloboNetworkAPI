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
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from networkapi.log import Log
from networkapi.semaforo.model import Semaforo
from networkapi.models.BaseModel import BaseModel
from _mysql_exceptions import OperationalError
from networkapi.infrastructure.ipaddr import IPNetwork
from networkapi.util import clone
from networkapi.filter.models import verify_subnet_and_equip
from networkapi.equipamento.models import Equipamento

class RackError(Exception):

    """Representa um erro ocorrido durante acesso ?|  tabela racks."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')

class InvalidMacValueError(RackError):

    """Retorna exceção quando o valor da variávmac é inválido."""

    def __init__(self, cause, message=None):
        RackError.__init__(self, cause, message)

class RackNumberDuplicatedValueError(RackError):

    """Retorna exceção quando numero do rack for repetido."""

    def __init__(self, cause, message=None):
        RackError.__init__(self, cause, message)

class RackNameDuplicatedError(RackError):

    """Retorna exceção quando numero do rack for repetido."""

    def __init__(self, cause, message=None):
        RackError.__init__(self, cause, message)

class RackNumberNotFoundError(RackError):

    """Retorna exceção quando rack nao for encontrado."""

    def __init__(self, cause, message=None):
        RackError.__init__(self, cause, message)

class RackConfigError(Exception):

    """Retorna exceção quao a configuracao nao for criada."""

    def __init__(self, cause, param=None, value=None):
        self.cause = cause
        self.param = param
        self.value = value

class RackAplError(Exception):

    """Retorna exceção quao a configuracao nao pode ser aplicada."""

    def __init__(self, cause, param=None, value=None):
        self.cause = cause
        self.param = param
        self.value = value


class Rack(BaseModel):

    log = Log('Rack')

    id = models.AutoField(primary_key=True, db_column='id_rack')
    numero = models.IntegerField(unique=True)
    nome = models.CharField(max_length=4, unique=True)
    mac_sw1 = models.CharField(max_length=17, blank=True, null=True)
    mac_sw2 = models.CharField(max_length=17, blank=True, null=True)
    mac_ilo = models.CharField(max_length=17, blank=True, null=True)
    id_sw1 = models.ForeignKey(Equipamento, blank=True, null=True, db_column='id_equip1', related_name='equipamento_sw1')
    id_sw2 = models.ForeignKey(Equipamento, blank=True, null=True, db_column='id_equip2', related_name='equipamento_sw2')
    id_ilo = models.ForeignKey(Equipamento, blank=True, null=True, db_column='id_equip3', related_name='equipamento_ilo')
    config = models.BooleanField(default=False)
    create_vlan_amb = models.BooleanField(default=False)


    class Meta(BaseModel.Meta):
        db_table = u'racks'
        managed = True

    def get_by_pk(cls, idt):
        """"Get  Rack id.

        @return: Rack.

        @raise RackNumberNotFoundError: Rack is not registered.
        @raise RackError: Failed to search for the Rack.
        """
        try:
            return Rack.objects.filter(id=idt).uniqueResult()
        except ObjectDoesNotExist, e:
            raise RackNumberNotFoundError(e, u'Dont there is a Rack by pk = %s.' % idt)
        except Exception, e:
            cls.log.error(u'Failure to search the Rack.')
            raise RackError(e, u'Failure to search the Rack.') 


    def get_by_id(cls, number):
        """"Get  Rack number.

        @return: Rack.

        @raise RackNumberNotFoundError: Rack is not registered.
        @raise RackError: Failed to search for the Rack.
        """
        try:
            return Rack.objects.get(numero__iexact=number)
        except ObjectDoesNotExist, e:
            raise RackNumberNotFoundError(e, u'Dont there is a Rack by pk = %s.' % idt)
        except Exception, e:
            cls.log.error(u'Failure to search the Rack.')
            raise RackError(e, u'Failure to search the Rack.')

    def insert_new(self, authenticated_user):
        try:
            Rack.objects.get(numero__iexact=self.numero)
            raise RackNumberDuplicatedValueError(
                None, u'Numero de Rack %s ja existe.' % (self.numero))
        except ObjectDoesNotExist, e:
            pass
        
        try:
            Rack.objects.get(nome__iexact=self.nome)
            raise RackNameDuplicatedError(
                None, u'Nome %s ja existe.' % (self.nome))
        except ObjectDoesNotExist, e:
            pass

        try:
            return self.save(authenticated_user)
        except Exception, e:
            self.log.error(u'Falha ao inserir Rack.')
            raise RackError(e, u'Falha ao inserir Rack.')



class Tipo_Config(BaseModel):

    log = Log('Tipo_Config')

    id = models.AutoField(primary_key=True, db_column='id_tipo_config')
    tipo_equip = models.CharField(max_length=20)

    class Meta(BaseModel.Meta):
        db_table = u'tipo_config'
        managed = True
