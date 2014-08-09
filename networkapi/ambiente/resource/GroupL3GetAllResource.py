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
from networkapi.ambiente.models import GrupoL3, AmbienteError
from django.forms.models import model_to_dict


class GroupL3GetAllResource(RestResource):

    log = Log('GroupL3GetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Group l3.

        URL: groupl3/all
        """
        try:

            self.log.info("GET to list all the Group l3")

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.ENVIRONMENT_MANAGEMENT,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            groupl3_list = []
            for group in GrupoL3.objects.all():
                groupl3_list.append(model_to_dict(group))

            return self.response(dumps_networkapi({'group_l3': groupl3_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except AmbienteError:
            return self.response_error(1)
