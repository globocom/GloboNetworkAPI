# -*- coding: utf-8 -*-
from rest_framework import serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    mapping = dict()

    def __init__(self, *args, **kwargs):

        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', tuple())
        include = kwargs.pop('include', tuple())
        exclude = kwargs.pop('exclude', tuple())

        fields_serializer = tuple()
        if args:
            fields = include + fields
            fields_serializer = fields

            # get first part
            # Example: x__details__y
            # first part = x
            fields_aux = [f.split('__')[0] for f in fields]
            fields = list()
            for fd in fields_aux:
                fields.append(fd)
            if fields:
                try:
                    queryset = args[0]
                    # get fields with prefetch_related
                    mapping = self.get_mapping_eager_loading(self)
                    for key in mapping:
                        if key in fields and key not in exclude:
                            queryset = mapping[key](queryset)
                    args = (queryset,)
                except:
                    pass

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        # Use default_fields when exists
        existing = set(self.fields.keys())

        if not fields or include or exclude:
            try:
                fields = self.Meta.default_fields + include
                fields_serializer = fields
                fields_aux = [f.split('__')[0] for f in fields]
                fields = list()
                for fd in fields_aux:
                    fields.append(fd)
            except:
                pass

        if fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            for field_name in existing - allowed:
                try:
                    self.fields.pop(field_name)
                except:
                    pass

        if exclude:
            forbidden = set(exclude)
            for field_name in existing & forbidden:
                try:
                    self.fields.pop(field_name)
                except:
                    pass

        # Prepare field for serializer
        self.context = {'serializers': dict()}

        for key in fields_serializer:

            fields_aux = key.split('__')

            fd_key = fields_aux[0]

            key_aux = key.split('__')[0]

            if len(fields_aux) > 1:
                if fields_aux[1] in ('details', 'basic'):
                    key_aux = '%s__%s' % (fd_key, fields_aux[1])
                    del fields_aux[0]
            del fields_aux[0]

            # Example: field: field_details | field: field
            self.context['serializers'].update({
                fd_key: key_aux
            })

            if fields_aux:

                self.mapping = self.get_serializers()
                if self.mapping.get(fd_key):
                    fields_aux = '__'.join(fields_aux)
                    if self.mapping.get(key_aux).get('kwargs'):
                        inc_ser = self.mapping.get(key_aux).get(
                            'kwargs').get('include', tuple())
                        self.mapping[key_aux]['kwargs'][
                            'include'] = inc_ser + (fields_aux,)
                    else:
                        self.mapping[key_aux].update({
                            'kwargs': {
                                'include': (fields_aux,)
                            }
                        })

    def extends_serializer(self, obj, default_field):

        key = self.context.get('serializers').get(default_field, default_field)
        slr_model = self.get_serializers().get(key)

        # obj costum
        if slr_model.get('obj'):

            obj = obj.__getattribute__(slr_model.get('obj'))

        if not obj:
            return None

        # If has not serializer return obj
        if not slr_model.get('serializer'):
            return obj
        else:

            model_serializer = slr_model.get('serializer')(
                obj, **slr_model.get('kwargs', dict())
            )

            ret_srl = model_serializer.data
            source = slr_model.get('kwargs', dict()).get('source')
            if source:
                return model_serializer.data.get(source)

        return ret_srl


class RecursiveField(serializers.Serializer):

    def to_native(self, value):

        return self.parent.to_native(value)
