# -*- coding:utf-8 -*-

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
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param,\
    destroy_cache_function, mount_ipv6_string
from networkapi.exception import InvalidValueError
from networkapi.ip.models import NetworkIPv6, Ipv6Equipament, NetworkIPv6NotFoundError, IpCantRemoveFromServerPool
from networkapi.distributedlock import distributedlock, LOCK_NETWORK_IPV6
from networkapi.ip.models import IpCantBeRemovedFromVip
from networkapi.equipamento.models import EquipamentoAmbienteNotFoundError,\
    Equipamento
from networkapi.requisicaovips.models import ServerPoolMember


class NetworkIPv6DeallocateResource(RestResource):

    log = Log('NetworkIPv6DeallocateResource')

    def handle_delete(self, request, user, *args, **kwargs):
        '''Handles DELETE requests to deallocate all relationships between NetworkIPv6.

        URL: network/ipv6/<id_ipv6>/deallocate/
        '''

        self.log.info("Deallocate all relationships between NetworkIPv6.")

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Load URL param
            network_ipv6_id = kwargs.get('id_network_ipv6')

            # Valid NetworkIpv6 ID
            if not is_valid_int_greater_zero_param(network_ipv6_id):
                self.log.error(
                    u'Parameter id_network_ipv6 is invalid. Value: %s.', network_ipv6_id)
                raise InvalidValueError(
                    None, 'id_network_ipv6', network_ipv6_id)

            # Existing NetworkIpv6 ID
            network_ipv6 = NetworkIPv6().get_by_pk(network_ipv6_id)

            for ip in network_ipv6.ipv6_set.all():

                server_pool_member_list = ServerPoolMember.objects.filter(ipv6=ip)

                if server_pool_member_list.count() != 0:

                    # IP associated with Server Pool
                    server_pool_name_list = set()

                    for member in server_pool_member_list:
                        item = '{}: {}'.format(member.server_pool.id, member.server_pool.identifier)
                        server_pool_name_list.add(item)

                    server_pool_name_list = list(server_pool_name_list)
                    server_pool_identifiers = ', '.join(server_pool_name_list)

                    ip_formated = mount_ipv6_string(ip)
                    network_ipv6_ip = mount_ipv6_string(network_ipv6)

                    raise IpCantRemoveFromServerPool({'ip': ip_formated, 'network_ipv6_ip': network_ipv6_ip, 'server_pool_identifiers': server_pool_identifiers},
                                               "Não foi possível excluir a rede de id %s pois o ip %s contido nela esta sendo usado nos Server Pools (id:identifier) %s" % (network_ipv6_ip, ip_formated, server_pool_identifiers))

            with distributedlock(LOCK_NETWORK_IPV6 % network_ipv6_id):

                destroy_cache_function([network_ipv6.vlan_id])
                key_list_eqs = Equipamento.objects.filter(
                    ipv6equipament__ip__networkipv6=network_ipv6).values_list('id', flat=True)
                destroy_cache_function(key_list_eqs, True)
                # Remove NetworkIPv6 (will remove all relationships by cascade)
                network_ipv6.delete(user)

                # Return nothing
                return self.response(dumps_networkapi({}))

        except IpCantRemoveFromServerPool, e:
            return self.response_error(386, e.cause.get('network_ipv6_ip'), e.cause.get('ip'), e.cause.get('server_pool_identifiers'))
        except EquipamentoAmbienteNotFoundError, e:
            return self.response_error(320)
        except IpCantBeRemovedFromVip, e:
            return self.response_error(319, "network", 'networkipv6', network_ipv6_id)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv6NotFoundError, e:
            return self.response_error(286)
        except UserNotAuthorizedError, e:
            return self.not_authorized()
        except Exception, e:
            return self.response_error(1)
