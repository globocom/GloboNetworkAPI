# -*- coding: utf-8 -*-
import copy
import urllib

from django.db.models.loading import AppCache
from django.db.models.loading import import_module
from django.db.models.loading import module_has_submodule


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


class AppCacheExtend(AppCache):

    module = 'models'

    def __init__(self, *args, **kwargs):
        super(AppCacheExtend, self).__init__(*args, **kwargs)

    def load_app(self, app_name, can_postpone=False):
        """
        Loads the app with the provided fully qualified name, and returns the
        model module.
        """
        self.handled[app_name] = None
        self.nesting_level += 1
        app_module = import_module(app_name)
        try:
            models = import_module('.%s' % self.module, app_name)
        except ImportError:
            self.nesting_level -= 1
            # If the app doesn't have a models module, we can just ignore the
            # ImportError and return no models for it.
            if not module_has_submodule(app_module, 'models'):
                return None
            # But if the app does have a models module, we need to figure out
            # whether to suppress or propagate the error. If can_postpone is
            # True then it may be that the package is still being imported by
            # Python and the models module isn't available yet. So we add the
            # app to the postponed list and we'll try it again after all the
            # recursion has finished (in populate). If can_postpone is False
            # then it's time to raise the ImportError.
            else:
                if can_postpone:
                    self.postponed.append(app_name)
                    return None
                else:
                    raise

        self.nesting_level -= 1
        if models not in self.app_store:
            self.app_store[models] = len(self.app_store)
            self.app_labels[self._label_for(models)] = models
        return models

    def get_app(self, app_label, module_label='models', emptyok=False):

        self.module = module_label

        return super(AppCacheExtend, self).get_app(app_label, emptyOK=emptyok)

    # def get_model(self, app_label, item_name, module_label='models',
    #               seed_cache=True, only_installed=True):

    #     self.module = module_label

    #     model = super(AppCacheExtend, self).get_model(
    #         app_label, item_name, seed_cache, only_installed)

    #     return model

cache = AppCacheExtend()

get_app = cache.get_app
get_model = cache.get_model
