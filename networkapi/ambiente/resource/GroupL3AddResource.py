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
from networkapi.ambiente.models import GrupoL3, GrupoL3NameDuplicatedError, AmbienteError, GroupL3NotFoundError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_string_minsize, is_valid_string_maxsize, is_valid_regex


class GroupL3AddResource(RestResource):

    log = Log('GroupL3AddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Group l3.

        URL: groupl3/
        """

        try:

            self.log.info("Add Group l3")

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            group_l3_map = networkapi_map.get('group_l3')
            if group_l3_map is None:
                return self.response_error(3, u'There is no value to the group_l3 tag  of XML request.')

            # Get XML data
            name = group_l3_map.get('name')

            # Valid name
            if not is_valid_string_minsize(name, 2) or not is_valid_string_maxsize(name, 80) or not is_valid_regex(name, '^[-0-9a-zA-Z]+$'):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            try:
                GrupoL3.get_by_name(name)
                raise GrupoL3NameDuplicatedError(
                    None, u'Já existe um grupo l3 com o valor name %s.' % name)
            except GroupL3NotFoundError:
                pass

            l3_group = GrupoL3()

            # set variables
            l3_group.nome = name

            try:
                # save Group l3
                l3_group.save(user)
            except Exception, e:
                self.log.error(u'Failed to save the Group l3.')
                raise AmbienteError(e, u'Failed to save the Group l3.')

            l3_group_map = dict()
            l3_group_map['group_l3'] = model_to_dict(
                l3_group, exclude=["nome"])

            return self.response(dumps_networkapi(l3_group_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except GrupoL3NameDuplicatedError:
            return self.response_error(169, name)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except (AmbienteError):
            return self.response_error(1)
