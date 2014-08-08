# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission

from networkapi.rest import RestResource, UserNotAuthorizedError

from networkapi.requisicaovips.models import OptionVip

from networkapi.auth import has_perm

from networkapi.infrastructure.xml_utils import dumps_networkapi

from networkapi.log import Log

from networkapi.exception import OptionVipError

from django.forms.models import model_to_dict

class OptionVipAllResource(RestResource):

    log = Log('OptionVipAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Option VIP. 

        URL: optionvip/all'
        """

        try:

            self.log.info("GET to list all the Option VIP")

            # User permission
            if not has_perm(user, AdminPermission.OPTION_VIP, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Find All Option VIP
            option_vips = OptionVip.get_all();

            ovips = []

            for ov in option_vips:
                ovips.append(model_to_dict(ov))

            return self.response(dumps_networkapi({'option_vip':ovips}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except OptionVipError:
            return self.response_error(1)