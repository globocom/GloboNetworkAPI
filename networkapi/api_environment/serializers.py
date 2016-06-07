# -*- coding:utf-8 -*-
from networkapi.ambiente.models import Ambiente

from rest_framework import serializers


class EnvironmentSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    name = serializers.RelatedField(source='name')

    class Meta:
        model = Ambiente
        fields = (
            'id',
            'name',
        )
