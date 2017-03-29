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

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.equipamento.models import EquipamentoError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import NetworkIPv6Error
from networkapi.ip.models import NetworkIPv6NotFoundError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class IPv6GetAvailableResource(RestResource):

    log = logging.getLogger('IPv6GetAvailableResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests get an IP6 available.

        URL: ip/availableip6/ip_rede
        """

        self.log.info('Get an IP6 available')

        try:
            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Valid id access
            id_network6 = kwargs.get('id_rede')

            if not is_valid_int_greater_zero_param(id_network6):
                self.log.error(
                    u'Parameter id_rede6 is invalid. Value: %s.', id_network6)
                raise InvalidValueError(None, 'id_rede6', id_network6)

            # Business Rules

            ip6 = Ipv6.get_available_ip6(id_network6)

            list_ip = []
            list_ip.append(ip6)
            network_map = dict()
            map_aux = dict()
            map_aux['ip6'] = list_ip

            network_map['ip6'] = map_aux

            # Business Rules

            return self.response(dumps_networkapi(network_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv6NotFoundError:
            return self.response_error(286)
        except IpNotAvailableError, e:
            return self.response_error(150, e.message)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except (IpError, NetworkIPv6Error, EquipamentoError, GrupoError):
            return self.response_error(1)
