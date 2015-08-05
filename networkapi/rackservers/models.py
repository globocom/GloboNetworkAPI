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
from networkapi.log import Log
from networkapi.models.BaseModel import BaseModel
from networkapi.equipamento.models import Equipamento
from networkapi.ambiente.models import Ambiente
from networkapi.rack.models import Rack

class RackServersError(Exception):

    """Representa um erro ocorrido durante acesso a  tabela rackservers."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)

        return msg.encode('utf-8', 'replace')


class ServerType(BaseModel):

    log = Log('ServerType')

    id = models.AutoField(primary_key=True, db_column='id_tipo')
    nome = models.CharField(max_length=20, unique=True)

    class Meta(BaseModel.Meta):
        db_table = u'tiposervidor'
        managed = True


class RackServers(BaseModel):

    log = Log('RackServers')

    id = models.AutoField(primary_key=True, db_column='id_rackservers')
    id_equip = models.ForeignKey(Equipamento, blank=True, null=True, db_column='id_equip')
    id_rack = models.ForeignKey(Rack, blank=True, null=True, db_column='id_rack')
    id_tipo = models.ForeignKey(ServerType, blank=True, null=True, db_column='id_tipo')
    id_ambiente = models.ForeignKey(Ambiente, blank=True, null=True, db_column='id_ambiente')


    class Meta(BaseModel.Meta):
        db_table = u'racksservers'
        managed = True


    def inserir (self, authenticated_user):

        try:
            return self.save(authenticated_user)
        except Exception, e:
            self.log.error(u'Falha ao inserir o Servidor.')
            raise RackServersError(e, u'Falha ao inserir o Servidor.')
