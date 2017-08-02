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

from django.db.utils import IntegrityError

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_IPV6
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.requisicaovips.models import ServerPoolMember
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import destroy_cache_function
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import mount_ipv6_string


class Ipv6RemoveResource(RestResource):

    log = logging.getLogger('Ipv6RemoveResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat DELETE requests to remove the relationship between IPv6 and equipment.

        URL: ipv6/<id_ipv6>/equipment/<id_equip>/remove/
        """
        from networkapi.ip.models import Ipv6, Ipv6Equipament, IpNotFoundError, IpEquipmentNotFoundError, IpEquipamentoDuplicatedError, IpError, IpCantBeRemovedFromVip, IpEquipCantDissociateFromVip, \
            IpCantRemoveFromServerPool

        from networkapi.equipamento.models import Equipamento, EquipamentoNotFoundError, EquipamentoError
        self.log.info('Remove an IPv6 to a equipament.')

        try:

            ipv6_id = kwargs.get('id_ipv6')
            equip_id = kwargs.get('id_equip')

            # Valid Ipv6 ID
            if not is_valid_int_greater_zero_param(ipv6_id):
                self.log.error(
                    u'The id_ipv6 parameter is not a valid value: %s.', ipv6_id)
                raise InvalidValueError(None, 'id_ipv6', ipv6_id)

            # Valid Ipv6 ID
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'The id_equip parameter is not a valid value: %s.', equip_id)
                raise InvalidValueError(None, 'id_equip', equip_id)

            # Find Equipament by ID to check if it exist
            Equipamento().get_by_pk(equip_id)

            # Find IPv6 by ID to check if it exist
            Ipv6().get_by_pk(ipv6_id)

            with distributedlock(LOCK_IPV6 % ipv6_id):

                # User permission
                if not has_perm(user, AdminPermission.IPS, AdminPermission.WRITE_OPERATION, None, equip_id, AdminPermission.EQUIP_WRITE_OPERATION):
                    self.log.error(
                        u'User does not have permission to perform the operation.')
                    raise UserNotAuthorizedError(None)

                ip = Ipv6().get_by_pk(ipv6_id)
                equipament = Equipamento().get_by_pk(equip_id)
                # Delete vlan's cache
                destroy_cache_function([ip.networkipv6.vlan_id])

                # delete equipment's cache
                destroy_cache_function([equip_id], True)

                # Remove Ipv6Equipament
                ipv6_equipament = Ipv6Equipament()

                server_pool_member_list = ServerPoolMember.objects.filter(
                    ipv6=ip)

                if server_pool_member_list.count() != 0:
                    # IP associated with Server Pool

                    server_pool_name_list = set()
                    for member in server_pool_member_list:
                        item = '{}: {}'.format(
                            member.server_pool.id, member.server_pool.identifier)
                        server_pool_name_list.add(item)

                    server_pool_name_list = list(server_pool_name_list)
                    server_pool_identifiers = ', '.join(server_pool_name_list)

                    raise IpCantRemoveFromServerPool({'ip': mount_ipv6_string(ip), 'equip_name': equipament.nome, 'server_pool_identifiers': server_pool_identifiers},
                                                     'Ipv6 não pode ser disassociado do equipamento %s porque ele está sendo utilizando nos Server Pools (id:identifier) %s' % (equipament.nome, server_pool_identifiers))

                ipv6_equipament.remove(user, ipv6_id, equip_id)

                return self.response(dumps_networkapi({}))

        except IpCantRemoveFromServerPool, e:
            return self.response_error(385, e.cause.get('ip'), e.cause.get('equip_name'), e.cause.get('server_pool_identifiers'))
        except IpCantBeRemovedFromVip, e:
            return self.response_error(319, 'ip', 'ipv6', ipv6_id)
        except IpEquipCantDissociateFromVip, e:
            return self.response_error(352, e.cause['ip'], e.cause['equip_name'], e.cause['vip_id'])
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError:
            return self.response_error(119)
        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)
        except IpEquipmentNotFoundError:
            return self.response_error(288)
        except IpEquipamentoDuplicatedError:
            return self.response_error(120)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except (IpError, EquipamentoError, GrupoError, IntegrityError), e:
            return self.response_error(1)
