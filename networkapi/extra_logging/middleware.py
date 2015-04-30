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

from networkapi.extra_logging import local, REQUEST_ID_HEADER, NO_REQUEST_ID, NO_REQUEST_USER


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
    return request.META.get(user_key, NO_REQUEST_USER)


class ExtraLoggingMiddleware(object):

    def process_request(self, request):

        identity = get_identity(request)
        username = get_username(request)
        local.request_id = identity
        local.request_user = username
        local.request_path = request.get_full_path()
        request.id = identity




