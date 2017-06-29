# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class VirtualInterfaceV4Serializer(DynamicFieldsModelSerializer):

    vrf = serializers.SerializerMethodField('get_vrf')

    def get_vrf(self, obj):
        return self.extends_serializer(obj, 'vrf')

    class Meta:
        VirtualInterface = get_model('api_virtual_interface', 'VirtualInterface')
        model = VirtualInterface

        fields = (
            'id',
            'name',
            'vrf'
        )

        basic_fields = (
            'id',
            'name',
        )

        default_fields = (
            'id',
            'name',
        )

        details_fields = fields

    def get_serializers(self):
        # serializers

        vrf_slz = get_app('api_vrf', module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {

                'vrf': {
                    'obj': 'vrf_id'
                },
                'vrf__details': {
                    'serializer': vrf_slz.VrfV3Serializer,
                    'kwargs': {

                    },
                    'obj': 'vrf'
                },
            }

