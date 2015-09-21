# -*- coding:utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid
import base64

from django.conf import settings

import logging
from networkapi.extra_logging import local, REQUEST_ID_HEADER, NO_REQUEST_ID, NO_REQUEST_USER
from networkapi.extra_logging.filters import ExtraLoggingFilter

import weakref
weakref_type = type(weakref.ref(lambda: None))

def deref(x):
    return x() if x and type(x) == weakref_type else x

def get_identity(request):
    x_request_id = getattr(settings, REQUEST_ID_HEADER, None)
    if x_request_id:
        return request.META.get(x_request_id, NO_REQUEST_ID)

    identity = uuid.uuid4().bytes
    encoded_id = base64.urlsafe_b64encode(identity)
    safe_id = encoded_id.replace('=', '')

    return safe_id.upper()


def get_username(request):

    user_key = "HTTP_NETWORKAPI_USERNAME"
    auth_key = "HTTP_AUTHORIZATION"
    encoding = 'iso-8859-1'
    username = NO_REQUEST_USER

    if user_key in request.META:
        username = request.META.get(user_key)
        request.is_api = False

    elif auth_key in request.META:
        authorization = request.META.get(auth_key, b'')
        auth = authorization.encode(encoding).split()
        auth_parts = base64.b64decode(auth[1]).decode(encoding).partition(':')
        username = auth_parts[0].upper()
        request.is_api = True

    return username


class ExtraLoggingMiddleware(object):

    FILTER = ExtraLoggingFilter
    logger = logging.getLogger(__name__)

    def __init__(self, root=''):
        self.root = root

    def find_loggers(self):
        """
        Returns a :class:`dict` of names and the associated loggers.
        """
        # Extract the full logger tree from Logger.manager.loggerDict
        # that are under ``self.root``.
        result = {}
        prefix = self.root + '.'
        for name, logger in logging.Logger.manager.loggerDict.iteritems():
            if self.root and not name.startswith(prefix):
                # Does not fall under self.root
                continue
            result[name] = logger
        # Add the self.root logger
        result[self.root] = logging.getLogger(self.root)
        return result

    def find_handlers(self):
        """
        Returns a list of handlers.
        """
        return list(logging._handlerList)

    def _find_filterer_with_filter(self, filterers, filter_cls):
        """
        Returns a :class:`dict` of filterers mapped to a list of filters.

        *filterers* should be a list of filterers.

        *filter_cls* should be a logging filter that should be matched.
        """
        result = {}
        for logger in map(deref, filterers):
            filters = [f for f in map(deref, getattr(logger, 'filters', []))
                       if isinstance(f, filter_cls)]
            if filters:
                result[logger] = filters
        return result

    def find_loggers_with_filter(self, filter_cls):
        """
        Returns a :class:`dict` of loggers mapped to a list of filters.

        Looks for instances of *filter_cls* attached to each logger.
        If the logger has at least one, it is included in the result.
        """
        return self._find_filterer_with_filter(self.find_loggers().values(),
                                               filter_cls)

    def find_handlers_with_filter(self, filter_cls):
        """
        Returns a :class:`dict` of handlers mapped to a list of filters.

        Looks for instances of *filter_cls* attached to each handler.
        If the handler has at least one, it is included in the result.
        """
        return self._find_filterer_with_filter(self.find_handlers(),
                                               filter_cls)

    def logger_has_filter(self, logger, filter_cls):
        """
        Checks if the logger has the filter class
        """
        for filter in logger.filters:
            if isinstance(filter, filter_cls):
                return True

        return False

    def add_filter(self, f, filter_cls=None):
        """Add filter *f* to any loggers that have *filter_cls* filters."""
        if filter_cls is None:
            filter_cls = type(f)
        for logger in self.find_loggers_with_filter(filter_cls):
            if not self.logger_has_filter(logger, filter_cls):
                logger.addFilter(f)
        for handler in self.find_handlers_with_filter(filter_cls):
            handler.addFilter(f)

    def remove_filter(self, f):
        """Remove filter *f* from all loggers."""
        for logger in self.find_loggers_with_filter(type(f)):
            logger.removeFilter(f)
        for handler in self.find_handlers_with_filter(type(f)):
            handler.removeFilter(f)

    def process_request(self, request):
        """Adds a filter, bound to *request*, to the appropriate loggers."""
        request.logging_filter = ExtraLoggingFilter(request)
        identity = get_identity(request)
        username = get_username(request)

        request.request_id = identity
        request.request_user = username
        request.request_path = request.get_full_path()

        #self.add_filter(request.logging_filter)
        # if not self.logger_has_filter(self.logger, type(request.logging_filter)):
        #     self.logger.addFilter(request.logging_filter)

        self.logger.debug(u'INICIO da requisição %s. Data: [%s].' % (request.method, request.raw_post_data))


    def process_response(self, request, response):
        """Removes this *request*'s filter from all loggers."""
        if 399 < response.status_code < 600:
            #logger.debug(u'Requisição concluída com falha. Conteúdo: [%s].' % response.content)
            self.logger.debug(u'Requisição concluída com falha. Conteúdo: [].' )
        else:
            self.logger.debug(u'Requisição concluída com sucesso.')

        self.logger.debug(u'FIM da requisição.')

        f = getattr(request, 'logging_filter', None)
        if f:
            self.remove_filter(f)
        return response

    def process_exception(self, request, exception):
        """Removes this *request*'s filter from all loggers."""
        self.logger.error(u'Erro não esperado.')
        f = getattr(request, 'logging_filter', None)
        if f:
            self.remove_filter(f)

    # def process_request(self, request):
    #
    #     identity = get_identity(request)
    #     username = get_username(request)
    #     local.request_id = identity
    #     local.request_user = username
    #     local.request_path = request.get_full_path()
    #     request.id = identity
    #
    #     logger.debug(u'INICIO da requisição %s. Data: [%s].' % (request.method, request.raw_post_data))
    #
    # def process_response(self, request, response):
    #
    #     if 399 < response.status_code < 600:
    #         #logger.debug(u'Requisição concluída com falha. Conteúdo: [%s].' % response.content)
    #         logger.debug(u'Requisição concluída com falha. Conteúdo: [].' )
    #     else:
    #         logger.debug(u'Requisição concluída com sucesso.')
    #
    #     logger.debug(u'FIM da requisição.')
    #
    #     return response
    #
    # def process_exception(self, request, exception):
    #
    #     logger.error(u'Erro não esperado.')




