# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: csilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.rest import RestResource
from networkapi.filter.models import Filter, FilterError, FilterNotFoundError, FilterDuplicateError
from networkapi.auth import has_perm
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.infrastructure.xml_utils import dumps_networkapi, loads
from networkapi.exception import InvalidValueError
from networkapi.log import Log
from networkapi.filterequiptype.models import CantDissociateError

class FilterAlterRemoveResource(RestResource):
    '''Class that receives requests to edit and remove Filters.'''
    
    log = Log('FilterAlterRemoveResource')
    
    def handle_put(self, request, user, *args, **kwargs):
        """Treat PUT requests to edit Filters.
        
        URL: filter/<id_filter>/
        """
        
        try:
            
            self.log.info("Alter Filter")
            ## Commons Validations
            
            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                return self.not_authorized()       

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            filter_map = networkapi_map.get('filter')
            if filter_map is None:
                return self.response_error(3, u'There is no value to the filter tag  of XML request.')
            
            if not is_valid_int_greater_zero_param(kwargs['id_filter']):
                self.log.error(u'Parameter id_filter is invalid. Value: %s.', kwargs['id_filter'])
                raise InvalidValueError(None, 'id_filter', kwargs['id_filter'])
            else:
                #Check existence
                fil = Filter().get_by_pk(kwargs['id_filter'])
            
            fil.validate_filter(filter_map)
                
            try:
                # Save filter
                fil.save(user)
            except Exception, e:
                self.log.error(u'Failed to edit the filter.')
                raise e


            return self.response(dumps_networkapi({}))
            
        except FilterDuplicateError, e:
            return self.response_error(344, e.message)
        except CantDissociateError, e:
            return self.response_error(348, e.cause['equiptype'], e.cause['filter_name'])
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except FilterNotFoundError, e:
            return self.response_error(339)
        except FilterError, e:
            return self.response_error(340)
        except BaseException, e:
            return self.response_error(1)
    
    def handle_delete(self, request, user, *args, **kwargs):
        """Treat DELETE requests to remove Filters.
        
        URL: filter/<id_filter>/
        """
        
        try:
        
            self.log.info("Remove Filter")
            ## Commons Validations
            
            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                return self.not_authorized()       

            if not is_valid_int_greater_zero_param(kwargs['id_filter']):
                self.log.error(u'Parameter id_filter is invalid. Value: %s.', kwargs['id_filter'])
                raise InvalidValueError(None, 'id_filter', kwargs['id_filter'])
            else:
                #Check existence
                fil = Filter().get_by_pk(kwargs['id_filter'])
                
            try:
                # Remove filter and its relationships
                fil.delete(user)
            except Exception, e:
                self.log.error(u'Failed to remove the filter.')
                raise e

            return self.response(dumps_networkapi({}))
        
        except CantDissociateError, e:
            return self.response_error(348, e.cause['equiptype'], e.cause['filter_name'])
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except FilterNotFoundError, e:
            return self.response_error(339)
        except FilterError, e:
            return self.response_error(341)
        except BaseException, e:
            return self.response_error(1)