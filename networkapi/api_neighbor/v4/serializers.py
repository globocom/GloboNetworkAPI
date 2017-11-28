# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer

log = logging.getLogger(__name__)


class NeighborV4V4Serializer(DynamicFieldsModelSerializer):

    local_asn = serializers.SerializerMethodField('get_local_asn')
    remote_asn = serializers.SerializerMethodField('get_remote_asn')
    local_ip = serializers.SerializerMethodField('get_local_ip')
    remote_ip = serializers.SerializerMethodField('get_remote_ip')
    peer_group = serializers.SerializerMethodField('get_peer_group')

    class Meta:
        NeighborV4 = get_model('api_neighbor', 'NeighborV4')
        model = NeighborV4

        fields = (
            'id',
            'local_asn',
            'remote_asn',
            'local_ip',
            'remote_ip',
            'peer_group',
            'virtual_interface',
            'created'
        )

        basic_fields = fields

        default_fields = fields

        details_fields = fields

    def get_local_asn(self, obj):
        return self.extends_serializer(obj, 'local_asn')

    def get_remote_asn(self, obj):
        return self.extends_serializer(obj, 'remote_asn')

    def get_local_ip(self, obj):
        return self.extends_serializer(obj, 'local_ip')

    def get_remote_ip(self, obj):
        return self.extends_serializer(obj, 'remote_ip')

    def get_peer_group(self, obj):
        return self.extends_serializer(obj, 'peer_group')

    def get_serializers(self):
        ip_slzs = get_app('api_ip', module_label='v4.serializers')
        asn_slzs = get_app('api_asn', module_label='v4.serializers')
        prg_slzs = get_app('api_peer_group', module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {
                'local_asn': {
                    'obj': 'local_asn_id',
                },
                'local_asn__basic': {
                    'serializer': asn_slzs.AsnV4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'local_asn'
                },
                'local_asn__details': {
                    'serializer': asn_slzs.AsnV4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'local_asn'
                },
                'remote_asn': {
                    'obj': 'remote_asn_id',
                },
                'remote_asn__basic': {
                    'serializer': asn_slzs.AsnV4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'remote_asn'
                },
                'remote_asn__details': {
                    'serializer': asn_slzs.AsnV4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'remote_asn'
                },
                'local_ip': {
                    'obj': 'local_ip_id',
                },
                'local_ip__basic': {
                    'serializer': ip_slzs.IPv4V4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'local_ip'
                },
                'local_ip__details': {
                    'serializer': ip_slzs.IPv4V4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'local_ip'
                },
                'remote_ip': {
                    'obj': 'remote_ip_id',
                },
                'remote_ip__basic': {
                    'serializer': ip_slzs.IPv4V4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'remote_ip'
                },
                'remote_ip__details': {
                    'serializer': ip_slzs.IPv4V4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'remote_ip'
                },
                'peer_group': {
                    'obj': 'peer_group_id',
                },
                'peer_group__basic': {
                    'serializer': prg_slzs.PeerGroupV4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'peer_group'
                },
                'peer_group__details': {
                    'serializer': prg_slzs.PeerGroupV4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'peer_group'
                },
            }


class NeighborV6V4Serializer(DynamicFieldsModelSerializer):

    local_asn = serializers.SerializerMethodField('get_local_asn')
    remote_asn = serializers.SerializerMethodField('get_remote_asn')
    local_ip = serializers.SerializerMethodField('get_local_ip')
    remote_ip = serializers.SerializerMethodField('get_remote_ip')
    peer_group = serializers.SerializerMethodField('get_peer_group')

    class Meta:
        NeighborV6 = get_model('api_neighbor', 'NeighborV6')
        model = NeighborV6

        fields = (
            'id',
            'local_asn',
            'remote_asn',
            'local_ip',
            'remote_ip',
            'peer_group',
            'virtual_interface',
            'created'
        )

        basic_fields = fields

        default_fields = fields

        details_fields = fields

    def get_local_asn(self, obj):
        return self.extends_serializer(obj, 'local_asn')

    def get_remote_asn(self, obj):
        return self.extends_serializer(obj, 'remote_asn')

    def get_local_ip(self, obj):
        return self.extends_serializer(obj, 'local_ip')

    def get_remote_ip(self, obj):
        return self.extends_serializer(obj, 'remote_ip')

    def get_peer_group(self, obj):
        return self.extends_serializer(obj, 'peer_group')

    def get_serializers(self):
        ip_slzs = get_app('api_ip', module_label='v4.serializers')
        asn_slzs = get_app('api_asn', module_label='v4.serializers')
        prg_slzs = get_app('api_peer_group', module_label='v4.serializers')

        if not self.mapping:
            self.mapping = {
                'local_asn': {
                    'obj': 'local_asn_id',
                },
                'local_asn__basic': {
                    'serializer': asn_slzs.AsnV4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'local_asn'
                },
                'local_asn__details': {
                    'serializer': asn_slzs.AsnV4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'local_asn'
                },
                'remote_asn': {
                    'obj': 'remote_asn_id',
                },
                'remote_asn__basic': {
                    'serializer': asn_slzs.AsnV4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'remote_asn'
                },
                'remote_asn__details': {
                    'serializer': asn_slzs.AsnV4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'remote_asn'
                },
                'local_ip': {
                    'obj': 'local_ip_id',
                },
                'local_ip__basic': {
                    'serializer': ip_slzs.Ipv6V4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'local_ip'
                },
                'local_ip__details': {
                    'serializer': ip_slzs.Ipv6V4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'local_ip'
                },
                'remote_ip': {
                    'obj': 'remote_ip_id',
                },
                'remote_ip__basic': {
                    'serializer': ip_slzs.Ipv6V4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'remote_ip'
                },
                'remote_ip__details': {
                    'serializer': ip_slzs.Ipv6V4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'remote_ip'
                },
                'peer_group': {
                    'obj': 'peer_group_id',
                },
                'peer_group__basic': {
                    'serializer': prg_slzs.PeerGroupV4Serializer,
                    'kwargs': {
                        'kind': 'basic'
                    },
                    'obj': 'peer_group'
                },
                'peer_group__details': {
                    'serializer': prg_slzs.PeerGroupV4Serializer,
                    'kwargs': {
                        'kind': 'details'
                    },
                    'obj': 'peer_group'
                },
            }
