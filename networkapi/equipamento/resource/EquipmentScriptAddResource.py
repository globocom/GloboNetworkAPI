# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.equipamento.models import EquipamentoNotFoundError, EquipamentoRoteiroDuplicatedError, EquipamentoError, Equipamento, EquipamentoRoteiro
from networkapi.roteiro.models import Roteiro, RoteiroError, RoteiroNotFoundError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param

class EquipmentScriptAddResource(RestResource):

    log = Log('EquipmentScriptAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Equipment Script.

        URL: equipmentscript/
        """
        
        try:
            
            self.log.info("Add Equipment Script")
            
            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            equipment_script_map = networkapi_map.get('equipment_script')
            if equipment_script_map is None:
                return self.response_error(3, u'There is no value to the equipment_script tag  of XML request.')
            
            # Get XML data
            id_equipment = equipment_script_map.get('id_equipment')
            id_script = equipment_script_map.get('id_script')
            
            # Valid ID Equipment
            if not is_valid_int_greater_zero_param(id_equipment):
                self.log.error(u'The id_equipment parameter is not a valid value: %s.', id_equipment)
                raise InvalidValueError(None, 'id_equipment', id_equipment)
            
            # Valid ID Script
            if not is_valid_int_greater_zero_param(id_script):
                self.log.error(u'The id_script parameter is not a valid value: %s.', id_script)
                raise InvalidValueError(None, 'id_script', id_script)
            
            # Find Equipment by ID to check if it exist
            equipment = Equipamento.get_by_pk(id_equipment)
            
            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, id_equipment, AdminPermission.EQUIP_WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
            
            
            # Find Script by ID to check if it exist
            script = Roteiro.get_by_pk(id_script)

            equip_script = EquipamentoRoteiro()
            
            # set variables
            equip_script.equipamento = equipment
            equip_script.roteiro = script

            # save Equipment Type
            equip_script.create(user)

            equip_script_map = dict()
            equip_script_map['id'] =  equip_script.id
            networkapi_map = dict()
            networkapi_map['equipamento_roteiro'] = equip_script_map
            
            return self.response(dumps_networkapi(networkapi_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()
        
        except EquipamentoRoteiroDuplicatedError:
            return self.response_error(198, id_script, id_equipment)
         
        except RoteiroNotFoundError:
            return self.response_error(165, id_script)
         
        except EquipamentoNotFoundError:
            return self.response_error(117, id_equipment)  
        
        except (EquipamentoError, RoteiroError):
            return self.response_error(1)