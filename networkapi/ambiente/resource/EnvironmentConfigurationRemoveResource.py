# -*- coding:utf-8 -*-
'''
@author: William Vedroni da Silva
@organization: S2it
@copyright: 2014 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import PermissionError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.ambiente.models import IPConfig, AmbienteNotFoundError, \
    Ambiente, IPConfigNotFoundError, IPConfigError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.exception import InvalidValueError


class EnvironmentConfigurationRemoveResource(RestResource):

    log = Log('EnvironmentConfigurationRemoveResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests GET to Remove Prefix Configuration.

        URL: /environment/configuration/remove/environment_id/configuration_id/
        """
        try:

            configuration_id = kwargs.get('configuration_id')

            environment_id = kwargs.get('environment_id')

            self._validate_permission(user)

            self._validate_configuration_id(configuration_id)

            self._validate_environment_id(environment_id)

            ip_config = IPConfig.remove(
                self,
                user,
                environment_id,
                configuration_id)

            return self.response(dumps_networkapi({'ip_config': ip_config}))

        except PermissionError:
            return self.not_authorized()

        except IPConfigNotFoundError as e:
            self.log.error(u'IpCofig not registred')
            return self.response_error(301)

        except InvalidValueError as e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.',
                e.param,
                e.value)
            return self.response_error(269, e.param, e.value)

        except AmbienteNotFoundError as e:
            self.log.error(u'Environment not registred')
            return self.response_error(112)

        except IPConfigError:
            return self.response_error(1)

    """Validations"""

    def _validate_permission(self, user):

        if not has_perm(
                user,
                AdminPermission.ENVIRONMENT_MANAGEMENT,
                AdminPermission.ENVIRONMENT_MANAGEMENT):
            self.log.error(
                u'User does not have permission to perform the operation.')
            raise PermissionError(None, None)

    def _validate_configuration_id(self, id_configuration):

        if not is_valid_int_greater_zero_param(id_configuration):
            self.log.error(
                u'The id_configuration parameter is invalid value: %s.',
                id_configuration)
            raise InvalidValueError(None, 'id_configuration', id_configuration)

        ''' Check if exists'''
        IPConfig().get_by_pk(id_configuration)

    def _validate_environment_id(self, id_environment):

        if not is_valid_int_greater_zero_param(id_environment):
            self.log.error(
                u'The id_environment parameter is invalid value: %s.',
                id_environment)
            raise InvalidValueError(None, 'id_environment', id_environment)

        ''' Check if exists'''
        Ambiente().get_by_pk(id_environment)
