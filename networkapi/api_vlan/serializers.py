# -*- coding: utf-8 -*-
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class VlanV3Serializer(DynamicFieldsModelSerializer):
    name = serializers.Field(source='nome')
    description = serializers.Field(source='descricao')
    active = serializers.Field(source='ativada')
    environment = serializers.SerializerMethodField('get_environment')
    networks_ipv4 = serializers.SerializerMethodField('get_networks_ipv4')
    networks_ipv6 = serializers.SerializerMethodField('get_networks_ipv6')

    def get_environment(self, obj):
        return self.extends_serializer(obj, 'environment')

    def get_networks_ipv4(self, obj):
        return self.extends_serializer(obj, 'networks_ipv4')

    def get_networks_ipv6(self, obj):
        return self.extends_serializer(obj, 'networks_ipv6')

    class Meta:
        vlan_model = get_app('vlan', module_label='models')
        model = vlan_model.Vlan
        fields = (
            'id',
            'name',
            'num_vlan',
            'environment',
            'description',
            'acl_file_name',
            'acl_valida',
            'acl_file_name_v6',
            'acl_valida_v6',
            'active',
            'vrf',
            'acl_draft',
            'acl_draft_v6',
            'networks_ipv4',
            'networks_ipv6',
        )

        default_fields = (
            'id',
            'name',
            'num_vlan',
            'environment',
            'description',
            'acl_file_name',
            'acl_valida',
            'acl_file_name_v6',
            'acl_valida_v6',
            'active',
            'vrf',
            'acl_draft',
            'acl_draft_v6',
        )

        basic_fields = (
            'id',
            'name',
            'num_vlan',
        )

        details_fields = fields

    @classmethod
    def get_serializers(cls):
        """Returns the mapping of serializers."""
        env_slz = get_app('api_environment', module_label='serializers')
        ip_slz = get_app('api_network', module_label='serializers.v3')

        if not cls.mapping:
            cls.mapping = {
                'environment': {
                    'obj': 'ambiente_id'
                },
                'environment__basic': {
                    'serializer': env_slz.EnvironmentV3Serializer,
                    'kwargs': {
                        'fields': (
                            'id',
                            'name',
                        )
                    },
                    'obj': 'ambiente',
                    'eager_loading': cls.setup_eager_loading_environment
                },
                'environment__details': {
                    'serializer': env_slz.EnvironmentV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'ambiente',
                    'eager_loading': cls.setup_eager_loading_environment
                },
                'networks_ipv4': {
                    'serializer': ip_slz.NetworkIPv4V3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': ('id',)
                    },
                    'obj': 'networks_ipv4',
                },
                'networks_ipv6': {
                    'serializer': ip_slz.NetworkIPv6V3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': ('id',)
                    },
                    'obj': 'networks_ipv6',
                },
                'networks_ipv4__details': {
                    'serializer': ip_slz.NetworkIPv4V3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'networks_ipv4',
                },
                'networks_ipv6__details': {
                    'serializer': ip_slz.NetworkIPv6V3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'networks_ipv6',
                }
            }

        return cls.mapping

    @staticmethod
    def setup_eager_loading_environment(queryset):
        """Eager loading of environment for related Vlan."""
        queryset = queryset.select_related(
            'environment',
        )
        return queryset
