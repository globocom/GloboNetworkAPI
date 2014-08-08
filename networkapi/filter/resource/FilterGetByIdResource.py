# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: csilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.rest import RestResource
from networkapi.filter.models import Filter, FilterError, FilterNotFoundError
from networkapi.auth import has_perm
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.exception import InvalidValueError
from networkapi.log import Log
from django.forms.models import model_to_dict

class FilterGetByIdResource(RestResource):
    '''Class that receives requests to get a Filter by id.'''
    
    log = Log('FilterGetByIdResource')
    
    def handle_get(self, request, user, *args, **kwargs):
        """Treat GET requests to get a Filter by id.
        
        URL: filter/get/<id_filter>/
        """
        
        try:
            
            self.log.info("Get Filter by id")
            ## Commons Validations
            
            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                return self.not_authorized()
            
            if not is_valid_int_greater_zero_param(kwargs['id_filter']):
                self.log.error(u'Parameter id_filter is invalid. Value: %s.', kwargs['id_filter'])
                raise InvalidValueError(None, 'id_filter', kwargs['id_filter'])
            else:
                #Check existence
                fil = Filter().get_by_pk(kwargs['id_filter'])
            
            filter_dict = model_to_dict(fil)
            filter_dict['equip_types'] = list()
            for fil_equip_type in fil.filterequiptype_set.all():
                filter_dict['equip_types'].append(model_to_dict(fil_equip_type.equiptype))
                
            
            
            return self.response(dumps_networkapi({'filter': filter_dict}))
        
        
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except FilterNotFoundError, e:
            return self.response_error(339)
        except FilterError, e:
            return self.response_error(1)
        except BaseException, e:
            return self.response_error(1)
    