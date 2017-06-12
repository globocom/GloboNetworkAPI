# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class AsV3Serializer(DynamicFieldsModelSerializer):

    equipments = serializers.SerializerMethodField('get_equipments')

    def get_equipments(self, obj):
        return self.extends_serializer(obj, 'equipments')

    class Meta:
        As_ = get_model('api_as', 'As')
        model = As_

        fields = (
            'id',
            'name',
            'description',
            'equipments'
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
                'equipments': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'equipments',
                },
                'equipments__basic': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic'
                    },
                    'obj': 'equipments',
                },
                'equipments__details': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'equipments',
                }
            }
