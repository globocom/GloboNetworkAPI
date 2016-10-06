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
# -*- coding:utf-8 -*-
from rest_framework import serializers

from networkapi.api_environment.serializers import EnvironmentV3Serializer
from networkapi.util.serializers import DynamicFieldsModelSerializer
from networkapi.vlan.models import Vlan


class VlanSerializerV3(DynamicFieldsModelSerializer):
    name = serializers.Field(source='nome')
    description = serializers.Field(source='descricao')
    active = serializers.Field(source='ativada')
    environment = serializers.SerializerMethodField('get_environment')

    class Meta:
        model = Vlan
        fields = (
            'id',
            'name',
            'num_vlan',
            'environment',
            'description',
            'acl_file_name',
            'acl_valida',
            'acl_file_name_v6',
            'acl_valida_v6',
            'active',
            'vrf',
            'acl_draft',
            'acl_draft_v6',
        )
        default_fields = (
            'id',
            'name',
            'num_vlan',
            'environment',
            'description',
            'acl_file_name',
            'acl_valida',
            'acl_file_name_v6',
            'acl_valida_v6',
            'active',
            'vrf',
            'acl_draft',
            'acl_draft_v6',
        )

    def get_environment(self, obj):
        return self.extends_serializer(obj.ambiente, 'environment')

    @staticmethod
    def get_mapping_eager_loading(self):
        mapping = {}

        return mapping

    @classmethod
    def get_serializers(cls):
        if not cls.mapping:
            cls.mapping = {
                'environment': {
                    'serializer': EnvironmentV3Serializer,
                    'kwargs': {
                        'source': 'id'
                    }
                },
                'environment__details': {
                    'serializer': EnvironmentV3Serializer,
                    'kwargs': {
                        'include': ('configs',)
                    }
                }
            }

        return cls.mapping
