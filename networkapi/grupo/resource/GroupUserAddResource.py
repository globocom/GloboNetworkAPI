# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi, loads, XMLError
from networkapi.exception import InvalidValueError
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.grupo.models import UGrupo, GrupoError, UGrupoNameDuplicatedError,\
    PermissaoAdministrativa, Permission
from networkapi.util import is_valid_string_maxsize, is_valid_string_minsize, is_valid_text, is_valid_yes_no_choice
from networkapi.settings import ASSOCIATE_PERMISSION_AUTOMATICALLY,\
    ID_AUTHENTICATE_PERMISSION

class GroupUserAddResource(RestResource):
    
    log = Log('GroupUserAddResource')
    
    def handle_post(self, request, user, *args, **kwargs):
        """Treat POST request to add new user group.
        
        URL: ugroup/
        """
        try:
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.WRITE_OPERATION):
                self.log.error(u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)
    
            xml_map, attrs_map = loads(request.raw_post_data)
            self.log.debug('XML_MAP: %s', xml_map)
        
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no networkapi tag in request XML.')
        
            ugroup_map = networkapi_map.get('user_group')
            if ugroup_map is None:
                return self.response_error(3, u'There is no user_group tag in request XML.')
            
            #Valid name
            name = ugroup_map.get('nome')
            if not is_valid_string_minsize(name,3) or not is_valid_string_maxsize(name, 100) or not is_valid_text(name):
                self.log.error(u'Parameter name is invalid. Value: %s',name)
                raise InvalidValueError(None, 'name', name)
            
            read = ugroup_map.get('leitura')
            if not is_valid_yes_no_choice(read):
                self.log.error(u'Parameter read is invalid. Value: %s', read)
                raise InvalidValueError(None, 'read', read)
            
            write = ugroup_map.get('escrita')
            if not is_valid_yes_no_choice(write):
                self.log.error(u'Parameter write is invalid. Value: %s', write)
                raise InvalidValueError(None, 'write', write)
            
            edit = ugroup_map.get('edicao')
            if not is_valid_yes_no_choice(edit):
                self.log.error(u'Parameter edit is invalid. Value: %s', edit)
                raise InvalidValueError(None, 'edit', edit)
            
            remove = ugroup_map.get('exclusao')
            if not is_valid_yes_no_choice(remove):
                self.log.error(u'Parameter remove is invalid. Value: %s', remove)
                raise InvalidValueError(None, 'remove', remove)
            
            ugroup = UGrupo()
            ugroup.nome = name
            ugroup.leitura = read
            ugroup.escrita = write
            ugroup.edicao = edit
            ugroup.exclusao = remove
            
            try:
                UGrupo.objects.get(nome__iexact=ugroup.nome)
                raise UGrupoNameDuplicatedError(None, u'User group with name %s already exists' % name)
            except UGrupo.DoesNotExist:
                pass
            
            
            try:
                # save user group
                ugroup.save(user)
                
                adm_perm = PermissaoAdministrativa()
                
                
                if ASSOCIATE_PERMISSION_AUTOMATICALLY:
                    # Automatically associate 'authenticate' permission for this group
                    adm_perm.permission = Permission.get_by_pk(ID_AUTHENTICATE_PERMISSION) 
                    adm_perm.ugrupo = ugroup
                    adm_perm.leitura = False
                    adm_perm.escrita = True
                    adm_perm.save(user)
                
            except Exception, e:
                self.log.error(u'Failed to save the GroupUser.')
                raise GrupoError(e, u'Failed to save the GroupUser.')
            
            return self.response(dumps_networkapi({'user_group':{'id':ugroup.id}}))
        
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except UGrupoNameDuplicatedError:
            return self.response_error(182, name)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)
        except GrupoError:
            return self.response_error(1)