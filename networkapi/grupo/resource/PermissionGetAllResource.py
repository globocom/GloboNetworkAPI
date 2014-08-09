# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError, Permission
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from django.forms.models import model_to_dict


class PermissionGetAllResource(RestResource):

    log = Log('PermissionGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Permissions.

        URL: perms/all
        """
        try:

            self.log.info("GET to list all the Permissions")

            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            perms_list = []
            for perm in Permission.objects.all():
                perms_list.append(model_to_dict(perm))

            return self.response(dumps_networkapi({'perms': perms_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except GrupoError:
            return self.response_error(1)
