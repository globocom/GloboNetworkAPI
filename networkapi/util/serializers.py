# -*- coding: utf-8 -*-
import logging

from rest_framework import serializers

from networkapi.models.BaseManager import BaseQuerySet

log = logging.getLogger(__name__)


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
        prohibited = kwargs.pop('prohibited', tuple())
        kind = kwargs.pop('kind', None)

        try:
            self.get_serializers()
        except:
            self.mapping = dict()

        filtred_fields = tuple()
        all_fields = tuple()
        if args:
            queryset = args[0]

            if not fields:
                try:
                    fields_class = None

                    if kind == 'basic' and self.Meta.__dict__.get('basic_fields'):
                        fields_class = self.Meta.basic_fields
                    elif kind == 'details' and self.Meta.__dict__.get('details_fields'):
                        fields_class = self.Meta.details_fields
                    elif self.Meta.__dict__.get('default_fields'):
                        fields_class = self.Meta.default_fields
                    else:
                        fields_class = self.Meta.fields

                    all_fields = fields_class + include
                except:
                    pass
            else:
                all_fields = include + fields

            filtred_fields = [self.get_main_key(field, kind)[0]
                              for field in all_fields]

            if filtred_fields and type(queryset) == BaseQuerySet:
                # import pdb; pdb.Pdb(skip=['django.*']).set_trace()  #
                # breakpoint 184999ff //

                # for key in all_fields:
                # import pdb; pdb.Pdb(skip=['django.*']).set_trace()  #
                # breakpoint 50ca06f4 //

                #     queryset = self.recur(self, key, kind, queryset)

                queryset = self.exec_eager_loading(filtred_fields, queryset)

            args = (queryset,)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        # Prepare field for serializer
        self.context = {'serializers': dict()}

        # Use default_fields when exists
        existing = set(self.fields.keys())

        if filtred_fields:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set([field.split('__')[0] for field in filtred_fields])

            for field_name in existing - allowed:
                try:
                    self.fields.pop(field_name)
                except:
                    pass

        if exclude:
            # Drop any fields that are specified in the `exclude` argument.
            forbidden = set([field.split('__')[0] for field in exclude])
            for field_name in existing & forbidden:
                try:
                    self.fields.pop(field_name)
                except:
                    pass

        for field in all_fields:

            field_filtered, other_fields = self.get_main_key(field, kind)

            key_split = field_filtered.split('__')
            fd_key = key_split[0]

            if self.mapping.get(field_filtered):

                # remove field because is prohibited
                if prohibited:
                    if other_fields in prohibited or field_filtered in prohibited or\
                            field in prohibited:
                        self.fields.pop(field_filtered.split('__')[0])
                        continue

                if other_fields:
                    param = self.mapping.get(
                        field_filtered).get('kwargs', dict())

                    if param:

                        inc_ser = param.get('include', tuple())

                        self.mapping[field_filtered]['kwargs']['include'] = \
                            inc_ser + (other_fields,)
                    else:
                        self.mapping[field_filtered].update({
                            'kwargs': {
                                'include': (other_fields,)
                            }
                        })

                # Example: field: field_details | field: field
                self.context['serializers'].update({
                    fd_key: field_filtered
                })

    def extends_serializer(self, obj, default_field):

        key = self.context.get('serializers').get(default_field, default_field)
        slr_model = self.mapping.get(key)

        # keys
        if slr_model.get('keys'):
            keys = slr_model.get('keys')
            render = dict()
            for k in keys:

                render[k] = self.render_serializer(obj.get(k), slr_model)

            return render
        else:
            return self.render_serializer(obj, slr_model)

    def render_serializer(self, obj, slr_model):
        # obj costum

        if obj and slr_model.get('obj'):

            obj = obj.__getattribute__(slr_model.get('obj'))

        if not obj:
            if slr_model.get('kwargs', dict()).get('many'):
                return []
            return None

        # If has not serializer return obj
        elif not slr_model.get('serializer'):
            return obj
        else:

            try:
                model_serializer = slr_model.get('serializer')(
                    obj, **slr_model.get('kwargs', dict())
                )
                ret_srl = model_serializer.data
            except:
                return None

            return ret_srl

    def get_main_key(self, key, kind):

        # split field
        # Example: y__details__z__details
        # key = y__details
        fields_aux = key.split('__')

        main_key = fields_aux[0]

        kind_key = None

        # many keys
        if len(fields_aux) > 1:
            kind_key = fields_aux[1]
            if kind_key in ('details', 'basic'):
                del fields_aux[0]
            else:
                kind_key = None
        del fields_aux[0]
        fields_aux = '__'.join(fields_aux)

        # kind serializer for all
        if kind:
            kind_key = kind
        if not kind_key:
            key = main_key
        else:
            key = '%s__%s' % (main_key, kind_key)

        return key, fields_aux

    def exec_eager_loading(self, filted_fields, queryset):
        try:

            # get fields with prefetch_related
            mapping = self.mapping

            # For each field
            for key in filted_fields:
                # if has key
                eager_loading = mapping.get(key, {}).get('eager_loading')
                if eager_loading:
                    queryset = eager_loading(queryset)
        except Exception, e:
            log.info(e)
            pass
        return queryset


class RecursiveField(serializers.Serializer):

    def to_native(self, value):

        return self.parent.to_native(value)
