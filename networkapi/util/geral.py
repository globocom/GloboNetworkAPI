# -*- coding:utf-8 -*-
import urllib


def generate_return_json(obj_serializer, main_property, **kwargs):

    data = {
        main_property: obj_serializer.data
    }

    request = kwargs.get('request', None)
    obj_model = kwargs.get('obj_model', None)
    only_main_property = kwargs.get('only_main_property', False)

    if not only_main_property and request:
        protocol = 'https' if request.is_secure() else 'http'

        if obj_model.get('next_search'):
            next_search = urllib.urlencode({
                "search": obj_model.get('next_search')
            })
            url_next_search = '%s://%s%s?%s' % (
                protocol, request.get_host(), request.path, next_search)
        else:
            url_next_search = None

        if obj_model.get('prev_search'):
            prev_search = urllib.urlencode({
                "search": obj_model.get('prev_search')
            })
            url_prev_search = '%s://%s%s?%s' % (
                protocol, request.get_host(), request.path, prev_search)
        else:
            url_prev_search = None

        data.update({
            'total': obj_model.get('total'),
            'url_next_search': url_next_search,
            'next_search': obj_model.get('next_search'),
            'url_prev_search': url_prev_search,
            'prev_search': obj_model.get('prev_search')
        })

    return data
