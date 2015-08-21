from rest_framework import serializers
from networkapi.ip.models import NetworkIPv4

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
        )

