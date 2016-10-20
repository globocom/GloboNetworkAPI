# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.serializers import DynamicFieldsModelSerializer


class EnvironmentVipSerializer(DynamicFieldsModelSerializer):

    """Serilizes EnvironmentVip Model."""

    class Meta:
        EnvironmentVip = get_model('ambiente', 'EnvironmentVip')
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

    @classmethod
    def get_serializers(cls):
        """Returns the mapping of serializers."""
        pass


class OptionVipSerializer(DynamicFieldsModelSerializer):
    id = serializers.Field()

    class Meta:
        OptionVip = get_model('requisicaovips', 'OptionVip')
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
        OptionVipEnvironmentVip = get_model('requisicaovips',
                                            'OptionVipEnvironmentVip')
        model = OptionVipEnvironmentVip
        fields = (
            'option',
        )
