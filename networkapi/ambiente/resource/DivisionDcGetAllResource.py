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
from networkapi.ambiente.models import DivisaoDc, AmbienteError
from django.forms.models import model_to_dict


class DivisionDcGetAllResource(RestResource):

    log = Log('DivisionDcGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Division Dc.

        URL: divisiondc/all
        """
        try:

            self.log.info("GET to list all the Division Dc")

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.ENVIRONMENT_MANAGEMENT,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            division_dc_list = []
            for division in DivisaoDc.objects.all():
                division_dc_list.append(model_to_dict(division))

            return self.response(
                dumps_networkapi({'division_dc': division_dc_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except AmbienteError:
            return self.response_error(1)
