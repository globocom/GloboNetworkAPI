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
from networkapi.ambiente.models import AmbienteLogico, AmbienteError
from django.forms.models import model_to_dict


class LogicalEnvironmentGetAllResource(RestResource):

    log = Log('LogicalEnvironmentGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Logical Environment.

        URL: logicalenvironment/all
        """
        try:

            self.log.info("GET to list all the Logical Environment")

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.ENVIRONMENT_MANAGEMENT,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            logical_environment_list = []
            for group in AmbienteLogico.objects.all():
                logical_environment_list.append(model_to_dict(group))

            return self.response(
                dumps_networkapi({'logical_environment': logical_environment_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except AmbienteError:
            return self.response_error(1)
