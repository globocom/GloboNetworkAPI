# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.requisicaovips.models import RequisicaoVips, \
    RequisicaoVipsNotFoundError, RequisicaoVipsError
from networkapi.rest import RestResource


class RequestAllVipsResource(RestResource):

    log = Log('RequestAllVipsResource')

    def handle_get(self, request, user, *args, **kwargs):
        """
        Handles GET requests to list all the VIPs.

        URL: vip/all/
        """

        try:
            if not has_perm(user,
                            AdminPermission.VIPS_REQUEST,
                            AdminPermission.READ_OPERATION):
                return self.not_authorized()

            request_vips = RequisicaoVips.get_all()
            vips = {}

            for vip in request_vips:
                request_vip_map = vip.variables_to_map()
                request_vip_map['id'] = vip.id
                request_vip_map['validado'] = vip.validado
                request_vip_map['vip_criado'] = vip.vip_criado
                request_vip_map['id_ip'] = vip.ip_id
                request_vip_map['id_ipv6'] = vip.ipv6_id
                request_vip_map[
                    'id_healthcheck_expect'] = vip.healthcheck_expect_id
                vips['vip_%s' % (vip.id)] = request_vip_map

            return self.response(dumps_networkapi(vips))

        except (RequisicaoVipsNotFoundError):
            return self.response_error(152)
        except (RequisicaoVipsError, GrupoError):
            return self.response_error(1)
