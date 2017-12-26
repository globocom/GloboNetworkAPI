# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class PeerGroupV4Serializer(DynamicFieldsModelSerializer):

    route_map_in = serializers.SerializerMethodField('get_route_map_in')
    route_map_out = serializers.SerializerMethodField('get_route_map_out')
    environments = serializers.SerializerMethodField('get_environments')

    class Meta:
        PeerGroup = get_model('api_peer_group', 'PeerGroup')
        model = PeerGroup

        fields = (
            'id',
            'name',
            'route_map_in',
            'route_map_out',
            'environments'
        )

        basic_fields = (
            'id',
            'name'
        )

        default_fields = fields

        details_fields = fields

    def get_route_map_in(self, obj):
        return self.extends_serializer(obj, 'route_map_in')

    def get_route_map_out(self, obj):
        return self.extends_serializer(obj, 'route_map_out')

    def get_environments(self, obj):
        return self.extends_serializer(obj, 'environments')

    def get_serializers(self):
        routemap_slzs = get_app('api_route_map', module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {
                'route_map_in': {
                    'obj': 'route_map_in_id',
                },
                'route_map_in__basic': {
                    'serializer': routemap_slzs.RouteMapV4Serializer,
                    'kwargs': {
                        'kind': 'basic',
                        'prohibited': (
                            'peer_groups__basic',
                        )
                    },
                    'obj': 'route_map_in'
                },
                'route_map_in__details': {
                    'serializer': routemap_slzs.RouteMapV4Serializer,
                    'kwargs': {
                        'kind': 'details',
                        'prohibited': (
                            'peer_groups__details',
                        )
                    },
                    'obj': 'route_map_in'
                },
                'route_map_out': {
                    'obj': 'route_map_out_id',
                },
                'route_map_out__basic': {
                    'serializer': routemap_slzs.RouteMapV4Serializer,
                    'kwargs': {
                        'kind': 'basic',
                        'prohibited': (
                            'peer_groups__basic',
                        )
                    },
                    'obj': 'route_map_out'
                },
                'route_map_out__details': {
                    'serializer': routemap_slzs.RouteMapV4Serializer,
                    'kwargs': {
                        'kind': 'details',
                        'prohibited': (
                            'peer_groups__details',
                        )
                    },
                    'obj': 'route_map_out'
                },
                'environments': {
                    'obj': 'environments_id',
                },
                'environments__basic': {
                    'serializer': EnvironmentPeerGroupV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'basic',
                        'prohibited': (
                            'peer_group__basic',
                        )
                    },
                    'obj': 'environments'
                },
                'environments__details': {
                    'serializer': EnvironmentPeerGroupV4Serializer,
                    'kwargs': {
                        'many': True,
                        'kind': 'details',
                        'prohibited': (
                            'peer_group__details',
                        )
                    },
                    'obj': 'environments'
                }
            }


class EnvironmentPeerGroupV4Serializer(DynamicFieldsModelSerializer):

    environment = serializers.SerializerMethodField('get_environment')
    peer_group = serializers.SerializerMethodField('get_peer_group')

    class Meta:
        EnvironmentPeerGroup = get_model('api_peer_group',
                                         'EnvironmentPeerGroup')
        model = EnvironmentPeerGroup

        fields = (
            'id',
            'environment',
            'peer_group'
        )

        basic_fields = fields

        default_fields = fields

        details_fields = fields

    def get_environment(self, obj):
        return self.extends_serializer(obj, 'environment')

    def get_peer_group(self, obj):
        return self.extends_serializer(obj, 'peer_group')

    def get_serializers(self):
        env_slzs = get_app('api_environment', module_label='serializers')

        if not self.mapping:
            self.mapping = {
                'environment': {
                    'obj': 'environment_id',
                },
                'environment__basic': {
                    'serializer': env_slzs.EnvironmentV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'environment'
                },
                'environment__details': {
                    'serializer': env_slzs.EnvironmentV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'environment'
                },
                'peer_group': {
                    'obj': 'peer_group_id',
                },
                'peer_group__basic': {
                    'serializer': PeerGroupV4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'peer_group'
                },
                'peer_group__details': {
                    'serializer': PeerGroupV4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'peer_group'
                }
            }
