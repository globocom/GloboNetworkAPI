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
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv4Error
from networkapi.ip.models import NetworkIPv4NotFoundError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class NetworkIPv4GetResource(RestResource):

    log = logging.getLogger('NetworkIPv4GetResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to list all network IPv4 by network ipv4 id.

        URLs: network/ipv4/id/id_rede4
         """

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Valid id access
            id_network = kwargs.get('id_rede4')

            if not is_valid_int_greater_zero_param(id_network):
                self.log.error(
                    u'Parameter id_rede is invalid. Value: %s.', id_network)
                raise InvalidValueError(None, 'id_rede4', id_network)

            # Business Rules

            network = NetworkIPv4.get_by_pk(id_network)

            network_map = dict()
            network_map['network'] = model_to_dict(network)

            # Return XML
            return self.response(dumps_networkapi(network_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv4NotFoundError, e:
            return self.response_error(281)
        except (NetworkIPv4Error):
            return self.response_error(1)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
