# -*- coding: utf-8 -*-
import logging
from django.db.models import get_model
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class ListConfigBGPV4Serializer(DynamicFieldsModelSerializer):

    class Meta:
        ListConfigBGP = get_model('api_list_config_bgp', 'ListConfigBGP')
        model = ListConfigBGP

        fields = (
            'id',
            'name',
            'type',
            'config'
        )

        basic_fields = fields

        default_fields = fields

        details_fields = fields
