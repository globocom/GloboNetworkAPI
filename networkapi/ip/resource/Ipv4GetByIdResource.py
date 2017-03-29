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
from networkapi.ip.models import Ip
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotFoundError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class Ipv4GetByIdResource(RestResource):

    log = logging.getLogger('IPv4GetResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to get a ipv4 by id.

        URLs: ip/get-ipv4/id_ip
        """

        try:
            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Valid id access
            id_ip = kwargs.get('id_ip')

            if not is_valid_int_greater_zero_param(id_ip):
                raise InvalidValueError(None, 'id_ip', id_ip)

            # Business Rules

            ip = Ip()
            ip = ip.get_by_pk(id_ip)

            ip_map = dict()
            equip_list = []

            for ipequip in ip.ipequipamento_set.all():
                equip_list.append(ipequip.equipamento.nome)

            # IP map
            ip_map = model_to_dict(ip)
            ip_map['equipamentos'] = equip_list if len(
                equip_list) > 0 else None

            # Return XML
            return self.response(dumps_networkapi({'ipv4': ip_map}))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError, e:
            return self.response_error(119)
        except (IpError):
            return self.response_error(1)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
