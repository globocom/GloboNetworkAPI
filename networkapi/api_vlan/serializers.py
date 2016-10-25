# -*- coding: utf-8 -*-
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class VlanSerializerV3(DynamicFieldsModelSerializer):
    name = serializers.Field(source='nome')
    description = serializers.Field(source='descricao')
    active = serializers.Field(source='ativada')
    environment = serializers.SerializerMethodField('get_environment')

    def get_environment(self, obj):
        return self.extends_serializer(obj, 'environment')

    vrfs = serializers.SerializerMethodField('get_vrfs')

    def get_vrfs(self, obj):
        return self.extends_serializer(obj, 'vrfs')

    class Meta:
        vlan_model = get_app('vlan', module_label='models')
        model = vlan_model.Vlan
        fields = (
            'id',
            'name',
            'num_vlan',
            'environment',
            'description',
            'acl_file_name',
            'acl_valida',
            'acl_file_name_v6',
            'acl_valida_v6',
            'active',
            'vrf',
            'acl_draft',
            'acl_draft_v6',
            'vrfs',
        )
        default_fields = (
            'id',
            'name',
            'num_vlan',
            'environment',
            'description',
            'acl_file_name',
            'acl_valida',
            'acl_file_name_v6',
            'acl_valida_v6',
            'active',
            'vrf',
            'acl_draft',
            'acl_draft_v6',
        )

    @classmethod
    def get_serializers(cls):
        """Returns the mapping of serializers."""
        env_slz = get_app('api_environment', module_label='serializers')
        vrf_slz = get_app('api_vrf', module_label='serializers')
        if not cls.mapping:
            cls.mapping = {
                'environment': {
                    'obj': 'ambiente_id'
                },
                'environment__details': {
                    'serializer': env_slz.EnvironmentDetailsSerializer,
                    'kwargs': {
                    },
                    'obj': 'ambiente',
                    'eager_loading': cls.setup_eager_loading_environment
                },

                'vrfs': {
                    'serializer': vrf_slz.VrfV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': ('id',)
                    },
                    'obj': 'vrfs'
                },
                'vrfs__details': {
                    'serializer': vrf_slz.VrfV3Serializer,
                    'kwargs': {
                        'many': True,
                    },
                    'obj': 'vrfs'
                },
            }

        return cls.mapping

    @staticmethod
    def setup_eager_loading_environment(queryset):
        """Eager loading of environment for related Vlan."""
        queryset = queryset.select_related(
            'environment',
        )
        return queryset
