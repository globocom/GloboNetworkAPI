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
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.exception import EnvironmentVipError
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class RequestAllVipsEnviromentVipResource(RestResource):

    log = logging.getLogger('RequestAllVipsEnviromentVipResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the VIPs related to Environment VIP.

        URL: environmentvip/<id_environment_vip>/vip/all'
        """

        try:

            self.log.info(
                'GET to list all the VIPs related to Environment VIP')

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_VIP, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Get data
            id_environment_vip = kwargs.get('id_environment_vip')

            # Valid Environment VIP ID
            if not is_valid_int_greater_zero_param(id_environment_vip):
                self.log.error(
                    u'The id_environment_vip parameter is not a valid value: %s.', id_environment_vip)
                raise InvalidValueError(
                    None, 'id_environment_vip', id_environment_vip)

            # Find Environment VIP by ID to check if it exist
            environment_vip = EnvironmentVip.get_by_pk(id_environment_vip)

            # Find Request VIP - IPv4 by ID Environment
            vips_ipv4 = RequisicaoVips.objects.filter(
                ip__networkipv4__ambient_vip__id=environment_vip.id)

            # Find Request VIP - IPv6 by ID Environment
            vips_ipv6 = RequisicaoVips.objects.filter(
                ipv6__networkipv6__ambient_vip__id=environment_vip.id)

            vips = {}
            for vips_ip in [vips_ipv4, vips_ipv6]:

                for vip in vips_ip:

                    v = {}
                    v = vip.variables_to_map()
                    v['id'] = vip.id
                    v['validado'] = vip.validado
                    v['vip_criado'] = vip.vip_criado
                    v['id_ip'] = vip.ip_id
                    v['id_ipv6'] = vip.ipv6_id
                    v['id_healthcheck_expect'] = vip.healthcheck_expect_id
                    vips['vip_%s' % (vip.id)] = v

            return self.response(dumps_networkapi(vips))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except EnvironmentVipNotFoundError:
            return self.response_error(283)

        except EnvironmentVipError:
            return self.response_error(1)
