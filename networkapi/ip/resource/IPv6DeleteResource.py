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
from networkapi.equipamento.models import EquipamentoAmbienteNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.ip.models import IpCantBeRemovedFromVip
from networkapi.ip.models import IpCantRemoveFromServerPool
from networkapi.ip.models import IpEquipCantDissociateFromVip
from networkapi.ip.models import IpEquipmentNotFoundError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import NetworkIPv4Error
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class IPv6DeleteResource(RestResource):

    log = logging.getLogger('IPv6DeleteResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests for delete an IP6

        URL: ip6/delete/id_ip6
        """

        self.log.info('Delete an IP6')

        try:

            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations
            # Valid id access
            id_ip = kwargs.get('id_ipv6')

            if not is_valid_int_greater_zero_param(id_ip):
                self.log.error(
                    u'Parameter id_ip is invalid. Value: %s.', id_ip)
                raise InvalidValueError(None, 'id_rede', id_ip)

            ip = Ipv6.get_by_pk(id_ip)

            with distributedlock(LOCK_IPV6 % id_ip):

                locks_list = [LOCK_IPV6 % id_ip]
                # Business Rules
                ip.delete_v3(locks_list)

                return self.response(dumps_networkapi({}))

        except IpCantBeRemovedFromVip, e:
            return self.response_error(319, 'ip', 'ipv6', id_ip)
        except IpCantRemoveFromServerPool, e:
            return self.response_error(385, e.cause.get('ip'), e.cause.get('equip_name'), e.cause.get('server_pool_identifiers'))
        except IpEquipCantDissociateFromVip, e:
            return self.response_error(352, e.cause.get('ip'), e.cause.get('equip_name'), e.cause.get('vip_id'))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except IpEquipmentNotFoundError, e:
            return self.response_error(308, id_ip)
        except EquipamentoAmbienteNotFoundError, e:
            return self.response_error(307, e.message)
        except IpNotFoundError, e:
            return self.response_error(119)
        except (IpError, NetworkIPv4Error, GrupoError):
            return self.response_error(1)
