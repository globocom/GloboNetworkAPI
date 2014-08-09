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
from networkapi.roteiro.models import Roteiro, RoteiroError
from django.forms.models import model_to_dict

class ScriptGetAllResource(RestResource):

    log = Log('ScriptGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Script.

        URL: script/all
        """
        try:
            
            self.log.info("GET to list all the Script")
            
            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
            
            script_list = []
            for script in Roteiro.objects.all():
                script_list.append(model_to_dict(script))

            return self.response(dumps_networkapi({'script':script_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RoteiroError:
            return self.response_error(1)