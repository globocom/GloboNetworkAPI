# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

class PoolPermissionV3Serializer(DynamicFieldsModelSerializer):

    group = serializers.SerializerMethodField('get_group')

    def get_group(self, obj):
        return self.extends_serializer(obj, 'group')

    class Meta:
        ServerPoolGroupPermission = get_model('requisicaovips',
                                              'ServerPoolGroupPermission')
        model = ServerPoolGroupPermission
        fields = (
            'id',
            'group',
            'user_group',
            'read',
            'write',
            'change_config',
            'delete'
        )
        default_fields = (
            'group',
            'read',
            'write',
            'change_config',
            'delete'
        )

    def get_serializers(self):
        # serializers
        group_slz = get_app('api_group', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'group': {
                    'obj': 'user_group_id',
                },
                'group__details': {
                    'serializer': group_slz.UserGroupV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'user_group',
                },
            }

        return self.mapping


class OptionPoolV3Serializer(DynamicFieldsModelSerializer):

    class Meta:
        OptionPool = get_model('api_pools', 'OptionPool')
        model = OptionPool
        depth = 1
        fields = (
            'id',
            'type',
            'name'
        )
        default_fields = (
            'id',
            'name'
        )


class HealthcheckV3Serializer(DynamicFieldsModelSerializer):

    class Meta:
        Healthcheck = get_model('healthcheckexpect', 'Healthcheck')
        model = Healthcheck
        fields = (
            'identifier',
            'healthcheck_type',
            'healthcheck_request',
            'healthcheck_expect',
            'destination'
        )


class PoolMemberV3Serializer(DynamicFieldsModelSerializer):

    last_status_update_formated = serializers.\
        Field(source='last_status_update_formated')

    server_pool = serializers.SerializerMethodField('get_server_pool')
    ip = serializers.SerializerMethodField('get_ip')
    ipv6 = serializers.SerializerMethodField('get_ipv6')
    equipments = serializers.SerializerMethodField('get_equipments')
    equipment = serializers.SerializerMethodField('get_equipment')

    def get_server_pool(self, obj):
        return self.extends_serializer(obj, 'server_pool')

    def get_ip(self, obj):
        return self.extends_serializer(obj, 'ip')

    def get_ipv6(self, obj):
        return self.extends_serializer(obj, 'ipv6')

    def get_equipments(self, obj):
        return self.extends_serializer(obj, 'equipments')

    def get_equipment(self, obj):
        return self.extends_serializer(obj, 'equipment')

    class Meta:
        ServerPoolMember = get_model('requisicaovips', 'ServerPoolMember')
        model = ServerPoolMember
        depth = 2
        fields = (
            'id',
            'server_pool',
            'identifier',
            'ip',
            'ipv6',
            'priority',
            'weight',
            'limit',
            'port_real',
            'member_status',
            'last_status_update',
            'last_status_update_formated',
            'equipments',
            'equipment',
        )

        default_fields = (
            'id',
            'identifier',
            'ipv6',
            'ip',
            'priority',
            'equipment',
            'weight',
            'limit',
            'port_real',
            'last_status_update_formated',
            'member_status',
        )

        basic_fields = (
            'id',
            'identifier',
            'ipv6',
            'ip',
            'port_real',
            'member_status',
        )

        details_fields = fields

    def get_serializers(self):
        # serializers
        eqpt_slz = get_app('api_equipment', module_label='serializers')
        ip_slz = get_app('api_ip', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'server_pool': {
                    'obj': 'server_pool_id',
                },
                'server_pool__basic': {
                    'serializer': PoolV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'server_pool',
                },
                'server_pool__details': {
                    'serializer': PoolV3Serializer,
                    'kwargs': {
                        'include': (
                            'servicedownaction__details',
                            'environment__details',
                            'groups_permissions__details',
                        )
                    },
                    'obj': 'server_pool',
                },
                'ip': {
                    'serializer': ip_slz.Ipv4V3Serializer,
                    'kwargs': {
                        'fields': (
                            'id',
                            'ip_formated',
                        )
                    },
                    'obj': 'ip',
                },
                'ip__details': {
                    'serializer': ip_slz.Ipv4V3Serializer,
                    'kwargs': {
                    },
                    'obj': 'ip',
                },
                'ipv6': {
                    'serializer': ip_slz.Ipv6V3Serializer,
                    'kwargs': {
                        'fields': (
                            'id',
                            'ip_formated',
                        )
                    },
                    'obj': 'ipv6',
                },
                'ipv6__details': {
                    'serializer': ip_slz.Ipv6V3Serializer,
                    'kwargs': {
                    },
                    'obj': 'ipv6',
                },
                'equipments': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'equipments',
                },
                'equipments__details': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'equipments',
                },
                'equipment': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'fields': (
                            'id',
                            'name',
                        )
                    },
                    'obj': 'equipment',
                },

            }

        return self.mapping


class PoolV3Serializer(DynamicFieldsModelSerializer):

    dscp = serializers.Field(source='dscp')

    healthcheck = serializers.SerializerMethodField('get_healthcheck')
    servicedownaction = serializers.SerializerMethodField(
        'get_servicedownaction')
    server_pool_members = serializers.SerializerMethodField(
        'get_server_pool_members')
    vips = serializers.SerializerMethodField('get_vips')
    groups_permissions = serializers.SerializerMethodField(
        'get_groups_permissions')
    environment = serializers.SerializerMethodField(
        'get_environment')

    def get_healthcheck(self, obj):
        return self.extends_serializer(obj, 'healthcheck')

    def get_servicedownaction(self, obj):
        return self.extends_serializer(obj, 'servicedownaction')

    def get_server_pool_members(self, obj):
        return self.extends_serializer(obj, 'server_pool_members')

    def get_vips(self, obj):
        return self.extends_serializer(obj, 'vips')

    def get_groups_permissions(self, obj):
        return self.extends_serializer(obj, 'groups_permissions')

    def get_environment(self, obj):
        return self.extends_serializer(obj, 'environment')

    class Meta:
        ServerPool = get_model('requisicaovips', 'ServerPool')
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'default_port',
            'environment',
            'servicedownaction',
            'lb_method',
            'healthcheck',
            'default_limit',
            'server_pool_members',
            'pool_created',
            'vips',
            'dscp',
            'groups_permissions',
        )

        default_fields = (
            'id',
            'identifier',
            'default_port',
            'environment',
            'servicedownaction',
            'lb_method',
            'healthcheck',
            'default_limit',
            'server_pool_members',
            'pool_created'
        )

        basic_fields = (
            'id',
            'identifier',
            'pool_created'
        )
        details_fields = fields

    def get_serializers(self):
        # serializers
        vip_slz = get_app('api_vip_request', module_label='serializers.v3')
        env_slz = get_app('api_environment', module_label='serializers')
        ogp_slz = get_app('api_ogp', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'healthcheck': {
                    'serializer': HealthcheckV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'healthcheck',
                },
                'healthcheck__details': {
                    'serializer': HealthcheckV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'healthcheck',
                },
                'servicedownaction': {
                    'serializer': OptionPoolV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'servicedownaction',
                },
                'servicedownaction__details': {
                    'serializer': OptionPoolV3Serializer,
                    'kwargs': {
                        'include': (
                            'type',
                        )
                    },
                    'obj': 'servicedownaction',
                },
                'environment': {
                    'obj': 'environment_id',
                },
                'environment__details': {
                    'serializer': env_slz.EnvironmentV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'environment',
                },
                'server_pool_members': {
                    'serializer': PoolMemberV3Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'server_pool_members',
                },
                'server_pool_members__details': {
                    'serializer': PoolMemberV3Serializer,
                    'kwargs': {
                        'many': True,
                        'include': (
                            'server_pool',
                        ),
                    },
                    'obj': 'server_pool_members',
                },
                'vips': {
                    'serializer': vip_slz.VipRequestV3Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'vips',
                },
                'vips__basic': {
                    'serializer': vip_slz.VipRequestV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic'
                    },
                    'obj': 'vips',
                },
                'vips__details': {
                    'serializer': vip_slz.VipRequestV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'vips',
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
                }
            }

        return self.mapping
