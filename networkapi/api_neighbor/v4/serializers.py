# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class NeighborV4Serializer(DynamicFieldsModelSerializer):

    class Meta:
        Neighbor = get_model('api_neighbor',
                             'Neighbor')
        model = Neighbor

        fields = (
            'id',
            'description',
        )

        basic_fields = (
            'id',
            'description',
        )

        default_fields = (
            'id',
            'description',
        )

        details_fields = fields
