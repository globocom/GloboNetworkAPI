# -*- coding:utf-8 -*-
"""
Title: Infrastructure NetworkAPI
Author: avanzolin / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
"""

from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.exception import InvalidValueError
from networkapi.requisicaovips.models import RequisicaoVips, RequisicaoVipsNotFoundError, RequisicaoVipsError
from networkapi.distributedlock import distributedlock, LOCK_VIP

class RequestVipValidateResource(RestResource):
    
    log = Log('RequestVipValidateResource')
    
    def handle_get(self, request, user, *args, **kwargs):
        """Handles get requests to validate Vip Requests by id.
        
        URLs: /vip/validate/<id_vip>/
        """
        
        self.log.info('Validate Vip Request by id')
        
        try:
            ## Commons Validations
            
            # User permission
            if not has_perm(user, AdminPermission.VIP_VALIDATION, AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                return self.not_authorized()
            
            ## Business Validations
            
            id_vip = kwargs.get('id_vip')
            
            # Valid vip id
            if not is_valid_int_greater_zero_param(id_vip):
                self.log.error(u'Parameter id_vip is invalid. Value: %s.', id_vip)
                raise InvalidValueError(None, 'id_vip', id_vip)
            
            vip = RequisicaoVips.get_by_pk(id_vip)
            
            with distributedlock(LOCK_VIP % id_vip):
                vip.validado = True
                vip.save(user)
                
            return self.response(dumps_networkapi({}))
        
        except RequisicaoVipsNotFoundError:
            return self.response_error(152)
        except RequisicaoVipsError:
            return self.response_error(150, 'Failed to validate vip request.')
        except InvalidValueError, e:
            self.log.error(u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except BaseException, e:
            return self.response_error(1)
