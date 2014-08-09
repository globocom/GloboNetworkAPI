# -*- coding:utf-8 -*-

'''
Title: Infrastructure NetworkAPI
Author: avanzolin / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.ip.models import Ipv6, IpError, NetworkIPv4Error,\
    IpNotFoundError, IpEquipmentNotFoundError, IpCantBeRemovedFromVip, IpEquipCantDissociateFromVip
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.exception import InvalidValueError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.distributedlock import distributedlock, LOCK_IPV6
from networkapi.equipamento.models import EquipamentoAmbienteNotFoundError

class IPv6DeleteResource(RestResource):
    
    log = Log('IPv6DeleteResource')

    def handle_get(self, request, user, *args, **kwargs):
        '''Handles GET requests for delete an IP6 

        URL: ip6/delete/id_ip6
        '''

        self.log.info('Delete an IP6')
        
        try:
            
            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                return self.not_authorized()
            
            ## Business Validations            
            # Valid id access
            id_ip = kwargs.get('id_ipv6')
            
            if not is_valid_int_greater_zero_param(id_ip):
                self.log.error(u'Parameter id_ip is invalid. Value: %s.', id_ip)
                raise InvalidValueError(None, 'id_rede', id_ip)
            
            ip = Ipv6.get_by_pk(id_ip)
            
            with distributedlock(LOCK_IPV6 % id_ip):
                
                ## Business Rules
                ip.delete(user)
                ## Business Rules
    
                return self.response(dumps_networkapi({}))
            
        except IpCantBeRemovedFromVip, e:
            return self.response_error(319,"ip",'ipv6',id_ip)
        except IpEquipCantDissociateFromVip, e:
            return self.response_error(352, e.cause['ip'], e.cause['equip_name'], e.cause['vip_id'])
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except IpEquipmentNotFoundError, e:
            return self.response_error(308,id_ip)
        except EquipamentoAmbienteNotFoundError, e:
            return self.response_error(307,e.message)
        except IpNotFoundError, e:
            return self.response_error(119)
        except (IpError, NetworkIPv4Error, GrupoError):
            return self.response_error(1)