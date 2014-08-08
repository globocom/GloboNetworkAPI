# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.usuario.models import Usuario, UsuarioError
from django.forms.models import model_to_dict

class UserGetAllResource(RestResource):

    log = Log('UserGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the users.

        URL: user/all
        """
        try:
            
            self.log.info("GET to list all the Users")
            
            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
            
            users_list = []
            for user in Usuario.objects.all():
                users_list.append(model_to_dict(user))

            return self.response(dumps_networkapi({'usuario':users_list}))


        except UserNotAuthorizedError:
            return self.not_authorized()

        except UsuarioError:
            return self.response_error(1)