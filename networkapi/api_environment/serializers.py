# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.serializers import DynamicFieldsModelSerializer
from networkapi.util.serializers import RecursiveField


class IpConfigSerializer(DynamicFieldsModelSerializer):

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


class AmbienteLogicoSerializer(DynamicFieldsModelSerializer):
    name = serializers.RelatedField(source='nome')

    class Meta:
        AmbienteLogico = get_model('ambiente', 'AmbienteLogico')
        model = AmbienteLogico
        fields = (
            'id',
            'name',
        )


class DivisaoDcSerializer(DynamicFieldsModelSerializer):
    name = serializers.RelatedField(source='nome')

    class Meta:
        DivisaoDc = get_model('ambiente', 'DivisaoDc')
        model = DivisaoDc
        fields = (
            'id',
            'name',
        )


class EnvironmentSerializer(DynamicFieldsModelSerializer):
    id = serializers.Field()
    name = serializers.RelatedField(source='name')

    class Meta:
        Ambiente = get_model('ambiente', 'Ambiente')
        model = Ambiente
        fields = (
            'id',
            'name',
        )


class EnvironmentV3Serializer(DynamicFieldsModelSerializer):
    id = serializers.Field()
    name = serializers.RelatedField(source='name')
    configs = serializers.SerializerMethodField('get_configs')

    class Meta:
        Ambiente = get_model('ambiente', 'Ambiente')
        model = Ambiente
        fields = (
            'id',
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
            'configs'
        )
        default_fields = (
            'id',
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
            'father_environment'
        )

    def get_configs(self, obj):
        configs = obj.configenvironment_set.all()
        configs_serializer = IpConfigSerializer(configs, many=True)

        return configs_serializer.data

    @staticmethod
    def get_mapping_eager_loading(self):
        mapping = {
            'configs': self.setup_eager_loading_configs
        }

        return mapping

    @staticmethod
    def setup_eager_loading_configs(queryset):
        queryset = queryset.prefetch_related(
            'configenvironment_set',
            'configenvironment_set__ip_config',
        )
        return queryset


class EnvironmentDetailsSerializer(DynamicFieldsModelSerializer):
    name = serializers.RelatedField(source='name')
    children = serializers.RelatedField(source='children')
    configs = IpConfigSerializer(source='configs', many=True)

    # father_environment = RecursiveField()
    children = RecursiveField(source='children')

    father_environment = serializers.SerializerMethodField(
        'get_father_environment')
    grupo_l3 = serializers.SerializerMethodField('get_grupo_l3')
    ambiente_logico = serializers.SerializerMethodField('get_ambiente_logico')
    divisao_dc = serializers.SerializerMethodField('get_divisao_dc')

    def get_father_environment(self, obj):
        return self.extends_serializer(obj, 'father_environment')

    def get_grupo_l3(self, obj):
        return self.extends_serializer(obj, 'grupo_l3')

    def get_ambiente_logico(self, obj):
        return self.extends_serializer(obj, 'ambiente_logico')

    def get_divisao_dc(self, obj):
        return self.extends_serializer(obj, 'divisao_dc')

    class Meta:
        Ambiente = get_model('ambiente', 'Ambiente')
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

    @classmethod
    def get_serializers(cls):
        """Returns the mapping of serializers."""

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
                    'serializer': AmbienteLogicoSerializer,
                    'kwargs': {},
                    'obj': 'ambiente_logico'
                },
                'divisao_dc': {
                    'obj': 'divisao_dc_id'
                },
                'divisao_dc__details': {
                    'serializer': DivisaoDcSerializer,
                    'kwargs': {},
                    'obj': 'divisao_dc'
                },
                'father_environment': {
                    'obj': 'father_environment_id'
                },
                'father_environment__basic': {
                    'serializer': EnvironmentDetailsSerializer,
                    'kwargs': {
                        'fields': (
                            'id',
                            'father_environment__basic',
                        )
                    },
                    'obj': 'father_environment'
                },
                'father_environment__details': {
                    'serializer': EnvironmentDetailsSerializer,
                    'kwargs': {
                        'include': (
                            'father_environment__details',
                        )
                    },
                    'obj': 'father_environment'
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
