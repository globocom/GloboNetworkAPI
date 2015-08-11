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
    destroy_cache_function, mount_ipv4_string
from networkapi.exception import InvalidValueError
from networkapi.ip.models import NetworkIPv4, NetworkIPv4NotFoundError, IpEquipamento, IpCantRemoveFromServerPool
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.distributedlock import distributedlock, LOCK_NETWORK_IPV4
from networkapi.ip.models import IpCantBeRemovedFromVip
from networkapi.equipamento.models import EquipamentoAmbienteNotFoundError
from django.db.utils import IntegrityError
from networkapi.requisicaovips.models import ServerPoolMember
from networkapi.equipamento.models import Equipamento


class NetworkIPv4DeallocateResource(RestResource):

    log = Log('NetworkIPv4DeallocateResource')

    def handle_delete(self, request, user, *args, **kwargs):
        '''Handles DELETE requests to deallocate all relationships between NetworkIPv4.

        URL: network/ipv4/<id_network_ipv4>/deallocate/
        '''

        self.log.info("Deallocate all relationships between NetworkIPv4.")

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Load URL param
            network_ipv4_id = kwargs.get('id_network_ipv4')

            # Valid NetworkIpv4 ID
            if not is_valid_int_greater_zero_param(network_ipv4_id):
                self.log.error(
                    u'Parameter id_network_ipv4 is invalid. Value: %s.', network_ipv4_id)
                raise InvalidValueError(
                    None, 'id_network_ipv4', network_ipv4_id)

            # Existing NetworkIpv4 ID
            network_ipv4 = NetworkIPv4().get_by_pk(network_ipv4_id)

            for ipv4 in network_ipv4.ip_set.all():

                server_pool_member_list = ServerPoolMember.objects.filter(ip=ipv4)

                if server_pool_member_list.count() != 0:

                    # IP associated with Server Pool
                    server_pool_name_list = set()

                    for member in server_pool_member_list:
                        item = '{}: {}'.format(member.server_pool.id, member.server_pool.identifier)
                        server_pool_name_list.add(item)

                    server_pool_name_list = list(server_pool_name_list)
                    server_pool_identifiers = ', '.join(server_pool_name_list)

                    ip_formated = mount_ipv4_string(ipv4)
                    network_ipv4_ip = mount_ipv4_string(network_ipv4)

                    raise IpCantRemoveFromServerPool({'ip': ip_formated, 'network_ip': network_ipv4_ip, 'server_pool_identifiers': server_pool_identifiers},
                                               "Não foi possível excluir a rede %s pois o ip %s contido nela esta sendo usado nos Server Pools (id:identifier) %s" % (network_ipv4_ip, ip_formated, server_pool_identifiers))

            with distributedlock(LOCK_NETWORK_IPV4 % network_ipv4_id):

                destroy_cache_function([network_ipv4.vlan_id])
                key_list_eqs = Equipamento.objects.filter(
                    ipequipamento__ip__networkipv4=network_ipv4).values_list('id', flat=True)
                destroy_cache_function(key_list_eqs, True)
                # Business Rules
                # Remove NetworkIPv4 (will remove all relationships by cascade)
                network_ipv4.delete(user)

                # Return nothing
                return self.response(dumps_networkapi({}))

        except IpCantRemoveFromServerPool, e:
            return self.response_error(386, e.cause.get('network_ip'), e.cause.get('ip'), e.cause.get('server_pool_identifiers'))
        except EquipamentoAmbienteNotFoundError, e:
            return self.response_error(320)
        except IpCantBeRemovedFromVip, e:
            return self.response_error(319, "network", "networkipv4", network_ipv4_id)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv4NotFoundError, e:
            return self.response_error(281)
        except UserNotAuthorizedError, e:
            return self.not_authorized()
        except Exception, e:
            if isinstance(e, IntegrityError):
                # IP associated VIP
                self.log.error(u'Failed to update the request vip.')
                return self.response_error(355, network_ipv4_id)
            else:
                return self.response_error(1)
