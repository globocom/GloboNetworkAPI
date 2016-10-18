# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

UGrupo = get_model('grupo', 'UGrupo')


class UserGroupSerializer(serializers.ModelSerializer):

    name = serializers.Field(source='nome')

    class Meta:
        model = UGrupo
        fields = (
            'id',
            'name'
        )
