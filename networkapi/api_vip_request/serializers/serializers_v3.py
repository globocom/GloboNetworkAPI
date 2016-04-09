# -*- coding:utf-8 -*-
from networkapi.ambiente.models import Ambiente
from networkapi.api_environment_vip.serializers import EnvironmentVipSerializer, OptionVipSerializer
from networkapi.api_equipment.serializers import EquipmentSerializer
from networkapi.api_pools.serializers import Ipv4BasicSerializer, Ipv4Serializer, Ipv6BasicSerializer,\
    Ipv6Serializer
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

    class Meta:
        model = VipRequestPortPool
        fields = (
            'server_pool',
            'optionvip',
            'val_optionvip',
        )


class VipRequestPortSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    options = serializers.SerializerMethodField('get_options')

    def get_options(self, obj):
        options = obj.viprequestportoptionvip_set.all()
        opt = {
            'protocol_l7': None,
            'protocol_l4': None
        }
        for option in options:
            if option.optionvip.tipo_opcao == 'protocol_l7':
                opt['protocol_l7'] = option.optionvip.id
            elif option.optionvip.tipo_opcao == 'protocol_l4':
                opt['protocol_l4'] = option.optionvip.id

    pools = serializers.SerializerMethodField('get_server_pools')

    def get_server_pools(self, obj):
        pools = obj.viprequestportpool_set.all()
        pools_serializer = VipRequestPortPoolSerializer(pools, many=True)

        return pools_serializer.data

    class Meta:
        model = VipRequestPort
        fields = (
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

    pools = serializers.SerializerMethodField('get_server_pools')

    def get_server_pools(self, obj):
        pools = obj.viprequestpool_set.all()
        pools_serializer = VipRequestPortPoolSerializer(pools, many=True)

        return pools_serializer.data

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
            'pools',
            'options',
            'created'
        )
