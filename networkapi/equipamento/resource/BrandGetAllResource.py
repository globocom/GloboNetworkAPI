# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.equipamento.models import Marca, EquipamentoError
from django.forms.models import model_to_dict


class BrandGetAllResource(RestResource):

    log = Log('BrandGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Brand.

        URL: brand/all
        """
        try:

            self.log.info("GET to list all the Brand")

            # User permission
            if not has_perm(user, AdminPermission.BRAND_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            brand_list = []
            for brand in Marca.objects.all():
                brand_list.append(model_to_dict(brand))

            return self.response(dumps_networkapi({'brand': brand_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except EquipamentoError:
            return self.response_error(1)
