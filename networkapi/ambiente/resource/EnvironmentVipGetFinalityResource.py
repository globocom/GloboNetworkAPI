# -*- coding:utf-8 -*-
"""
Title: Infrastructure NetworkAPI
Author: avanzolin / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
"""

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.exception import InvalidValueError
from networkapi.ambiente.models import EnvironmentVip


class EnvironmentVipGetFinalityResource(RestResource):

    log = Log('EnvironmentVipGetFinalityResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to find all finalitys of environment VIP.

        URLs: /vip/get/finality
        """

        self.log.info('Find all finality distinct of environment_vip')

        try:
            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VIPS_REQUEST, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            evip = EnvironmentVip()
            # Business Validations
            evips = evip.list_all_finalitys()

            finality_map = dict()
            finality_list = []

            for evip in evips:
                finality_map['finality'] = evip.get('finalidade_txt')
                finality_list.append(finality_map)
                finality_map = dict()

            return self.response(dumps_networkapi({'finalidade': finality_list}))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except BaseException, e:
            return self.response_error(1)
