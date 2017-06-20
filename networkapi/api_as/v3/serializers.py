# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class AsV3Serializer(DynamicFieldsModelSerializer):

    equipment = serializers.SerializerMethodField('get_equipment')

    def get_equipment(self, obj):
        return self.extends_serializer(obj, 'equipment')

    class Meta:
        As_ = get_model('api_as', 'As')
        model = As_

        fields = (
            'id',
            'name',
            'description',
            'equipment'
        )

        basic_fields = (
            'id',
            'name'
        )

        default_fields = (
            'id',
            'name',
            'description'
        )

        details_fields = fields

    def get_serializers(self):
        # serializers
        eqpt_slz = get_app('api_equipment', module_label='serializers')

        if not self.mapping:
            self.mapping = {

                'equipment': {
                    'obj': 'equipment_id'
                },
                'equipment__basic': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {

                    },
                    'obj': 'equipment'
                },
                'equipment__details': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {

                    },
                    'obj': 'equipment'
                }
            }
