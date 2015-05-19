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

from rest_framework import serializers
from networkapi.ambiente.models import Ambiente
from networkapi.infrastructure.script_utils import exec_script
from networkapi.ip.models import Ip, Ipv6
from networkapi.requisicaovips.models import ServerPool, ServerPoolMember, VipPortToPool
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.equipamento.models import Equipamento
from networkapi.api_pools.models import OpcaoPoolAmbiente, OpcaoPool
from networkapi.settings import POOL_REAL_CHECK


class ServerPoolDatatableSerializer(serializers.ModelSerializer):

    healthcheck = serializers.RelatedField(
        source='healthcheck.healthcheck_type'
    )

    environment = serializers.RelatedField(
        source='environment.name'
    )


    class Meta:
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'default_port',
            'healthcheck',
            'environment',
            'pool_created'
        )


class Ipv4Serializer(serializers.ModelSerializer):

    ip_formated = serializers.Field(source='ip_formated')

    class Meta:
        model = Ip


class Ipv6Serializer(serializers.ModelSerializer):

    ip_formated = serializers.Field(source='ip_formated')

    class Meta:
        model = Ipv6


class ServerPoolMemberSerializer(serializers.ModelSerializer):

    #pool_enabled = serializers.SerializerMethodField('check_pool_member_enabled')

    equipment_name = serializers.SerializerMethodField('get_name_equipment')

    ip = Ipv4Serializer()
    ipv6 = Ipv6Serializer()

    class Meta:
        depth = 1
        model = ServerPoolMember
        fields = ('id',
                  'server_pool',
                  'identifier',
                  'ipv6', 'ip',
                  'priority',
                  'weight',
                  'limit',
                  'port_real',
                  'healthcheck',
                  'member_status',
                  'last_status_update',
                  'equipment_name',
                  )

    def check_pool_member_enabled(self, obj):

        command = POOL_REAL_CHECK % (obj.server_pool.id, obj.ip.id, obj.port_real)


        code, _, _ = exec_script(command)

        if code == 0:
            return True

        return False

    def get_name_equipment(self, obj):

        ipv4 = obj.ip
        ipv6 = obj.ipv6

        ip_equipment_set = ipv4 and ipv4.ipequipamento_set or ipv6 and ipv6.ipv6equipament_set

        ip_equipment_obj = ip_equipment_set.select_related().uniqueResult()

        equipment = ip_equipment_obj.equipamento

        return equipment.nome


class ServerPoolSerializer(serializers.ModelSerializer):

    class Meta:
        depth = 1
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'default_port',
            'default_limit',
            'healthcheck',
            'environment',
            'pool_created',
            'lb_method'
        )


class PoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'default_port',
            'healthcheck',
            'environment',
            'pool_created'
        )


class HealthcheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Healthcheck
        fields = ('id',
                  'identifier',
                  'healthcheck_type',
                  'healthcheck_request',
                  'healthcheck_expect',
                  'destination'
                  )

class EquipamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipamento
        fields = ('id',
                  'tipo_equipamento',
                  'modelo',
                  'nome',
                  'grupos'
                 )

class OpcaoPoolAmbienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcaoPoolAmbiente
        depth = 1
        fields = ('id',
                  'opcao_pool',
                  'ambiente'
                 )


class VipPortToPoolSerializer(serializers.ModelSerializer):

    environment_vip_ipv4 = serializers.RelatedField(
        source='requisicao_vip.ip.networkipv4.ambient_vip.name'
    )

    environment_vip_ipv6 = serializers.RelatedField(
        source='requisicao_vip.ipv6.networkipv6.ambient_vip.name'
    )

    class Meta:
        model = VipPortToPool
        depth = 2
        fields = ('id',
                  'requisicao_vip',
                  'server_pool',
                  'port_vip',
                  'environment_vip_ipv4',
                  'environment_vip_ipv6'
                 )


class AmbienteSerializer(serializers.ModelSerializer):

    name = serializers.Field(source='name')

    class Meta:
        model = Ambiente


class ServerPoolMemberStatusSerializer(serializers.ModelSerializer):

    status = serializers.SerializerMethodField('check_pool_member_status')

    class Meta:
        depth = 1
        model = ServerPoolMember
        fields = (
            'id',
            'status',
        )

    def check_pool_member_status(self, obj):

        command = POOL_REAL_CHECK % (obj.server_pool.id, obj.ip.id, obj.port_real)

        code, _, _ = exec_script(command)

        return code