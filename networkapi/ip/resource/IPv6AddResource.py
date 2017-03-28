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
from networkapi.distributedlock import LOCK_NETWORK_IPV6
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import NetworkIPv6Error
from networkapi.ip.models import NetworkIPv6NotFoundError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class IPv6AddResource(RestResource):

    log = logging.getLogger('IPv6AddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to add an IP and associate it to an equipment.

        URL: ipv6/
        """

        self.log.info('Add an IPv6 and associate it to an equipment')

        try:

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            ip_map = networkapi_map.get('ip')
            if ip_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            equip_id = ip_map.get('id_equip')
            network_ipv6_id = ip_map.get('id_network_ipv6')
            description = ip_map.get('description')

            # Valid equip_id
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'Parameter id_equip is invalid. Value: %s.', equip_id)
                raise InvalidValueError(None, 'id_equip', equip_id)

            # Valid network_ipv6_id
            if not is_valid_int_greater_zero_param(network_ipv6_id):
                self.log.error(
                    u'Parameter id_network_ipv6 is invalid. Value: %s.', network_ipv6_id)
                raise InvalidValueError(
                    None, 'id_network_ipv6', network_ipv6_id)

            # Description can NOT be greater than 100
            if not is_valid_string_maxsize(description, 100) or not is_valid_string_minsize(description, 3):
                self.log.error(
                    u'Parameter description is invalid. Value: %s.', description)
                raise InvalidValueError(None, 'description', description)

            # User permission
            if not has_perm(user,
                            AdminPermission.IPS,
                            AdminPermission.WRITE_OPERATION,
                            None,
                            equip_id,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                raise UserNotAuthorizedError(
                    None, u'User does not have permission to perform the operation.')

            # Business Rules

            with distributedlock(LOCK_NETWORK_IPV6 % network_ipv6_id):

                # New IPv6
                ipv6 = Ipv6()
                ipv6.description = description

                # Persist
                ipv6.create(user, equip_id, network_ipv6_id)

                # Generate return map
                ip_map = dict()
                ip_map['id'] = ipv6.id
                ip_map['id_redeipv6'] = ipv6.networkipv6.id
                ip_map['bloco1'] = ipv6.block1
                ip_map['bloco2'] = ipv6.block2
                ip_map['bloco3'] = ipv6.block3
                ip_map['bloco4'] = ipv6.block4
                ip_map['bloco5'] = ipv6.block5
                ip_map['bloco6'] = ipv6.block6
                ip_map['bloco7'] = ipv6.block7
                ip_map['bloco8'] = ipv6.block8
                ip_map['descricao'] = ipv6.description

                return self.response(dumps_networkapi({'ip': ip_map}))

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except NetworkIPv6NotFoundError:
            return self.response_error(286)

        except EquipamentoNotFoundError:
            return self.response_error(117, ip_map.get('id_equipment'))

        except IpNotAvailableError, e:
            return self.response_error(150, e.message)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except (IpError, NetworkIPv6Error, EquipamentoError, GrupoError):
            return self.response_error(1)
