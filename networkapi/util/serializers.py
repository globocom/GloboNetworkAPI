# -*- coding:utf-8 -*-
from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):

        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', tuple())
        include = kwargs.pop('include', tuple())
        exclude = kwargs.pop('exclude', tuple())

        if args:
            fields = include + fields
            if fields:
                try:
                    queryset = args[0]
                    # get fields with prefetch_related
                    maping = self.get_maping_eager_loading(self)
                    for key in maping:
                        if key in fields and key not in exclude:
                            queryset = maping[key](queryset)
                    args = (queryset,)
                except:
                    pass

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if exclude:
            forbidden = set(exclude)
            existing = set(self.fields.keys())
            for field_name in existing & forbidden:
                self.fields.pop(field_name)
