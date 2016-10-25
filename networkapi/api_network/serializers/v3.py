# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class NetworkTypeV3Serializer(DynamicFieldsModelSerializer):

    """Serilizes TipoRede Model."""

    network_type = serializers.Field(source='tipo_rede')

    class Meta:
        TipoRede = get_model('vlan', 'TipoRede')
        model = TipoRede
        fields = (
            'id',
            'tipo_rede',
        )


class NetworkIPv4V3Serializer(DynamicFieldsModelSerializer):

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
        """Returns the mapping of serializers."""
        envvip_slz = get_app('api_environment_vip', module_label='serializers')
        vlan_slz = get_app('api_vlan', module_label='serializers')

        if not cls.mapping:
            cls.mapping = {
                'environmentvip': {
                    'obj': 'ambient_vip_id'
                },
                'environmentvip__details': {
                    'serializer': envvip_slz.EnvironmentVipV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'ambient_vip',
                    'eager_loading': cls.setup_eager_loading_envvip
                },
                'vlan': {
                    'obj': 'vlan_id'
                },
                'vlan__details': {
                    'serializer': vlan_slz.VlanV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'vlan',
                    'eager_loading': cls.setup_eager_loading_vlan
                },
                'network_type': {
                    'obj': 'network_type_id'
                },
                'network_type__details': {
                    'serializer': NetworkTypeV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'network_type',
                    'eager_loading': cls.setup_eager_loading_net_type
                },
            }

        return cls.mapping

    @staticmethod
    def setup_eager_loading_net_type(queryset):
        """Eager loading of network type vip for related NetworkIPv6."""
        queryset = queryset.select_related(
            'network_type',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_vlan(queryset):
        """Eager loading of vlan vip for related NetworkIPv6."""
        queryset = queryset.select_related(
            'vlan',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_envvip(queryset):
        """Eager loading of environment vip for related NetworkIPv6."""
        queryset = queryset.select_related(
            'ambient_vip',
        )
        return queryset

    class Meta:
        NetworkIPv4 = get_model('ip', 'NetworkIPv4')
        model = NetworkIPv4
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

        basic_fields = (
            'id',
            'networkv4',
            'mask_formated',
            'broadcast',
            'vlan',
            'network_type',
            'environmentvip',
        )

        details_fields = fields


class NetworkIPv6V3Serializer(DynamicFieldsModelSerializer):

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
        """Returns the mapping of serializers."""
        envvip_slz = get_app('api_environment_vip', module_label='serializers')
        vlan_slz = get_app('api_vlan', module_label='serializers')

        if not cls.mapping:
            cls.mapping = {
                'environmentvip': {
                    'obj': 'ambient_vip_id'
                },
                'environmentvip__details': {
                    'serializer': envvip_slz.EnvironmentVipV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'ambient_vip',
                    'eager_loading': cls.setup_eager_loading_envvip
                },
                'vlan': {
                    'obj': 'vlan_id'
                },
                'vlan__details': {
                    'serializer': vlan_slz.VlanV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'vlan',
                    'eager_loading': cls.setup_eager_loading_vlan
                },
                'network_type': {
                    'obj': 'network_type_id'
                },
                'network_type__details': {
                    'serializer': NetworkTypeV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'network_type',
                    'eager_loading': cls.setup_eager_loading_net_type
                },
            }

        return cls.mapping

    @staticmethod
    def setup_eager_loading_net_type(queryset):
        """Eager loading of network type vip for related NetworkIPv6."""
        queryset = queryset.select_related(
            'network_type',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_vlan(queryset):
        """Eager loading of vlan vip for related NetworkIPv6."""
        queryset = queryset.select_related(
            'vlan',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_envvip(queryset):
        """Eager loading of environment vip for related NetworkIPv6."""
        queryset = queryset.select_related(
            'ambient_vip',
        )
        return queryset

    class Meta:
        NetworkIPv6 = get_model('ip', 'NetworkIPv6')
        model = NetworkIPv6
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

        basic_fields = (
            'id',
            'networkv6',
            'mask_formated',
            'broadcast',
            'vlan',
            'network_type',
            'environmentvip',
        )

        details_fields = fields
