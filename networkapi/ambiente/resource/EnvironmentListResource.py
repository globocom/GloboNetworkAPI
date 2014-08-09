# -*- coding:utf-8 -*-
"""
Title: Infrastructure NetworkAPI
Author: avanzolin / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
"""

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.ambiente.models import Ambiente
from django.forms.models import model_to_dict


def get_envs(self, user, no_blocks = False):
    try:
        
        ## Commons Validations
        
        # User permission
        if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
            return self.not_authorized()
        
        ## Business Rules
        
        # Get all environments in DB
        environments = Ambiente.objects.all().order_by("divisao_dc__nome", "ambiente_logico__nome", "grupo_l3__nome").select_related("grupo_l3", "ambiente_logico", "divisao_dc", "filter")
        
        lists = []
        
        for env in environments:
            if env.blockrules_set.count() == 0 or not no_blocks:
                env_map = model_to_dict(env)
                env_map["grupo_l3_name"] = env.grupo_l3.nome
                env_map["ambiente_logico_name"] = env.ambiente_logico.nome
                env_map["divisao_dc_name"] = env.divisao_dc.nome
                if env.filter is not None:
                    env_map["filter_name"] = env.filter.name
                lists.append(env_map)
            
        # Return XML
        environment_list = dict()
        environment_list["ambiente"] = lists
        return self.response(dumps_networkapi(environment_list))
    
    except GrupoError:
        return self.response_error(1)   

class EnvironmentListResource(RestResource):
    
    log = Log('EnvironmentListResource')
    
    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests POST to list all Environments.

        URL: /ambiente/list/
        """
        
        return get_envs(self, user)
        
    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to list all Environments without blocks.

        URL: /ambiente/list_no_blocks/
        """
        
        return get_envs(self, user, True)
     