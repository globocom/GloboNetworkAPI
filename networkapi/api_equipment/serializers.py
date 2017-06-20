# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class EquipmentEnvironmentV3Serializer(DynamicFieldsModelSerializer):

    environment = serializers.SerializerMethodField('get_environment')
    equipment = serializers.SerializerMethodField('get_equipment')

    class Meta:
        EquipamentoAmbiente = get_model('equipamento', 'EquipamentoAmbiente')
        model = EquipamentoAmbiente
        fields = (
            'is_router',
            'is_controller',
            'environment',
            'equipment',
        )

    def get_environment(self, obj):
        return self.extends_serializer(obj, 'environment')

    def get_equipment(self, obj):
        return self.extends_serializer(obj, 'equipment')

    def get_serializers(self):
        # serializers
        eqpt_slz = get_app('api_equipment', module_label='serializers')
        env_slz = get_app('api_environment', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'environment': {
                    'obj': 'ambiente_id'
                },
                'environment__details': {
                    'serializer': env_slz.EnvironmentV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'ambiente'
                },
                'equipment': {
                    'obj': 'equipamento_id'
                },
                'equipment__details': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'equipamento'
                }
            }

    @staticmethod
    def setup_eager_loading_networkipv4(queryset):

        log.info('Using setup_eager_loading_networkipv4')
        queryset = queryset.select_related(
            'networkipv4',
        )
        return queryset


class BrandV3Serializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')

    class Meta:
        Marca = get_model('equipamento', 'Marca')
        model = Marca
        fields = (
            'id',
            'name'
        )


class ModelV3Serializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')

    brand = serializers.SerializerMethodField('get_brand')

    def get_brand(self, obj):

        return self.extends_serializer(obj.marca, 'brand')

    def get_serializers(self):
        if not self.mapping:
            self.mapping = {
                'brand': {
                    'serializer': BrandV3Serializer,
                    'kwargs': {
                        'source': 'id'
                    }
                },
                'brand__details': {
                    'serializer': BrandV3Serializer,
                    'kwargs': {
                    }
                },
            }

    class Meta:
        Modelo = get_model('equipamento', 'Modelo')
        model = Modelo
        fields = (
            'id',
            'name',
            'brand'
        )

        default_fields = (
            'id',
            'name'
        )


class EquipmentTypeV3Serializer(DynamicFieldsModelSerializer):

    equipment_type = serializers.Field(source='tipo_equipamento')

    class Meta:
        TipoEquipamento = get_model('equipamento', 'TipoEquipamento')
        model = TipoEquipamento
        fields = (
            'id',
            'equipment_type'
        )


class EquipmentV3Serializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')
    ipv4 = serializers.SerializerMethodField('get_ipv4')
    ipv6 = serializers.SerializerMethodField('get_ipv6')
    equipment_type = serializers.SerializerMethodField('get_equipment_type')
    model = serializers.SerializerMethodField('get_model')
    environments = serializers.SerializerMethodField('get_environments')
    groups = serializers.SerializerMethodField('get_groups')

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

    def get_serializers(self):
        ip_slz = get_app('api_ip', module_label='serializers')
        grp_slz = get_app('api_group', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'model': {
                    'obj': 'modelo_id'
                },
                'model__details': {
                    'serializer': ModelV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'modelo'
                },
                'equipment_type': {
                    'obj': 'tipo_equipamento_id'
                },
                'equipment_type__details': {
                    'serializer': EquipmentTypeV3Serializer,
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
                    'serializer': EquipmentEnvironmentV3Serializer,
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
                    'serializer': EquipmentEnvironmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'is_router',
                            'is_controller',
                            'environment__details',
                        ),
                    },
                    'obj': 'environments'
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
