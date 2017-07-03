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
from networkapi.ip.models import NetworkIPv6
from networkapi.ip.models import NetworkIPv6NotFoundError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class IPv6ListResource(RestResource):

    log = logging.getLogger('NetworkIPv6GetResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to list all network IPv6 by network ipv6 id.

        URLs: ip/id_network_ipv6/id_rede
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
            id_network = kwargs.get('id_rede')

            if not is_valid_int_greater_zero_param(id_network):
                raise InvalidValueError(None, 'id_rede', id_network)

            # Business Rules

            NetworkIPv6.get_by_pk(id_network)

            ips = Ipv6.list_by_network(id_network)

            try:
                len(ips)
            except Exception, e:
                raise InvalidValueError(None, 'id_rede', id_network)

            if ips is None or len(ips) <= 0:
                raise IpNotFoundError(305, id_network)

            EquipIps = []
            mapa = dict()
            # lista = []

            try:
                for ip in ips:
                    EquipIps = []
                    equipsIp = Ipv6Equipament.list_by_ip6(ip.id)
                    for eIp in equipsIp:
                        EquipIps.append(eIp)
                    mapa[ip.id] = EquipIps
                    # lista.append(mapa)bora pegar cafe

            except IpEquipmentNotFoundError:
                EquipIps.append(None)
            except IpError:
                EquipIps.append(None)

            network_map = dict()
            list_ips = []
            lequips = []

            for ip in ips:
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

            network_map['ips'] = list_ips

            network_map
            # Return XML
            return self.response(dumps_networkapi(network_map))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError:
            return self.response_error(305, id_network)
        except (IpEquipmentNotFoundError, NetworkIPv6NotFoundError):
            return self.response_error(286)
        except (EquipamentoNotFoundError, EquipamentoError, IpError):
            return self.response_error(1)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
