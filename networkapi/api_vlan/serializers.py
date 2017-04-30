# -*- coding: utf-8 -*-
import logging

from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class VlanV3Serializer(DynamicFieldsModelSerializer):
    name = serializers.Field(source='nome')
    description = serializers.Field(source='descricao')
    active = serializers.Field(source='ativada')
    environment = serializers.SerializerMethodField('get_environment')
    networks_ipv4 = serializers.SerializerMethodField('get_networks_ipv4')
    networks_ipv6 = serializers.SerializerMethodField('get_networks_ipv6')
    vrfs = serializers.SerializerMethodField('get_vrfs')
    groups_permissions = serializers\
        .SerializerMethodField('get_groups_permissions')

    def get_environment(self, obj):
        return self.extends_serializer(obj, 'environment')

    def get_networks_ipv4(self, obj):
        return self.extends_serializer(obj, 'networks_ipv4')

    def get_networks_ipv6(self, obj):
        return self.extends_serializer(obj, 'networks_ipv6')

    def get_vrfs(self, obj):
        return self.extends_serializer(obj, 'vrfs')

    def get_groups_permissions(self, obj):
        return self.extends_serializer(obj, 'groups_permissions')

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
            'vrfs',
            'groups_permissions',
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

        details_fields = default_fields

    def get_serializers(self):
        """Returns the mapping of serializers."""
        env_slz = get_app('api_environment', module_label='serializers')
        ip_slz = get_app('api_network', module_label='serializers.v3')
        vrf_slz = get_app('api_vrf', module_label='serializers')
        ogp_slz = get_app('api_ogp', module_label='serializers')

        if not self.mapping:
            self.mapping = {
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
                    'eager_loading': self.setup_eager_loading_environment
                },
                'environment__details': {
                    'serializer': env_slz.EnvironmentV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'ambiente',
                    'eager_loading': self.setup_eager_loading_environment
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
                    'eager_loading': self.setup_eager_loading_networks_ipv4
                },
                'networks_ipv6__details': {
                    'serializer': ip_slz.NetworkIPv6V3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'networks_ipv6',
                    'eager_loading': self.setup_eager_loading_networks_ipv6
                },
                'vrfs': {
                    'serializer': vrf_slz.VrfV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': ('id',)
                    },
                    'obj': 'vrfs'
                },
                'vrfs__details': {
                    'serializer': vrf_slz.VrfV3Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'vrfs'
                },
                'groups_permissions': {
                    'serializer': ogp_slz.ObjectGroupPermissionV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'user_group',
                            'read',
                            'write',
                            'change_config',
                            'delete',
                        )
                    },
                    'obj': 'groups_permissions',
                },
                'groups_permissions__details': {
                    'serializer': ogp_slz.ObjectGroupPermissionV3Serializer,
                    'kwargs': {
                        'include': (
                            'group__details',
                        ),
                        'many': True,
                    },
                    'obj': 'groups_permissions',
                },
            }

    @staticmethod
    def setup_eager_loading_environment(queryset):
        """Eager loading of environment for related Vlan."""

        log.info('Using setup_eager_loading_environment')
        queryset = queryset.select_related(
            'environment',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_networks_ipv4(queryset):
        """Eager loading of environment for related Networks Ipv4."""

        log.info('Using setup_eager_loading_networks_ipv4')
        queryset = queryset.select_related(
            'networkipv4_set',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_networks_ipv6(queryset):
        """Eager loading of environment for related Networks Ipv6."""

        log.info('Using setup_eager_loading_networks_ipv6')
        queryset = queryset.select_related(
            'networkipv6_set',
        )
        return queryset
