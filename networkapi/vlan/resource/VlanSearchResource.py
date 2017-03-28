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
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv4NotFoundError
from networkapi.ip.models import NetworkIPv6
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanNotFoundError


class VlanSearchResource(RestResource):

    log = logging.getLogger('VlanSearchResource')

    def get_vlan_map(self, vlan, network_ipv4, network_ipv6):
        vlan_map = model_to_dict(vlan)

        if network_ipv4 is not None and len(network_ipv4) > 0:
            net_map = []
            for net in network_ipv4:
                net_dict = model_to_dict(net)
                net_map.append(net_dict)

            vlan_map['redeipv4'] = net_map
        else:
            vlan_map['redeipv4'] = None

        if network_ipv6 is not None and len(network_ipv6) > 0:
            net_map = []
            for net in network_ipv6:
                net_dict = model_to_dict(net)
                net_map.append(net_dict)

            vlan_map['redeipv6'] = net_map
        else:
            vlan_map['redeipv6'] = None

        return vlan_map

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to search VLAN by ID.
        Network IPv4/IPv6 related will also be fetched.

        URLs: /vlan/<id_vlan>/network/
        """

        self.log.info('Search VLAN by ID')

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Load URL param
            vlan_id = kwargs.get('id_vlan')

            # Valid VLAN ID
            if not is_valid_int_greater_zero_param(vlan_id):
                self.log.error(
                    u'Parameter id_vlan is invalid. Value: %s.', vlan_id)
                raise InvalidValueError(None, 'id_vlan', vlan_id)

            # Existing VLAN ID
            vlan = Vlan().get_by_pk(vlan_id)

            # Get all network_ipv4/ipv6 related to vlan
            try:
                network_ipv4 = NetworkIPv4.objects.filter(
                    vlan=vlan).order_by('id')
                network_ipv6 = NetworkIPv6.objects.filter(
                    vlan=vlan).order_by('id')
            except Exception, e:
                self.log.error(
                    u'Error finding the first network_ipv4 from vlan.')
                raise NetworkIPv4NotFoundError(
                    e, u'Error finding the first network_ipv4 from vlan.')

            vlan_map = self.get_vlan_map(vlan, network_ipv4, network_ipv6)

            map = dict()
            map['vlan'] = vlan_map

            return self.response(dumps_networkapi(map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except VlanNotFoundError:
            return self.response_error(116)

        except NetworkIPv4NotFoundError:
            return self.response_error(281)

        except (VlanError, GrupoError):
            return self.response_error(1)

        except Exception, e:
            return self.response_error(1)
