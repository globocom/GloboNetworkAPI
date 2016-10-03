# -*- coding:utf-8 -*-
from rest_framework import serializers

from networkapi.api_vlan.serializers import VlanSerializerV3
from networkapi.ip.models import Ip
from networkapi.ip.models import Ipv6
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv6
from networkapi.util.serializers import DynamicFieldsModelSerializer


class NetworkIPv4DetailsSerializerV3(DynamicFieldsModelSerializer):
    networkv4 = serializers.Field(source='networkv4')
    mask_formated = serializers.Field(source='mask_formated')

    vlan = VlanSerializerV3()

    class Meta:
        model = NetworkIPv4
        fields = (
            'id',
            'oct1',
            'oct2',
            'oct3',
            'oct4',
            'block',
            'mask_oct1',
            'mask_oct2',
            'mask_oct3',
            'mask_oct4',
            'broadcast',
            'networkv4',
            'mask_formated',
            'network_type',
            'vlan'
        )
        default_fields = (
            'id',
            'networkv4',
            'mask_formated',
            'network_type',
        )


class NetworkIPv6DetailsSerializerV3(DynamicFieldsModelSerializer):
    networkv6 = serializers.Field(source='networkv6')
    mask_formated = serializers.Field(source='mask_formated')

    vlan = VlanSerializerV3()

    class Meta:
        model = NetworkIPv6
        fields = (
            'id',
            'block1',
            'block2',
            'block3',
            'block4',
            'block5',
            'block6',
            'block7',
            'block8',
            'block',
            'mask1',
            'mask2',
            'mask3',
            'mask4',
            'mask5',
            'mask6',
            'mask7',
            'mask8',
            'networkv6',
            'mask_formated',
            'network_type',
        )

        default_fields = (
            'id',
            'networkv6',
            'mask_formated',
            'network_type',
            'vlan'
        )


class Ipv4DetailsSerializer(DynamicFieldsModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')
    description = serializers.Field(source='descricao')
    networkipv4 = NetworkIPv4DetailsSerializerV3()

    class Meta:
        model = Ip
        fields = (
            'id',
            'ip_formated',
            'oct4',
            'oct3',
            'oct2',
            'oct1',
            'description',
            'networkipv4',
            'description'
        )

        default_fields = (
            'id',
            'ip_formated',
            'description'
        )


class Ipv6DetailsSerializer(DynamicFieldsModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')
    networkipv6 = NetworkIPv6DetailsSerializerV3()

    class Meta:
        model = Ipv6
        fields = (
            'id',
            'ip_formated',
            'block1',
            'block2',
            'block3',
            'block4',
            'block5',
            'block6',
            'block7',
            'block8',
            'description',
            'networkipv6',
            'description'
        )

        default_fields = (
            'id',
            'ip_formated',
            'description'
        )
