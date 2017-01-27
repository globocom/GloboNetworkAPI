# -*- coding: utf-8 -*-
from networkapi.util.geral import get_app
from networkapi.util.serializers import DynamicFieldsModelSerializer


class FilterV3Serializer(DynamicFieldsModelSerializer):

    class Meta:
        filter_model = get_app('filter', module_label='models')
        model = filter_model.Filter
        fields = (
            'id',
            'name',
            'description',
        )

        default_fields = (
            'id',
            'name',
            'description',
        )

        details_fields = fields

    def get_serializers(self):
        """Returns the mapping of serializers."""
        pass
