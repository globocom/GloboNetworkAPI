# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.rest import RestResource  
from networkapi.auth import has_perm
from networkapi.admin_permission import AdminPermission
from networkapi.infrastructure.xml_utils import XMLError, dumps_networkapi  
from networkapi.log import Log
from networkapi.exception import InvalidValueError
from networkapi.util import is_valid_int_greater_zero_param
from django.forms.models import model_to_dict
from networkapi.ip.models import IpNotFoundError, IpError, Ipv6

class Ipv6GetByIdResource(RestResource):

    log = Log('IPv4GetResource')
   
    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to get a ipv6 by id.
       
        URLs: ip/get-ipv6/id_ip
        """
        
        try:
            ## Commons Validations
            
            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                return self.not_authorized()
            
            ## Business Validations
            
            # Valid id access
            id_ip = kwargs.get('id_ip')
            
            if not is_valid_int_greater_zero_param(id_ip):
                raise InvalidValueError(None, 'id_ip', id_ip)
            
            ## Business Rules
            
            ip = Ipv6()
            ip = ip.get_by_pk(id_ip)
            
            ip_map = dict()
            equip_list = []
            
            for ipequip in ip.ipv6equipament_set.all():
                equip_list.append(ipequip.equipamento.nome)
            
            #IP map
            ip_map = model_to_dict(ip)
            ip_map['equipamentos'] = equip_list if len(equip_list) > 0 else None
            
            
            # Return XML
            return self.response(dumps_networkapi({'ipv6':ip_map}))
            
        except InvalidValueError, e:
            self.log.error(u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError, e:
            return self.response_error(119) 
        except (IpError):
            return self.response_error(1)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
