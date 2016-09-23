# -*- coding:utf-8 -*-
import ast
import functools
import json
import logging

from jsonspec.validators.exceptions import ValidationError
from rest_framework import exceptions as exceptions_api

from networkapi.api_rest import exceptions as rest_exceptions

log = logging.getLogger(__name__)


class cached_property(object):

    """
    Decorator that converts a method with a single self argument into a
    property cached on the instance.
    # https://github.com/django/django/blob/2456ffa42c33d63b54579eae0f5b9cf2a8cd3714/django/utils/functional.py#L38-50
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.func.__name__] = self.func(instance)
        return res


def deprecated(new_uri=None):
    """This is a decorator which can be used to mark functions
        as deprecated. It will result in a warning being emitted
        when the function is used.
    """
    def outer(fun):
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            import os
            basename = os.path.basename(fun.func_code.co_filename)
            log = logging.getLogger(basename)
            message = "%s:%s: %s is deprecated. Use the new rest API." % (
                basename,
                fun.func_code.co_firstlineno + 1,
                fun.__name__,
            )

            if new_uri:
                message += " Uri to access: %s" % new_uri

            log.warning(message)
            return fun(*args, **kwargs)
        return inner
    return outer


def logs_method_apiview(func):
    @functools.wraps(func)
    def inner(self, request, *args, **kwargs):

        log = logging.getLogger(type(self).__name__)

        log.info(
            "View:%s, method:%s - Data send: %s -  Url params: %s" % (
                type(self).__name__, request.method, request.DATA, kwargs))
        return func(self, request, *args, **kwargs)
    return inner


def state_change(func):
    @functools.wraps(func)
    def inner(self, request, *args, **kwargs):
        self.update_state(state='STARTED')
        return func(self, request, *args, **kwargs)
    return inner


def permission_classes_apiview(permission_classes):
    def outer(func):
        @functools.wraps(func)
        def inner(self, request, *args, **kwargs):
            self.permission_classes = permission_classes
            self.initial(request, *args, **kwargs)
            return func(self, request, *args, **kwargs)
        return inner
    return outer


def permission_obj_apiview(functions):
    def outer(func):
        @functools.wraps(func)
        def inner(self, request, *args, **kwargs):
            permission_classes = list(self.permission_classes)

            for param in functions:

                perm_add = param(request, *args, **kwargs)
                permission_classes.append(perm_add)

            self.permission_classes = tuple(permission_classes)
            self.initial(request, *args, **kwargs)
            return func(self, request, *args, **kwargs)
        return inner
    return outer


def raise_exception_treat(func):
    @functools.wraps(func)
    def inner(self, request, *args, **kwargs):
        try:
            return func(self, request, *args, **kwargs)
        except ValidationError, error:
            log.error(error)
            raise rest_exceptions.ValidationExceptionJson(error)
        except (exceptions_api.APIException, exceptions_api.AuthenticationFailed,
                exceptions_api.MethodNotAllowed, exceptions_api.NotAcceptable,
                exceptions_api.NotAuthenticated, exceptions_api.ParseError,
                exceptions_api.PermissionDenied, exceptions_api.Throttled,
                exceptions_api.UnsupportedMediaType, rest_exceptions.ValidationAPIException), error:
            log.error(error)
            raise error
        except Exception, error:
            log.error(error)
            raise rest_exceptions.NetworkAPIException(error)
    return inner


def prepare_search(func):
    @functools.wraps(func)
    def inner(self, request, *args, **kwargs):

        data = request.GET

        # param search
        try:
            search = json.loads(data.get('search'))
        except:
            try:
                search = ast.literal_eval(data.get('search'))
            except:
                search = {
                    'extends_search': []
                }
        finally:
            self.search = search

        # param fields
        self.fields = tuple(data.get('fields').split(','))\
            if data.get('fields') else tuple()

        self.include = tuple(data.get('include').split(','))\
            if data.get('include') else tuple()

        self.exclude = tuple(data.get('exclude').split(','))\
            if data.get('exclude') else tuple()

        return func(self, request, *args, **kwargs)
    return inner
