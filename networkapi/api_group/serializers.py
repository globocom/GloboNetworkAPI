# -*- coding: utf-8 -*-
from rest_framework import serializers

from networkapi.grupo.models import UGrupo


class UserGroupSerializer(serializers.ModelSerializer):

    name = serializers.Field(source='nome')

    class Meta:
        model = UGrupo
        fields = (
            'id',
            'name'
        )
