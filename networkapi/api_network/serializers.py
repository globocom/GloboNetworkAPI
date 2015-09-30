from rest_framework import serializers
from networkapi.ip.models import NetworkIPv4, NetworkIPv6
from networkapi.api_network.models import DHCPRelayIPv4, DHCPRelayIPv6

class DHCPRelayIPv4Serializer(serializers.ModelSerializer):
    id = serializers.Field()
    ipv4 = serializers.PrimaryKeyRelatedField()
    networkipv4 = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = DHCPRelayIPv4
        fields = (
            'id',
            'ipv4',
            'networkipv4',
            )

class DHCPRelayIPv6Serializer(serializers.ModelSerializer):
    id = serializers.Field()
    ipv6 = serializers.Field()
    networkipv6 = serializers.Field()

    class Meta:
        model = DHCPRelayIPv6
        fields = (
            'id',
            'ipv6',
            'networkipv6',
            )

class NetworkIPv4Serializer(serializers.ModelSerializer):

    id = serializers.Field()
    oct1 = serializers.Field()
    oct2 = serializers.Field()
    oct3 = serializers.Field()
    oct4 = serializers.Field()
    block = serializers.Field()
    mask_oct1 = serializers.Field()
    mask_oct2 = serializers.Field()
    mask_oct3 = serializers.Field()
    mask_oct4 = serializers.Field()
    broadcast = serializers.Field()
    vlan = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True
    )
    network_type = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True
    )
    ambient_vip = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True
    )
    active = serializers.Field()

    dhcprelay = DHCPRelayIPv4Serializer()

    class Meta:
        model = NetworkIPv4
        fields = (
            'id',
            'oct1',
            'oct2',
            'oct3',
            'oct4',
            'block',
            'mask_oct1',
            'mask_oct2',
            'mask_oct3',
            'mask_oct4',
            'broadcast',
            'vlan',
            'network_type',
            'ambient_vip',
            'active',
            'dhcprelay'
        )


class NetworkIPv6Serializer(serializers.ModelSerializer):

    id = serializers.Field()
    vlan = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True
    )
    network_type = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True
    )
    ambient_vip = serializers.PrimaryKeyRelatedField(
        many=False,
        required=True
    )
    block1 = serializers.Field()
    block2 = serializers.Field()
    block3 = serializers.Field()
    block4 = serializers.Field()
    block5 = serializers.Field()
    block6 = serializers.Field()
    block7 = serializers.Field()
    block8 = serializers.Field()
    block = serializers.Field()
    mask1 = serializers.Field()
    mask2 = serializers.Field()
    mask3 = serializers.Field()
    mask4 = serializers.Field()
    mask5 = serializers.Field()
    mask6 = serializers.Field()
    mask7 = serializers.Field()
    mask8 = serializers.Field()
    active = serializers.Field()

    class Meta:
        model = NetworkIPv6
        fields = (
            'id',
            'block1',
            'block2',
            'block3',
            'block4',
            'block5',
            'block6',
            'block7',
            'block8',
            'block',
            'mask1',
            'mask2',
            'mask3',
            'mask4',
            'mask5',
            'mask6',
            'mask7',
            'mask8',
            'vlan',
            'network_type',
            'ambient_vip',
            'active',
        )

