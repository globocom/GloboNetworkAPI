# -*- coding: utf-8 -*-
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

# serializers
envvip_slz = get_app('api_environment_vip', module_label='serializers')
vlan_slz = get_app('api_vlan', module_label='serializers')

# models
type_model = get_app('vlan', module_label='models')
net4_model = get_app('ip', module_label='models')
net6_model = get_app('ip', module_label='models')


class NetworkTypeSerializer(DynamicFieldsModelSerializer):

    network_type = serializers.Field(source='tipo_rede')

    class Meta:
        model = type_model.TipoRede
        fields = (
            'id',
            'tipo_rede',
        )


class NetworkIPv4Serializer(DynamicFieldsModelSerializer):

    """Serilizes NetworkIPv4 Model."""

    networkv4 = serializers.Field(source='networkv4')
    mask_formated = serializers.Field(source='mask_formated')
    dhcprelay = serializers.Field(source='dhcprelay')
    environmentvip = serializers.SerializerMethodField('get_environmentvip')
    vlan = serializers.SerializerMethodField('get_vlan')
    network_type = serializers.SerializerMethodField('get_network_type')

    def get_environmentvip(self, obj):
        return self.extends_serializer(obj, 'environmentvip')

    def get_vlan(self, obj):
        return self.extends_serializer(obj, 'vlan')

    def get_network_type(self, obj):
        return self.extends_serializer(obj, 'network_type')

    @classmethod
    def get_serializers(cls):
        if not cls.mapping:
            cls.mapping = {
                'environmentvip': {
                    'obj': 'ambient_vip_id'
                },
                'environmentvip__details': {
                    'serializer': envvip_slz.EnvironmentVipSerializer,
                    'kwargs': {
                    },
                    'obj': 'ambient_vip'
                },
                'vlan': {
                    'obj': 'vlan_id'
                },
                'vlan__details': {
                    'serializer': vlan_slz.VlanSerializerV3,
                    'kwargs': {
                    },
                    'obj': 'vlan'
                },
                'network_type': {
                    'obj': 'network_type_id'
                },
                'network_type__details': {
                    'serializer': NetworkTypeSerializer,
                    'kwargs': {
                    },
                    'obj': 'network_type'
                },
            }

        return cls.mapping

    class Meta:
        model = net4_model.NetworkIPv4
        default_fields = (
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
            'vlan',
            'network_type',
            'environmentvip',
            'active',
        )

        fields = (
            'id',
            'oct1',
            'oct2',
            'oct3',
            'oct4',
            'block',
            'networkv4',
            'mask_oct1',
            'mask_oct2',
            'mask_oct3',
            'mask_oct4',
            'mask_formated',
            'broadcast',
            'vlan',
            'network_type',
            'environmentvip',
            'active',
            'dhcprelay',
        )


class NetworkIPv6Serializer(DynamicFieldsModelSerializer):

    """Serilizes NetworkIPv6 Model."""

    networkv6 = serializers.Field(source='networkv6')
    mask_formated = serializers.Field(source='mask_formated')
    dhcprelay = serializers.Field(source='dhcprelay')
    environmentvip = serializers.SerializerMethodField('get_environmentvip')
    vlan = serializers.SerializerMethodField('get_vlan')
    network_type = serializers.SerializerMethodField('get_network_type')

    def get_environmentvip(self, obj):
        return self.extends_serializer(obj, 'environmentvip')

    def get_vlan(self, obj):
        return self.extends_serializer(obj, 'vlan')

    def get_network_type(self, obj):
        return self.extends_serializer(obj, 'network_type')

    @classmethod
    def get_serializers(cls):
        if not cls.mapping:
            cls.mapping = {
                'environmentvip': {
                    'obj': 'ambient_vip_id'
                },
                'environmentvip__details': {
                    'serializer': envvip_slz.EnvironmentVipSerializer,
                    'kwargs': {
                    },
                    'obj': 'ambient_vip'
                },
                'vlan': {
                    'obj': 'vlan_id'
                },
                'vlan__details': {
                    'serializer': vlan_slz.VlanSerializerV3,
                    'kwargs': {
                    },
                    'obj': 'vlan'
                },
                'network_type': {
                    'obj': 'network_type_id'
                },
                'network_type__details': {
                    'serializer': NetworkTypeSerializer,
                    'kwargs': {
                    },
                    'obj': 'network_type'
                },
            }

        return cls.mapping

    class Meta:
        model = net6_model.NetworkIPv6
        default_fields = (
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
            'vlan',
            'network_type',
            'environmentvip',
            'active',
        )
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
            'networkv6',
            'mask1',
            'mask2',
            'mask3',
            'mask4',
            'mask5',
            'mask6',
            'mask7',
            'mask8',
            'mask_formated',
            'vlan',
            'network_type',
            'environmentvip',
            'active',
            'dhcprelay'
        )
