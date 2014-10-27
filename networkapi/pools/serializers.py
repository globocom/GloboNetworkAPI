from rest_framework import serializers
from networkapi.infrastructure.script_utils import exec_script
from networkapi.requisicaovips.models import ServerPool, ServerPoolMember, VipPortToPool
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.equipamento.models import Equipamento
from networkapi.pools.models import OpcaoPoolAmbiente, OpcaoPool
from networkapi.settings import POOL_REAL_CHECK


class ServerPoolDatatableSerializer(serializers.ModelSerializer):

    healthcheck = serializers.RelatedField(
        source='healthcheck.healthcheck_type'
    )

    environment = serializers.RelatedField(
        source='environment.name'
    )


    class Meta:
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'default_port',
            'healthcheck',
            'environment',
            'pool_created'
        )




class ServerPoolMemberSerializer(serializers.ModelSerializer):

    pool_enabled = serializers.SerializerMethodField('check_pool_member_enabled')

    class Meta:
        depth = 1
        model = ServerPoolMember
        fields = ('id',
                  'server_pool',
                  'identifier',
                  'ipv6', 'ip',
                  'priority',
                  'weight',
                  'limit',
                  'port_real',
                  'healthcheck',
                  'pool_enabled'
                  )

    def check_pool_member_enabled(self, obj):

        command = POOL_REAL_CHECK % (obj.server_pool.id, obj.ip.id, obj.port_real)

        code, _, _ = exec_script(command)

        if code == 0:
            return True

        return False


class ServerPoolSerializer(serializers.ModelSerializer):

    class Meta:
        depth = 1
        model = ServerPool
        fields = (
            'id',
            'identifier',
            'default_port',
            'healthcheck',
            'environment',
            'pool_created',
            'lb_method'
        )


class HealthcheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Healthcheck
        fields = ('id',
                  'identifier',
                  'healthcheck_type',
                  'healthcheck_request',
                  'healthcheck_expect',
                  'destination'
                  )

class EquipamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipamento
        fields = ('id',
                  'tipo_equipamento',
                  'modelo',
                  'nome',
                  'grupos'
                 )

class OpcaoPoolAmbienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcaoPoolAmbiente
        depth = 1
        fields = ('id',
                  'opcao_pool',
                  'ambiente'
                 )


class VipPortToPoolSerializer(serializers.ModelSerializer):

    environment_vip_ipv4 = serializers.RelatedField(
        source='requisicao_vip.ip.networkipv4.ambient_vip.name'
    )

    environment_vip_ipv6 = serializers.RelatedField(
        source='requisicao_vip.ipv6.networkipv6.ambient_vip.name'
    )

    class Meta:
        model = VipPortToPool
        depth = 2
        fields = ('id',
                  'requisicao_vip',
                  'server_pool',
                  'port_vip',
                  'environment_vip_ipv4',
                  'environment_vip_ipv6'
                 )
