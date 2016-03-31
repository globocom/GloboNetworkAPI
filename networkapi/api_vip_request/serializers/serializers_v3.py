# -*- coding:utf-8 -*-
from networkapi.ambiente.models import Ambiente
from networkapi.api_environment_vip.serializers import EnvironmentVipSerializer, OptionVipSerializer
from networkapi.api_equipment.serializers import EquipmentSerializer
from networkapi.api_pools.serializers import Ipv4Serializer, Ipv6Serializer, Ipv4BasicSerializer,\
    Ipv6BasicSerializer, PoolV3SimpleSerializer
from networkapi.api_vip_request.models import VipRequest, VipRequestOptionVip, VipRequestPool

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


class VipRequestPoolSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    class Meta:
        model = VipRequestPool
        fields = (
            'server_pool',
            'port',
            'optionvip',
            'val_optionvip',
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

    options = VipRequestOptionVipSerializer(
        source='get_options',
        read_only=True
    )

    options = serializers.SerializerMethodField('get_options')

    def get_options(self, obj):
        options = obj.viprequestoptionvip_set.all()
        options = [option.optionvip_id for option in options]

        return options

    pools = serializers.SerializerMethodField('get_server_pools')

    def get_server_pools(self, obj):
        pools = obj.viprequestpool_set.all()
        pools_serializer = VipRequestPoolSerializer(pools, many=True)

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
        )
