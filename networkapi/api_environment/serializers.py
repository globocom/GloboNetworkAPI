# -*- coding:utf-8 -*-
from rest_framework import serializers

from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteLogico
from networkapi.ambiente.models import DivisaoDc
from networkapi.ambiente.models import GrupoL3
from networkapi.util.serializers import DynamicFieldsModelSerializer


class GrupoL3Serializer(serializers.ModelSerializer):
    name = serializers.RelatedField(source='nome')

    class Meta:
        model = GrupoL3
        fields = (
            'id',
            'name',
        )


class AmbienteLogicoSerializer(serializers.ModelSerializer):
    name = serializers.RelatedField(source='nome')

    class Meta:
        model = AmbienteLogico
        fields = (
            'id',
            'name',
        )


class DivisaoDcSerializer(serializers.ModelSerializer):
    name = serializers.RelatedField(source='nome')

    class Meta:
        model = DivisaoDc
        fields = (
            'id',
            'name',
        )


class EnvironmentSerializer(serializers.ModelSerializer):
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
            'father_environment'
        )


class EnvironmentDetaailsSerializer(DynamicFieldsModelSerializer):
    id = serializers.Field()
    name = serializers.RelatedField(source='name')

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
            'filter'
        )
