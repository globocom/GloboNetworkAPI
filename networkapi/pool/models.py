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

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from networkapi.log import Log

from networkapi.models.BaseModel import BaseModel

from networkapi.distributedlock import distributedlock, LOCK_SCRIPT


class PoolError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com Roteiro."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class PoolNotFoundError(PoolError):

    """Retorna exceção para pesquisa de Roteiro."""

    def __init__(self, cause, message=None):
        PoolError.__init__(self, cause, message)


class ServerPool(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_server_pool')
    identifier = models.CharField(max_length=200, blank=True)
    default_port = models.IntegerField(max_length=10)

    log = Log('ServerPool')

    class Meta(BaseModel.Meta):
        db_table = u'server_pool'
        managed = True

    @classmethod
    def get_by_pk(cls, idt):
        """"Get Script by id.

        @return: Script.

        @raise RoteiroNotFoundError: Script is not registered.
        @raise PoolError: Failed to search for the Script.
        """
        try:
            return ServerPool.objects.filter(id=idt).uniqueResult()
        except ObjectDoesNotExist, e:
            raise PoolNotFoundError(
                e, u'Dont there is a Pool by pk = %s.' % idt)
        except Exception, e:
            cls.log.error(u'Failure to search the Pool.')
            raise PoolError(e, u'Failure to search the Pool.')