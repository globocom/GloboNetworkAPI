# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.api_vrf.serializers import VrfV3Serializer
from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


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
    name = serializers.RelatedField(source='name')
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
            'vrf',
            'default_vrf',
        )

        basic_fields = (
            'id',
            'name',
        )

        details_fields = fields

    @classmethod
    def get_serializers(cls):
        """Returns the mapping of serializers."""

        filter_slz = get_app('api_filter', module_label='serializers')
        eqpt_slz = get_app('api_equipment', module_label='serializers')

        if not cls.mapping:
            cls.mapping = {
                'grupo_l3': {
                    'obj': 'grupo_l3_id'
                },
                'grupo_l3__details': {
                    'serializer': GrupoL3Serializer,
                    'kwargs': {},
                    'obj': 'grupo_l3'
                },
                'ambiente_logico': {
                    'obj': 'ambiente_logico_id'
                },
                'ambiente_logico__details': {
                    'serializer': AmbienteLogicoV3Serializer,
                    'kwargs': {},
                    'obj': 'ambiente_logico'
                },
                'divisao_dc': {
                    'obj': 'divisao_dc_id'
                },
                'divisao_dc__details': {
                    'serializer': DivisaoDcV3Serializer,
                    'kwargs': {},
                    'obj': 'divisao_dc'
                },
                'filter': {
                    'obj': 'filter_id'
                },
                'filter__details': {
                    'serializer': filter_slz.FilterV3Serializer,
                    'kwargs': {},
                    'obj': 'filter'
                },
                'default_vrf': {
                    'obj': 'default_vrf_id'
                },
                'default_vrf__details': {
                    'serializer': VrfV3Serializer,
                    'kwargs': {
                        'include': (
                            'default_vrf__details',
                        )
                    },
                    'obj': 'default_vrf'
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
                    'obj': 'father_environment'
                },
                'father_environment__details': {
                    'serializer': EnvironmentV3Serializer,
                    'kwargs': {
                        'include': (
                            'father_environment__details',
                        )
                    },
                    'obj': 'father_environment'
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
            }

        return cls.mapping

    @staticmethod
    def setup_eager_loading_father(queryset):
        queryset = queryset.prefetch_related(
            'father_environment_set',
            'father_environment_set__environment',
        )
        return queryset
