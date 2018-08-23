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
            'lacp'
        )

        details_fields = fields


class InterfaceEnvironmentV3Serializer(DynamicFieldsModelSerializer):

    log.info("InterfaceEnvironmentV3Serializer")

    range_vlans = serializers.RelatedField(source='vlans')

    environment = serializers.SerializerMethodField('get_environment')
    interface = serializers.SerializerMethodField('get_interface')

    def get_interface(self, obj):
        return self.extends_serializer(obj, 'interface')

    def get_environment(self, obj):
        return self.extends_serializer(obj, 'environment')

    class Meta:
        model = get_model('interface', 'EnvironmentInterface')


        fields = (
            'id',
            'interface',
            'environment',
            'range_vlans',
        )

        default_fields = fields

        basic_fields = fields

        details_fields = fields

    def get_serializers(self):
        """Returns the mapping of serializers."""

        environment_serializers = get_app('api_environment', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'range_vlans': {
                    'obj': 'vlans'
                },
                'interface': {
                    'obj': 'interface_id'
                },
                'interface__basic': {
                    'serializer': InterfaceV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'interface',
                },
                'interface__details': {
                    'serializer': InterfaceV3Serializer,
                    'kwargs': {
                        'kind': 'details',
                    },
                    'obj': 'interface'
                },
                'environment': {
                    'obj': 'ambiente_id'
                },
                'environment__basic': {
                    'serializer': environment_serializers.EnvironmentV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'ambiente',
                },
                'environment__details': {
                    'serializer': environment_serializers.EnvironmentV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'ambiente',
                },
            }

    @staticmethod
    def setup_eager_loading_environment(queryset):
        log.info('Using setup_eager_loading_environment')
        queryset = queryset.select_related('environment')
        return queryset


class InterfaceV3Serializer(DynamicFieldsModelSerializer):

    log.info("InterfaceV3Serializer")

    protected = serializers.Field(source='protegida')
    description = serializers.Field(source='descricao')
    native_vlan = serializers.Field(source='vlan_nativa')

    equipment = serializers.SerializerMethodField('get_equipment')
    type = serializers.SerializerMethodField('get_interface_type')
    channel = serializers.SerializerMethodField('get_channel')
    front_interface = serializers.SerializerMethodField('get_front_interface')
    back_interface = serializers.SerializerMethodField('get_back_interface')

    def get_interface_type(self, obj):
        return self.extends_serializer(obj, 'type')

    def get_channel(self, obj):
        return self.extends_serializer(obj, 'channel')

    def get_front_interface(self, obj):
        return self.extends_serializer(obj, 'front_interface')

    def get_back_interface(self, obj):
        return self.extends_serializer(obj, 'back_interface')

    def get_equipment(self, obj):
        return self.extends_serializer(obj, 'equipment')

    class Meta:
        interface_model = get_app('interface', module_label='models')
        model = interface_model.Interface
        fields = (
            'id',
            'interface',
            'protected',
            'description',
            'equipment',
            'description',
            'native_vlan',
            'type',
            'channel',
            'front_interface',
            'back_interface',
        )

        default_fields = fields

        basic_fields = (
            'id',
            'interface',
            'equipment',
            'channel',
        )

        details_fields = fields

    def get_serializers(self):
        """Returns the mapping of serializers."""

        equipment_serializers = get_app('api_equipment', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'type': {
                    'obj': 'tipo_id'
                },
                'type__details': {
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
                'front_interface': {
                    'obj': 'ligacao_front_id'
                },
                'front_interface__basic': {
                    'serializer': InterfaceV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'ligacao_front',
                },
                'front_interface__details': {
                    'serializer': InterfaceV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'ligacao_front',
                },
                'back_interface': {
                    'obj': 'ligacao_back_id'
                },
                'back_interface__basic': {
                    'serializer': InterfaceV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'ligacao_back',
                },
                'back_interface__details': {
                    'serializer': InterfaceV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'ligacao_back',
                },
                'equipment': {
                    'obj': 'equipamento_id'
                },
                'equipment__basic': {
                    'serializer': equipment_serializers.EquipmentV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'equipamento',
                },
                'equipment__details': {
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
