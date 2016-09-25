# -*- coding:utf-8 -*-
from rest_framework import serializers

from networkapi.equipamento.models import Equipamento
from networkapi.util.serializers import DynamicFieldsModelSerializer


class EquipmentSerializer(serializers.ModelSerializer):

    equipment_type = serializers.Field(source='tipo_equipamento')
    model = serializers.Field(source='modelo')
    name = serializers.Field(source='nome')
    # groups = serializers.Field(source='grupos')

    class Meta:
        model = Equipamento
        fields = (
            'id',
            'name',
            'equipment_type',
            'model'
        )


class EquipmentBasicSerializer(serializers.ModelSerializer):

    name = serializers.Field(source='nome')

    class Meta:
        model = Equipamento
        fields = (
            'id',
            'name'
        )


class EquipmentV3Serializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')

    class Meta:
        model = Equipamento
        fields = (
            'id',
            'name'
        )
