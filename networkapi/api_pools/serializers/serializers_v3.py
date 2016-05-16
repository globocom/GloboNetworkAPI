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
from networkapi.api_equipment import serializers as eqpt_serializers
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.ip.models import Ip, Ipv6
from networkapi.requisicaovips.models import OptionPool, ServerPool, ServerPoolMember

from rest_framework import serializers


class Ipv4BasicSerializer(serializers.ModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')

    class Meta:
        model = Ip
        fields = (
            'id',
            'ip_formated'
        )


class Ipv6BasicSerializer(serializers.ModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')

    class Meta:
        model = Ipv6
        fields = (
            'id',
            'ip_formated'
        )


class Ipv4DetailsSerializer(serializers.ModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')
    description = serializers.Field(source='descricao')

    class Meta:
        model = Ip
        fields = (
            'id',
            'ip_formated',
            'description'
        )


class Ipv6DetailsSerializer(serializers.ModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')
    description = serializers.Field(source='descricao')

    class Meta:
        model = Ipv6
        fields = (
            'id',
            'ip_formated',
            'description'
        )


class OptionPoolV3Serializer(serializers.ModelSerializer):

    class Meta:
        model = OptionPool
        depth = 1
        fields = ('id',
                  'name'
                  )


class HealthcheckV3Serializer(serializers.ModelSerializer):

    class Meta:
        model = Healthcheck
        fields = (
            'identifier',
            'healthcheck_type',
            'healthcheck_request',
            'healthcheck_expect',
            'destination'
        )


class PoolV3SimpleSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    server_pool_members = serializers.SerializerMethodField('get_server_pool_members')

    def get_server_pool_members(self, obj):
        members = obj.serverpoolmember_set.all()
        members_serializer = PoolMemberBasicSerializer(members, many=True)

        return members_serializer.data

    class Meta:
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'environment',
            'server_pool_members',
            'pool_created'
        )


class PoolMemberBasicSerializer(serializers.ModelSerializer):

    id = serializers.Field()
    ipv6 = Ipv6BasicSerializer()
    ip = Ipv4BasicSerializer()
    last_status_update_formated = serializers.Field(source='last_status_update_formated')

    class Meta:
        depth = 1
        model = ServerPoolMember
        fields = (
            'id',
            'identifier',
            'ipv6',
            'priority',
            'ip',
            'port_real',
            'last_status_update_formated',
            'member_status'
        )


class PoolMemberV3Serializer(serializers.ModelSerializer):
    id = serializers.Field()

    ipv6 = serializers.SerializerMethodField('get_ipv6')
    ip = serializers.SerializerMethodField('get_ip')
    last_status_update_formated = serializers.Field(source='last_status_update_formated')

    equipment = eqpt_serializers.EquipmentBasicSerializer()

    def get_ipv6(self, obj):
        obj_ipv6 = None
        if obj.ipv6:
            obj_ipv6 = {
                'id': obj.ipv6_id,
                'ip_formated': obj.ipv6.ip_formated
            }
        return obj_ipv6

    def get_ip(self, obj):
        obj_ip = None
        if obj.ip:
            obj_ip = {
                'id': obj.ip_id,
                'ip_formated': obj.ip.ip_formated
            }
        return obj_ip

    class Meta:
        depth = 1
        model = ServerPoolMember
        fields = (
            'id',
            'identifier',
            'ipv6',
            'ip',
            'priority',
            'equipment',
            'weight',
            'limit',
            'port_real',
            'last_status_update_formated',
            'member_status'
        )


class PoolV3Serializer(serializers.ModelSerializer):
    id = serializers.Field()
    server_pool_members = serializers.SerializerMethodField('get_server_pool_members')
    healthcheck = HealthcheckV3Serializer()
    servicedownaction = OptionPoolV3Serializer()

    def get_server_pool_members(self, obj):
        members = obj.serverpoolmember_set.all()
        members_serializer = PoolMemberV3Serializer(members, many=True)

        return members_serializer.data

    class Meta:
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'default_port',
            'environment',
            'servicedownaction',
            'lb_method',
            'healthcheck',
            'default_limit',
            'server_pool_members',
            'pool_created'
        )


class PoolV3DatatableSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    server_pool_members = serializers.SerializerMethodField('get_server_pool_members')
    healthcheck = HealthcheckV3Serializer()
    servicedownaction = OptionPoolV3Serializer()
    environment = serializers.RelatedField(source='environment.name')

    def get_server_pool_members(self, obj):
        members = obj.serverpoolmember_set.all()
        members_serializer = PoolMemberV3Serializer(members, many=True)

        return members_serializer.data

    class Meta:
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'default_port',
            'environment',
            'servicedownaction',
            'lb_method',
            'healthcheck',
            'default_limit',
            'server_pool_members',
            'pool_created'
        )
