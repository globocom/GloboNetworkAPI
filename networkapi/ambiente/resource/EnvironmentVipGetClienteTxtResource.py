# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission

from networkapi.rest import RestResource, UserNotAuthorizedError

from networkapi.ambiente.models import EnvironmentVip

from networkapi.auth import has_perm

from networkapi.infrastructure.xml_utils import dumps_networkapi, loads, XMLError

from networkapi.log import Log

from networkapi.util import is_valid_string_maxsize, is_valid_text, is_valid_string_minsize

from networkapi.exception import InvalidValueError, EnvironmentVipError, EnvironmentVipNotFoundError

class EnvironmentVipGetClienteTxtResource(RestResource):
    '''Class that receives requests related to the table 'EnvironmentVip'.'''

    log = Log('EnvironmentVipGetClienteTxtResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests Post to search cliente_txt of  Environment VIP by finalidade_txt

        URL: environmentvip/search/
        """

        try:

            self.log.info("Search cliente_txt Environment VIP by finalidade_txt")

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_VIP, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag of XML request.')

            environmentvip_map = networkapi_map.get('vip')
            if environmentvip_map is None:
                return self.response_error(3, u'There is no value to the vip tag of XML request.')

            # Get XML data
            finalidade = environmentvip_map.get('finalidade_txt')
            if not is_valid_string_maxsize(finalidade, 50) or not is_valid_string_minsize(finalidade, 3) or not is_valid_text(finalidade):
                self.log.error(u'The finalidade_txt parameter is not a valid value: %s.', finalidade)
                raise InvalidValueError(None, 'finalidade_txt', finalidade)
            
            environmentVip = EnvironmentVip()
            
            evip_values = environmentVip.list_all_clientes_by_finalitys(finalidade)
           
            evips = dict()
            evips_list = []
            
            for evip in evip_values:
                evips['finalidade_txt'] = finalidade
                evips['cliente_txt'] = evip.get('cliente_txt')
                evips_list.append(evips)
                evips = dict()

            return self.response(dumps_networkapi({'cliente_txt':evips_list}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)

        except EnvironmentVipNotFoundError:
            return self.response_error(283)

        except EnvironmentVipError:
            return self.response_error(1)

        except Exception, e:
            return self.response_error(1)