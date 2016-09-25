# -*- coding:utf-8 -*-
import copy
import urllib


def url_search(obj_model, property_search, request):

    if obj_model.get(property_search):
        protocol = 'https' if request.is_secure() else 'http'

        params = copy.deepcopy(request.GET)
        params['search'] = obj_model.get(property_search)

        search = dict()
        for key in params.keys():
            search.update({key: params.get(key)})

        search = urllib.urlencode(search)

        url_search_str = '%s://%s%s?%s' % (
            protocol, request.get_host(), request.path, search)
    else:
        url_search_str = None

    return url_search_str


def generate_return_json(obj_serializer, main_property, **kwargs):

    data = {
        main_property: obj_serializer.data
    }

    request = kwargs.get('request', None)
    obj_model = kwargs.get('obj_model', None)
    only_main_property = kwargs.get('only_main_property', False)

    if not only_main_property and request:

        url_next_search = url_search(obj_model, 'next_search', request)
        url_prev_search = url_search(obj_model, 'prev_search', request)

        data.update({
            'total': obj_model.get('total'),
            'url_next_search': url_next_search,
            'next_search': obj_model.get('next_search'),
            'url_prev_search': url_prev_search,
            'prev_search': obj_model.get('prev_search')
        })

    return data


def render_to_json(serializer_obj, **kwargs):

    data = generate_return_json(
        serializer_obj,
        kwargs.get('main_property'),
        obj_model=kwargs.get('obj_model', None),
        request=kwargs.get('request', None),
        only_main_property=kwargs.get('only_main_property', False)
    )
    return data
