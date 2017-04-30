# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class VipRequestPortPoolV3Serializer(DynamicFieldsModelSerializer):
    l7_value = serializers.Field(source='val_optionvip')

    server_pool = serializers.SerializerMethodField('get_server_pool')
    l7_rule = serializers.SerializerMethodField('get_l7_rule')

    def get_server_pool(self, obj):

        return self.extends_serializer(obj, 'server_pool')

    def get_l7_rule(self, obj):

        return self.extends_serializer(obj, 'l7_rule')

    class Meta:
        VipRequestPortPool = get_model('api_vip_request',
                                       'VipRequestPortPool')
        model = VipRequestPortPool
        fields = (
            'id',
            'server_pool',
            'l7_rule',
            'l7_value',
            'order'
        )

    def get_serializers(self):

        pool_slz = get_app('api_pools', module_label='serializers.v3')
        envvip_slz = get_app('api_environment_vip', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'server_pool': {
                    'obj': 'server_pool_id',
                },
                'server_pool__basic': {
                    'serializer': pool_slz.PoolV3Serializer,
                    'kwargs': {
                        'kind': 'basic',
                    },
                    'obj': 'server_pool'
                },
                'server_pool__details': {
                    'serializer': pool_slz.PoolV3Serializer,
                    'kwargs': {
                        'kind': 'details',
                        'exclude': (
                            'vips',
                            'vips__details',
                        )
                    },
                    'obj': 'server_pool'
                },
                'l7_rule': {
                    'kwargs': {
                    },
                    'obj': 'optionvip_id'
                },
                'l7_rule__details': {
                    'serializer': envvip_slz.OptionVipV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'l7_rule',
                },
            }


class VipRequestPortV3Serializer(DynamicFieldsModelSerializer):
    id = serializers.Field()

    options = serializers.SerializerMethodField('get_options')
    pools = serializers.SerializerMethodField('get_pools')

    def get_pools(self, obj):
        return self.extends_serializer(obj, 'pools')

    def get_options(self, obj):
        options = obj.options
        opt = {
            'l4_protocol': None,
            'l7_protocol': None
        }
        for option in options:
            if option.optionvip.tipo_opcao == 'l4_protocol':
                opt['l4_protocol'] = option
            elif option.optionvip.tipo_opcao == 'l7_protocol':
                opt['l7_protocol'] = option

        return self.extends_serializer(opt, 'options')

    class Meta:
        VipRequestPort = get_model('api_vip_request', 'VipRequestPort')
        model = VipRequestPort
        fields = (
            'id',
            'port',
            'options',
            'pools',
            'identifier',
        )

        default_fields = (
            'id',
            'port',
            'options',
            'pools',
        )

    def get_serializers(self):

        envvip_slz = get_app('api_environment_vip', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'pools': {
                    'serializer': VipRequestPortPoolV3Serializer,
                    'kwargs': {
                        'many': True
                    },
                    'obj': 'pools',
                },
                'pools__details': {
                    'serializer': VipRequestPortPoolV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'pools'
                },
                'options': {
                    'keys': (
                        'l4_protocol',
                        'l7_protocol',
                    ),
                    'kwargs': {
                    },
                    'obj': 'optionvip_id'
                },
                'options__details': {
                    'keys': (
                        'l4_protocol',
                        'l7_protocol',
                    ),
                    'serializer': envvip_slz.OptionVipV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'optionvip',
                },
            }


class VipRequestV3Serializer(DynamicFieldsModelSerializer):

    dscp = serializers.RelatedField(source='dscp')
    default_names = serializers.RelatedField(source='default_names')

    environmentvip = serializers.SerializerMethodField('get_environmentvip')
    ipv4 = serializers.SerializerMethodField('get_ipv4')
    ipv6 = serializers.SerializerMethodField('get_ipv6')
    ports = serializers.SerializerMethodField('get_ports')
    options = serializers.SerializerMethodField('get_options')
    groups_permissions = serializers\
        .SerializerMethodField('get_groups_permissions')
    equipments = serializers.SerializerMethodField('get_equipments')

    def get_environmentvip(self, obj):
        return self.extends_serializer(obj, 'environmentvip')

    def get_ipv4(self, obj):
        return self.extends_serializer(obj, 'ipv4')

    def get_ipv6(self, obj):
        return self.extends_serializer(obj, 'ipv6')

    def get_ports(self, obj):
        return self.extends_serializer(obj, 'ports')

    def get_options(self, obj):
        options = obj.options
        opt = {
            'cache_group': None,
            'persistence': None,
            'timeout': None,
            'traffic_return': None,
        }
        for option in options:
            if option.optionvip.tipo_opcao == 'cache':
                opt['cache_group'] = option
            elif option.optionvip.tipo_opcao == 'Persistencia':
                opt['persistence'] = option
            elif option.optionvip.tipo_opcao == 'Retorno de trafego':
                opt['traffic_return'] = option
            elif option.optionvip.tipo_opcao == 'timeout':
                opt['timeout'] = option

        return self.extends_serializer(opt, 'options')

    def get_groups_permissions(self, obj):
        return self.extends_serializer(obj, 'groups_permissions')

    def get_equipments(self, obj):
        return self.extends_serializer(obj, 'equipments')

    class Meta:
        VipRequest = get_model('api_vip_request', 'VipRequest')
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
            'default_names',
            'dscp',
            'ports',
            'options',
            'groups_permissions',
            'created'
        )

        default_fields = (
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

        basic_fields = (
            'id',
            'name',
            'ipv4',
            'ipv6',
        )

        details_fields = fields

    def get_serializers(self):

        envvip_slz = get_app('api_environment_vip', module_label='serializers')
        ip_slz = get_app('api_ip', module_label='serializers')
        eqpt_slz = get_app('api_equipment', module_label='serializers')
        ogp_slz = get_app('api_ogp', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'environmentvip': {
                    'obj': 'environmentvip_id'
                },
                'environmentvip__details': {
                    'serializer': envvip_slz.EnvironmentVipV3Serializer,
                    'kwargs': {
                        'fields': (
                            'id',
                            'finalidade_txt',
                            'cliente_txt',
                            'ambiente_p44_txt',
                            'description',
                        )
                    },
                    'obj': 'environmentvip',
                    'eager_loading': self.setup_eager_loading_environmentvip
                },
                'ipv4': {
                    'obj': 'ipv4_id'
                },
                'ipv4__details': {
                    'serializer': ip_slz.Ipv4V3Serializer,
                    'kwargs': {
                        'fields': (
                            'id',
                            'ip_formated',
                            'description',
                        )
                    },
                    'obj': 'ipv4',
                    'eager_loading': self.setup_eager_loading_ipv4
                },
                'ipv6': {
                    'obj': 'ipv6_id'
                },
                'ipv6__details': {
                    'serializer': ip_slz.Ipv6V3Serializer,
                    'kwargs': {
                        'fields': (
                            'id',
                            'ip_formated',
                            'description',
                        )
                    },
                    'obj': 'ipv6',
                    'eager_loading': self.setup_eager_loading_ipv6
                },
                'ports': {
                    'serializer': VipRequestPortV3Serializer,
                    'kwargs': {
                        'many': True
                    },
                    'obj': 'ports',
                },
                'ports__details': {
                    'serializer': VipRequestPortV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'ports'
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
                            'user_group__details',
                        ),
                        'many': True,
                    },
                    'obj': 'groups_permissions',
                },
                'options': {
                    'keys': (
                        'cache_group',
                        'persistence',
                        'timeout',
                        'traffic_return',
                    ),
                    'kwargs': {
                    },
                    'obj': 'optionvip_id'
                },
                'options__details': {
                    'keys': (
                        'cache_group',
                        'persistence',
                        'timeout',
                        'traffic_return',
                    ),
                    'serializer': envvip_slz.OptionVipV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'optionvip',
                },
                'equipments': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': {
                            'id'
                        }
                    },
                    'obj': 'equipments',
                },
                'equipments__basic': {
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
                        'kind': 'details',
                        'fields': (
                            'id',
                            'name',
                            'maintenance',
                            'equipment_type',
                            'model',
                        )
                    },
                    'obj': 'equipments',
                }
            }

    @staticmethod
    def setup_eager_loading_environmentvip(queryset):

        log.info('Using setup_eager_loading_environmentvip')
        queryset = queryset.select_related(
            'environmentvip',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_ipv4(queryset):

        log.info('Using setup_eager_loading_ipv4')
        queryset = queryset.select_related(
            'ipv4',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_ipv6(queryset):

        log.info('Using setup_eager_loading_ipv6')
        queryset = queryset.select_related(
            'ipv6',
        )
        return queryset

