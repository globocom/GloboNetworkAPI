# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.serializers import DynamicFieldsModelSerializer


class EnvironmentVipV3Serializer(DynamicFieldsModelSerializer):

    """Serilizes EnvironmentVip Model."""

    name = serializers.Field(source='name')

    class Meta:
        EnvironmentVip = get_model('ambiente', 'EnvironmentVip')
        model = EnvironmentVip
        fields = (
            'id',
            'finalidade_txt',
            'cliente_txt',
            'ambiente_p44_txt',
            'description',
            'name',
            'conf'
        )

        default_fields = (
            'id',
            'finalidade_txt',
            'cliente_txt',
            'ambiente_p44_txt',
            'description',
        )

        details_fields = fields

        basic_fields = (
            'id',
            'name',
        )

    @classmethod
    def get_serializers(cls):
        """Returns the mapping of serializers."""
        pass


class OptionVipV3Serializer(DynamicFieldsModelSerializer):
    id = serializers.Field()

    class Meta:
        OptionVip = get_model('requisicaovips', 'OptionVip')
        model = OptionVip
        fields = (
            'id',
            'tipo_opcao',
            'nome_opcao_txt'
        )

        default_fields = (
            'id',
            'tipo_opcao'
        )

    @classmethod
    def get_serializers(cls):
        """Returns the mapping of serializers."""
        pass


class OptionVipEnvironmentVipV3Serializer(DynamicFieldsModelSerializer):
    id = serializers.Field()
    option = OptionVipV3Serializer()

    class Meta:
        OptionVipEnvironmentVip = get_model('requisicaovips',
                                            'OptionVipEnvironmentVip')
        model = OptionVipEnvironmentVip
        fields = (
            'option',
        )

    @classmethod
    def get_serializers(cls):
        """Returns the mapping of serializers."""
        pass
