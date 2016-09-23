# -*- coding:utf-8 -*-
from rest_framework import serializers

from networkapi.api_environment import serializers as env_serializers
from networkapi.api_equipment import serializers as eqpt_serializers
from networkapi.api_group import serializers as grp_serializers
from networkapi.api_pools.models import OptionPool
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.ip.models import Ip
from networkapi.ip.models import Ipv6
from networkapi.requisicaovips.models import ServerPool
from networkapi.requisicaovips.models import ServerPoolGroupPermission
from networkapi.requisicaovips.models import ServerPoolMember
from networkapi.util.serializers import DynamicFieldsModelSerializer


class Ipv4BasicSerializer(serializers.ModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')

    class Meta:
        model = Ip
        fields = (
            'id',
            'ip_formated'
        )


class PoolPermissionSerializer(serializers.ModelSerializer):

    group = serializers.Field(source='user_group.id')

    class Meta:
        model = ServerPoolGroupPermission
        fields = (
            'group',
            'read',
            'write',
            'change_config',
            'delete'
        )


class PoolPermissionDetailsSerializer(serializers.ModelSerializer):

    group = grp_serializers.UserGroupSerializer(source='user_group')

    class Meta:
        model = ServerPoolGroupPermission
        fields = (
            'group',
            'read',
            'write',
            'change_config',
            'delete'
        )


class Ipv6BasicSerializer(serializers.ModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')

    class Meta:
        model = Ipv6
        fields = (
            'id',
            'ip_formated'
        )


class Ipv4DetailsSerializer(serializers.ModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')
    description = serializers.Field(source='descricao')

    class Meta:
        model = Ip
        fields = (
            'id',
            'ip_formated',
            'description'
        )


class Ipv6DetailsSerializer(serializers.ModelSerializer):

    id = serializers.Field()
    ip_formated = serializers.Field(source='ip_formated')
    description = serializers.Field(source='descricao')

    class Meta:
        model = Ipv6
        fields = (
            'id',
            'ip_formated',
            'description'
        )


class OptionPoolV3DetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = OptionPool
        depth = 1
        fields = ('id',
                  'type',
                  'name'
                  )


class OptionPoolV3Serializer(serializers.ModelSerializer):

    class Meta:
        model = OptionPool
        depth = 1
        fields = ('id',
                  'name'
                  )


class HealthcheckV3Serializer(serializers.ModelSerializer):

    class Meta:
        model = Healthcheck
        fields = (
            'identifier',
            'healthcheck_type',
            'healthcheck_request',
            'healthcheck_expect',
            'destination'
        )


class PoolV3SimpleSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    server_pool_members = serializers.SerializerMethodField('get_server_pool_members')

    def get_server_pool_members(self, obj):
        members = obj.serverpoolmember_set.all()
        members_serializer = PoolMemberBasicSerializer(members, many=True)

        return members_serializer.data

    class Meta:
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'environment',
            'server_pool_members',
            'pool_created'
        )


class PoolV3MinimumSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'default_port',
            'environment',
            'pool_created'
        )


class PoolMemberBasicSerializer(serializers.ModelSerializer):

    id = serializers.Field()
    ipv6 = Ipv6BasicSerializer()
    ip = Ipv4BasicSerializer()
    last_status_update_formated = serializers.Field(source='last_status_update_formated')

    class Meta:
        depth = 1
        model = ServerPoolMember
        fields = (
            'id',
            'identifier',
            'ipv6',
            'priority',
            'ip',
            'port_real',
            'last_status_update_formated',
            'member_status'
        )


class PoolMemberV3Serializer(serializers.ModelSerializer):
    id = serializers.Field()

    ipv6 = serializers.SerializerMethodField('get_ipv6')
    ip = serializers.SerializerMethodField('get_ip')
    last_status_update_formated = serializers.Field(source='last_status_update_formated')

    equipment = eqpt_serializers.EquipmentBasicSerializer()

    def get_ipv6(self, obj):
        obj_ipv6 = None
        if obj.ipv6:
            obj_ipv6 = {
                'id': obj.ipv6_id,
                'ip_formated': obj.ipv6.ip_formated
            }
        return obj_ipv6

    def get_ip(self, obj):
        obj_ip = None
        if obj.ip:
            obj_ip = {
                'id': obj.ip_id,
                'ip_formated': obj.ip.ip_formated
            }
        return obj_ip

    class Meta:
        depth = 1
        model = ServerPoolMember
        fields = (
            'id',
            'identifier',
            'ipv6',
            'ip',
            'priority',
            'equipment',
            'weight',
            'limit',
            'port_real',
            'last_status_update_formated',
            'member_status'
        )


class PoolV3Serializer(serializers.ModelSerializer):
    id = serializers.Field()
    server_pool_members = serializers.SerializerMethodField('get_server_pool_members')
    # groups_permissions = serializers.SerializerMethodField('get_perms')
    healthcheck = HealthcheckV3Serializer()
    servicedownaction = OptionPoolV3Serializer()

    # def get_perms(self, obj):
    #     perms = obj.serverpoolgrouppermission_set.all()
    #     perms_serializer = PoolPermissionSerializer(perms, many=True)

    #     return perms_serializer.data

    def get_server_pool_members(self, obj):
        members = obj.serverpoolmember_set.all()
        members_serializer = PoolMemberV3Serializer(members, many=True)

        return members_serializer.data

    class Meta:
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'default_port',
            'environment',
            'servicedownaction',
            'lb_method',
            'healthcheck',
            'default_limit',
            'server_pool_members',
            # 'groups_permissions',
            'pool_created'
        )


class PoolV3DatatableSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    server_pool_members = serializers.SerializerMethodField('get_server_pool_members')

    healthcheck = HealthcheckV3Serializer()
    servicedownaction = OptionPoolV3Serializer()
    environment = serializers.RelatedField(source='environment.name')

    def get_server_pool_members(self, obj):
        members = obj.serverpoolmember_set.all()
        members_serializer = PoolMemberV3Serializer(members, many=True)

        return members_serializer.data

    class Meta:
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'default_port',
            'environment',
            'servicedownaction',
            'lb_method',
            'healthcheck',
            'default_limit',
            'server_pool_members',
            'pool_created'
        )


class PoolV3DetailsSerializer(DynamicFieldsModelSerializer):
    id = serializers.Field()
    server_pool_members = serializers.SerializerMethodField('get_server_pool_members')
    groups_permissions = serializers.SerializerMethodField('get_perms')
    healthcheck = HealthcheckV3Serializer()
    servicedownaction = OptionPoolV3DetailsSerializer()
    environment = env_serializers.EnvironmentSerializer()

    def get_server_pool_members(self, obj):
        members = obj.serverpoolmember_set.all()
        members_serializer = PoolMemberV3Serializer(members, many=True)

        return members_serializer.data

    def get_perms(self, obj):
        perms = obj.serverpoolgrouppermission_set.all()
        perms_serializer = PoolPermissionDetailsSerializer(perms, many=True)

        return perms_serializer.data

    class Meta:
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'default_port',
            'environment',
            'servicedownaction',
            'lb_method',
            'healthcheck',
            'default_limit',
            'server_pool_members',
            'groups_permissions',
            'pool_created'
        )

# class PoolMemberDynamicSerializer(DynamicFieldsModelSerializer):
#     id = serializers.Field()

#     equipment = eqpt_serializers.EquipmentBasicSerializer()

#     @staticmethod
#     def setup_eager_loading(queryset):
#         queryset = queryset.prefetch_related(
#             'ipv6',
#             'ip',
#         )
#         return queryset

#     class Meta:
#         depth = 1
#         model = ServerPoolMember
#         fields = (
#             'id',
#             'identifier',
#             'ipv6',
#             'ip',
#             'priority',
#             'equipment',
#             'weight',
#             'limit',
#             'port_real',
#             'last_status_update_formated',
#             'member_status'
#         )


# class PoolDynamicSerializer(DynamicFieldsModelSerializer):


#     server_pool_members = PoolMemberDynamicSerializer(source='serverpoolmember_set')

#     @staticmethod
#     def setup_eager_loading(queryset):
#         queryset = queryset.prefetch_related(
#             'serverpoolmember_set',
#         )
#         return queryset

#     class Meta:
#         model = ServerPool
#         fields = (
#             'id',
#             'identifier',
#             'default_port',
#             'environment',
#             'servicedownaction',
#             'lb_method',
#             'healthcheck',
#             'default_limit',
#             'server_pool_members',
#             'pool_created'
#         )
