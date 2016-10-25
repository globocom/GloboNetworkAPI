# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.serializers import DynamicFieldsModelSerializer


class VrfV3Serializer(DynamicFieldsModelSerializer):

    class Meta:
        Vrf = get_model('api_vrf', 'Vrf')
        # type of Vrf variable: networkapi.api_vrf.models.Vrf
        model = Vrf

        fields = (
            'id',
            'internal_name',
            'vrf'
        )
