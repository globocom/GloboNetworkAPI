# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param,\
    destroy_cache_function
from networkapi.exception import InvalidValueError
from networkapi.ip.models import NetworkIPv6, Ipv6Equipament, NetworkIPv6NotFoundError
from networkapi.distributedlock import distributedlock, LOCK_NETWORK_IPV6
from networkapi.ip.models import IpCantBeRemovedFromVip
from networkapi.equipamento.models import EquipamentoAmbienteNotFoundError,\
    Equipamento
from networkapi.requisicaovips.models import ServerPoolMember


class NetworkIPv6DeallocateResource(RestResource):
    
    log = Log('NetworkIPv6DeallocateResource')

    def handle_delete(self, request, user, *args, **kwargs):
        '''Handles DELETE requests to deallocate all relationships between NetworkIPv6.

        URL: network/ipv6/<id_ipv6>/deallocate/
        '''
        
        self.log.info("Deallocate all relationships between NetworkIPv6.")
        
        try:
            
            ## Commons Validations
            
            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                return self.not_authorized()
            
            ## Business Validations
            
            # Load URL param
            network_ipv6_id = kwargs.get('id_network_ipv6')

            # Valid NetworkIpv6 ID
            if not is_valid_int_greater_zero_param(network_ipv6_id):
                self.log.error(u'Parameter id_network_ipv6 is invalid. Value: %s.', network_ipv6_id)
                raise InvalidValueError(None, 'id_network_ipv6', network_ipv6_id)
            
            # Existing NetworkIpv6 ID
            network_ipv6 = NetworkIPv6().get_by_pk(network_ipv6_id)


            for ip in network_ipv6.ipv6_set.all():
                if ServerPoolMember.objects.filter(ipv6 = ip).count() != 0:
                    # IP associated with VIP
                    return self.response_error(355, network_ipv6_id)
                        
            with distributedlock(LOCK_NETWORK_IPV6 % network_ipv6_id):
                
                destroy_cache_function([network_ipv6.vlan_id])
                key_list_eqs = Equipamento.objects.filter(ipv6equipament__ip__networkipv6=network_ipv6).values_list('id', flat=True)
                destroy_cache_function(key_list_eqs, True)
                # Remove NetworkIPv6 (will remove all relationships by cascade)
                network_ipv6.delete(user)
                
                # Return nothing
                return self.response(dumps_networkapi({}))
        
        except EquipamentoAmbienteNotFoundError, e:
            return self.response_error(320)
        except IpCantBeRemovedFromVip, e:
            return self.response_error(319,"network",'networkipv6',network_ipv6_id)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv6NotFoundError, e:
            return self.response_error(286)
        except UserNotAuthorizedError, e:
            return self.not_authorized()
        except Exception, e:
            return self.response_error(1)
