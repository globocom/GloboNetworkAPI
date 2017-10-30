# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model

from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class EquipmentV4Serializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')
    ipsv4 = serializers.SerializerMethodField('get_ipsv4')
    ipsv6 = serializers.SerializerMethodField('get_ipsv6')
    equipment_type = serializers.SerializerMethodField('get_equipment_type')
    model = serializers.SerializerMethodField('get_model')
    environments = serializers.SerializerMethodField('get_environments')
    groups = serializers.SerializerMethodField('get_groups')
    asn = serializers.SerializerMethodField('get_asn')

    class Meta:
        Equipment = get_model('equipamento', 'Equipamento')
        model = Equipment
        fields = (
            'id',
            'name',
            'maintenance',
            'equipment_type',
            'model',
            'ipsv4',
            'ipsv6',
            'environments',
            'groups',
            'asn'
        )

        basic_fields = (
            'id',
            'name'
        )

        default_fields = (
            'id',
            'name',
            'maintenance',
            'equipment_type',
            'model',
        )

        details_fields = fields

    def get_model(self, obj):
        return self.extends_serializer(obj, 'model')

    def get_equipment_type(self, obj):
        return self.extends_serializer(obj, 'equipment_type')

    def get_groups(self, obj):
        return self.extends_serializer(obj, 'groups')

    def get_environments(self, obj):
        return self.extends_serializer(obj, 'environments')

    def get_ipsv4(self, obj):
        return self.extends_serializer(obj, 'ipsv4')

    def get_ipsv6(self, obj):
        return self.extends_serializer(obj, 'ipsv6')

    def get_asn(self, obj):
        return self.extends_serializer(obj, 'asn')

    def get_serializers(self):
        eqptv3_slzs = get_app('api_equipment', module_label='serializers')
        v4_ip_slz = get_app('api_ip', module_label='v4.serializers')
        grp_slz = get_app('api_group', module_label='serializers')
        asn_slz = get_app('api_asn', module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {
                'model': {
                    'obj': 'modelo_id'
                },
                'model__details': {
                    'serializer': eqptv3_slzs.ModelV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'modelo'
                },
                'equipment_type': {
                    'obj': 'tipo_equipamento_id'
                },
                'equipment_type__details': {
                    'serializer': eqptv3_slzs.EquipmentTypeV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'tipo_equipamento'
                },
                'ipsv4': {
                    'serializer': v4_ip_slz. \
                        IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'ipv4_equipment'
                },
                'ipsv4__basic': {
                    'serializer': v4_ip_slz. \
                        IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic'
                    },
                    'obj': 'ipv4_equipment',
                },
                'ipsv4__details': {
                    'serializer': v4_ip_slz. \
                        IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'ipv4_equipment',
                },
                'ipsv6': {
                    'serializer': v4_ip_slz. \
                        IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'ipv6_equipment'
                },
                'ipsv6__basic': {
                    'serializer': v4_ip_slz. \
                        IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic'
                    },
                    'obj': 'ipv6_equipment',
                },
                'ipsv6__details': {
                    'serializer': v4_ip_slz. \
                        IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'ipv6_equipment',
                },
                'groups': {
                    'serializer': grp_slz.EquipmentGroupV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'id',
                        )
                    },
                    'obj': 'groups'
                },
                'groups__details': {
                    'serializer': grp_slz.EquipmentGroupV3Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'groups'
                },
                'environments': {
                    'serializer': eqptv3_slzs.\
                        EquipmentEnvironmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'is_router',
                            'is_controller',
                            'environment',
                        )
                    },
                    'obj': 'environments'
                },
                'environments__details': {
                    'serializer': eqptv3_slzs.\
                        EquipmentEnvironmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'is_router',
                            'is_controller',
                            'environment__details',
                        ),
                    },
                    'obj': 'environments'
                },
                'asn':{
                    'obj': 'asn_id'
                },
                'asn__basic': {
                    'serializer': asn_slz.AsnV4Serializer,
                    'kwargs': {

                    },
                    'obj': 'asn'
                },
                'asn__details': {
                    'serializer': asn_slz.AsnV4Serializer,
                    'kwargs': {

                    },
                    'obj': 'asn'
                }
            }
