# -*- coding:utf-8 -*-
from rest_framework import serializers

from networkapi.ambiente.models import Ambiente
from networkapi.api_environment_vip.serializers import EnvironmentVipSerializer
from networkapi.api_environment_vip.serializers import OptionVipSerializer
from networkapi.api_equipment.serializers import EquipmentSerializer
from networkapi.api_group import serializers as grp_serializers
from networkapi.api_pools.serializers import Ipv4DetailsSerializer
from networkapi.api_pools.serializers import Ipv4Serializer
from networkapi.api_pools.serializers import Ipv6DetailsSerializer
from networkapi.api_pools.serializers import Ipv6Serializer
from networkapi.api_pools.serializers import PoolV3DetailsSerializer
from networkapi.api_vip_request.models import VipRequest
from networkapi.api_vip_request.models import VipRequestGroupPermission
from networkapi.api_vip_request.models import VipRequestOptionVip
from networkapi.api_vip_request.models import VipRequestPort
from networkapi.api_vip_request.models import VipRequestPortPool
from networkapi.util.serializers import DynamicFieldsModelSerializer


class VipRequestOptionVipSerializer(serializers.ModelSerializer):
    id = serializers.Field()
    optionvip = OptionVipSerializer()

    class Meta:
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
        model = Ambiente
        fields = (
            'id',
            'name'
        )


class VipRequestListSerializer(serializers.ModelSerializer):

    eqpt = serializers.SerializerMethodField('get_eqpt')

    ipv4 = Ipv4Serializer()

    ipv6 = Ipv6Serializer()

    environmentvip = EnvironmentVipSerializer(
        fields=(
            'id',
            'finalidade_txt',
            'cliente_txt',
            'ambiente_p44_txt',
            'description'
        )
    )

    def get_eqpt(self, obj):
        eqpts = list()
        equipments = list()
        if obj.ipv4:
            eqpts = obj.ipv4.ipequipamento_set.all()
        if obj.ipv6:
            eqpts |= obj.ipv6.ipv6equipament_set.all()

        for eqpt in eqpts:
            equipments.append(eqpt.equipamento)
        eqpt_serializer = EquipmentSerializer(equipments, many=True)

        return eqpt_serializer.data

    class Meta:
        model = VipRequest
        fields = (
            'environmentvip',
            'ipv4',
            'ipv6',
            'eqpt',
        )


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
        model = VipRequestGroupPermission
        fields = (
            'group',
            'read',
            'write',
            'change_config',
            'delete'
        )


class VipRequestTableSerializer(DynamicFieldsModelSerializer):
    id = serializers.Field()

    business = serializers.CharField(
        required=True
    )

    service = serializers.CharField(
        required=True
    )

    name = serializers.CharField(
        required=True
    )

    options = serializers.SerializerMethodField('get_options')

    equipments = serializers.SerializerMethodField('get_eqpt')

    environmentvip = EnvironmentVipSerializer(
        fields=(
            'id',
            'finalidade_txt',
            'cliente_txt',
            'ambiente_p44_txt',
            'description'
        )
    )

    ipv4 = Ipv4DetailsSerializer()

    ipv6 = Ipv6DetailsSerializer()

    def get_eqpt(self, obj):
        eqpts = list()
        equipments = list()
        if obj.ipv4:
            eqpts = obj.ipv4.ipequipamento_set.all()
        if obj.ipv6:
            eqpts |= obj.ipv6.ipv6equipament_set.all()

        for eqpt in eqpts:
            equipments.append(eqpt.equipamento)
        eqpt_serializer = EquipmentSerializer(equipments, many=True)

        return eqpt_serializer.data

    def get_server_pools(self, obj):
        ports = obj.viprequestport_set.all()
        ports_serializer = VipRequestPortSerializer(ports, many=True)

        return ports_serializer.data

    dscp = serializers.SerializerMethodField('get_dscp')

    def get_dscp(self, obj):
        try:
            dscp = obj.viprequestdscp_set.get().dscp
        except:
            dscp = None
        return dscp

    default_names = serializers.SerializerMethodField('get_default_names')

    def get_default_names(self, obj):
        ip = obj.ipv4.ip_formated if obj.ipv4 else obj.ipv6.ip_formated
        names = list()
        for port in obj.viprequestport_set.all():
            names.append('VIP%s_%s_%s' % (obj.id, ip, port.port))
        return names

    class Meta:
        model = VipRequest
        fields = (
            'id',
            # 'name',
            # 'service',
            # 'business',
            'environmentvip',
            'ipv4',
            'ipv6',
            # 'ports',
            # 'options',
            'equipments',
            'default_names',
            'dscp',
            'created'
        )


# details
class VipRequestDetailsSerializer(DynamicFieldsModelSerializer):
    id = serializers.Field()

    environmentvip = EnvironmentVipSerializer(
        fields=(
            'id',
            'finalidade_txt',
            'cliente_txt',
            'ambiente_p44_txt',
            'description'
        )
    )

    ipv4 = Ipv4DetailsSerializer()

    ipv6 = Ipv6DetailsSerializer()

    options = serializers.SerializerMethodField('get_options')

    equipments = serializers.SerializerMethodField('get_eqpt')

    default_names = serializers.SerializerMethodField('get_default_names')

    dscp = serializers.SerializerMethodField('get_dscp')

    ports = serializers.SerializerMethodField('get_server_pools')

    groups_permissions = serializers.SerializerMethodField('get_perms')

    def get_dscp(self, obj):
        try:
            dscp = obj.viprequestdscp_set.get().dscp
        except:
            dscp = None
        return dscp

    def get_default_names(self, obj):
        ip = obj.ipv4.ip_formated if obj.ipv4 else obj.ipv6.ip_formated
        names = list()
        for port in obj.viprequestport_set.all():
            names.append('VIP%s_%s_%s' % (obj.id, ip, port.port))
        return names

    def get_eqpt(self, obj):
        eqpts = list()
        equipments = list()
        if obj.ipv4:
            eqpts = obj.ipv4.ipequipamento_set.all()
        if obj.ipv6:
            eqpts |= obj.ipv6.ipv6equipament_set.all()

        for eqpt in eqpts:
            equipments.append(eqpt.equipamento)
        eqpt_serializer = EquipmentSerializer(equipments, many=True)

        return eqpt_serializer.data

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
                opt['cache_group'] = OptionVipSerializer(option.optionvip).data
            elif option.optionvip.tipo_opcao == 'Persistencia':
                opt['persistence'] = OptionVipSerializer(option.optionvip).data
            elif option.optionvip.tipo_opcao == 'Retorno de trafego':
                opt['traffic_return'] = OptionVipSerializer(option.optionvip).data
            elif option.optionvip.tipo_opcao == 'timeout':
                opt['timeout'] = OptionVipSerializer(option.optionvip).data

        return opt

    def get_perms(self, obj):
        perms = obj.viprequestgrouppermission_set.all()
        perms_serializer = VipRequestPermDetailsSerializer(perms, many=True)

        return perms_serializer.data

    def get_server_pools(self, obj):
        ports = obj.viprequestport_set.all()
        ports_serializer = VipRequestPortDetailsSerializer(ports, many=True)

        return ports_serializer.data

    class Meta:
        model = VipRequest
        fields = (
            'id',
            'name',
            'service',
            'business',
            'environmentvip',
            'ipv4',
            'ipv6',
            'equipments',
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
                opt['l7_protocol'] = OptionVipSerializer(option.optionvip).data
            elif option.optionvip.tipo_opcao == 'l4_protocol':
                opt['l4_protocol'] = OptionVipSerializer(option.optionvip).data

        return opt

    pools = serializers.SerializerMethodField('get_server_pools')

    def get_server_pools(self, obj):
        pools = obj.viprequestportpool_set.all()
        pools_serializer = VipRequestPortPoolDetailsSerializer(pools, many=True)

        return pools_serializer.data

    class Meta:
        model = VipRequestPort
        fields = (
            'id',
            'port',
            'options',
            'pools',
        )


class VipRequestPortPoolDetailsSerializer(serializers.ModelSerializer):
    id = serializers.Field()

    server_pool = PoolV3DetailsSerializer()
    l7_rule = OptionVipSerializer(source='optionvip')
    l7_value = serializers.Field(source='val_optionvip')

    class Meta:
        model = VipRequestPortPool
        fields = (
            'id',
            'server_pool',
            'l7_rule',
            'l7_value',
            'order'
        )
