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
from networkapi.ambiente.models import IP_VERSION
from networkapi.auth import has_perm
from networkapi.equipamento.models import Equipamento
from networkapi.error_message_utils import error_messages
from networkapi.exception import InvalidValueError
from networkapi.exception import NetworkInactiveError
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv4NotFoundError
from networkapi.ip.models import NetworkIPv6
from networkapi.ip.models import NetworkIPv6NotFoundError
from networkapi.rest import RestResource
from networkapi.settings import NETWORKIPV4_REMOVE
from networkapi.settings import NETWORKIPV6_REMOVE
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_version_ip


class NetworkRemoveResource(RestResource):

    log = logging.getLogger('NetworkRemoveResource')

    NETWORK_TYPE_V4 = 'v4'
    CODE_MESSAGE_INACTIVE_NETWORK = 363
    CODE_MESSAGE_OBJECT_DOES_NOT_EXIST_V4 = 281
    CODE_MESSAGE_OBJECT_DOES_NOT_EXIST_V6 = 286
    CODE_MESSAGE_INVALID_PARAM = 269
    CODE_MESSAGE_DEFAULT_ERROR = 1

    def handle_put(self, request, user, *args, **kwargs):
        """Handles PUT requests to remove Network and Vlan.

        URL: network/remove/
        """
        try:

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            network_map = networkapi_map.get('network')
            ids = network_map.get('ids')

            # if 'ids' is a list
            if isinstance(ids, list):
                if not self.check_permission_equipment(user, ids):
                    return self.not_authorized()
                for id in ids:
                    code, stdout, stderr = self.deactivate_network(user, id)
            else:
                if not self.check_permission_equipment(user, [ids]):
                    return self.not_authorized()
                code, stdout, stderr = self.deactivate_network(user, ids)

            if code != 0:
                return self.response_error(2, stdout + stderr)

            return self.response(dumps_networkapi({'network': network_map}))

        except NetworkInactiveError, e:
            self.log.error(e.cause)
            return self.response_error(self.CODE_MESSAGE_INACTIVE_NETWORK)

        except NetworkIPv4NotFoundError, e:
            self.log.error(e.message)
            return self.response_error(self.CODE_MESSAGE_OBJECT_DOES_NOT_EXIST_V4)

        except NetworkIPv6NotFoundError, e:
            self.log.error(e.message)
            return self.response_error(self.CODE_MESSAGE_OBJECT_DOES_NOT_EXIST_V6)

        except InvalidValueError, e:
            return self.response_error(self.CODE_MESSAGE_INVALID_PARAM, e.param, e.value)

        except Exception, e:
            return self.response_error(self.CODE_MESSAGE_DEFAULT_ERROR)

    def check_permission_equipment(self, user, ids):
        # Check permission group equipments
        for row in ids:
            id_network, network_type = self.get_id_and_net_type(row)
            if network_type == self.NETWORK_TYPE_V4:
                equips_from_ipv4 = Equipamento.objects.filter(
                    ipequipamento__ip__networkipv4=id_network, equipamentoambiente__is_router=1)
                for equip in equips_from_ipv4:
                    # User permission
                    if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
                        self.log.error(
                            u'User does not have permission to perform the operation.')
                        return False
            else:
                equips_from_ipv6 = Equipamento.objects.filter(
                    ipv6equipament__ip__networkipv6=id_network, equipamentoambiente__is_router=1)
                for equip in equips_from_ipv6:
                    # User permission
                    if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
                        self.log.error(
                            u'User does not have permission to perform the operation.')
                        return False

        return True

    def deactivate_network(self, user, id):

        id_network, network_type = self.get_id_and_net_type(id)

        if not is_valid_int_greater_zero_param(id_network):
            self.log.error(
                u'The id network parameter is invalid. Value: %s.', id_network)
            raise InvalidValueError(None, 'id_network', id_network)

        if not is_valid_version_ip(network_type, IP_VERSION):
            self.log.error(
                u'The type network parameter is invalid value: %s.', network_type)
            raise InvalidValueError(None, 'network_type', network_type)

        if not self.is_active_netwok(net):
            code = 0
            stdout = 'Nothing to do. Network is not active.'
            stderr = ''
        else:
            if network_type == self.NETWORK_TYPE_V4:
                net = NetworkIPv4.get_by_pk(id_network)

                command = NETWORKIPV4_REMOVE % int(id_network)

                code, stdout, stderr = exec_script(command)
                if code == 0:
                    net = NetworkIPv4.get_by_pk(id_network)
                    net.deactivate(user)
            else:
                net = NetworkIPv6.get_by_pk(id_network)

                command = NETWORKIPV6_REMOVE % int(id_network)

                code, stdout, stderr = exec_script(command)
                if code == 0:
                    net.deactivate(user)

        return code, stdout, stderr

    def get_id_and_net_type(self, id):
        # id => ex: '55-v4' or '55-v6'
        value = id.split('-')

        if len(value) != 2:
            self.log.error(
                u'The id network parameter is invalid format: %s.', value)
            raise InvalidValueError(None, 'id_network', value)

        id_network = value[0]
        network_type = value[1]
        return id_network, network_type

    def is_active_netwok(self, network):
        return network.active
