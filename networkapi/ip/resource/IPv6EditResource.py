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
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_IPV6
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import IpEquipmentAlreadyAssociation
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import NetworkIPv6Error
from networkapi.ip.models import NetworkIPv6NotFoundError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class IPv6EditResource(RestResource):

    log = logging.getLogger('IPv6EditResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to edit an IP6.

        URL: ipv6/edit/
        """

        self.log.info('Edit an IP6 and associate it to an equipment')

        try:
            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            ip_map = networkapi_map.get('ip_map')
            if ip_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            id_ip = ip_map.get('id_ip')
            description = ip_map.get('descricao')
            ip6 = ip_map.get('ip6')

            # Valid equip_id
            if not is_valid_int_greater_zero_param(id_ip):
                self.log.error(
                    u'Parameter id_ip is invalid. Value: %s.', id_ip)
                raise InvalidValueError(None, 'id_ip', id_ip)

            # Description can NOT be greater than 100
            if not is_valid_string_maxsize(ip6, 39):
                self.log.error(
                    u'Parameter descricao is invalid. Value: %s.', ip6)
                raise InvalidValueError(None, 'ip6', ip6)

            if description is not None:
                if not is_valid_string_maxsize(description, 100) or not is_valid_string_minsize(description, 3):
                    self.log.error(
                        u'Parameter description is invalid. Value: %s.', description)
                    raise InvalidValueError(None, 'description', description)

            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.WRITE_OPERATION):
                raise UserNotAuthorizedError(
                    None, u'User does not have permission to perform the operation.')

            # Business Rules

            # New IP

            ipv6 = Ipv6()

            ipv6 = ipv6.get_by_pk(id_ip)

            with distributedlock(LOCK_IPV6 % id_ip):

                ip_error = ip6
                ip6 = ip6.split(':')

                # Ip informado de maneira incorreta
                if len(ip6) is not 8:
                    raise InvalidValueError(None, 'ip6', ip_error)

                ipv6.description = description
                ipv6.block1 = ip6[0]
                ipv6.block2 = ip6[1]
                ipv6.block3 = ip6[2]
                ipv6.block4 = ip6[3]
                ipv6.block5 = ip6[4]
                ipv6.block6 = ip6[5]
                ipv6.block7 = ip6[6]
                ipv6.block8 = ip6[7]
                # Persist
                ipv6.edit_ipv6(user)

                return self.response(dumps_networkapi({}))

        except IpNotFoundError, e:
            return self.response_error(150, e.message)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv6NotFoundError:
            return self.response_error(281)
        except EquipamentoNotFoundError:
            return self.response_error(117, ip_map.get('id_equipment'))
        except IpNotAvailableError, e:
            return self.response_error(150, e.message)
        except IpEquipmentAlreadyAssociation:
            return self.response_error(150, e.message)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except (IpError, NetworkIPv6Error, EquipamentoError, GrupoError), e:
            self.log.error(e)
            return self.response_error(1)
