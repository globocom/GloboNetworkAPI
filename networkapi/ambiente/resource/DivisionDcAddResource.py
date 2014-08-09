# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from django.forms.models import model_to_dict
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.ambiente.models import DivisaoDc, DivisaoDcNameDuplicatedError, AmbienteError, DivisaoDcNotFoundError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_string_minsize, is_valid_string_maxsize, is_valid_regex

class DivisionDcAddResource(RestResource):

    log = Log('DivisionDcAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Division Dc.

        URL: divisiondc/
        """
        
        try:
            
            self.log.info("Add Division Dc")
            
            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
            
            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            division_dc_map = networkapi_map.get('division_dc')
            if division_dc_map is None:
                return self.response_error(3, u'There is no value to the division_dc tag  of XML request.')
            
            # Get XML data
            name = division_dc_map.get('name')
            
            #Valid name
            if not is_valid_string_minsize(name,2) or not is_valid_string_maxsize(name, 80) or not is_valid_regex(name, '^[-0-9a-zA-Z]+$'):
                self.log.error(u'Parameter name is invalid. Value: %s',name)
                raise InvalidValueError(None,'name',name)

            try:
                DivisaoDc.get_by_name(name)
                raise DivisaoDcNameDuplicatedError(None, u'Já existe um divisào dc com o valor name %s.' % name)
            except DivisaoDcNotFoundError:
                pass
            
            division_dc = DivisaoDc()
            
            # set variables
            division_dc.nome  = name
            
            try:
                # save Division Dc
                division_dc.save(user)
            except Exception, e:
                self.log.error(u'Failed to save the Division Dc.')
                raise AmbienteError(e, u'Failed to save the Division Dc.')
            
            division_dc_map = dict()
            division_dc_map['division_dc'] = model_to_dict(division_dc, exclude=["nome"])
            
            return self.response(dumps_networkapi(division_dc_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        
        except DivisaoDcNameDuplicatedError:
            return self.response_error(175, name)

        except UserNotAuthorizedError:
            return self.not_authorized()
        
        except AmbienteError:
            return self.response_error(1)