# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class AsV4Serializer(DynamicFieldsModelSerializer):

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

        if not self.mapping:
            self.mapping = {

                'equipments': {
                    'serializer': AsEquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'equipment',
                        )
                    },
                    'obj': 'equipments'
                },
                'equipments__details': {
                    'serializer': AsEquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'equipment__details',
                        ),
                    },
                    'obj': 'equipments'
                },
            }


class AsEquipmentV4Serializer(DynamicFieldsModelSerializer):

    id_as = serializers.SerializerMethodField('get_id_as')
    equipment = serializers.SerializerMethodField('get_equipment')

    class Meta:
        AsEquipment = get_model('api_as', 'AsEquipment')
        model = AsEquipment

        fields = (
            'id',
            'id_as',
            'equipment'
        )

    def get_id_as(self, obj):
        return self.extends_serializer(obj, 'id_as')

    def get_equipment(self, obj):
        return self.extends_serializer(obj, 'equipment')

    def get_serializers(self):

        # serializers
        as_slz = get_app('api_as', module_label='v4.serializers')
        eqpt_slz = get_app('api_equipment', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'id_as': {
                    'obj': 'id_as_id'
                },
                'id_as__details': {
                    'serializer': as_slz.AsV4Serializer,
                    'kwargs': {
                    },
                    'obj': 'id_as'
                },
                'equipment': {
                    'obj': 'equipment_id'
                },
                'equipment__details': {
                    'serializer': eqpt_slz.EquipmentV3Serializer,
                    'kwargs': {
                        'kind': 'details'

                    },
                    'obj': 'equipment'
                }
            }
