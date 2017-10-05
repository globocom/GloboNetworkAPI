# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class VirtualInterfaceV4Serializer(DynamicFieldsModelSerializer):

    vrf = serializers.SerializerMethodField('get_vrf')
    ipv4_equipment = serializers.SerializerMethodField('get_ipv4_equipment')
    ipv6_equipment = serializers.SerializerMethodField('get_ipv6_equipment')

    def get_vrf(self, obj):
        return self.extends_serializer(obj, 'vrf')

    def get_ipv4_equipment(self, obj):
        return self.extends_serializer(obj, 'ipv4_equipment')

    def get_ipv6_equipment(self, obj):
        return self.extends_serializer(obj, 'ipv6_equipment')

    class Meta:
        VirtualInterface = get_model('api_virtual_interface',
                                     'VirtualInterface')
        model = VirtualInterface

        fields = (
            'id',
            'name',
            'vrf',
            'ipv4_equipment',
            'ipv6_equipment'
        )

        basic_fields = (
            'id',
            'name',
            'vrf'
        )

        default_fields = (
            'id',
            'name',
            'vrf'
        )

        details_fields = fields
              
    def get_serializers(self):
        v4_ip_slz = get_app('api_ip', module_label='v4.serializers')
        vrf_slz = get_app('api_vrf', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'ipv4_equipment': {
                    'serializer': v4_ip_slz. \
                        IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'ipv4_equipment_virtual_interface'
                },
                'ipv4_equipment__basic': {
                    'serializer': v4_ip_slz. \
                        IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic'
                    },
                    'obj': 'ipv4_equipment_virtual_interface',
                },
                'ipv4_equipment__details': {
                    'serializer': v4_ip_slz. \
                        IPv4EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'ipv4_equipment_virtual_interface',
                },
                'ipv6_equipment': {
                    'serializer': v4_ip_slz. \
                        IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'ipv6_equipment_virtual_interface'
                },
                'ipv6_equipment__basic': {
                    'serializer': v4_ip_slz. \
                        IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic'
                    },
                    'obj': 'ipv6_equipment_virtual_interface',
                },
                'ipv6_equipment__details': {
                    'serializer': v4_ip_slz. \
                        IPv6EquipmentV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details'
                    },
                    'obj': 'ipv6_equipment_virtual_interface',
                },
                'vrf': {
                    'obj': 'vrf_id'
                },
                'vrf__basic': {
                    'serializer': vrf_slz.VrfV3Serializer,
                    'kwargs': {
                        'kind': 'basic',
                    },
                    'obj': 'vrf'
                },
                'vrf__details': {
                    'serializer': vrf_slz.VrfV3Serializer,
                    'kwargs': {
                        'kind': 'details',
                    },
                    'obj': 'vrf'
                },
            }
