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
import logging

from django.db import models


class SemaforoError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com semaforo."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class Semaforo(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_semaforo')
    descricao = models.CharField(max_length=50)

    log = logging.getLogger('Semaforo')

    CRIAR_IP_ID = 1
    ALOCAR_VLAN_ID = 2
    PROVISIONAR_GRUPO_VIRTUAL_ID = 3

    class Meta:
        db_table = u'semaforo'
        managed = False

    @classmethod
    def lock(cls, id):
        try:
            semaforo = Semaforo.objects.get(pk=id)
            semaforo.descricao = semaforo.descricao
            semaforo.save()
        except Exception, e:
            cls.log.error(
                u'Falha ao realizar o lock para o identificador %s.' % id)
            raise SemaforoError(
                e, u'Falha ao realizar o lock para o identificador %s.' % id)
