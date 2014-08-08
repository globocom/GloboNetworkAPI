# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from django.forms.models import model_to_dict
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError, EnvironmentVipNotFoundError
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.ip.models import IpError, IpNotFoundError, IP_VERSION, IpNotFoundByEquipAndVipError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_ipv4, is_valid_ipv6, is_valid_int_greater_zero_param, is_valid_string_minsize, is_valid_string_maxsize, is_valid_ip_ipaddr, is_valid_regex
from networkapi.equipamento.models import Equipamento
from networkapi.ambiente.models import EnvironmentVip
from networkapi.requisicaovips.models import RequisicaoVips

class RequestVipRealValidResource(RestResource):

    log = Log('RequestVipRealValidResource')

    def handle_post(self, request, user, *args, **kwargs):
        '''Handles POST requests to valid Real server.

        URL: vip/real/valid/
        '''
        self.log.info('Valid Real Server')

        try:

            ## Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            real_map = networkapi_map.get('real')
            if real_map is None:
                return self.response_error(3, u'There is no value to the vip tag  of XML request.')

            # Get XML data
            ip = real_map.get('ip')
            name = real_map.get('name_equipment')
            id_evip = real_map.get('id_environment_vip')
            valid = real_map.get('valid')

            # User permission
            if not has_perm(user, AdminPermission.VIPS_REQUEST, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                return self.not_authorized()
        
            # Valid IP
            if not is_valid_ip_ipaddr(ip):
                self.log.error(u'Parameter ip is invalid. Value: %s.', ip)
                raise InvalidValueError(None, 'ip', ip)

            # Valid Name Equipment
            if not is_valid_string_minsize(name,3) or not is_valid_string_maxsize(name, 80) or not is_valid_regex(name, "^[A-Z0-9-_]+$"):
                self.log.error(u'Parameter name_equipment is invalid. Value: %s',name)
                raise InvalidValueError(None,'name_equipment',name)
            
            # Valid Environment Vip
            if not is_valid_int_greater_zero_param(id_evip):
                self.log.error(u'Parameter id_environment_vip is invalid. Value: %s.', id_evip)
                raise InvalidValueError(None, 'id_environment_vip', id_evip)
            
            
            #Valid Equipment
            equip = Equipamento.get_by_name(name)
            
            #Valid EnvironmentVip
            evip = EnvironmentVip.get_by_pk(id_evip)
            

            version = ""
            if is_valid_ipv4(ip):
                version = IP_VERSION.IPv4[1]
            
            elif is_valid_ipv6(ip):
                version = IP_VERSION.IPv6[1]
            
            ip, equip, evip = RequisicaoVips.valid_real_server(ip, equip, evip, valid)
           
            real_dict =  {}
            ip_dict = model_to_dict(ip)
            ip_dict["version"] = version
            
            real_dict["ip"] = ip_dict
            real_dict["equipment"] = model_to_dict(equip)
            real_dict["environmentvip"] = model_to_dict(evip)
            
            return self.response(dumps_networkapi({'real':real_dict}))

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)        
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except IpNotFoundError, e:
            return self.response_error(334, e.message)
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except EquipamentoNotFoundError:
            return self.response_error(117, name)
        except IpNotFoundByEquipAndVipError:
            return self.response_error(334, e.message)
        except (IpError):
            return self.response_error(1)