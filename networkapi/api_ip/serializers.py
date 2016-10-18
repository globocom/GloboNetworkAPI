# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.api_vlan.serializers import VlanSerializerV3
from networkapi.util.serializers import DynamicFieldsModelSerializer

Ip = get_model('ip', 'Ip')
Ipv6 = get_model('ip', 'Ipv6')
NetworkIPv4 = get_model('ip', 'NetworkIPv4')
NetworkIPv6 = get_model('ip', 'NetworkIPv6')


class NetworkIPv4DetailsSerializerV3(DynamicFieldsModelSerializer):
    networkv4 = serializers.Field(source='networkv4')
    mask_formated = serializers.Field(source='mask_formated')

    vlan = serializers.SerializerMethodField('get_vlan')

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
            'vlan'
        )

    @classmethod
    def get_serializers(cls):
        if not cls.mapping:
            cls.mapping = {
                'vlan': {
                    'serializer': VlanSerializerV3,
                    'kwargs': {
                    }
                },
                'vlan__details': {
                    'serializer': VlanSerializerV3,
                    'kwargs': {
                        'include': ('environment',)
                    }
                }
            }

        return cls.mapping

    def get_vlan(self, obj):

        return self.extends_serializer(obj.vlan, 'vlan')

    @staticmethod
    def get_mapping_eager_loading(self):
        mapping = {
            'vlan': self.setup_eager_loading_vlan,
        }

        return mapping

    @staticmethod
    def setup_eager_loading_vlan(queryset):
        queryset = queryset.select_related(
            'vlan',
        )
        return queryset


class NetworkIPv6DetailsSerializerV3(DynamicFieldsModelSerializer):
    networkv6 = serializers.Field(source='networkv6')
    mask_formated = serializers.Field(source='mask_formated')
    vlan = serializers.SerializerMethodField('get_vlan')

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

    @classmethod
    def get_serializers(cls):
        if not cls.mapping:
            cls.mapping = {
                'vlan': {
                    'serializer': VlanSerializerV3,
                    'kwargs': {
                    }
                },
                'vlan__details': {
                    'serializer': VlanSerializerV3,
                    'kwargs': {
                        'include': ('vlan',)
                    }
                }
            }

        return cls.mapping

    def get_vlan(self, obj):

        return self.extends_serializer(obj.vlan, 'vlan')


class Ipv4Serializer(DynamicFieldsModelSerializer):

    ip_formated = serializers.Field(source='ip_formated')

    class Meta:
        model = get_model('ip', 'Ip')


class Ipv6Serializer(DynamicFieldsModelSerializer):

    ip_formated = serializers.Field(source='ip_formated')

    class Meta:
        model = Ipv6


class Ipv4DetailsSerializer(DynamicFieldsModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')
    description = serializers.Field(source='descricao')
    networkipv4 = serializers.SerializerMethodField('get_networkipv4')

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

    @classmethod
    def get_serializers(cls):
        if not cls.mapping:
            cls.mapping = {
                'networkipv4': {
                    'serializer': NetworkIPv4DetailsSerializerV3,
                    'kwargs': {
                    }
                },
                'networkipv4__details': {
                    'serializer': NetworkIPv4DetailsSerializerV3,
                    'kwargs': {
                        'include': ('vlan',)
                    }
                }
            }

        return cls.mapping

    def get_networkipv4(self, obj):

        return self.extends_serializer(obj.networkipv4, 'networkipv4')

    @staticmethod
    def get_mapping_eager_loading(self):
        mapping = {
            'networkipv4': self.setup_eager_loading_networkipv4,
        }

        return mapping

    @staticmethod
    def setup_eager_loading_networkipv4(queryset):
        queryset = queryset.select_related(
            'networkipv4',
        )
        return queryset


class Ipv6DetailsSerializer(DynamicFieldsModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')
    networkipv6 = serializers.SerializerMethodField('get_networkipv6')

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

    @classmethod
    def get_serializers(cls):
        if not cls.mapping:
            cls.mapping = {
                'networkipv6': {
                    'serializer': NetworkIPv6DetailsSerializerV3,
                    'kwargs': {
                    }
                },
                'networkipv6__details': {
                    'serializer': NetworkIPv6DetailsSerializerV3,
                    'kwargs': {
                        'include': ('vlan',)
                    }
                }
            }

        return cls.mapping

    def get_networkipv6(self, obj):

        return self.extends_serializer(obj.networkipv6, 'networkipv6networkipv6')

    @staticmethod
    def get_mapping_eager_loading(self):
        mapping = {
            'networkipv6': self.setup_eager_loading_networkipv6,
        }

        return mapping

    @staticmethod
    def setup_eager_loading_networkipv6(queryset):
        queryset = queryset.select_related(
            'networkipv6',
        )
        return queryset
