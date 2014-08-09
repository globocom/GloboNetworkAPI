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
from networkapi.grupo.models import UGrupo, GrupoError
from django.forms.models import model_to_dict


class GroupUserGetAllResource(RestResource):

    log = Log('GroupUserGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the user groups.

        URL: ugroup/all
        """
        try:

            self.log.info("GET to list all the GroupUser")

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.USER_ADMINISTRATION,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            ugroup_list = []
            for ugrp in UGrupo.objects.all():
                ugroup_list.append(model_to_dict(ugrp))

            return self.response(dumps_networkapi({'user_group': ugroup_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except GrupoError:
            return self.response_error(1)
