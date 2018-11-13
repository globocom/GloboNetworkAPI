# -*- coding: utf-8 -*-
from django.db.models import get_model

from networkapi.util.serializers import DynamicFieldsModelSerializer


class AwsVPCSerializer(DynamicFieldsModelSerializer):

    class Meta:
        VPC = get_model('api_aws', 'VPC')
        depth = 1
        model = VPC

        fields = (
            'id',
            'vpc'
        )

        default_fields = fields

        basic_fields = fields

        details_fields = fields
