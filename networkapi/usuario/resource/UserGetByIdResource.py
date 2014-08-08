# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.log import Log
from networkapi.usuario.models import Usuario, UsuarioError, UsuarioNotFoundError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.exception import InvalidValueError
from django.forms.models import model_to_dict

class UserGetByIdResource(RestResource):
    
    log = Log('UserGetByIdResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to get User by the identifier.

        URL: user/get/<id_user>/
        """
        try:
            
            self.log.info("Get User by the identifier")
            
            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
            
            id_user = kwargs.get('id_user')
            
            # Valid User ID
            if not is_valid_int_greater_zero_param(id_user):
                self.log.error(u'The id_user parameter is not a valid value: %s.', id_user)
                raise InvalidValueError(None, 'id_user', id_user)
            
            
            # Find User by ID to check if it exist
            usr = Usuario.get_by_pk(id_user)
            
            user_map = dict()
            user_map['usuario'] = model_to_dict(usr)
            user_map['usuario']['grupos'] = user_map['usuario']['grupos'] if user_map['usuario']['grupos'] is not None and len(user_map['usuario']['grupos']) > 0 else [None] 
             
            return self.response(dumps_networkapi(user_map))
        
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()
        
        except UsuarioNotFoundError:
            return self.response_error(177, id_user)

        except (UsuarioError, GrupoError):
            return self.response_error(1)             