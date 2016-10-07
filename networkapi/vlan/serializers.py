# -*- coding: utf-8 -*-
from rest_framework import serializers

from networkapi.api_network.serializers import NetworkIPv4Serializer
from networkapi.api_network.serializers import NetworkIPv6Serializer
from networkapi.vlan.models import Vlan


class VlanSerializer(serializers.ModelSerializer):

    id_vlan = serializers.Field(source='id')

    id_environment = serializers.RelatedField(
        source='ambiente.id'
    )

    networks_ipv4 = NetworkIPv4Serializer(
        many=True, source='networkipv4_set.select_related')
    networks_ipv6 = NetworkIPv6Serializer(
        many=True, source='networkipv6_set.select_related')

    class Meta:
        model = Vlan
        fields = (
            'id_vlan',
            'num_vlan',
            'id_environment',
            'networks_ipv4',
            'networks_ipv6',
        )
