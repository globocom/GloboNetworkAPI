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
from networkapi.grupo.models import EGrupo, GrupoError, EGrupoNotFoundError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param

class GroupEquipmentResource(RestResource):
    '''Class that receives requests related to the table 'GroupEquipment'.'''

    log = Log('GroupEquipmentResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to get Group Equipment.

        URL: egroup/<id_egroup>/
        """
        try:

            self.log.info("Get Group Equipment by ID")

            id_egroup = kwargs.get('id_egroup')

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_GROUP_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Group Equipment ID
            if not is_valid_int_greater_zero_param(id_egroup):
                self.log.error(u'The id_egroup parameter is not a valid value: %s.', id_egroup)
                raise InvalidValueError(None, 'id_egroup', id_egroup)

            # Find Group Equipment by ID to check if it exist
            egroup = EGrupo.get_by_pk(id_egroup)

            egroup_map = dict()
            egroup_map['group_equipament'] = model_to_dict(egroup)

            return self.response(dumps_networkapi(egroup_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        
        except EGrupoNotFoundError:
            return self.response_error(102)
        
        except UserNotAuthorizedError:
            return self.not_authorized()

        except GrupoError, e:
            return self.response_error(1)