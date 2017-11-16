# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class ListConfigBGPV4Serializer(DynamicFieldsModelSerializer):

    route_map_entries = serializers.\
        SerializerMethodField('get_route_map_entries')

    class Meta:
        ListConfigBGP = get_model('api_list_config_bgp', 'ListConfigBGP')
        model = ListConfigBGP

        fields = (
            'id',
            'name',
            'type',
            'config',
            'route_map_entries',
            'created'
        )

        basic_fields = (
            'id',
            'name',
            'type',
            'config',
            'created'
        )

        default_fields = basic_fields

        details_fields = fields

    def get_route_map_entries(self, obj):
        return self.extends_serializer(obj, 'route_map_entries')

    def get_serializers(self):
        routemap_slzs = get_app('api_route_map',
                                module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {
                'route_map_entries': {
                    'obj': 'route_map_entries_id',
                },
                'route_map_entries__basic': {
                    'serializer': routemap_slzs.RouteMapEntryV4Serializer,
                    'kwargs': {
                        'kind': 'basic',
                        'many': True,
                    },
                    'obj': 'route_map_entries'
                },
                'route_map_entries__details': {
                    'serializer': routemap_slzs.RouteMapEntryV4Serializer,
                    'kwargs': {
                        'kind': 'details',
                        'many': True
                    },
                    'obj': 'route_map_entries'
                }
            }
