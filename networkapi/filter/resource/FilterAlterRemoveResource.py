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
from networkapi.filter.models import FilterNotFoundError
from networkapi.filterequiptype.models import CantDissociateError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class FilterAlterRemoveResource(RestResource):

    """Class that receives requests to edit and remove Filters."""

    log = logging.getLogger('FilterAlterRemoveResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat PUT requests to edit Filters.

        URL: filter/<id_filter>/
        """

        try:

            self.log.info('Alter Filter')
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

            if not is_valid_int_greater_zero_param(kwargs['id_filter']):
                self.log.error(
                    u'Parameter id_filter is invalid. Value: %s.', kwargs['id_filter'])
                raise InvalidValueError(None, 'id_filter', kwargs['id_filter'])
            else:
                # Check existence
                fil = Filter().get_by_pk(kwargs['id_filter'])

            fil.validate_filter(filter_map)

            try:
                # Save filter
                fil.save()
            except Exception, e:
                self.log.error(u'Failed to edit the filter.')
                raise e

            return self.response(dumps_networkapi({}))

        except FilterDuplicateError, e:
            return self.response_error(344, e.message)
        except CantDissociateError, e:
            return self.response_error(348, e.cause['equiptype'], e.cause['filter_name'])
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except FilterNotFoundError, e:
            return self.response_error(339)
        except FilterError, e:
            return self.response_error(340)
        except BaseException, e:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat DELETE requests to remove Filters.

        URL: filter/<id_filter>/
        """

        try:

            self.log.info('Remove Filter')
            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            if not is_valid_int_greater_zero_param(kwargs['id_filter']):
                self.log.error(
                    u'Parameter id_filter is invalid. Value: %s.', kwargs['id_filter'])
                raise InvalidValueError(None, 'id_filter', kwargs['id_filter'])
            else:
                # Check existence
                fil = Filter().get_by_pk(kwargs['id_filter'])

            try:
                # Remove filter and its relationships
                fil.delete()
            except Exception, e:
                self.log.error(u'Failed to remove the filter.')
                raise e

            return self.response(dumps_networkapi({}))

        except CantDissociateError, e:
            return self.response_error(348, e.cause['equiptype'], e.cause['filter_name'])
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except FilterNotFoundError, e:
            return self.response_error(339)
        except FilterError, e:
            return self.response_error(341)
        except BaseException, e:
            return self.response_error(1)
