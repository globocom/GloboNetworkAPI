# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi

from networkapi.rest import RestResource

from networkapi.admin_permission import AdminPermission

from networkapi.auth import has_perm

from networkapi.log import Log

from networkapi.equipamento.models import EquipamentoGrupo, Equipamento,\
    EquipamentoNotFoundError, EquipamentoError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import EGrupo, EGrupoNotFoundError





class GrupoEquipamentoGetByEquipResource(RestResource):
    
    log = Log('GrupoEquipamentoGetByEquipResource')

    def handle_get(self, request, user, *args, **kwargs):
        '''Trata as requisições de GET para listar todos os grupos de equipamento de um determindo equipamento.
        
        URL: egrupo/equip/id_equip
        '''
        try:
            
            if not has_perm(user, AdminPermission.EQUIPMENT_GROUP_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()
            
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()
            
            id_equip = kwargs.get('id_equip')
            
            if not is_valid_int_greater_zero_param(id_equip):
                raise InvalidValueError(None, 'id_equip', id_equip)
            
            equip = Equipamento.get_by_pk(id_equip)

            egroups = EquipamentoGrupo.get_by_equipment(equip.id)
            
            group_list = []
            map_list = []
            
            for egroup in egroups:
                group_list.append(EGrupo.get_by_pk(egroup.egrupo.id))
            
            for egroup in group_list:
                egroup_map = dict()
                egroup_map['id'] = egroup.id
                egroup_map['nome'] =  egroup.nome
                map_list.append(egroup_map)
                
            network_map = dict()
            
            network_map['grupo'] = map_list
                 
            return self.response(dumps_networkapi(network_map))
        
        except InvalidValueError, e:
            self.log.error(u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except EquipamentoNotFoundError,e:
            return self.response_error(117, id_equip)
        except EGrupoNotFoundError, e:
            return self.response_error(150, e.message)
        except EquipamentoError, e:
            return self.response_error(1)
        except (XMLError):
            return self.response_error(1)              
  