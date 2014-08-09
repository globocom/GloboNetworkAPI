# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: rfabri / S2IT
Copyright: ( c )  2013 globo.com todos os direitos reservados.
'''
from networkapi.auth import has_perm
from networkapi.admin_permission import AdminPermission
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.exception import InvalidValueError
from networkapi.ambiente.models import AmbienteError, Ambiente
from networkapi.rest import RestResource


class EnvironmentGetAclPathsResource(RestResource):

    def handle_get(self, request, user, *args, **kwargs):
        '''Handles a get request to a environment lookup.

        Lists all distinct ACL paths

        URL: /environment/acl_path/ 
        '''
        try:
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()

            acl_paths = list(Ambiente.objects.values_list(
                'acl_path', flat=True).distinct().exclude(acl_path=None))

            return self.response(dumps_networkapi({'acl_paths': acl_paths}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except (AmbienteError):
            return self.response_error(1)
