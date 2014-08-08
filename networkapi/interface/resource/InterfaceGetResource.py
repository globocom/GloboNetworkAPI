# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.equipamento.models import EquipamentoError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import XMLError, dumps_networkapi
from networkapi.interface.models import Interface, InterfaceError, InterfaceNotFoundError
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.exception import InvalidValueError
from django.forms.models import model_to_dict
from networkapi.util import is_valid_int_greater_zero_param


def get_new_interface_map(interface):
    int_map = model_to_dict(interface)
    int_map['tipo_equip'] = interface.equipamento.tipo_equipamento_id
    int_map['equipamento_nome'] = interface.equipamento.nome
    int_map['marca'] = interface.equipamento.modelo.marca_id
    if interface.ligacao_front is not None:
        int_map['nome_ligacao_front'] = interface.ligacao_front.interface
        int_map['nome_equip_l_front'] = interface.ligacao_front.equipamento.nome
    if interface.ligacao_back is not None:
        int_map['nome_ligacao_back'] = interface.ligacao_back.interface
        int_map['nome_equip_l_back'] = interface.ligacao_back.equipamento.nome
    
    return int_map

class InterfaceGetResource(RestResource):
    
    log = Log('InterfaceGetResource')
    
    def handle_get(self, request, user, *args, **kwargs):
        """Treat GET requests to list interface by ID
        
        URL: interface/<id_interface>/get/
        """
        
        try:
            
            ## Business Validations
            
            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
            
            # Get id_interface param
            id_interface = kwargs.get('id_interface')
            
            # Valid Interface ID
            if not is_valid_int_greater_zero_param(id_interface):
                self.log.error(u'The id_interface parameter is not a valid value: %s.', id_interface)
                raise InvalidValueError(None, 'id_interface', id_interface)
            
            # Checks if interface exists in database
            interface = Interface.get_by_pk(id_interface)
            
            int_map = get_new_interface_map(interface)
            
            # Return interface map
            return self.response(dumps_networkapi({'interface': int_map}))
        
        except UserNotAuthorizedError:
            return self.not_authorized()
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except InterfaceNotFoundError:
            return self.response_error(141)
        except (InterfaceError, GrupoError, EquipamentoError):
            return self.response_error(1)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)