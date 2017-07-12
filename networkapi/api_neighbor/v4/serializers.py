# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class NeighborV4Serializer(DynamicFieldsModelSerializer):

    soft_reconfiguration = serializers.Field(source='soft_reconfiguration')

    community = serializers.Field(source='community')

    remove_private_as = serializers.Field(source='remove_private_as')

    next_hop_self = serializers.Field(source='next_hop_self')

    created = serializers.Field(source='created')

    virtual_interface = serializers.SerializerMethodField(
        'get_virtual_interface')

    class Meta:
        Neighbor = get_model('neighbor', 'Neighbor')
        model = Neighbor
        fields = (
            'id',
            'remote_as',
            'remote_ip',
            'password',
            'maximum_hops',
            'timer_keepalive',
            'timer_timeout',
            'description',
            'soft_reconfiguration',
            'community',
            'remove_private_as',
            'next_hop_self',
            'kind',
            'created',
        )

        default_fields = fields

        basic_fields = fields

        details_fields = fields

    def get_virtual_interface(self, obj):
        return self.extends_serializer(obj, 'virtual_interface')

    def get_serializers(self):
        # serializers
        neg_slz = get_app('api_neighbor', module_label='serializers.v3')

        if not self.mapping:
            self.mapping = {
                'virtual_interface': {
                    'obj': 'virtual_interface_id'
                },
                'virtual_interface__details': {
                    'serializer': neg_slz.VirtualInterfaceV3Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'virtual_interface',
                    'eager_loading': self.setup_eager_loading_interface
                },
                'virtual_interface__basic': {
                    'serializer': neg_slz.VirtualInterfaceV3Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'virtual_interface',
                    'eager_loading': self.setup_eager_loading_interface
                },
            }

    @staticmethod
    def setup_eager_loading_interface(queryset):

        log.info('Using setup_eager_loading_interface')
        queryset = queryset.select_related(
            'virtual_interface',
        )
        return queryset
