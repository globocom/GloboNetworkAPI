# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class EnvironmentVipV3Serializer(DynamicFieldsModelSerializer):

    """Serilizes EnvironmentVip Model."""

    name = serializers.Field(source='name')

    optionsvip = serializers.SerializerMethodField('get_optionsvip')
    environments = serializers.SerializerMethodField('get_environments')

    def get_optionsvip(self, obj):

        return self.extends_serializer(obj, 'optionsvip')

    def get_environments(self, obj):
        return self.extends_serializer(obj, 'environments')

    class Meta:
        EnvironmentVip = get_model('ambiente', 'EnvironmentVip')
        model = EnvironmentVip
        fields = (
            'id',
            'finalidade_txt',
            'cliente_txt',
            'ambiente_p44_txt',
            'description',
            'name',
            'conf',
            'optionsvip',
            'environments',
        )

        default_fields = (
            'id',
            'finalidade_txt',
            'cliente_txt',
            'ambiente_p44_txt',
            'description',
        )

        details_fields = (
            'id',
            'finalidade_txt',
            'cliente_txt',
            'ambiente_p44_txt',
            'description',
            'name',
            'conf',
        )

        basic_fields = (
            'id',
            'name',
        )

    @classmethod
    def get_serializers(cls):
        """Returns the mapping of serializers."""

        if not cls.mapping:
            cls.mapping = {
                'optionsvip': {
                    'serializer': OptionVipEnvironmentVipV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': ('option',)
                    },
                    'obj': 'optionsvip',
                },
                'environments': {
                    'serializer': EnvironmentEnvironmentVipV3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': ('environment',)
                    },
                    'obj': 'environments',
                },
                'optionsvip__details': {
                    'serializer': OptionVipEnvironmentVipV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details',
                        'fields': ('option',)
                    },
                    'obj': 'optionsvip',
                },
                'environments__details': {
                    'serializer': EnvironmentEnvironmentVipV3Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details',
                        'fields': ('environment',)
                    },
                    'obj': 'environments',
                },
            }

        return cls.mapping


class OptionVipV3Serializer(DynamicFieldsModelSerializer):
    id = serializers.Field()

    class Meta:
        OptionVip = get_model('requisicaovips', 'OptionVip')
        model = OptionVip
        fields = (
            'id',
            'tipo_opcao',
            'nome_opcao_txt'
        )

        default_fields = (
            'id',
            'tipo_opcao'
        )

        details_fields = fields

    @classmethod
    def get_serializers(cls):
        """Returns the mapping of serializers."""

        return {}


class OptionVipEnvironmentVipV3Serializer(DynamicFieldsModelSerializer):

    option = serializers.SerializerMethodField('get_optionsvip')
    environment_vip = serializers.SerializerMethodField('get_environment_vip')

    def get_optionsvip(self, obj):
        return self.extends_serializer(obj, 'option')

    def get_environment_vip(self, obj):
        return self.extends_serializer(obj, 'environment')

    class Meta:
        OptionVipEnvironmentVip = get_model('requisicaovips',
                                            'OptionVipEnvironmentVip')
        model = OptionVipEnvironmentVip
        fields = (
            'option',
            'environment_vip',
        )

    @classmethod
    def get_serializers(cls):
        """Returns the mapping of serializers."""

        if not cls.mapping:
            cls.mapping = {
                'option': {
                    'obj': 'option_id',
                },
                'environment_vip': {
                    'obj': 'environment_id',
                },
                'option__details': {
                    'serializer': OptionVipV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'option'
                },
                'environment_vip__details': {
                    'serializer': EnvironmentVipV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'environment',
                },
            }
        return cls.mapping


class EnvironmentEnvironmentVipV3Serializer(DynamicFieldsModelSerializer):

    environment_vip = serializers.\
        SerializerMethodField('get_environment_vip')
    environment = serializers.\
        SerializerMethodField('get_environment')

    def get_environment_vip(self, obj):
        return self.extends_serializer(obj, 'environment_vip')

    def get_environment(self, obj):
        return self.extends_serializer(obj, 'environment')

    class Meta:
        EnvironmentEnvironmentVip = \
            get_model('ambiente', 'EnvironmentEnvironmentVip')
        model = EnvironmentEnvironmentVip

        fields = (
            'environment',
            'environment_vip',
        )

        default_fields = fields
        basic_fields = fields
        basic_fields = fields
        details_fields = fields

    @classmethod
    def get_serializers(cls):
        """Returns the mapping of serializers."""

        env_slz = get_app('api_environment', module_label='serializers')

        if not cls.mapping:
            cls.mapping = {
                'environment': {
                    'obj': 'environment_id',
                },
                'environment_vip': {
                    'obj': 'environment_vip_id',
                },
                'environment__details': {
                    'serializer': env_slz.EnvironmentV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'environment',
                },
                'environment_vip__details': {
                    'serializer': EnvironmentVipV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'environment_vip',
                },
            }
        return cls.mapping
