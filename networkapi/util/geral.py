# -*- coding:utf-8 -*-
import urllib


def generate_return_json(obj_serializer, main_property, obj_model=None,
                         request=None, only_main_property=False):

    if request:
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

    if only_main_property:
        data = {
            main_property: obj_serializer.data
        }
        return data

    data = {
        main_property: obj_serializer.data,
        'total': obj_model.get('total'),
        'url_next_search': url_next_search,
        'next_search': obj_model.get('next_search'),
        'url_prev_search': url_prev_search,
        'prev_search': obj_model.get('prev_search')
    }

    return data
