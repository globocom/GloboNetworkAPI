import logging
from django.db.models import get_model
from rest_framework import serializers
from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class RouteMapV4Serializer(DynamicFieldsModelSerializer):

    class Meta:
        RouteMap = get_model('api_route_map', 'RouteMap')
        model = RouteMap

        fields = (
            'id',
            'name'
        )

        basic_fields = fields

        default_fields = fields

        details_fields = fields


class RouteMapEntryV4Serializer(DynamicFieldsModelSerializer):

    list_config_bgp = serializers.SerializerMethodField('get_list_config_bgp')
    route_map = serializers.SerializerMethodField('get_route_map')

    class Meta:
        RouteMapEntry = get_model('api_route_map',
                                  'RouteMapEntry')
        model = RouteMapEntry

        fields = (
            'id',
            'action',
            'action_reconfig',
            'order',
            'list_config_bgp',
            'route_map'
        )

        basic_fields = fields

        default_fields = (
            'id',
            'action',
            'action_reconfig',
            'order'
        )

        details_fields = fields

    def get_list_config_bgp(self, obj):
        return self.extends_serializer(obj, 'list_config_bgp')

    def get_route_map(self, obj):
        return self.extends_serializer(obj, 'route_map')

    def get_serializers(self):
        lcb_slzs = get_app('api_list_config_bgp', module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {
                'list_config_bgp': {
                    'obj': 'list_config_bgp_id',
                },
                'list_config_bgp__basic': {
                    'serializer': lcb_slzs.ListConfigBGPV4Serializer,
                    'kwargs': {
                    },
                    'obj': 'list_config_bgp'
                },
                'list_config_bgp__details': {
                    'serializer': lcb_slzs.ListConfigBGPV4Serializer,
                    'kwargs': {
                    },
                    'obj': 'list_config_bgp'
                },
                'route_map': {
                    'obj': 'route_map_id',
                },
                'route_map__basic': {
                    'serializer': RouteMapV4Serializer,
                    'kwargs': {
                    },
                    'obj': 'route_map'
                },
                'route_map__details': {
                    'serializer': RouteMapV4Serializer,
                    'kwargs': {
                    },
                    'obj': 'route_map'
                }
            }

