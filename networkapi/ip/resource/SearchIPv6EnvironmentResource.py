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
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.ipaddr import IPv6Address
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import Ipv6
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_ipv6


class SearchIPv6EnvironmentResource(RestResource):

    log = logging.getLogger('SearchIPv6EnvironmentResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to verify that the IPv6 belongs to environment.

        URL:  /ipv6/environment/
        """

        self.log.info('Verify that the IPv6 belongs to environment')

        try:

            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            ipv6_map = networkapi_map.get('ipv6_map')
            if ipv6_map is None:
                return self.response_error(3, u'There is no value to the ipv6_map tag  of XML request.')

            # Get XML data
            environment_id = ipv6_map.get('id_environment')
            ipv6 = ipv6_map.get('ipv6')

            # Valid Environment ID
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'The id_environment parameter is not a valid value: %s.', environment_id)
                raise InvalidValueError(None, 'id_environment', environment_id)

            # Valid IPv6 ID
            if not is_valid_ipv6(ipv6):
                self.log.error(
                    u'The ipv6 parameter is not a valid value: %s.', ipv6)
                raise InvalidValueError(None, 'ipv6', ipv6)

            blocks = str(IPv6Address(ipv6).exploded).split(':')

            # Find Environment by ID to check if it exist
            environment = Ambiente.get_by_pk(environment_id)

            # Find Ipv6 by blocks to check if it exist
            IPv6 = Ipv6.get_by_octs_and_environment(blocks[0], blocks[1], blocks[2], blocks[
                                                    3], blocks[4], blocks[5], blocks[6], blocks[7], environment_id)

            # Generate return map
            ipv6_map = dict()
            ipv6_map['id'] = IPv6.id
            ipv6_map['id_vlan'] = IPv6.networkipv6.vlan.id
            ipv6_map['bloco1'] = IPv6.block1
            ipv6_map['bloco2'] = IPv6.block2
            ipv6_map['bloco3'] = IPv6.block3
            ipv6_map['bloco4'] = IPv6.block4
            ipv6_map['bloco5'] = IPv6.block5
            ipv6_map['bloco6'] = IPv6.block6
            ipv6_map['bloco7'] = IPv6.block7
            ipv6_map['bloco8'] = IPv6.block8
            ipv6_map['descricao'] = IPv6.description

            return self.response(dumps_networkapi({'ipv6': ipv6_map}))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError:
            return self.response_error(119)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except (IpError, AmbienteError):
            return self.response_error(1)
