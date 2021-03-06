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
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import IpEquipmentNotFoundError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import Ipv6Equipament
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class IPv6GetResource(RestResource):

    log = logging.getLogger('IPv6GetResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to get a ipv6.

        URLs: ipv6/get/id_ip6
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
            id_ip = kwargs.get('id_ipv6')

            if not is_valid_int_greater_zero_param(id_ip):
                raise InvalidValueError(None, 'id_ip', id_ip)

            # Business Rules

            ip = Ipv6()

            ip = ip.get_by_pk(id_ip)

            EquipIps = []
            mapa = dict()
            # lista = []

            try:

                EquipIps = []
                equipsIp = Ipv6Equipament.list_by_ip6(ip.id)
                for eIp in equipsIp:
                    EquipIps.append(eIp)
                mapa[ip.id] = EquipIps
                # lista.append(mapa)

            except IpEquipmentNotFoundError:
                EquipIps.append(None)
            except IpError:
                EquipIps.append(None)

            network_map = dict()

            list_ips = []
            lequips = []

            lequips = []
            ip_maps = dict()
            ip_maps['id'] = ip.id
            ip_maps['block1'] = ip.block1
            ip_maps['block2'] = ip.block2
            ip_maps['block3'] = ip.block3
            ip_maps['block4'] = ip.block4
            ip_maps['block5'] = ip.block5
            ip_maps['block6'] = ip.block6
            ip_maps['block7'] = ip.block7
            ip_maps['block8'] = ip.block8
            ip_maps['descricao'] = ip.description
            for equip in mapa.get(ip.id):
                equip = Equipamento.get_by_pk(equip.equipamento.id)
                lequips.append(model_to_dict(equip))
            ip_maps['equipamento'] = lequips
            list_ips.append(ip_maps)

            list_ips

            network_map['ips'] = list_ips

            # Return XML
            return self.response(dumps_networkapi(network_map))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError, e:
            return self.response_error(119)
        except EquipamentoNotFoundError, e:
            return self.response_error(281, id_ip)
        except EquipamentoError, e:
            return self.response_error(1)
        except IpEquipmentNotFoundError, e:
            return self.response_error(281, id_ip)
        except (IpError):
            return self.response_error(1)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
