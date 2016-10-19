# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.serializers import DynamicFieldsModelSerializer

EnvironmentVip = get_model('ambiente', 'EnvironmentVip')
OptionVip = get_model('requisicaovips', 'OptionVip')
OptionVipEnvironmentVip = get_model(
    'requisicaovips', 'OptionVipEnvironmentVip')


class EnvironmentVipSerializer(DynamicFieldsModelSerializer):
    id = serializers.Field()

    class Meta:
        model = EnvironmentVip
        default_fields = (
            'id',
            'finalidade_txt',
            'cliente_txt',
            'ambiente_p44_txt',
            'description'
        )
        fields = (
            'id',
            'finalidade_txt',
            'cliente_txt',
            'ambiente_p44_txt',
            'description',
            'conf'
        )


class OptionVipSerializer(DynamicFieldsModelSerializer):
    id = serializers.Field()

    class Meta:
        model = OptionVip
        fields = (
            'id',
            'tipo_opcao',
            'nome_opcao_txt'
        )


class OptionVipEnvironmentVipSerializer(DynamicFieldsModelSerializer):
    id = serializers.Field()
    option = OptionVipSerializer()

    class Meta:
        model = OptionVipEnvironmentVip
        fields = (
            'option',
        )
