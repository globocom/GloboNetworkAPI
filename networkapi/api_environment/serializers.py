# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class IpConfigV3Serializer(DynamicFieldsModelSerializer):

    id = serializers.RelatedField(source='ip_config.id')
    subnet = serializers.RelatedField(source='ip_config.subnet')
    new_prefix = serializers.RelatedField(source='ip_config.new_prefix')
    type = serializers.RelatedField(source='ip_config.type')
    network_type = serializers.RelatedField(source='ip_config.network_type.id')

    class Meta:
        ConfigEnvironment = get_model('ambiente', 'ConfigEnvironment')
        model = ConfigEnvironment
        fields = (
            'id',
            'subnet',
            'new_prefix',
            'type',
            'network_type'
        )


class GrupoL3Serializer(DynamicFieldsModelSerializer):
    name = serializers.RelatedField(source='nome')

    class Meta:
        GrupoL3 = get_model('ambiente', 'GrupoL3')
        model = GrupoL3
        fields = (
            'id',
            'name',
        )


class AmbienteLogicoV3Serializer(DynamicFieldsModelSerializer):
    name = serializers.RelatedField(source='nome')

    class Meta:
        AmbienteLogico = get_model('ambiente', 'AmbienteLogico')
        model = AmbienteLogico
        fields = (
            'id',
            'name',
        )


class DivisaoDcV3Serializer(DynamicFieldsModelSerializer):
    name = serializers.RelatedField(source='nome')

    class Meta:
        DivisaoDc = get_model('ambiente', 'DivisaoDc')
        model = DivisaoDc
        fields = (
            'id',
            'name',
        )


class EnvironmentV3Serializer(DynamicFieldsModelSerializer):

    configs = IpConfigV3Serializer(source='configs', many=True)

    father_environment = serializers.SerializerMethodField(
        'get_father_environment')
    grupo_l3 = serializers.SerializerMethodField('get_grupo_l3')
    ambiente_logico = serializers.SerializerMethodField('get_ambiente_logico')
    divisao_dc = serializers.SerializerMethodField('get_divisao_dc')
    children = serializers.SerializerMethodField('get_children')
    filter = serializers.SerializerMethodField('get_filter')
    default_vrf = serializers.SerializerMethodField('get_default_vrf')
    routers = serializers.SerializerMethodField('get_routers')
    equipments = serializers.SerializerMethodField('get_equipments')
    name = serializers.SerializerMethodField('get_name')
    sdn_controlled = serializers.BooleanField()

    def get_name(self, obj):
        return self.extends_serializer(obj, 'name')

    def get_default_vrf(self, obj):
        return self.extends_serializer(obj, 'default_vrf')

    def get_children(self, obj):
        return self.extends_serializer(obj, 'children')

    def get_father_environment(self, obj):
        return self.extends_serializer(obj, 'father_environment')

    def get_grupo_l3(self, obj):
        return self.extends_serializer(obj, 'grupo_l3')

    def get_ambiente_logico(self, obj):
        return self.extends_serializer(obj, 'ambiente_logico')

    def get_divisao_dc(self, obj):
        return self.extends_serializer(obj, 'divisao_dc')

    def get_filter(self, obj):
        return self.extends_serializer(obj, 'filter')

    def get_routers(self, obj):
        return self.extends_serializer(obj, 'routers')

    def get_equipments(self, obj):
        return self.extends_serializer(obj, 'equipments')

    class Meta:
        Ambiente = get_model('ambiente', 'Ambiente')
        depth = 1
        model = Ambiente
        fields = (
            'id',
            'name',
            'grupo_l3',
            'ambiente_logico',
            'divisao_dc',
            'filter',
            'acl_path',
            'ipv4_template',
            'ipv6_template',
            'link',
            'min_num_vlan_1',
            'max_num_vlan_1',
            'min_num_vlan_2',
            'max_num_vlan_2',
            'vrf',
            'default_vrf',
            'father_environment',
            'children',
            'configs',
            'routers',
            'equipments',
            'sdn_controlled',
        )
        default_fields = (
            'id',
            'name',
            'grupo_l3',
            'ambiente_logico',
            'divisao_dc',
            'filter',
            'acl_path',
            'ipv4_template',
            'ipv6_template',
            'link',
            'min_num_vlan_1',
            'max_num_vlan_1',
            'min_num_vlan_2',
            'max_num_vlan_2',
            'default_vrf',
            'father_environment',
            'sdn_controlled',
        )

        basic_fields = (
            'id',
            'name',
        )

        details_fields = default_fields

    def get_serializers(self):
        """Returns the mapping of serializers."""

        filter_slz = get_app('api_filter', module_label='serializers')
        eqpt_slz = get_app('api_equipment', module_label='serializers')
        vrf_slz = get_app('api_vrf', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'name': {
                    'obj': 'name',
                    'eager_loading': self.setup_eager_loading_name
                },
                'grupo_l3': {
                    'obj': 'grupo_l3_id'
                },
                'grupo_l3__details': {
                    'serializer': GrupoL3Serializer,
                    'kwargs': {},
                    'obj': 'grupo_l3',
                    'eager_loading': self.setup_eager_loading_grupo_l3
                },
                'ambiente_logico': {
                    'obj': 'ambiente_logico_id'
                },
                'ambiente_logico__details': {
                    'serializer': AmbienteLogicoV3Serializer,
                    'kwargs': {},
                    'obj': 'ambiente_logico',
                    'eager_loading': self.setup_eager_loading_ambiente_logico
                },
                'divisao_dc': {
                    'obj': 'divisao_dc_id'
                },
                'divisao_dc__details': {
                    'serializer': DivisaoDcV3Serializer,
                    'kwargs': {},
                    'obj': 'divisao_dc',
                    'eager_loading': self.setup_eager_loading_divisao_dc
                },
                'filter': {
                    'obj': 'filter_id'
                },
                'filter__details': {
                    'serializer': filter_slz.FilterV3Serializer,
                    'kwargs': {},
                    'obj': 'filter',
                    'eager_loading': self.setup_eager_loading_filter
                },
                'default_vrf': {
                    'obj': 'default_vrf_id'
                },
                'default_vrf__basic': {
                    'serializer': vrf_slz.VrfV3Serializer,
                    'kwargs': {
                        'fields': (
                            'id',
                            'vrf',
                        ),
                        'kind': 'basic'
                    },
                    'obj': 'default_vrf',
                    'eager_loading': self.setup_eager_loading_default_vrf
                },
                'default_vrf__details': {
                    'serializer': vrf_slz.VrfV3Serializer,
                    'kwargs': {
                        'fields': (
                            'id',
                            'vrf',
                            'internal_name'
                        )
                    },
                    'obj': 'default_vrf',
                    'eager_loading': self.setup_eager_loading_default_vrf
                },

                'father_environment': {
                    'obj': 'father_environment_id'
                },
                'father_environment__basic': {
                    'serializer': EnvironmentV3Serializer,
                    'kwargs': {
                        'fields': (
                            'id',
                            'name',
                            'father_environment__basic',
                        )
                    },
                    'obj': 'father_environment',
                    'eager_loading': self.setup_eager_loading_father
                },
                'father_environment__details': {
                    'serializer': EnvironmentV3Serializer,
                    'kwargs': {
                        'include': (
                            'father_environment__details',
                        )
                    },
                    'obj': 'father_environment',
                    'eager_loading': self.setup_eager_loading_father
                },
                'children': {
                    'serializer': EnvironmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'id',
                            'name',
                            'children',
                        )
                    },
                    'obj': 'children'
                },
                'children__details': {
                    'serializer': EnvironmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'include': (
                            'children__details',
                        ),
                        'prohibited': (
                            'father_environment__details',
                        )

                    },
                    'obj': 'children'
                },
                'routers': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'id',
                        )
                    },
                    'obj': 'routers'
                },
                'routers__details': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'routers'
                },
                'equipments': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'id',
                        )
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
                }
            }

    @staticmethod
    def setup_eager_loading_father(queryset):
        log.info('Using setup_eager_loading_father')
        queryset = queryset.prefetch_related(
            'father_environment',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_name(queryset):
        log.info('Using setup_eager_loading_name')
        queryset = queryset.select_related(
            'ambiente_logico',
            'grupo_l3',
            'divisao_dc',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_ambiente_logico(queryset):
        log.info('Using setup_eager_loading_ambiente_logico')
        queryset = queryset.select_related(
            'ambiente_logico',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_grupo_l3(queryset):
        log.info('Using setup_eager_loading_grupo_l3')
        queryset = queryset.select_related(
            'grupo_l3',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_divisao_dc(queryset):
        log.info('Using setup_eager_loading_divisao_dc')
        queryset = queryset.select_related(
            'divisao_dc',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_filter(queryset):
        log.info('Using setup_eager_loading_filter')
        queryset = queryset.select_related(
            'filter',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_default_vrf(queryset):
        log.info('Using setup_eager_loading_default_vrf')
        queryset = queryset.select_related(
            'default_vrf',
        )
        return queryset
