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
"""
"""
from __future__ import with_statement

import logging

from networkapi.admin_permission import AdminPermission
from networkapi.api_vip_request.syncs import delete_new
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_VIP
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.ip.models import IpCantBeRemovedFromVip
from networkapi.ip.models import IpCantRemoveFromServerPool
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsError
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.requisicaovips.models import ServerPoolMember
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import mount_ipv4_string
from networkapi.util import mount_ipv6_string


class RequisicaoVipDeleteResource(RestResource):

    log = logging.getLogger('RequisicaoVipDeleteResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """
        Treat DELETE requests to remove a vip request.
        Also remove reals related and balancer ips (if this ips isn't used for another vip).

        URL: vip/delete/<id_vip>/
        """

        try:
            vip_id = kwargs.get('id_vip')
            keep_ip = bool(request.REQUEST.get('keep_ip', False))

            # User permission
            if not has_perm(user, AdminPermission.VIPS_REQUEST, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Valid vip ID
            if not is_valid_int_greater_zero_param(vip_id):
                self.log.error(
                    u'Parameter id_vip is invalid. Value: %s.', vip_id)
                raise InvalidValueError(None, 'id_vip', vip_id)

            vip = RequisicaoVips.get_by_pk(vip_id)

            if vip.vip_criado:
                return self.response_error(370, vip_id)

            ipv4 = vip.ip
            ipv6 = vip.ipv6

            with distributedlock(LOCK_VIP % vip_id):
                try:
                    vip.delete_vips_and_reals(user)

                    vip.remove(user, vip_id)

                    # SYNC_VIP
                    delete_new(vip_id)

                    if ipv4 and not keep_ip:
                        if not self.is_ipv4_in_use(ipv4, vip_id):
                            ipv4.delete()
                    if ipv6 and not keep_ip:
                        if not self.is_ipv6_in_use(ipv6, vip_id):
                            ipv6.delete()
                except IpCantRemoveFromServerPool, e:
                    raise e
                except IpCantBeRemovedFromVip, e:
                    raise e
                except Exception, e:
                    raise RequisicaoVipsError(
                        e, u'Failed to remove Vip Request.')

            return self.response(dumps_networkapi({}))

        except IpCantRemoveFromServerPool, e:
            return self.response_error(389, e.cause.get('vip_id'), e.cause.get('ip'), e.cause.get('server_pool_identifiers'))
        except IpCantBeRemovedFromVip, e:
            return self.response_error(390, e.cause.get('vip_id'), e.cause.get('vip_id_identifiers'), e.cause.get('ip'))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except RequisicaoVipsNotFoundError, e:
            self.log.error(e.message)
            return self.response_error(152)
        except RequisicaoVipsError, e:
            self.log.error(e.message)
            return self.response_error(1)

    # =======================================================
    # Check if balancer ips from vip is used in another vips
    # =======================================================

    def is_ipv4_in_use(self, ipv4, vip_id):

        is_in_use = True
        pool_member_count = ServerPoolMember.objects.filter(ip=ipv4).exclude(
            server_pool__vipporttopool__requisicao_vip__id=vip_id).count()
        vip_count = RequisicaoVips.get_by_ipv4_id(
            ipv4.id).exclude(pk=vip_id).count()
        if vip_count == 0 and pool_member_count == 0:
            is_in_use = False

        return is_in_use

    def is_ipv6_in_use(self, ipv6, vip_id):

        is_in_use = True
        pool_member_count = ServerPoolMember.objects.filter(ipv6=ipv6).exclude(
            server_pool__vipporttopool__requisicao_vip__ipv6=vip_id).count()
        vip_count = RequisicaoVips.get_by_ipv6_id(
            ipv6.id).exclude(pk=vip_id).count()
        if vip_count == 0 and pool_member_count == 0:
            is_in_use = False

        return is_in_use
