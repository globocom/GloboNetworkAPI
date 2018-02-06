# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class EquipmentControllerEnvironmentV4Serializer(DynamicFieldsModelSerializer):

    environment = serializers.SerializerMethodField('get_environment')
    equipment = serializers.SerializerMethodField('get_equipment')

    class Meta:
        EquipmentControllerEnvironment = get_model(
            'equipamento', 'EquipmentControllerEnvironment')
        model = EquipmentControllerEnvironment

        fields = (
            'id',
            'environment',
            'equipment',
        )

        details_fields = (
            'environment',
            'equipment',
        )

    def get_environment(self, obj):
        return self.extends_serializer(obj, 'environment')

    def get_equipment(self, obj):
        return self.extends_serializer(obj, 'equipment')

    def get_serializers(self):
        # serializers
        eqpt_slz = get_app('api_equipment', module_label='v4.serializers')
        env_slz = get_app('api_environment', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'environment': {
                    'obj': 'environment_id'
                },
                'environment__details': {
                    'serializer': env_slz.EnvironmentV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'environment'
                },
                'equipment': {
                    'obj': 'equipment_id'
                },
                'equipment__details': {
                    'serializer': eqpt_slz.EquipmentV4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'equipment'
                }
            }


class EquipmentV4Serializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')
    ipsv4 = serializers.SerializerMethodField('get_ipsv4')
    ipsv6 = serializers.SerializerMethodField('get_ipsv6')
    equipment_type = serializers.SerializerMethodField('get_equipment_type')
    model = serializers.SerializerMethodField('get_model')
    environments = serializers.SerializerMethodField('get_environments')
    sdn_controlled_environment = serializers.SerializerMethodField(
        'get_sdn_controlled_environment')
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
            'sdn_controlled_environment',
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

    def get_sdn_controlled_environment(self, obj):
        return self.extends_serializer(obj, 'sdn_controlled_environment')

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
                    'serializer': v4_ip_slz.
                    IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'prohibited': (
                            'equipment',
                        )
                    },
                    'obj': 'ipv4_equipment'
                },
                'ipsv4__basic': {
                    'serializer': v4_ip_slz.
                    IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic',
                        'prohibited': (
                            'equipment__basic',
                        )
                    },
                    'obj': 'ipv4_equipment',
                },
                'ipsv4__details': {
                    'serializer': v4_ip_slz.
                    IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details',
                        'prohibited': (
                            'equipment__details',
                        )
                    },
                    'obj': 'ipv4_equipment',
                },
                'ipsv6': {
                    'serializer': v4_ip_slz.
                    IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'prohibited': (
                            'equipment',
                        )
                    },
                    'obj': 'ipv6_equipment'
                },
                'ipsv6__basic': {
                    'serializer': v4_ip_slz.
                    IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic',
                        'prohibited': (
                            'equipment__basic',
                        ),
                    },
                    'obj': 'ipv6_equipment',
                },
                'ipsv6__details': {
                    'serializer': v4_ip_slz.
                    IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details',
                        'prohibited': (
                            'equipment__details',
                        ),
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
                    'serializer': eqptv3_slzs.
                    EquipmentEnvironmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'is_router',
                            'environment',
                        )
                    },
                    'obj': 'environments'
                },
                'environments__details': {
                    'serializer': eqptv3_slzs.
                    EquipmentEnvironmentV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'is_router',
                            'environment__details',
                        ),
                    },
                    'obj': 'environments'
                },
                'sdn_controlled_environment': {
                    'serializer': EquipmentControllerEnvironmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'environment',
                        )
                    },
                    'obj': 'equipment_controller_environment'
                },
                'sdn_controlled_environment__details': {
                    'serializer': EquipmentControllerEnvironmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'environment__details',
                        ),
                    },
                    'obj': 'equipment_controller_environment'
                },
                'asn': {
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
