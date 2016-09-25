# -*- coding:utf-8 -*-
from rest_framework import serializers

from networkapi.ambiente.models import EnvironmentVip
from networkapi.requisicaovips.models import OptionVip
from networkapi.requisicaovips.models import OptionVipEnvironmentVip
from networkapi.util.serializers import DynamicFieldsModelSerializer


class EnvironmentVipSerializer(DynamicFieldsModelSerializer):
    id = serializers.Field()

    class Meta:
        model = EnvironmentVip
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
