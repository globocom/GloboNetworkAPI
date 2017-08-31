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

import ast
import logging
from rest_framework import serializers
from networkapi.rack.models import Rack, Datacenter, DatacenterRooms

log = logging.getLogger(__name__)


class RackSerializer(serializers.ModelSerializer):


    id_sw1 = serializers.RelatedField(source='id_sw1.nome')
    id_sw2 = serializers.RelatedField(source='id_sw2.nome')
    id_ilo = serializers.RelatedField(source='id_ilo.nome')

    class Meta:
        model = Rack
        fields = ('id',
                  'nome',
                  'numero',
                  'mac_sw1',
                  'mac_sw2',
                  'mac_ilo',
                  'id_sw1',
                  'id_sw2',
                  'id_ilo',
                  'config',
                  'create_vlan_amb',
                  'dcroom'
                  )

class DCSerializer(serializers.ModelSerializer):

    class Meta:
        model = Datacenter
        fields = ('id',
                  'dcname',
                  'address'
                  )

class DCRoomSerializer(serializers.ModelSerializer):

    config = serializers.SerializerMethodField('get_config')


    def get_config(self, obj):
        if obj.config:
            try:
                config = ast.literal_eval(obj.config)
                return config
            except:
                return obj.config
        return []

    class Meta:
        model = DatacenterRooms
        fields = ('id',
                  'name',
                  'dc',
                  'racks',
                  'spines',
                  'leafs',
                  'config'
                  )