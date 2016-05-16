# -*- coding:utf-8 -*-
from networkapi.ambiente.models import Ambiente
from networkapi.api_environment_vip.serializers import EnvironmentVipSerializer, OptionVipSerializer
from networkapi.api_equipment.serializers import EquipmentSerializer
from networkapi.api_pools.serializers import Ipv4BasicSerializer, Ipv4DetailsSerializer, Ipv4Serializer,\
    Ipv6BasicSerializer, Ipv6DetailsSerializer, Ipv6Serializer, PoolV3Serializer
from networkapi.api_vip_request.models import VipRequest, VipRequestOptionVip, VipRequestPort,\
    VipRequestPortPool

from rest_framework import serializers


class VipRequestOptionVipSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    optionvip = OptionVipSerializer()

    class Meta:
        model = VipRequestOptionVip
        fields = (
            'id',
            'optionvip',
        )


class VipRequestPortPoolSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    l7_rule = serializers.Field(source='optionvip.id')
    l7_value = serializers.Field(source='val_optionvip')

    class Meta:
        model = VipRequestPortPool
        fields = (
            'server_pool',
            'l7_rule',
            'l7_value'
        )


class VipRequestPortSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    options = serializers.SerializerMethodField('get_options')

    def get_options(self, obj):
        options = obj.viprequestportoptionvip_set.all()
        opt = {
            'l7_protocol': None,
            'l4_protocol': None
        }
        for option in options:
            if option.optionvip.tipo_opcao == 'l7_protocol':
                opt['l7_protocol'] = option.optionvip.id
            elif option.optionvip.tipo_opcao == 'l4_protocol':
                opt['l4_protocol'] = option.optionvip.id

        return opt

    pools = serializers.SerializerMethodField('get_server_pools')

    def get_server_pools(self, obj):
        pools = obj.viprequestportpool_set.all()
        pools_serializer = VipRequestPortPoolSerializer(pools, many=True)

        return pools_serializer.data

    class Meta:
        model = VipRequestPort
        fields = (
            'id',
            'port',
            'options',
            'pools',
        )


class EnvironmentOptionsSerializer(serializers.ModelSerializer):

    name = serializers.Field()

    class Meta:
        model = Ambiente
        fields = (
            'id',
            'name'
        )


class VipRequestListSerializer(serializers.ModelSerializer):

    eqpt = serializers.SerializerMethodField('get_eqpt')

    ipv4 = Ipv4Serializer()

    ipv6 = Ipv6Serializer()

    environmentvip = EnvironmentVipSerializer()

    def get_eqpt(self, obj):
        eqpts = list()
        equipments = list()
        if obj.ipv4:
            eqpts = obj.ipv4.ipequipamento_set.all()
        if obj.ipv6:
            eqpts |= obj.ipv6.ipv6equipament_set.all()

        for eqpt in eqpts:
            equipments.append(eqpt.equipamento)
        eqpt_serializer = EquipmentSerializer(equipments, many=True)

        return eqpt_serializer.data

    class Meta:
        model = VipRequest
        fields = (
            'environmentvip',
            'ipv4',
            'ipv6',
            'eqpt',
        )


class VipRequestSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    business = serializers.CharField(
        required=True
    )

    service = serializers.CharField(
        required=True
    )

    name = serializers.CharField(
        required=True
    )

    ipv4 = Ipv4BasicSerializer()

    ipv6 = Ipv6BasicSerializer()

    options = serializers.SerializerMethodField('get_options')

    def get_options(self, obj):
        options = obj.viprequestoptionvip_set.all()
        opt = {
            'traffic_return': None,
            'cache_group': None,
            'persistence': None,
            'timeout': None,
        }
        for option in options:
            if option.optionvip.tipo_opcao == 'cache':
                opt['cache_group'] = option.optionvip.id
            elif option.optionvip.tipo_opcao == 'Persistencia':
                opt['persistence'] = option.optionvip.id
            elif option.optionvip.tipo_opcao == 'Retorno de trafego':
                opt['traffic_return'] = option.optionvip.id
            elif option.optionvip.tipo_opcao == 'timeout':
                opt['timeout'] = option.optionvip.id

        return opt

    ports = serializers.SerializerMethodField('get_server_pools')

    def get_server_pools(self, obj):
        ports = obj.viprequestport_set.all()
        ports_serializer = VipRequestPortSerializer(ports, many=True)

        return ports_serializer.data

    class Meta:
        model = VipRequest
        fields = (
            'id',
            'name',
            'service',
            'business',
            'environmentvip',
            'ipv4',
            'ipv6',
            'ports',
            'options',
            'created'
        )


class VipRequestDetailsSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    business = serializers.CharField(
        required=True
    )

    service = serializers.CharField(
        required=True
    )

    name = serializers.CharField(
        required=True
    )

    environmentvip = EnvironmentVipSerializer()

    ipv4 = Ipv4DetailsSerializer()

    ipv6 = Ipv6DetailsSerializer()

    options = serializers.SerializerMethodField('get_options')

    equipments = serializers.SerializerMethodField('get_eqpt')

    def get_eqpt(self, obj):
        eqpts = list()
        equipments = list()
        if obj.ipv4:
            eqpts = obj.ipv4.ipequipamento_set.all()
        if obj.ipv6:
            eqpts |= obj.ipv6.ipv6equipament_set.all()

        for eqpt in eqpts:
            equipments.append(eqpt.equipamento)
        eqpt_serializer = EquipmentSerializer(equipments, many=True)

        return eqpt_serializer.data

    def get_options(self, obj):
        options = obj.viprequestoptionvip_set.all()
        opt = {
            'traffic_return': None,
            'cache_group': None,
            'persistence': None,
            'timeout': None,
        }
        for option in options:
            if option.optionvip.tipo_opcao == 'cache':
                opt['cache_group'] = OptionVipSerializer(option.optionvip).data
            elif option.optionvip.tipo_opcao == 'Persistencia':
                opt['persistence'] = OptionVipSerializer(option.optionvip).data
            elif option.optionvip.tipo_opcao == 'Retorno de trafego':
                opt['traffic_return'] = OptionVipSerializer(option.optionvip).data
            elif option.optionvip.tipo_opcao == 'timeout':
                opt['timeout'] = OptionVipSerializer(option.optionvip).data

        return opt

    ports = serializers.SerializerMethodField('get_server_pools')

    def get_server_pools(self, obj):
        ports = obj.viprequestport_set.all()
        ports_serializer = VipRequestPortDetailsSerializer(ports, many=True)

        return ports_serializer.data

    class Meta:
        model = VipRequest
        fields = (
            'id',
            'name',
            'service',
            'business',
            'environmentvip',
            'ipv4',
            'ipv6',
            'equipments',
            'ports',
            'options',
            'created'
        )


class VipRequestPortDetailsSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    options = serializers.SerializerMethodField('get_options')

    def get_options(self, obj):
        options = obj.viprequestportoptionvip_set.all()
        opt = {
            'l7_protocol': None,
            'l4_protocol': None
        }
        for option in options:
            if option.optionvip.tipo_opcao == 'l7_protocol':
                opt['l7_protocol'] = OptionVipSerializer(option.optionvip).data
            elif option.optionvip.tipo_opcao == 'l4_protocol':
                opt['l4_protocol'] = OptionVipSerializer(option.optionvip).data

        return opt

    pools = serializers.SerializerMethodField('get_server_pools')

    def get_server_pools(self, obj):
        pools = obj.viprequestportpool_set.all()
        pools_serializer = VipRequestPortPoolDetailsSerializer(pools, many=True)

        return pools_serializer.data

    class Meta:
        model = VipRequestPort
        fields = (
            'id',
            'port',
            'options',
            'pools',
        )


class VipRequestPortPoolDetailsSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    server_pool = PoolV3Serializer()
    l7_rule = OptionVipSerializer(source='optionvip')
    l7_value = serializers.Field(source='val_optionvip')

    class Meta:
        model = VipRequestPortPool
        fields = (
            'server_pool',
            'l7_rule',
            'l7_value'
        )
