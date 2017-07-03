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
from __future__ import with_statement

import logging

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.filter.models import Filter
from networkapi.filter.models import FilterDuplicateError
from networkapi.filter.models import FilterError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource


class FilterAddResource(RestResource):

    """Class that receives requests to add new Filters."""

    log = logging.getLogger('FilterAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST requests to add new Filter.

        URL: filter/
        """

        try:

            self.log.info('Add Filter')
            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            filter_map = networkapi_map.get('filter')
            if filter_map is None:
                return self.response_error(3, u'There is no value to the filter tag  of XML request.')

            # New Filter
            filter_ = Filter()

            # Validates
            filter_.validate_filter(filter_map)

            try:
                # Save filter
                filter_.save()
            except Exception, e:
                self.log.error(u'Failed to save the filter.')
                raise FilterError(e, u'Failed to save the filter')

            filter_map = dict()
            filter_map['id'] = filter_.id

            return self.response(dumps_networkapi({'filter': filter_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except FilterDuplicateError, e:
            return self.response_error(344, e.message)
        except FilterError, e:
            return self.response_error(338)
        except BaseException, e:
            return self.response_error(1)
