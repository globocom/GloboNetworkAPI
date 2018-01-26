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

    type = serializers.RelatedField(source='tipo')

    class Meta:
        model = get_model('interface', 'TipoInterface')
        fields = (
            'id',
            'type',
        )


class PortChannelSerializer(DynamicFieldsModelSerializer):

    name = serializers.RelatedField(source='nome')

    class Meta:
        model = get_model('interface', 'PortChannel')
        fields = (
            'id',
            'name',
            'lacp',
        )


class InterfaceV3Serializer(DynamicFieldsModelSerializer):

    log.info("InterfaceV3Serializer")

    protected = serializers.Field(source='protegida')
    description = serializers.Field(source='descricao')
    equipment = serializers.Field(source='equipamento')
    native_vlan = serializers.Field(source='vlan_nativa')

    interface_type = serializers.SerializerMethodField('get_interface_type')
    channel = serializers.SerializerMethodField('get_channel')
    front_interface = serializers.SerializerMethodField('get_front_interface')
    back_interface = serializers.SerializerMethodField('get_back_interface')

    def get_interface_type(self, obj):
        return self.extends_serializer(obj, 'tipo_interface')

    def get_channel(self, obj):
        return self.extends_serializer(obj, 'port_channel')

    def get_front_interface(self, obj):
        return self.extends_serializer(obj, 'interfaces')

    def get_back_interface(self, obj):
        return self.extends_serializer(obj, 'interfaces')

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
            'interface_type',
            'channel',
            'front_interface',
            'back_interface',
        )

        default_fields = (
            'id',
            'interface',
            'protected',
            'description',
            'equipment',
            'description',
            'native_vlan',
            'interface_type',
            'channel',
            'front_interface',
            'back_interface',
        )

        basic_fields = default_fields

        details_fields = default_fields

    def get_serializers(self):
        """Returns the mapping of serializers."""

        if not self.mapping:
            self.mapping = {
                'interface_type': {
                    'obj': 'interface_type_id'
                },
                'channel': {
                    'obj': 'channel_id'
                },
                'front_interface': {
                    'obj': 'front_interface_id'
                },
                'back_interface': {
                    'obj': 'back_interface_id'
                },

            }
