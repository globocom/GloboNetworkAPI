# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class NeighborV4Serializer(DynamicFieldsModelSerializer):

    virtual_interface = serializers.\
        SerializerMethodField('get_virtual_interface')

    class Meta:
        Neighbor = get_model('api_neighbor',
                             'Neighbor')
        model = Neighbor

        fields = (
            'id',
            'description',
            'virtual_interface'
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

    def get_virtual_interface(self, obj):
        return self.extends_serializer(obj, 'virtual_interface')

    def get_serializers(self):
        vi_slz = get_app('api_virtual_interface', 'v4.serializers')

        if not self.mapping:

            self.mapping = {
                'virtual_interface': {
                    'obj': 'virtual_interface_id'
                },
                'virtual_interface__details': {
                    'serializer': vi_slz.VirtualInterfaceV4Serializer,
                    'kwargs': {

                    },
                    'obj': 'virtual_interface'
                },
            }
