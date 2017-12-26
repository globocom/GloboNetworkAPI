# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class RouteMapV4Serializer(DynamicFieldsModelSerializer):

    route_map_entries = serializers. \
        SerializerMethodField('get_route_map_entries')

    peer_groups = serializers. \
        SerializerMethodField('get_peer_groups')

    class Meta:
        RouteMap = get_model('api_route_map', 'RouteMap')
        model = RouteMap

        fields = (
            'id',
            'name',
            'route_map_entries',
            'peer_groups'
        )

        basic_fields = (
            'id',
            'name',
        )

        default_fields = fields

        details_fields = fields

    def get_route_map_entries(self, obj):
        return self.extends_serializer(obj, 'route_map_entries')

    def get_peer_groups(self, obj):
        return self.extends_serializer(obj, 'peer_groups')

    def get_serializers(self):
        routemap_slzs = get_app('api_route_map',
                                module_label='v4.serializers')
        peergroup_slzs = get_app('api_peer_group',
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
                        'many': True
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
                },
                'peer_groups': {
                    'obj': 'peer_groups_id',
                },
                'peer_groups__basic': {
                    'serializer': peergroup_slzs.PeerGroupV4Serializer,
                    'kwargs': {
                        'kind': 'basic',
                        'many': True
                    },
                    'obj': 'peer_groups'
                },
                'peer_groups__details': {
                    'serializer': peergroup_slzs.PeerGroupV4Serializer,
                    'kwargs': {
                        'kind': 'details',
                        'many': True
                    },
                    'obj': 'peer_groups'
                }
            }


class RouteMapEntryV4Serializer(DynamicFieldsModelSerializer):

    list_config_bgp = serializers.SerializerMethodField('get_list_config_bgp')
    route_map = serializers.SerializerMethodField('get_route_map')

    class Meta:
        RouteMapEntry = get_model('api_route_map', 'RouteMapEntry')
        model = RouteMapEntry

        fields = (
            'id',
            'action',
            'action_reconfig',
            'order',
            'list_config_bgp',
            'route_map'
        )

        basic_fields = (
            'id',
            'action',
            'action_reconfig',
            'order'
        )

        default_fields = fields

        details_fields = fields

    def get_list_config_bgp(self, obj):
        return self.extends_serializer(obj, 'list_config_bgp')

    def get_route_map(self, obj):
        return self.extends_serializer(obj, 'route_map')

    def get_serializers(self):
        lcb_slzs = get_app('api_list_config_bgp',
                           module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {
                'list_config_bgp': {
                    'obj': 'list_config_bgp_id',
                },
                'list_config_bgp__basic': {
                    'serializer': lcb_slzs.ListConfigBGPV4Serializer,
                    'kwargs': {
                        'kind': 'basic',
                        'prohibited': (
                            'route_map_entries__basic',
                        )
                    },
                    'obj': 'list_config_bgp'
                },
                'list_config_bgp__details': {
                    'serializer': lcb_slzs.ListConfigBGPV4Serializer,
                    'kwargs': {
                        'kind': 'details',
                        'prohibited': (
                            'route_map_entries__details',
                        )
                    },
                    'obj': 'list_config_bgp'
                },
                'route_map': {
                    'obj': 'route_map_id',
                },
                'route_map__basic': {
                    'serializer': RouteMapV4Serializer,
                    'kwargs': {
                        'kind': 'basic',
                        'prohibited': (
                            'route_map_entries__basic',
                        )
                    },
                    'obj': 'route_map'
                },
                'route_map__details': {
                    'serializer': RouteMapV4Serializer,
                    'kwargs': {
                        'kind': 'details',
                        'prohibited': (
                            'route_map_entries__details',
                        )
                    },
                    'obj': 'route_map'
                }
            }
