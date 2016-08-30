# -*- coding:utf-8 -*-
from rest_framework import serializers

from networkapi.ambiente.models import Ambiente
from networkapi.util.serializers import DynamicFieldsModelSerializer


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
            'name',
        )
