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
import logging
from networkapi.models.BaseModel import BaseModel
from networkapi.equipamento.models import Equipamento


class Rack(BaseModel):

    log = logging.getLogger('Rack')

    id = models.AutoField(primary_key=True, db_column='id_rack')
    numero = models.IntegerField(unique=True)
    nome = models.CharField(max_length=4, unique=True)
    mac_sw1 = models.CharField(max_length=17, blank=True, null=True, db_column='mac_sw1')
    mac_sw2 = models.CharField(max_length=17, blank=True, null=True, db_column='mac_sw2')
    mac_ilo = models.CharField(max_length=17, blank=True, null=True, db_column='mac_ilo')
    id_sw1 = models.ForeignKey(Equipamento, blank=True, null=True, db_column='id_equip1', related_name='equipamento_sw1')
    id_sw2 = models.ForeignKey(Equipamento, blank=True, null=True, db_column='id_equip2', related_name='equipamento_sw2')
    id_ilo = models.ForeignKey(Equipamento, blank=True, null=True, db_column='id_equip3', related_name='equipamento_ilo')
    config = models.BooleanField(default=False)
    create_vlan_amb = models.BooleanField(default=False)


    class Meta(BaseModel.Meta):
        db_table = u'racks'
        managed = True