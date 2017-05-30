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

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.filter.models import Filter
from networkapi.filter.models import FilterError
from networkapi.filter.models import FilterNotFoundError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class FilterGetByIdResource(RestResource):

    """Class that receives requests to get a Filter by id."""

    log = logging.getLogger('FilterGetByIdResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat GET requests to get a Filter by id.

        URL: filter/get/<id_filter>/
        """

        try:

            self.log.info('Get Filter by id')
            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
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

            filter_dict = model_to_dict(fil)
            filter_dict['equip_types'] = list()
            for fil_equip_type in fil.filterequiptype_set.all():
                filter_dict['equip_types'].append(
                    model_to_dict(fil_equip_type.equiptype))

            return self.response(dumps_networkapi({'filter': filter_dict}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except FilterNotFoundError, e:
            return self.response_error(339)
        except FilterError, e:
            return self.response_error(1)
        except BaseException, e:
            return self.response_error(1)
