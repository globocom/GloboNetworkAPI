# -*- coding: utf-8 -*-
from django.db.models import get_model
from rest_framework import serializers

from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class BrandV3Serializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')

    class Meta:
        Marca = get_model('equipamento', 'Marca')
        model = Marca
        fields = (
            'id',
            'name'
        )


class ModelV3Serializer(DynamicFieldsModelSerializer):

    name = serializers.Field(source='nome')

    brand = serializers.SerializerMethodField('get_brand')

    def get_brand(self, obj):

        return self.extends_serializer(obj.marca, 'brand')

    @classmethod
    def get_serializers(cls):
        if not cls.mapping:
            cls.mapping = {
                'brand': {
                    'serializer': BrandV3Serializer,
                    'kwargs': {
                        'source': 'id'
                    }
                },
                'brand__details': {
                    'serializer': BrandV3Serializer,
                    'kwargs': {
                    }
                },
            }

        return cls.mapping

    class Meta:
        Modelo = get_model('equipamento', 'Modelo')
        model = Modelo
        fields = (
            'id',
            'name',
            'brand'
        )

        default_fields = (
            'id',
            'name'
        )


class EquipmentTypeV3Serializer(DynamicFieldsModelSerializer):

    equipment_type = serializers.Field(source='tipo_equipamento')

    class Meta:
        TipoEquipamento = get_model('equipamento', 'TipoEquipamento')
        model = TipoEquipamento
        fields = (
            'id',
            'equipment_type'
        )


class EquipmentV3Serializer(DynamicFieldsModelSerializer):

    ipv4 = serializers.SerializerMethodField('get_ipv4')

    ipv6 = serializers.SerializerMethodField('get_ipv6')

    equipment_type = serializers.SerializerMethodField('get_equipment_type')

    model = serializers.SerializerMethodField('get_model')

    name = serializers.Field(source='nome')

    class Meta:
        Equipamento = get_model('equipamento', 'Equipamento')
        model = Equipamento
        fields = (
            'id',
            'name',
            'equipment_type',
            'model',
            'ipv4',
            'ipv6'
        )

        default_fields = (
            'id',
            'name'
        )

    def get_model(self, obj):

        return self.extends_serializer(obj.modelo, 'model')

    def get_equipment_type(self, obj):

        return self.extends_serializer(obj.tipo_equipamento, 'equipment_type')

    def get_ipv4(self, obj):
        ips = obj.ipequipamento_set.all()
        ips = [ip.ip for ip in ips]

        return self.extends_serializer(ips, 'ipv4')

    def get_ipv6(self, obj):
        ips = obj.ipv6equipament_set.all()
        ips = [ip.ip for ip in ips]

        return self.extends_serializer(ips, 'ipv6')

    @staticmethod
    def get_mapping_eager_loading(self):
        mapping = {
            'ipv4': self.setup_eager_loading_ipv4,
            'ipv6': self.setup_eager_loading_ipv6
        }

        return mapping

    @classmethod
    def get_serializers(cls):
        ip_slz = get_app('api_ip', module_label='serializers')

        if not cls.mapping:
            cls.mapping = {
                'model': {
                    'serializer': ModelV3Serializer,
                    'kwargs': {
                        'source': 'id'
                    }
                },
                'equipment_type': {
                    'serializer': EquipmentTypeV3Serializer,
                    'kwargs': {
                        'source': 'id'
                    }
                },
                'ipv4': {
                    'serializer': ip_slz.Ipv4V3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'id',
                            'ip_formated',
                            'description',
                        )
                    }
                },
                'ipv6': {
                    'serializer': ip_slz.Ipv6V3Serializer,
                    'kwargs': {
                        'many': True,
                        'fields': (
                            'id',
                            'ip_formated',
                            'description',
                        )
                    }
                },
                'ipv4__details': {
                    'serializer': ip_slz.Ipv4V3Serializer,
                    'kwargs': {
                        'many': True,
                        'include': ('networkipv4',)
                    }
                },
                'ipv6__details': {
                    'serializer': ip_slz.Ipv6V3Serializer,
                    'kwargs': {
                        'many': True,
                        'include': ('networkipv6',)
                    }
                },
                'equipment_type__details': {
                    'serializer': EquipmentTypeV3Serializer,
                    'kwargs': {
                    }
                },
                'model__details': {
                    'serializer': ModelV3Serializer,
                    'kwargs': {

                    }
                }
            }

        return cls.mapping

    @staticmethod
    def setup_eager_loading_ipv4(queryset):
        queryset = queryset.prefetch_related(
            'ipequipamento_set',
            'ipequipamento_set__ip',
        )
        return queryset

    @staticmethod
    def setup_eager_loading_ipv6(queryset):
        queryset = queryset.prefetch_related(
            'ipv6equipament_set',
            'ipv6equipament_set__ip',
        )
        return queryset
