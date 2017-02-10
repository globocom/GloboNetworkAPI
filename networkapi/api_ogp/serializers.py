# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class ObjectTypeV3Serializer(DynamicFieldsModelSerializer):

    class Meta:
        ObjectType = get_model('api_ogp', 'ObjectType')

        model = ObjectType
        fields = (
            'id',
            'name'
        )
        default_fields = (
            'id',
            'name'
        )


class ObjectGroupPermissionV3Serializer(DynamicFieldsModelSerializer):

    user_group = serializers.SerializerMethodField('get_user_group')
    object_type = serializers.SerializerMethodField('get_object_type')

    def get_user_group(self, obj):
        return self.extends_serializer(obj, 'user_group')

    def get_object_type(self, obj):
        return self.extends_serializer(obj, 'object_type')

    class Meta:
        ObjectGroupPermission = get_model('api_ogp',
                                          'ObjectGroupPermission')
        model = ObjectGroupPermission
        fields = (
            'id',
            'user_group',
            'object_type',
            'object_value',
            'read',
            'write',
            'change_config',
            'delete'
        )
        default_fields = (
            'user_group',
            'object_type',
            'object_value',
            'read',
            'write',
            'change_config',
            'delete'
        )

    def get_serializers(self):
        # serializers
        group_slz = get_app('api_group', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'user_group': {
                    'obj': 'user_group_id',
                },
                'user_group__details': {
                    'serializer': group_slz.UserGroupV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'user_group',
                },
                'object_type': {
                    'obj': 'object_type_id',
                },
                'object_type__details': {
                    'serializer': ObjectTypeV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'object_type',
                },
            }


class ObjectGroupPermissionGeneralV3Serializer(DynamicFieldsModelSerializer):

    user_group = serializers.SerializerMethodField('get_user_group')
    object_type = serializers.SerializerMethodField('get_object_type')

    def get_user_group(self, obj):
        return self.extends_serializer(obj, 'user_group')

    def get_object_type(self, obj):
        return self.extends_serializer(obj, 'object_type')

    class Meta:
        ObjectGroupPermissionGeneral = get_model(
            'api_ogp',
            'ObjectGroupPermissionGeneral')

        model = ObjectGroupPermissionGeneral
        fields = (
            'id',
            'user_group',
            'object_type',
            'read',
            'write',
            'change_config',
            'delete'
        )
        default_fields = (
            'id',
            'user_group',
            'object_type',
            'read',
            'write',
            'change_config',
            'delete'
        )

    def get_serializers(self):
        # serializers
        group_slz = get_app('api_group', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'user_group': {
                    'obj': 'user_group_id',
                },
                'user_group__details': {
                    'serializer': group_slz.UserGroupV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'user_group',
                },
                'object_type': {
                    'obj': 'object_type_id',
                },
                'object_type__details': {
                    'serializer': ObjectTypeV3Serializer,
                    'kwargs': {
                    },
                    'obj': 'object_type',
                },
            }
