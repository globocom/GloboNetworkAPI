from rest_framework import serializers
from networkapi.requisicaovips.models import VipPortToPool, RequisicaoVips
from networkapi.ambiente.models import Ambiente


class VipPortToPoolSerializer(serializers.ModelSerializer):

    server_pool = serializers.PrimaryKeyRelatedField(
        many=False,
    )

    requisicao_vip = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True
    )

    class Meta:
        model = VipPortToPool
        fields = (
            'id',
            'requisicao_vip',
            'server_pool',
            'port_vip',
        )


class RequesVipSerializer(serializers.ModelSerializer):

    ip = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True
    )

    ipv6 = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True
    )

    healthcheck_expect = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True
    )

    rule = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True
    )

    rule_applied = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True
    )

    rule_rollback = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True
    )

    class Meta:
        model = RequisicaoVips
        fields = (
            'id', 'ip', 'ipv6', 'l7_filter',
            'filter_applied', 'filter_rollback',
            'filter_valid', 'applied_l7_datetime',
            'healthcheck_expect', 'rule', 'rule_applied',
            'rule_rollback'
        )

class EnvironmentOptionsSerializer(serializers.ModelSerializer):

    name = serializers.Field()

    class Meta:
        model = Ambiente
        fields = (
            'id',
            'name'
        )
