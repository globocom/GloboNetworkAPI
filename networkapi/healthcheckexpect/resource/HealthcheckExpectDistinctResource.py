# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.rest import RestResource

from networkapi.auth import has_perm

from networkapi.healthcheckexpect.models import HealthcheckExpect, HealthcheckExpectError

from networkapi.admin_permission import AdminPermission

from networkapi.infrastructure.xml_utils import dumps_networkapi

from networkapi.grupo.models import GrupoError


class HealthcheckExpectDistinctResource(RestResource):
    
    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições GET para buscar expect_strings do Healthchecks_expects com distinct.
        
        URL:  /healthcheckexpect/distinct/
        """
        try:
            if not has_perm(user,
                            AdminPermission.HEALTH_CHECK_EXPECT,
                            AdminPermission.READ_OPERATION):
                return self.not_authorized()
            
            expect_strings = HealthcheckExpect.get_expect_strings()
            
            map_list = []  
            ex = []
            for es in expect_strings:
                
                if not es.expect_string in ex:
                    map_list.append({'expect_string':es.expect_string, 'id': es.id})
                    ex.append(es.expect_string)
           
        
            return self.response(dumps_networkapi({'healthcheck_expect':map_list}))
        
        except (HealthcheckExpectError, GrupoError):
            return self.response_error(1)