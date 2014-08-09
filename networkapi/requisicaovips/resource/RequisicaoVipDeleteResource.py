# -*- coding:utf-8 -*-
"""
Title: Infrastructure NetworkAPI
Author: avanzolin / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
"""

from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.requisicaovips.models import RequisicaoVips, RequisicaoVipsNotFoundError, RequisicaoVipsError, \
    ServerPoolMember
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.distributedlock import distributedlock, LOCK_VIP
from networkapi.exception import InvalidValueError


class RequisicaoVipDeleteResource(RestResource):

    log = Log('RequisicaoVipDeleteResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """
        Treat DELETE requests to remove a vip request.
        Also remove reals related and balancer ips (if this ips isn't used for another vip).

        URL: vip/remove/<id_vip>/
        """

        try:
            vip_id = kwargs.get('id_vip')

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
            ipv4 = vip.ip
            ipv6 = vip.ipv6

            with distributedlock(LOCK_VIP % vip_id):
                try:
                    vip.delete_vips_and_reals(user)
                    vip.delete(user)
                    if ipv4:
                        if not self.is_ipv4_in_use(ipv4, vip_id):
                            ipv4.delete(user)
                    if ipv6:
                        if not self.is_ipv6_in_use(ipv6, vip_id):
                            ipv6.delete(user)
                except Exception, e:
                    raise RequisicaoVipsError(
                        e, u'Failed to remove Vip Request.')

            return self.response(dumps_networkapi({}))

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
