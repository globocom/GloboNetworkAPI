# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class AsnV4Serializer(DynamicFieldsModelSerializer):

    equipments = serializers.SerializerMethodField('get_equipments')

    def get_equipments(self, obj):
        return self.extends_serializer(obj, 'equipments')

    class Meta:
        Asn = get_model('api_asn', 'Asn')
        model = Asn

        fields = (
            'id',
            'name',
            'description',
            'equipments'
        )

        basic_fields = fields

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
                    'serializer': AsnEquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'equipment',
                        )
                    },
                    'obj': 'equipments'
                },
                'equipments__basic': {
                    'serializer': AsnEquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'equipment__basic',
                        )
                    },
                    'obj': 'equipments'
                },
                'equipments__details': {
                    'serializer': AsnEquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'equipment__details',
                        ),
                    },
                    'obj': 'equipments'
                },
            }


class AsnEquipmentV4Serializer(DynamicFieldsModelSerializer):

    asn = serializers.SerializerMethodField('get_asn')
    equipment = serializers.SerializerMethodField('get_equipment')

    class Meta:
        AsnEquipment = get_model('api_asn', 'AsnEquipment')
        model = AsnEquipment

        fields = (
            'id',
            'asn',
            'equipment'
        )

    def get_asn(self, obj):
        return self.extends_serializer(obj, 'asn')

    def get_equipment(self, obj):
        return self.extends_serializer(obj, 'equipment')

    def get_serializers(self):

        # serializers
        asn_slz = get_app('api_asn', module_label='v4.serializers')
        eqpt_slz = get_app('api_equipment', module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {
                'asn': {
                    'obj': 'asn_id'
                },
                'asn__details': {
                    'serializer': asn_slz.AsnV4Serializer,
                    'kwargs': {
                    },
                    'obj': 'asn'
                },
                'equipment': {
                    'obj': 'equipment_id'
                },
                'equipment__basic': {
                    'serializer': eqpt_slz.EquipmentV4Serializer,
                    'kwargs': {
                        'kind': 'basic'

                    },
                    'obj': 'equipment'
                },
                'equipment__details': {
                    'serializer': eqpt_slz.EquipmentV4Serializer,
                    'kwargs': {
                        'kind': 'details'

                    },
                    'obj': 'equipment'
                }
            }
