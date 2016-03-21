# -*- coding:utf-8 -*-
from networkapi.ambiente.models import EnvironmentVip
from networkapi.requisicaovips.models import OptionVip, OptionVipEnvironmentVip

from rest_framework import serializers


class EnvironmentVipSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    class Meta:
        model = EnvironmentVip
        fields = (
            'id',
            'finalidade_txt',
            'cliente_txt',
            'ambiente_p44_txt',
            'description'
        )


class OptionVipSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    class Meta:
        model = OptionVip
        fields = (
            'id',
            'tipo_opcao',
            'nome_opcao_txt'
        )


class OptionVipEnvironmentVipSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    option = OptionVipSerializer()

    class Meta:
        model = OptionVipEnvironmentVip
        fields = (
            'id',
            'option',
        )
