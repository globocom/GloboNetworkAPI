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

from networkapi.models.BaseModel import BaseModel


class Configuration(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_config')
    IPv4_MIN = models.SmallIntegerField(db_column='ip_v4_min')
    IPv4_MAX = models.SmallIntegerField(db_column='ip_v4_max')
    IPv6_MIN = models.SmallIntegerField(db_column='ip_v6_min')
    IPv6_MAX = models.SmallIntegerField(db_column='ip_v6_max')

    log = logging.getLogger('Configuration')

    class Meta(BaseModel.Meta):
        db_table = u'config'
        managed = True

    @classmethod
    def get(cls):
        return Configuration.objects.all()[0]
