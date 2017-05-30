# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class Ipv4V3Serializer(DynamicFieldsModelSerializer):

    ip_formated = serializers.Field(source='ip_formated')
    description = serializers.Field(source='descricao')

    equipments = serializers.RelatedField(source='equipments')
    vips = serializers.RelatedField(source='vips')
    server_pool_members = serializers.RelatedField(
        source='server_pool_members')

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
        eqpt_slz = get_app('api_equipment', module_label='serializers')
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
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': ('id',)
                    },
                    'obj': 'equipments'
                },
                'equipments__details': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'equipments'
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


class Ipv6V3Serializer(DynamicFieldsModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')

    server_pool_members = serializers.RelatedField(
        source='server_pool_members')
    vips = serializers.RelatedField(source='vips')
    equipments = serializers.RelatedField(source='equipments')

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
        eqpt_slz = get_app('api_equipment', module_label='serializers')
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
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': ('id',)
                    },
                    'obj': 'equipments'
                },
                'equipments__details': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'equipments'
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
