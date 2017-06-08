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

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rack.models import Rack
from networkapi.rack.models import RackError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError


class GetRackResource(RestResource):

    log = logging.getLogger('GetRackResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to find all Racks

        URLs: /rack/find/
        """

        self.log.info('Get Rack')

        try:

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Get XML data
            nome = kwargs.get('nome')
            rack_map = []

            racks = Rack.objects.all().filter(nome__exact=nome)

            for var in racks:
                rack_map.append(model_to_dict(var))

            return self.response(dumps_networkapi({'rack': rack_map}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RackError:
            return self.response_error(1)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
