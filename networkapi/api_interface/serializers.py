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

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class InterfaceTypeSerializer(DynamicFieldsModelSerializer):

    log.info("InterfaceTypeV3Serializer")

    type = serializers.RelatedField(source='tipo')

    class Meta:
        model = get_model('interface', 'TipoInterface')
        fields = (
            'id',
            'type',
        )

        default_fields = fields

        basic_fields = fields

        details_fields = fields


class PortChannelSerializer(DynamicFieldsModelSerializer):

    log.info("PortChannelV3Serializer")

    name = serializers.RelatedField(source='nome')

    class Meta:
        model = get_model('interface', 'PortChannel')

        fields = (
            'id',
            'name',
            'lacp',
        )

        default_fields = fields

        basic_fields = (
            'id',
            'name',
        )

        details_fields = fields


class InterfaceV3Serializer(DynamicFieldsModelSerializer):

    log.info("InterfaceV3Serializer")

    protected = serializers.Field(source='protegida')
    description = serializers.Field(source='descricao')
    native_vlan = serializers.Field(source='vlan_nativa')

    equipamento = serializers.SerializerMethodField('get_equipment')
    tipo = serializers.SerializerMethodField('get_interface_type')
    channel = serializers.SerializerMethodField('get_channel')
    ligacao_front = serializers.SerializerMethodField('get_front_interface')
    ligacao_back = serializers.SerializerMethodField('get_back_interface')

    def get_interface_type(self, obj):
        return self.extends_serializer(obj, 'tipo')

    def get_channel(self, obj):
        return self.extends_serializer(obj, 'channel')

    def get_front_interface(self, obj):
        return self.extends_serializer(obj, 'ligacao_front')

    def get_back_interface(self, obj):
        return self.extends_serializer(obj, 'ligacao_back')

    def get_equipment(self, obj):
        return self.extends_serializer(obj, 'equipamento')

    class Meta:
        interface_model = get_app('interface', module_label='models')
        model = interface_model.Interface
        fields = (
            'id',
            'interface',
            'protected',
            'description',
            'equipamento',
            'description',
            'native_vlan',
            'tipo',
            'channel',
            'ligacao_front',
            'ligacao_back',
        )

        default_fields = fields

        basic_fields = (
            'id',
            'interface',
            'equipamento',
            'channel',
        )

        details_fields = fields

    def get_serializers(self):
        """Returns the mapping of serializers."""

        equipment_serializers = get_app('api_equipment', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'tipo__details': {
                    'serializer': InterfaceTypeSerializer,
                    'kwargs': {
                        'kind': 'details',
                    },
                    'obj': 'tipo'
                },
                'channel': {
                    'obj': 'channel_id'
                },
                'channel__basic': {
                    'serializer': PortChannelSerializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'channel',
                },
                'ligacao_front__basic': {
                    'serializer': InterfaceV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'ligacao_front',
                },
                'ligacao_front__details': {
                    'serializer': InterfaceV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'ligacao_front',
                },
                'ligacao_back__basic': {
                    'serializer': InterfaceV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'ligacao_back',
                },
                'ligacao_back__details': {
                    'serializer': InterfaceV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'ligacao_back',
                },
                'equipamento': {
                    'obj': 'equipamento_id'
                },
                'equipamento__basic': {
                    'serializer': equipment_serializers.EquipmentV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'equipamento',
                },
                'equipamento__details': {
                    'serializer': equipment_serializers.EquipmentV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'equipamento',
                },
            }

    @staticmethod
    def setup_eager_loading_channel(queryset):
        log.info('Using setup_eager_loading_channel')
        queryset = queryset.select_related('channel')
        return queryset
