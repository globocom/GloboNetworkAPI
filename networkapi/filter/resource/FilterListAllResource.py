# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: csilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.rest import RestResource
from networkapi.filter.models import Filter
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from django.forms.models import model_to_dict

class FilterListAllResource(RestResource):
    '''Class that receives requests to list all Filters.'''
    
    log = Log('FilterListAllResource')
    
    def handle_get(self, request, user, *args, **kwargs):
        """Treat GET requests list all Filters.
        
        URL: filter/all/
        """
        
        try:
            
            self.log.info("List all Filters")
            ## Commons Validations
            
            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                return self.not_authorized()
            
            ## Business Rules
            filters = Filter.objects.all() 
            
            filter_list = []
            for filter_ in filters:
                filter_dict = model_to_dict(filter_)
                filter_dict['equip_types'] = list()
                
                for fil_equip_type in filter_.filterequiptype_set.all():
                    filter_dict['equip_types'].append(model_to_dict(fil_equip_type.equiptype))
                    
                filter_list.append(filter_dict)
                
            
            return self.response(dumps_networkapi({'filter': filter_list}))
        
        except BaseException, e:
            return self.response_error(1)