# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.infrastructure.xml_utils import dumps_networkapi

from networkapi.vlan.models import Vlan, VlanError, VlanNotFoundError, VlanCantDeallocate
from networkapi.ip.models import IpCantBeRemovedFromVip
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.log import Log
from networkapi.util import is_valid_int_greater_zero_param,\
    destroy_cache_function
from networkapi.exception import InvalidValueError
from networkapi.distributedlock import distributedlock, LOCK_VLAN
from networkapi.equipamento.models import EquipamentoAmbienteNotFoundError
from django.db.utils import IntegrityError
from networkapi.requisicaovips.models import ServerPoolMember

class VlanDeallocateResource(RestResource):

    log = Log('VlanDeallocateResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to deallocate all relationships between Vlan.

        URL: vlan/<id_vlan>/deallocate/
        """

        self.log.info("Deallocate all relationships between Vlan.")

        try:

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
            
            # Load URL param
            id_vlan = kwargs.get('id_vlan')

            # Valid vlan id
            if not is_valid_int_greater_zero_param(id_vlan):
                self.log.error(u'The id_vlan parameter is not a valid value: %s.', id_vlan)
                raise InvalidValueError(None, 'id_vlan', id_vlan)

            # Find Vlan by id to check if it exist
            vlan = Vlan().get_by_pk(id_vlan)
                        
            # Delete vlan's cache
            destroy_cache_function([id_vlan]) 
            
            # Delete equipment's cache
            equip_id_list = []
    
            for netv4 in vlan.networkipv4_set.all():
                for ipv4 in netv4.ip_set.all():
                    
                    if ServerPoolMember.objects.filter(ip = ipv4).count() != 0:
                        # IP associated VIP
                        self.log.error(u'Failed to update the request vip.')
                        return self.response_error(356, id_vlan)
                    
                    for ip_equip in ipv4.ipequipamento_set.all():
                        equip_id_list.append(ip_equip.equipamento_id) 
            
            for netv6 in vlan.networkipv6_set.all():
                for ip in netv6.ipv6_set.all():
                    
                    if ServerPoolMember.objects.filter(ipv6 = ip).count() != 0:
                        # IP associated with VIP
                        return self.response_error(356, id_vlan)
                    
                    for ip_equip in ip.ipv6equipament_set.all():
                        equip_id_list.append(ip_equip.equipamento_id) 
            
            
            destroy_cache_function(equip_id_list, True)
            
            with distributedlock(LOCK_VLAN % id_vlan):
                
                # Remove Vlan
                vlan.delete(user)
    
                return self.response(dumps_networkapi({}))
        
        except EquipamentoAmbienteNotFoundError, e:
            return self.response_error(320)
        
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()
        
        except VlanCantDeallocate, e:
            return self.response_error(293)
        
        except IpCantBeRemovedFromVip, e:
            return self.response_error(319,"vlan",'vlan',id_vlan)

        except VlanNotFoundError:
            return self.response_error(116)

        except (VlanError):
            return self.response_error(1)
        
        except Exception, e:
            if isinstance(e, IntegrityError):
                # IP associated VIP
                self.log.error(u'Failed to update the request vip.')
                return self.response_error(356, id_vlan)
            else:
                return self.response_error(1)