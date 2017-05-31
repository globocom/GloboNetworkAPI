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
from networkapi.distributedlock import LOCK_IPV4
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpEquipmentAlreadyAssociation
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import NetworkIPv4Error
from networkapi.ip.models import NetworkIPv4NotFoundError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_int_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class IPv4EditResource(RestResource):

    log = logging.getLogger('IPv4EditResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to edit an IP.

        URL: ipv4/edit/
        """

        self.log.info('Edit an IP')

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
            ip4 = ip_map.get('ip4')

            # Valid id_ip
            if not is_valid_int_greater_zero_param(id_ip):
                self.log.error(
                    u'Parameter id_ip is invalid. Value: %s.', id_ip)
                raise InvalidValueError(None, 'id_ip', id_ip)

            if not is_valid_string_maxsize(ip4, 15):
                self.log.error(u'Parameter ip4 is invalid. Value: %s.', ip4)
                raise InvalidValueError(None, 'ip4', description)

            # Valid description
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

            ip = Ip()

            ip = ip.get_by_pk(id_ip)

            with distributedlock(LOCK_IPV4 % id_ip):

                # se Houver erro no ip informado para retorna-lo na mensagem
                ip_error = ip4

                # verificação se foi passado algo errado no ip
                ip4 = ip4.split('.')
                for oct in ip4:
                    if not is_valid_int_param(oct):
                        raise InvalidValueError(None, 'ip4', ip_error)

                # Ip passado de forma invalida
                if len(ip4) is not 4:
                    raise IndexError

                ip.descricao = description
                ip.oct1 = ip4[0]
                ip.oct2 = ip4[1]
                ip.oct3 = ip4[2]
                ip.oct4 = ip4[3]

                # Persist
                ip.edit_ipv4(user)

                return self.response(dumps_networkapi({}))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except IndexError:
            msg = 'Invalid IP %s' % ip_error
            return self.response_error(150, msg)
        except IpNotFoundError, e:
            return self.response_error(150, e.message)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv4NotFoundError:
            return self.response_error(281)
        except EquipamentoNotFoundError:
            return self.response_error(117, ip_map.get('id_equipment'))
        except IpNotAvailableError, e:
            return self.response_error(150, e.message)
        except IpEquipmentAlreadyAssociation:
            return self.response_error(150, e.message)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except (IpError, NetworkIPv4Error, EquipamentoError, GrupoError), e:
            self.log.error(e)
            return self.response_error(1)
