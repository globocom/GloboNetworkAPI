from rest_framework import serializers
from networkapi.requisicaovips.models import ServerPool
from networkapi.healthcheckexpect.models import Healthcheck


class ServerPoolSerializer(serializers.ModelSerializer):

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


class HealthcheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = Healthcheck
        fields = ('id', 'identifier', 'healthcheck_type', 'healthcheck_request', 'healthcheck_expect', 'destination')
