# -*- coding:utf-8 -*-
from networkapi.equipamento.models import Equipamento

from rest_framework import serializers


class EquipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Equipamento
        fields = (
            'id',
            'tipo_equipamento',
            'modelo',
            'nome',
            'grupos'
        )


class EquipmentBasicSerializer(serializers.ModelSerializer):

    name = serializers.Field(source='nome')

    class Meta:
        model = Equipamento
        fields = (
            'id',
            'name'
        )
