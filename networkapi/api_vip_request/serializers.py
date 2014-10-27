from rest_framework import serializers
from networkapi.requisicaovips.models import VipPortToPool


class VipPortToPoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = VipPortToPool
        fields = (
            'id',
            'requisicao_vip',
            'server_pool',
            'port_vip',
        )
