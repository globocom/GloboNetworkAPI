# -*- coding: utf-8 -*-
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
import logging

from networkapi.api_rest.authentication import BasicAuthentication
from networkapi.extra_logging import local
from networkapi.rest import RestResource
# from django.conf import settings


class SQLLogMiddleware(object):

    log = logging.getLogger('SQLLogMiddleware')

    """Log the execution time of a SQL in a request."""

    def process_response(self, request, response):
        from django.db import connection
        for q in connection.queries:
            self.log.debug(
                u'Query: %s, Time spent: %s', q['sql'], q['time'])
        return response


class TrackingRequestOnThreadLocalMiddleware(object):

    """
    Middleware that gets various objects from the request
    object and saves them in thread local storage.

    """

    def _get_ip(self, request):
        # get real ip
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        elif 'Client-IP' in request.META:
            ip = request.META['Client-IP']
        else:
            ip = request.META['REMOTE_ADDR']
        ip = ip.split(',')[0]
        return ip

    def process_request(self, request):

        from networkapi.eventlog.models import AuditRequest
        if not request.user.is_anonymous():
            ip = self._get_ip(request)
            context = local.request_id
            identity = local.request_context

            AuditRequest.new_request(request.get_full_path(), request.user,
                                     ip, identity, context)
        else:
            user_auth_tuple = BasicAuthentication().authenticate(request)

            if user_auth_tuple is not None:
                user, token = user_auth_tuple
            else:  # keeps compatibility with old authentication method
                user = RestResource.authenticate_user(request)

            if user is not None:
                ip = self._get_ip(request)
                context = local.request_id
                identity = local.request_context
                AuditRequest.new_request(request.get_full_path(), user,
                                         ip, identity, context)

    def process_response(self, request, response):
        from networkapi.eventlog.models import AuditRequest
        AuditRequest.cleanup_request()

        return response
