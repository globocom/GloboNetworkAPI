from rest_framework import serializers
from networkapi.requisicaovips.models import VipPortToPool
from networkapi.ambiente.models import Ambiente


class VipPortToPoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = VipPortToPool
        fields = (
            'id',
            'requisicao_vip',
            'server_pool',
            'port_vip',
        )


class EnvironmentOptionsSerializer(serializers.ModelSerializer):

    name = serializers.Field()

    class Meta:
        model = Ambiente
        fields = (
            'id',
            'name'
        )
