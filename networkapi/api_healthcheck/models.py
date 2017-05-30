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

from networkapi.ambiente.models import Ambiente
from networkapi.models.BaseModel import BaseModel


class OpcaoPool(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_opcao_pool')
    description = models.CharField(blank=False, max_length=200)

    log = logging.getLogger('OpcaoPool')

    class Meta(BaseModel.Meta):
        db_table = u'opcoes_pool'
        managed = True


class OpcaoPoolAmbiente(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_opcao_pool_ambiente')
    opcao_pool = models.ForeignKey(OpcaoPool, db_column='id_opcao_pool')
    ambiente = models.ForeignKey(Ambiente, db_column='id_ambiente')

    log = logging.getLogger('OpcaoPoolAmbiente')

    class Meta(BaseModel.Meta):
        db_table = u'opcoes_pool_ambiente'
        managed = True
