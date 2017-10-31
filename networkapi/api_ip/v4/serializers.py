# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class Ipv4V4Serializer(DynamicFieldsModelSerializer):

    ip_formated = serializers.Field(source='ip_formated')
    description = serializers.Field(source='descricao')

    server_pool_members = serializers.\
        SerializerMethodField('get_server_pool_members')
    vips = serializers.SerializerMethodField('get_vips')
    equipments = serializers.SerializerMethodField('get_equipments')
    networkipv4 = serializers.SerializerMethodField('get_networkipv4')

    class Meta:
        Ip = get_model('ip', 'Ip')
        model = Ip
        fields = (
            'id',
            'ip_formated',
            'oct4',
            'oct3',
            'oct2',
            'oct1',
            'networkipv4',
            'description',
            'equipments',
            'vips',
            'server_pool_members',
        )

        default_fields = (
            'id',
            'oct4',
            'oct3',
            'oct2',
            'oct1',
            'networkipv4',
            'description'
        )

        basic_fields = (
            'id',
            'ip_formated',
            'networkipv4',
            'description',
        )

        details_fields = (
            'id',
            'oct4',
            'oct3',
            'oct2',
            'oct1',
            'ip_formated',
            'networkipv4',
            'description',
            'equipments',
        )

    def get_networkipv4(self, obj):
        return self.extends_serializer(obj, 'networkipv4')

    def get_equipments(self, obj):
        return self.extends_serializer(obj, 'equipments')

    def get_vips(self, obj):
        return self.extends_serializer(obj, 'vips')

    def get_server_pool_members(self, obj):
        return self.extends_serializer(obj, 'server_pool_members')

    def get_serializers(self):
        # serializers
        net_slz = get_app('api_network', module_label='serializers.v3')
        vip_slz = get_app('api_vip_request', module_label='serializers.v3')
        pool_slz = get_app('api_pools', module_label='serializers.v3')

        if not self.mapping:
            self.mapping = {
                'networkipv4': {
                    'obj': 'networkipv4_id'
                },
                'networkipv4__details': {
                    'serializer': net_slz.NetworkIPv4V3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'networkipv4',
                    'eager_loading': self.setup_eager_loading_networkipv4
                },
                'networkipv4__basic': {
                    'serializer': net_slz.NetworkIPv4V3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'networkipv4',
                    'eager_loading': self.setup_eager_loading_networkipv4
                },
                'equipments': {
                    'serializer': IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'prohibited': (
                            'ip',
                        )
                    },
                    'obj': 'ipv4_equipment'
                },
                'equipments__basic': {
                    'serializer': IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic',
                        'prohibited': (
                            'ip__basic',
                        )
                    },
                    'obj': 'ipv4_equipment'
                },
                'equipments__details': {
                    'serializer': IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details',
                        'prohibited': (
                            'ip__details',
                        )
                    },
                    'obj': 'ipv4_equipment'
                },
                'vips': {
                    'serializer': vip_slz.VipRequestV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': ('id',)
                    },
                    'obj': 'vips'
                },
                'vips__details': {
                    'serializer': vip_slz.VipRequestV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'vips'
                },
                'server_pool_members': {
                    'serializer': pool_slz.PoolMemberV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': ('id',)
                    },
                    'obj': 'server_pool_members'
                },
                'server_pool_members__basic': {
                    'serializer': pool_slz.PoolMemberV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic'
                    },
                    'obj': 'server_pool_members'
                },
                'server_pool_members__details': {
                    'serializer': pool_slz.PoolMemberV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'server_pool_members'
                }
            }

    @staticmethod
    def setup_eager_loading_networkipv4(queryset):

        log.info('Using setup_eager_loading_networkipv4')
        queryset = queryset.select_related(
            'networkipv4',
        )
        return queryset


class Ipv6V4Serializer(DynamicFieldsModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')

    networkipv6 = serializers.SerializerMethodField('get_networkipv6')
    server_pool_members = serializers.SerializerMethodField(
        'get_server_pool_members')
    vips = serializers.SerializerMethodField('get_vips')
    equipments = serializers.SerializerMethodField('get_equipments')

    class Meta:
        Ipv6 = get_model('ip', 'Ipv6')
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
            'networkipv6',
            'description',
            'equipments',
            'vips',
            'server_pool_members',
        )

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
            'networkipv6',
            'description'
        )

        basic_fields = (
            'id',
            'ip_formated',
            'networkipv6',
            'description',
        )

        details_fields = (
            'id',
            'block1',
            'block2',
            'block3',
            'block4',
            'block5',
            'block6',
            'block7',
            'block8',
            'ip_formated',
            'networkipv6',
            'description',
            'equipments',
        )

    def get_networkipv6(self, obj):
        return self.extends_serializer(obj, 'networkipv6')

    def get_equipments(self, obj):
        return self.extends_serializer(obj, 'equipments')

    def get_vips(self, obj):
        return self.extends_serializer(obj, 'vips')

    def get_server_pool_members(self, obj):
        return self.extends_serializer(obj, 'server_pool_members')

    def get_serializers(self):

        net_slz = get_app('api_network', module_label='serializers.v3')
        vip_slz = get_app('api_vip_request', module_label='serializers.v3')
        eqpt_slz = get_app('api_equipment', module_label='v4.serializers')
        pool_slz = get_app('api_pools', module_label='serializers.v3')

        if not self.mapping:
            self.mapping = {
                'networkipv6': {
                    'obj': 'networkipv6_id'
                },
                'networkipv6__details': {
                    'serializer': net_slz.NetworkIPv6V3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'networkipv6',
                    'eager_loading': self.setup_eager_loading_networkipv6
                },
                'networkipv6__basic': {
                    'serializer': net_slz.NetworkIPv6V3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'networkipv6',
                    'eager_loading': self.setup_eager_loading_networkipv6
                },
                'equipments': {
                    'serializer': IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'prohibited': (
                            'ip',
                        )
                    },
                    'obj': 'ipv6_equipment'
                },
                'equipments__basic': {
                    'serializer': IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic',
                        'prohibited': (
                            'ip__basic',
                        )
                    },
                    'obj': 'ipv6_equipment'
                },
                'equipments__details': {
                    'serializer': IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details',
                        'prohibited': (
                            'ip__details',
                        )
                    },
                    'obj': 'ipv6_equipment'
                },
                'vips': {
                    'serializer': vip_slz.VipRequestV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': ('id',)
                    },
                    'obj': 'vips'
                },
                'vips__details': {
                    'serializer': vip_slz.VipRequestV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'vips'
                },
                'server_pool_members': {
                    'serializer': pool_slz.PoolMemberV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': ('id',)
                    },
                    'obj': 'server_pool_members'
                },
                'server_pool_members__details': {
                    'serializer': pool_slz.PoolMemberV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'server_pool_members'
                }
            }

    @staticmethod
    def setup_eager_loading_networkipv6(queryset):

        log.info('Using setup_eager_loading_networkipv6')
        queryset = queryset.select_related(
            'networkipv6',
        )
        return queryset


class IPv4EquipmentV4Serializer(DynamicFieldsModelSerializer):

    ip = serializers.SerializerMethodField('get_ip')
    equipment = serializers.SerializerMethodField('get_equipment')

    class Meta:
        model = get_model('ip', 'IpEquipamento')

        fields = (
            'id',
            'ip',
            'equipment',
        )

    def get_ip(self, obj):
        return self.extends_serializer(obj, 'ip')

    def get_equipment(self, obj):
        return self.extends_serializer(obj, 'equipment')

    def get_serializers(self):
        # serializers
        eqpt_slz = get_app('api_equipment', module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {
                'ip': {
                    'obj': 'ip_id'
                },
                'ip__basic': {
                    'serializer': Ipv4V4Serializer,
                    'kwargs': {
                        'kind': 'basic',
                        'prohibited': (
                            'equipments__basic',
                        )

                    },
                    'obj': 'ip'
                },
                'ip__details': {
                    'serializer': Ipv4V4Serializer,
                    'kwargs': {
                        'kind': 'details',
                        'prohibited': (
                            'equipments__details',
                        )

                    },
                    'obj': 'ip'
                },
                'equipment': {
                    'obj': 'equipamento_id'
                },
                'equipment__basic': {
                    'serializer': eqpt_slz.EquipmentV4Serializer,
                    'kwargs': {
                        'kind': 'basic',
                        'prohibited': (
                            'ipsv4__basic',
                            'ipsv6__basic',
                        )
                    },
                    'obj': 'equipamento'
                },
                'equipment__details': {
                    'serializer': eqpt_slz.EquipmentV4Serializer,
                    'kwargs': {
                        'kind': 'details',
                        'prohibited': (
                            'ipsv4__details',
                            'ipsv6__details',
                        )
                    },
                    'obj': 'equipamento'
                },
            }


class IPv6EquipmentV4Serializer(DynamicFieldsModelSerializer):

    ip = serializers.SerializerMethodField('get_ip')
    equipment = serializers.SerializerMethodField('get_equipment')

    class Meta:
        model = get_model('ip', 'Ipv6Equipament')

        fields = (
            'id',
            'ip',
            'equipment',
        )

    def get_ip(self, obj):
        return self.extends_serializer(obj, 'ip')

    def get_equipment(self, obj):
        return self.extends_serializer(obj, 'equipment')

    def get_serializers(self):
        # serializers
        eqpt_slz = get_app('api_equipment', module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {
                'ip': {
                    'obj': 'ip_id'
                },
                'ip__basic': {
                    'serializer': Ipv6V4Serializer,
                    'kwargs': {
                        'kind': 'basic',
                        'prohibited': (
                            'equipments__basic',
                        )
                    },
                    'obj': 'ip'
                },
                'ip__details': {
                    'serializer': Ipv6V4Serializer,
                    'kwargs': {
                        'kind': 'details',
                        'prohibited': (
                            'equipments__details',
                        )
                    },
                    'obj': 'ip'
                },
                'equipment': {
                    'obj': 'equipamento_id'
                },
                'equipment__basic': {
                    'serializer': eqpt_slz.EquipmentV4Serializer,
                    'kwargs': {
                        'kind': 'basic',
                        'prohibited': (
                            'ipsv4__basic',
                            'ipsv6__basic',
                        )
                    },
                    'obj': 'equipamento'
                },
                'equipment__details': {
                    'serializer': eqpt_slz.EquipmentV4Serializer,
                    'kwargs': {
                        'kind': 'details',
                        'prohibited': (
                            'ipsv4__details',
                            'ipsv6__details',
                        )
                    },
                    'obj': 'equipamento'
                },
            }
