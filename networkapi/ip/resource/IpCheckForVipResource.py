# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission

from networkapi.auth import has_perm

from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi

from networkapi.ip.models import  Ipv6, IpError,Ip, IpNotFoundError, IpNotAvailableError, NetworkNotInEvip

from networkapi.log import Log

from networkapi.rest import RestResource, UserNotAuthorizedError

from networkapi.exception import InvalidValueError, EnvironmentVipNotFoundError

from networkapi.util import is_valid_ipv4, is_valid_ipv6, is_valid_int_greater_zero_param
from django.forms.models import model_to_dict
from networkapi.equipamento.models import TipoEquipamento
from networkapi.ambiente.models import EnvironmentVip


class IpCheckForVipResource(RestResource):

    log = Log('IpCheckForVipResource')

    def handle_post(self, request, user, *args, **kwargs):
        '''Handles POST requests to check an IPv4 or Ipv6 for vip request.

        URL: ip/checkvipip/
        '''
        self.log.info('Check a Ipv4 or Ipv6 for Vip')

        try:

            ## Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            ip_map = networkapi_map.get('ip_map')
            if ip_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            ip = ip_map.get('ip')
            id_evip = ip_map.get('id_evip')

            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                return self.not_authorized()
            
            # Valid ip id
            if ip is None:
                self.log.error(u'Parameter ip is invalid. Value: %s.', ip)
                raise InvalidValueError(None, 'ip', ip)
            
            # Valid evip id
            if not is_valid_int_greater_zero_param(id_evip):
                raise InvalidValueError(None, 'id_evip', id_evip)

            ## Business Rules
            
            evip = EnvironmentVip.get_by_pk(id_evip)
               
            ip_list = ip.split(".")
            
            if len(ip_list) == 1:
                
                if not is_valid_ipv6(ip):
                    self.log.error(u'Parameter ip is invalid. Value: %s.', ip)
                    raise InvalidValueError(None, 'ip', ip)
                
                if len(evip.networkipv6_set.all()) <= 0:
                    raise NetworkNotInEvip('IPv6','Não há rede no ambiente vip fornecido')
                
                ip_list = ip.split(":")
                ip_checked = Ipv6.get_by_octs_and_environment_vip(ip_list[0], ip_list[1], ip_list[2], ip_list[3], ip_list[4], ip_list[5], ip_list[6], ip_list[7], id_evip)
                
                ip_ok = False
                    
                for ip_equip in ip_checked.ipv6equipament_set.all():
                    
                    if ip_equip.equipamento.tipo_equipamento == TipoEquipamento.get_tipo_balanceador():
                        
                        ip_ok = True
                        break
                                
                if  not ip_ok:
                    raise IpNotAvailableError(None,"Ipv6 indisponível para o Ambiente Vip: %s, pois não existe equipamento do Tipo Balanceador relacionado a este Ip."  % evip.show_environment_vip() )

            else:
                
                if not is_valid_ipv4(ip):
                    self.log.error(u'Parameter ip is invalid. Value: %s.', ip)
                    raise InvalidValueError(None, 'ip', ip)
                
                if len(evip.networkipv4_set.all()) <= 0:
                    raise NetworkNotInEvip('IPv4','Não há rede no ambiente vip fornecido')
                
                ip_checked = Ip.get_by_octs_and_environment_vip(ip_list[0], ip_list[1], ip_list[2], ip_list[3], id_evip)
                
                ip_ok = False
                    
                for ip_equip in ip_checked.ipequipamento_set.all():
                    
                    if ip_equip.equipamento.tipo_equipamento == TipoEquipamento.get_tipo_balanceador():
                        
                        ip_ok = True
                        break
                                
                if  not ip_ok:
                    raise IpNotAvailableError(None,"Ipv4 indisponível para o Ambiente Vip: %s, pois não existe equipamento do Tipo Balanceador relacionado a este Ip."  % evip.show_environment_vip() )
                
            ip_dict = model_to_dict(ip_checked)

            return self.response(dumps_networkapi({'ip':ip_dict}))
        
        except NetworkNotInEvip, e:
            return self.response_error(321, e.cause)
        except IpNotAvailableError, e:
            return self.response_error(150, e.message)        
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)              
        except EnvironmentVipNotFoundError, e:
            return self.response_error(283)   
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except UserNotAuthorizedError:
            return self.not_authorized()        
        except IpNotFoundError, e:
            return self.response_error(334, e.message)
        except (IpError):
            return self.response_error(1)