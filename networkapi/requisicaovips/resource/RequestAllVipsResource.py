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
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsError
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.rest import RestResource


class RequestAllVipsResource(RestResource):

    log = logging.getLogger('RequestAllVipsResource')

    def handle_get(self, request, user, *args, **kwargs):
        """
        Handles GET requests to list all the VIPs.

        URL: vip/all/
        """

        try:
            if not has_perm(user,
                            AdminPermission.VIPS_REQUEST,
                            AdminPermission.READ_OPERATION):
                return self.not_authorized()

            request_vips = RequisicaoVips.get_all()
            vips = {}

            for vip in request_vips:
                request_vip_map = vip.variables_to_map()
                request_vip_map['id'] = vip.id
                request_vip_map['validado'] = vip.validado
                request_vip_map['vip_criado'] = vip.vip_criado
                request_vip_map['id_ip'] = vip.ip_id
                request_vip_map['id_ipv6'] = vip.ipv6_id
                request_vip_map[
                    'id_healthcheck_expect'] = vip.healthcheck_expect_id
                vips['vip_%s' % (vip.id)] = request_vip_map

            return self.response(dumps_networkapi(vips))

        except (RequisicaoVipsNotFoundError):
            return self.response_error(152)
        except (RequisicaoVipsError, GrupoError):
            return self.response_error(1)
