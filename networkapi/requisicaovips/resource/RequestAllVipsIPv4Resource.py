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
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.ip.models import Ip
from networkapi.ip.models import IpNotFoundError
from networkapi.requisicaovips.models import RequisicaoVipsError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_param
from networkapi.util import is_valid_ip


class RequestAllVipsIPv4Resource(RestResource):

    log = logging.getLogger('RequestAllVipsIPv4Resource')

    def handle_post(self, request, user, *args, **kwargs):
        """
        Handles POST requests to list all the VIPs related to IPv4 id.

        URL: vip/ipv4/all/
        """

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VIPS_REQUEST, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag of XML request.')
            vip_map = networkapi_map.get('vip')
            if vip_map is None:
                return self.response_error(3, u'There is no value to the vip tag of XML request.')

            # Get XML data
            ip_str = str(vip_map['ipv4'])
            all_prop = str(vip_map['all_prop'])

            # Valid IPv4
            if not is_valid_ip(ip_str):
                self.log.error(
                    u'Parameter ipv4 is invalid. Value: %s.', ip_str)
                raise InvalidValueError(None, 'ipv4', ip_str)

            # Valid all_prop
            if not is_valid_int_param(all_prop):
                self.log.error(
                    u'Parameter all_prop is invalid. Value: %s.', all_prop)
                raise InvalidValueError(None, 'all_prop', all_prop)
            all_prop = int(all_prop)
            if all_prop not in (0, 1):
                self.log.error(
                    u'Parameter all_prop is invalid. Value: %s.', all_prop)
                raise InvalidValueError(None, 'all_prop', all_prop)

            # Find IPv4 by octs
            octs = ip_str.split('.')

            if len(octs) != 4:
                self.log.error(
                    u'Parameter ipv4 is invalid. Value: %s.', ip_str)
                raise InvalidValueError(None, 'ipv4', ip_str)

            ipv4 = Ip().get_by_octs(octs[0], octs[1], octs[2], octs[3])

            # Business Rules
            list_ips = []
            for ip in ipv4:

                ips_map = dict()
                ips_map = model_to_dict(ip)

                # Find all VIPs related to ipv4
                if all_prop == 1:
                    ips_map['vips'] = ip.requisicaovips_set.all().values()
                else:
                    vips = ip.requisicaovips_set.all().values_list(
                        'id', flat=True)
                    ips_map['vips'] = [int(item) for item in vips]

                list_ips.append(ips_map)

            # Return XML
            vips_map = dict()
            vips_map['ips'] = list_ips

            return self.response(dumps_networkapi(vips_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError, e:
            return self.response_error(119)
        except (RequisicaoVipsError, GrupoError):
            return self.response_error(1)
        except UserNotAuthorizedError:
            return self.not_authorized()
