# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.api_group import serializers as grp_serializers
from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

# serializers
envvip_slz = get_app('api_environment_vip', module_label='serializers')

ip_slz = get_app('api_network', module_label='serializers.v1')


class VipRequestOptionVipSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    optionvip = envvip_slz.OptionVipSerializer()

    class Meta:
        VipRequestOptionVip = get_model('api_vip_request',
                                        'VipRequestOptionVip')
        model = VipRequestOptionVip
        fields = (
            'id',
            'optionvip',
        )


class VipRequestPortPoolSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    l7_rule = serializers.Field(source='optionvip.id')
    l7_value = serializers.Field(source='val_optionvip')

    class Meta:
        VipRequestPortPool = get_model('api_vip_request',
                                       'VipRequestPortPool')
        model = VipRequestPortPool
        fields = (
            'id',
            'server_pool',
            'l7_rule',
            'l7_value',
            'order'
        )


class VipRequestPortSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    options = serializers.SerializerMethodField('get_options')

    def get_options(self, obj):
        options = obj.viprequestportoptionvip_set.all()
        opt = {
            'l7_protocol': None,
            'l4_protocol': None
        }
        for option in options:
            if option.optionvip.tipo_opcao == 'l7_protocol':
                opt['l7_protocol'] = option.optionvip.id
            elif option.optionvip.tipo_opcao == 'l4_protocol':
                opt['l4_protocol'] = option.optionvip.id

        return opt

    pools = serializers.SerializerMethodField('get_server_pools')

    def get_server_pools(self, obj):
        pools = obj.viprequestportpool_set.all()
        pools_serializer = VipRequestPortPoolSerializer(pools, many=True)

        return pools_serializer.data

    class Meta:
        VipRequestPort = get_model('api_vip_request', 'VipRequestPort')
        model = VipRequestPort
        fields = (
            'id',
            'port',
            'options',
            'pools',
        )


class EnvironmentOptionsSerializer(serializers.ModelSerializer):

    name = serializers.Field()

    class Meta:
        Ambiente = get_model('ambiente', 'Ambiente')
        model = Ambiente
        fields = (
            'id',
            'name'
        )


# class VipRequestListSerializer(serializers.ModelSerializer):

#     eqpt = serializers.SerializerMethodField('get_eqpt')

#     ipv4 = Ipv4Serializer()

#     ipv6 = Ipv6Serializer()

#     environmentvip = EnvironmentVipSerializer(
#         fields=(
#             'id',
#             'finalidade_txt',
#             'cliente_txt',
#             'ambiente_p44_txt',
#             'description'
#         )
#     )

#     def get_eqpt(self, obj):
#         eqpts = list()
#         equipments = list()
#         if obj.ipv4:
#             eqpts = obj.ipv4.ipequipamento_set.all()
#         if obj.ipv6:
#             eqpts |= obj.ipv6.ipv6equipament_set.all()

#         for eqpt in eqpts:
#             equipments.append(eqpt.equipamento)
#         eqpt_serializer = EquipmentSerializer(equipments, many=True)

#         return eqpt_serializer.data

#     class Meta:
#         model = VipRequest
#         fields = (
#             'environmentvip',
#             'ipv4',
#             'ipv6',
#             'eqpt',
#         )


class VipRequestSerializer(DynamicFieldsModelSerializer):
    id = serializers.Field()

    options = serializers.SerializerMethodField('get_options')
    ports = serializers.SerializerMethodField('get_server_pools')
    # groups_permissions = serializers.SerializerMethodField('get_perms')

    def get_options(self, obj):
        options = obj.viprequestoptionvip_set.all()
        opt = {
            'traffic_return': None,
            'cache_group': None,
            'persistence': None,
            'timeout': None,
        }
        for option in options:
            if option.optionvip.tipo_opcao == 'cache':
                opt['cache_group'] = option.optionvip.id
            elif option.optionvip.tipo_opcao == 'Persistencia':
                opt['persistence'] = option.optionvip.id
            elif option.optionvip.tipo_opcao == 'Retorno de trafego':
                opt['traffic_return'] = option.optionvip.id
            elif option.optionvip.tipo_opcao == 'timeout':
                opt['timeout'] = option.optionvip.id

        return opt

    def get_server_pools(self, obj):
        ports = obj.viprequestport_set.all()
        ports_serializer = VipRequestPortSerializer(ports, many=True)

        return ports_serializer.data

    # def get_perms(self, obj):
    #     perms = obj.viprequestgrouppermission_set.all()
    #     perms_serializer = VipRequestPermSerializer(perms, many=True)

    #     return perms_serializer.data

    class Meta:
        VipRequest = get_model('api_vip_request', 'VipRequest')
        model = VipRequest
        fields = (
            'id',
            'name',
            'service',
            'business',
            'environmentvip',
            'ipv4',
            'ipv6',
            'ports',
            'options',
            # 'groups_permissions',
            'created'
        )


class VipRequestPermSerializer(serializers.ModelSerializer):

    group = serializers.Field(source='user_group.id')

    class Meta:
        VipRequestGroupPermission = get_model('api_vip_request',
                                              'VipRequestGroupPermission')
        model = VipRequestGroupPermission
        fields = (
            'group',
            'read',
            'write',
            'change_config',
            'delete'
        )


class VipRequestPermDetailsSerializer(serializers.ModelSerializer):

    group = grp_serializers.UserGroupSerializer(source='user_group')

    class Meta:
        VipRequestGroupPermission = get_model('api_vip_request',
                                              'VipRequestGroupPermission')
        model = VipRequestGroupPermission
        fields = (
            'group',
            'read',
            'write',
            'change_config',
            'delete'
        )


# details
class VipRequestDetailsSerializer(DynamicFieldsModelSerializer):

    eqpt_slz = get_app('api_equipment', module_label='serializers')

    dscp = serializers.RelatedField(source='dscp')
    default_names = serializers.RelatedField(source='default_names')

    # equipments = eqpt_slz.EquipmentSerializer(source='equipments', many=True)
    ports = VipRequestPortSerializer(source='ports', many=True)

    environmentvip = envvip_slz.EnvironmentVipSerializer(
        fields=(
            'id',
            'finalidade_txt',
            'cliente_txt',
            'ambiente_p44_txt',
            'description'
        )
    )

    ipv4 = ip_slz.Ipv4Serializer(
        fields=(
            'id',
            'ip_formated',
            'description',
        )
    )

    ipv6 = ip_slz.Ipv6Serializer(
        fields=(
            'id',
            'ip_formated',
            'description',
        )
    )

    options = serializers.SerializerMethodField('get_options')

    groups_permissions = serializers.SerializerMethodField('get_perms')

    def get_options(self, obj):
        options = obj.viprequestoptionvip_set.all()
        opt = {
            'traffic_return': None,
            'cache_group': None,
            'persistence': None,
            'timeout': None,
        }
        for option in options:
            if option.optionvip.tipo_opcao == 'cache':
                opt['cache_group'] = envvip_slz.OptionVipSerializer(
                    option.optionvip).data
            elif option.optionvip.tipo_opcao == 'Persistencia':
                opt['persistence'] = envvip_slz.OptionVipSerializer(
                    option.optionvip).data
            elif option.optionvip.tipo_opcao == 'Retorno de trafego':
                opt['traffic_return'] = envvip_slz.OptionVipSerializer(
                    option.optionvip).data
            elif option.optionvip.tipo_opcao == 'timeout':
                opt['timeout'] = envvip_slz.OptionVipSerializer(
                    option.optionvip).data

        return opt

    def get_perms(self, obj):
        perms = obj.viprequestgrouppermission_set.all()
        perms_serializer = VipRequestPermDetailsSerializer(perms, many=True)

        return perms_serializer.data

    class Meta:
        VipRequest = get_model('api_vip_request', 'VipRequest')
        model = VipRequest
        fields = (
            'id',
            'name',
            'service',
            'business',
            'environmentvip',
            'ipv4',
            'ipv6',
            # 'equipments',
            'default_names',
            'dscp',
            'ports',
            'options',
            'groups_permissions',
            'created'
        )


class VipRequestPortDetailsSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    options = serializers.SerializerMethodField('get_options')

    def get_options(self, obj):
        options = obj.viprequestportoptionvip_set.all()
        opt = {
            'l7_protocol': None,
            'l4_protocol': None
        }
        for option in options:
            if option.optionvip.tipo_opcao == 'l7_protocol':
                opt['l7_protocol'] = envvip_slz.OptionVipSerializer(
                    option.optionvip).data
            elif option.optionvip.tipo_opcao == 'l4_protocol':
                opt['l4_protocol'] = envvip_slz.OptionVipSerializer(
                    option.optionvip).data

        return opt

    pools = serializers.SerializerMethodField('get_server_pools')

    def get_server_pools(self, obj):
        pools = obj.viprequestportpool_set.all()
        pools_serializer = VipRequestPortPoolDetailsSerializer(
            pools, many=True)

        return pools_serializer.data

    class Meta:
        VipRequestPort = get_model('api_vip_request', 'VipRequestPort')
        model = VipRequestPort
        fields = (
            'id',
            'port',
            'options',
            'pools',
        )


class VipRequestPortPoolDetailsSerializer(serializers.ModelSerializer):
    pool_slz = get_app('api_pools', module_label='serializers.v3')

    server_pool = pool_slz.PoolV3Serializer()
    l7_rule = envvip_slz.OptionVipSerializer(source='optionvip')
    l7_value = serializers.Field(source='val_optionvip')

    class Meta:
        VipRequestPortPool = get_model('api_vip_request',
                                       'VipRequestPortPool')
        model = VipRequestPortPool
        fields = (
            'id',
            'server_pool',
            'l7_rule',
            'l7_value',
            'order'
        )
