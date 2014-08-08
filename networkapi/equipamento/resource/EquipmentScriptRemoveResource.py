# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.distributedlock import distributedlock, LOCK_EQUIPMENT_SCRIPT
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.equipamento.models import EquipamentoNotFoundError, EquipamentoError, Equipamento, EquipamentoRoteiro, EquipamentoRoteiroNotFoundError
from networkapi.roteiro.models import Roteiro, RoteiroError, RoteiroNotFoundError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param

class EquipmentScriptRemoveResource(RestResource):

    log = Log('EquipmentScriptRemoveResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to remove Equipment Script.

        URL: equipmentscript/<id_equipment>/<id_script>/
        """
        try:
            self.log.info("Remove Equipment Script")
            
            id_equipment = kwargs.get('id_equipment') 
            id_script = kwargs.get('id_script') 
            
            # Valid ID Equipment
            if not is_valid_int_greater_zero_param(id_equipment):
                self.log.error(u'The id_equipment parameter is not a valid value: %s.', id_equipment)
                raise InvalidValueError(None, 'id_equipment', id_equipment)
            
            # Valid ID Script
            if not is_valid_int_greater_zero_param(id_script):
                self.log.error(u'The id_script parameter is not a valid value: %s.', id_script)
                raise InvalidValueError(None, 'id_script', id_script)
            
            # Find Equipment by ID to check if it exist
            Equipamento.get_by_pk(id_equipment)
            
            # Find Script by ID to check if it exist
            Roteiro.get_by_pk(id_script)
            
            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, id_equipment, AdminPermission.EQUIP_WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
            
            with distributedlock(LOCK_EQUIPMENT_SCRIPT % id_script):
                
                EquipamentoRoteiro.remove(user, id_equipment, id_script)
                return self.response(dumps_networkapi({}))
        
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()
        
        except RoteiroNotFoundError:
            return self.response_error(165, id_script)
         
        except EquipamentoNotFoundError:
            return self.response_error(117, id_equipment) 
        
        except EquipamentoRoteiroNotFoundError:
            return self.response_error(190, id_script, id_equipment) 
        
        except (EquipamentoError, RoteiroError):
            return self.response_error(1)