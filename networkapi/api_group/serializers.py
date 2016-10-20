# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.serializers import DynamicFieldsModelSerializer


class UserGroupSerializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')

    class Meta:
        UGrupo = get_model('grupo', 'UGrupo')
        model = UGrupo
        fields = (
            'id',
            'name'
        )
