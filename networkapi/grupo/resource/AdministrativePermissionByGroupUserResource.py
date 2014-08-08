# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from django.forms.models import model_to_dict
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import UGrupo, UGrupoNotFoundError, GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param

class AdministrativePermissionByGroupUserResource(RestResource):

    log = Log('AdministrativePermissionByGroupUserResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to get Administrative Permission by user group.

        URL: aperms/group/<id_ugroup>/
        """
        
        try:
            
            self.log.info("Get Administrative Permission by ID Group User")

            id_ugroup = kwargs.get('id_ugroup')

            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Group User ID
            if not is_valid_int_greater_zero_param(id_ugroup):
                self.log.error(u'The id_ugroup parameter is not a valid value: %s.', id_ugroup)
                raise InvalidValueError(None, 'id_ugroup', id_ugroup)

            # Find Group User by ID to check if it exist
            ugroup = UGrupo.get_by_pk(id_ugroup)

            perms_list = []
            for perms in ugroup.permissaoadministrativa_set.all():
                pm = model_to_dict(perms, exclude="permission")
                pm["permission"] = model_to_dict(perms.permission) 
                perms_list.append(pm)

            perms_map = dict()
            perms_map['perms'] = perms_list

            return self.response(dumps_networkapi(perms_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except UGrupoNotFoundError:
            return self.response_error(180, id_ugroup)

        except GrupoError, e:
            return self.response_error(1)