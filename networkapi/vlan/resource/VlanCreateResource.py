# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.ip.models import NetworkIPv4, NetworkIPv4NotFoundError, NetworkIPv6, NetworkIPv6NotFoundError, NetworkIPv6Error, NetworkIPv4Error
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.vlan.models import VlanNotFoundError, VlanError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.script_utils import exec_script, ScriptError
from networkapi.ambiente.models import IP_VERSION, AmbienteError
from networkapi.settings import VLAN_CREATE, NETWORKIPV4_CREATE,\
    NETWORKIPV6_CREATE
from networkapi.equipamento.models import Equipamento

class VlanCreateResource(RestResource):
    
    log = Log('VlanCreateResource')
    
    def handle_post(self, request, user, *args, **kwargs):
        '''Treat POST requests to run script creation for vlan and networks
        
        URL: vlan/v4/create/ or vlan/v6/create/
        '''
        
        try:
            
            ## Generic method for v4 and v6
            network_version = kwargs.get('network_version')
            
            ## Commons Validations
            
            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                return self.not_authorized()
            
            ## Business Validations
            
            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)
            
            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            vlan_map = networkapi_map.get('vlan')
            if vlan_map is None:
                msg = u'There is no value to the vlan tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            
            # Get XML data
            network_ip_id = vlan_map.get('id_network_ip')
            
            # Valid network_ip ID
            if not is_valid_int_greater_zero_param(network_ip_id):
                self.log.error(u'Parameter id_network_ip is invalid. Value: %s.', network_ip_id)
                raise InvalidValueError(None, 'id_network_ip', network_ip_id)
            
            # Network must exists in database
            if IP_VERSION.IPv4[0] == network_version:
                network_ip = NetworkIPv4().get_by_pk(network_ip_id)
            else:
                network_ip = NetworkIPv6().get_by_pk(network_ip_id)
            
            # Vlan must be active if Network is
            if network_ip.active:
                return self.response_error(299)
            
            # Check permission group equipments
            equips_from_ipv4 = Equipamento.objects.filter(ipequipamento__ip__networkipv4__vlan=network_ip.vlan.id, equipamentoambiente__is_router=1)
            equips_from_ipv6 = Equipamento.objects.filter(ipv6equipament__ip__networkipv6__vlan=network_ip.vlan.id, equipamentoambiente__is_router=1)
            for equip in equips_from_ipv4:
                # User permission
                if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
                    self.log.error(u'User does not have permission to perform the operation.')
                    return self.not_authorized()
            for equip in equips_from_ipv6:
                # User permission
                if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip.id, AdminPermission.EQUIP_WRITE_OPERATION):
                    self.log.error(u'User does not have permission to perform the operation.')
                    return self.not_authorized()
            
            ## Business Rules
            
            success_map = dict()
            
            # If Vlan is not active, need to be created before network
            if not network_ip.vlan.ativada:
                
                # Make command
                vlan_command = VLAN_CREATE % (network_ip.vlan.id)
                
                # Execute command
                code, stdout, stderr = exec_script(vlan_command)
                
                if code == 0:
                    
                    # After execute script, change to activated
                    network_ip.vlan.activate(user)
                    
                    vlan_success = dict()
                    vlan_success['codigo'] = '%04d' % code
                    vlan_success['descricao'] = {'stdout':stdout, 'stderr':stderr}
                    
                    success_map['vlan'] = vlan_success
                    
                else:
                    return self.response_error(2, stdout + stderr)
            
            # Make command to create Network
            
            if IP_VERSION.IPv4[0] == network_version:
                command = NETWORKIPV4_CREATE % (network_ip.id)
            else:
                command = NETWORKIPV6_CREATE % (network_ip.id)
            
            # Execute command
            code, stdout, stderr = exec_script(command)
            
            if code == 0:
                
                # After execute script, change the Network to activated
                network_ip.activate(user)
                
                network_success = dict()
                network_success['codigo'] = '%04d' % code
                network_success['descricao'] = {'stdout':stdout, 'stderr':stderr}
                
                success_map['network'] = network_success
                
            else:
                return self.response_error(2, stdout + stderr)
            
            map = dict()
            map['sucesso'] = success_map
            
            # Return XML
            return self.response(dumps_networkapi(map))
        
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except NetworkIPv4NotFoundError, e:
            return self.response_error(281)
        except NetworkIPv6NotFoundError, e:
            return self.response_error(286)
        except VlanNotFoundError, e:
            return self.response_error(116)
        except XMLError, e:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, e)
        except ScriptError, s:
            return self.response_error(2, s)
        except (GrupoError, VlanError, AmbienteError, NetworkIPv6Error, NetworkIPv4Error), e:
            return self.response_error(1)
