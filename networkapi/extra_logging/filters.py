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

from networkapi.extra_logging import local
from networkapi.extra_logging import NO_REQUEST_CONTEXT
from networkapi.extra_logging import NO_REQUEST_ID
from networkapi.extra_logging import NO_REQUEST_PATH
from networkapi.extra_logging import NO_REQUEST_USER


class ExtraLoggingFilter(logging.Filter):

    def filter(self, record):

        record.request_id = getattr(local, 'request_id', NO_REQUEST_ID)
        record.request_path = getattr(local, 'request_path', NO_REQUEST_PATH)
        record.request_user = getattr(local, 'request_user', NO_REQUEST_USER)
        record.request_context = getattr(
            local, 'request_context', NO_REQUEST_CONTEXT)
        return True


class StaticFieldFilter(logging.Filter):

    """
    Python logging filter that adds the given static contextual information
    in the ``fields`` dictionary to all logging records.
    """

    def __init__(self, fields):
        self.static_fields = fields

    def filter(self, record):
        for k, v in self.static_fields.items():
            setattr(record, k, v)
        return True


class RequestFilter(logging.Filter):

    """
    Python logging filter that removes the (non-pickable) Django ``request``
    object from the logging record.
    """

    def filter(self, record):
        if hasattr(record, 'request'):
            del record.request
        return True


class UserFilter(logging.Filter):

    """
    """

    def filter(self, record):

        if hasattr(record, 'request_user'):
            record.user = record.request_user
            del record.request_user

        return True
