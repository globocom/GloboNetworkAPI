# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model

from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class EquipmentV4Serializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')
    ipv4 = serializers.SerializerMethodField('get_ipv4')
    ipv6 = serializers.SerializerMethodField('get_ipv6')
    equipment_type = serializers.SerializerMethodField('get_equipment_type')
    model = serializers.SerializerMethodField('get_model')
    environments = serializers.SerializerMethodField('get_environments')
    groups = serializers.SerializerMethodField('get_groups')
    id_as = serializers.SerializerMethodField('get_id_as')

    class Meta:
        Equipamento = get_model('equipamento', 'Equipamento')
        model = Equipamento
        fields = (
            'id',
            'name',
            'maintenance',
            'equipment_type',
            'model',
            'ipv4',
            'ipv6',
            'environments',
            'groups',
            'id_as'
        )

        basic_fields = (
            'id',
            'name'
        )

        default_fields = (
            'id',
            'name',
            'maintenance',
            'equipment_type',
            'model',
        )

        details_fields = fields

    def get_model(self, obj):
        return self.extends_serializer(obj, 'model')

    def get_equipment_type(self, obj):
        return self.extends_serializer(obj, 'equipment_type')

    def get_groups(self, obj):
        return self.extends_serializer(obj, 'groups')

    def get_environments(self, obj):
        return self.extends_serializer(obj, 'environments')

    def get_ipv4(self, obj):
        return self.extends_serializer(obj, 'ipv4')

    def get_ipv6(self, obj):
        return self.extends_serializer(obj, 'ipv6')

    def get_id_as(self, obj):
        return self.extends_serializer(obj, 'id_as')

    def get_serializers(self):
        eqptv3_slzs = get_app('api_equipment', module_label='serializers')
        ip_slz = get_app('api_ip', module_label='serializers')
        grp_slz = get_app('api_group', module_label='serializers')
        as_slz = get_app('api_as', module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {
                'model': {
                    'obj': 'modelo_id'
                },
                'model__details': {
                    'serializer': eqptv3_slzs.ModelV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'modelo'
                },
                'equipment_type': {
                    'obj': 'tipo_equipamento_id'
                },
                'equipment_type__details': {
                    'serializer': eqptv3_slzs.EquipmentTypeV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'tipo_equipamento'
                },
                'ipv4': {
                    'serializer': ip_slz.Ipv4V3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'id',
                        )
                    },
                    'obj': 'ipv4'
                },
                'ipv4__basic': {
                    'serializer': ip_slz.Ipv4V3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'id',
                            'ip_formated',
                            'description',
                        ),
                        'exclude': ('equipments',),
                    },
                    'obj': 'ipv4',
                    'eager_loading': self.setup_eager_loading_ipv4
                },
                'ipv4__details': {
                    'serializer': ip_slz.Ipv4V3Serializer,
                    'kwargs': {
                        'many': True,
                        'include': ('networkipv4',),
                        'exclude': ('equipments',),
                    },
                    'obj': 'ipv4',
                    'eager_loading': self.setup_eager_loading_ipv4
                },
                'ipv6': {
                    'serializer': ip_slz.Ipv6V3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'id',
                        )
                    },
                    'obj': 'ipv6'
                },
                'ipv6__basic': {
                    'serializer': ip_slz.Ipv6V3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'id',
                            'ip_formated',
                            'description',
                        ),
                        'exclude': ('equipments',),
                    },
                    'obj': 'ipv6',
                    'eager_loading': self.setup_eager_loading_ipv6
                },
                'ipv6__details': {
                    'serializer': ip_slz.Ipv6V3Serializer,
                    'kwargs': {
                        'many': True,
                        'include': ('networkipv6',),
                        'exclude': ('equipments',),
                    },
                    'obj': 'ipv6',
                    'eager_loading': self.setup_eager_loading_ipv6
                },
                'groups': {
                    'serializer': grp_slz.EquipmentGroupV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'id',
                        )
                    },
                    'obj': 'groups'
                },
                'groups__details': {
                    'serializer': grp_slz.EquipmentGroupV3Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'groups'
                },
                'environments': {
                    'serializer': eqptv3_slzs.EquipmentEnvironmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'is_router',
                            'is_controller',
                            'environment',
                        )
                    },
                    'obj': 'environments'
                },
                'environments__details': {
                    'serializer': eqptv3_slzs.EquipmentEnvironmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'is_router',
                            'is_controller',
                            'environment__details',
                        ),
                    },
                    'obj': 'environments'
                },
                'id_as':{
                    'obj': 'id_as_id'
                },
                'id_as__basic': {
                    'serializer': as_slz.AsV4Serializer,
                    'kwargs': {

                    },
                    'obj': 'id_as'
                },
                'id_as__details': {
                    'serializer': as_slz.AsV4Serializer,
                    'kwargs': {

                    },
                    'obj': 'id_as'
                }
            }

    @staticmethod
    def setup_eager_loading_ipv4(queryset):

        log.info('Using setup_eager_loading_ipv4')
        queryset = queryset.prefetch_related(
            'ipequipamento_set',
            'ipequipamento_set__ip',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_ipv6(queryset):

        log.info('Using setup_eager_loading_ipv6')
        queryset = queryset.prefetch_related(
            'ipv6equipament_set',
            'ipv6equipament_set__ip',
        )
        return queryset
