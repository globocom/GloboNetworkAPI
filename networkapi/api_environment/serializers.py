# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.serializers import DynamicFieldsModelSerializer
# from networkapi.ambiente.models import IPConfig

Ambiente = get_model('ambiente', 'Ambiente')
AmbienteLogico = get_model('ambiente', 'AmbienteLogico')
ConfigEnvironment = get_model('ambiente', 'ConfigEnvironment')
DivisaoDc = get_model('ambiente', 'DivisaoDc')
GrupoL3 = get_model('ambiente', 'GrupoL3')


class GrupoL3Serializer(DynamicFieldsModelSerializer):
    name = serializers.RelatedField(source='nome')

    class Meta:
        model = GrupoL3
        fields = (
            'id',
            'name',
        )


class AmbienteLogicoSerializer(DynamicFieldsModelSerializer):
    name = serializers.RelatedField(source='nome')

    class Meta:
        model = AmbienteLogico
        fields = (
            'id',
            'name',
        )


class DivisaoDcSerializer(DynamicFieldsModelSerializer):
    name = serializers.RelatedField(source='nome')

    class Meta:
        model = DivisaoDc
        fields = (
            'id',
            'name',
        )


class EnvironmentSerializer(DynamicFieldsModelSerializer):
    id = serializers.Field()
    name = serializers.RelatedField(source='name')

    class Meta:
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
    id = serializers.Field()
    name = serializers.RelatedField(source='name')
    configs = serializers.SerializerMethodField('get_configs')

    grupo_l3 = GrupoL3Serializer()
    ambiente_logico = AmbienteLogicoSerializer()
    divisao_dc = DivisaoDcSerializer()

    class Meta:
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


class IpConfigSerializer(DynamicFieldsModelSerializer):

    id = serializers.RelatedField(source='ip_config.id')
    subnet = serializers.RelatedField(source='ip_config.subnet')
    new_prefix = serializers.RelatedField(source='ip_config.new_prefix')
    type = serializers.RelatedField(source='ip_config.type')
    network_type = serializers.RelatedField(source='ip_config.network_type.id')

    class Meta:
        model = ConfigEnvironment
        fields = (
            'id',
            'subnet',
            'new_prefix',
            'type',
            'network_type'
        )
