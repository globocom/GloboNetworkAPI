# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from django.forms.models import model_to_dict
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.equipamento.models import Equipamento, EquipamentoError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import XMLError, dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource


class EquipmentGetAllResource(RestResource):

    log = Log('EquipmentGetAllResource')
   
    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to list all equipment.
        
        URLs: equipament/list/
        """
        
        try:
            
            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                return self.not_authorized()
            
            equip_list = Equipamento.objects.all()
            
            map_dicts = []
            for equip in equip_list:
                map_dicts.append(model_to_dict(equip))
            
            equip_map = dict()
            equip_map['equipamentos'] = map_dicts
            
            # Return XML
            return self.response(dumps_networkapi(equip_map))
        
        except (EquipamentoError, GrupoError):
            return self.response_error(1)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
