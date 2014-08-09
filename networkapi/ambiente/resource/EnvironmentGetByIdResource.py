# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: poliveira / s2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.ambiente.models import AmbienteNotFoundError, AmbienteError, Ambiente
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param, get_environment_map
from networkapi.exception import InvalidValueError


class EnvironmentGetByIdResource(RestResource):

    log = Log('EnvironmentGetByIdResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handle GET requests to get Environment by id.

            URLs: /environment/id/<environment_id>/,
        """

        try:
            if not has_perm(
                    user,
                    AdminPermission.ENVIRONMENT_MANAGEMENT,
                    AdminPermission.READ_OPERATION):
                return self.not_authorized()

            environment_list = []

            environment_id = kwargs.get('environment_id')

            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'Parameter environment_id is invalid. Value: %s.',
                    environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            environment_list.append(
                get_environment_map(
                    Ambiente().get_by_pk(environment_id)))

            return self.response(
                dumps_networkapi({'ambiente': environment_list}))
        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except (AmbienteError, GrupoError):
            return self.response_error(1)

if __name__ == '__main__':
    pass
