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
from networkapi.ambiente.models import AmbienteLogico, AmbienteLogicoNameDuplicatedError, AmbienteError, AmbienteLogicoNotFoundError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_string_minsize, is_valid_string_maxsize, is_valid_regex


class LogicalEnvironmentAddResource(RestResource):

    log = Log('LogicalEnvironmentAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Logical Environment.

        URL: logicalenvironment/
        """

        try:

            self.log.info("Add Logical Environment")

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

            logical_environment_map = networkapi_map.get('logical_environment')
            if logical_environment_map is None:
                return self.response_error(3, u'There is no value to the logical_environment tag  of XML request.')

            # Get XML data
            name = logical_environment_map.get('name')

            # Valid name
            if not is_valid_string_minsize(name, 2) or not is_valid_string_maxsize(name, 80) or not is_valid_regex(name, '^[-0-9a-zA-Z]+$'):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            try:
                AmbienteLogico.get_by_name(name)
                raise AmbienteLogicoNameDuplicatedError(
                    None, u'Já existe um Ambiente Lógico com o valor name %s.' % name)
            except AmbienteLogicoNotFoundError:
                pass

            log_env = AmbienteLogico()

            # set variables
            log_env.nome = name

            try:
                # save Logical Environment
                log_env.save(user)
            except Exception, e:
                self.log.error(u'Failed to save the Logical Environment.')
                raise AmbienteError(
                    e, u'Failed to save the Logical Environment.')

            log_env_map = dict()
            log_env_map['logical_environment'] = model_to_dict(
                log_env, exclude=["nome"])

            return self.response(dumps_networkapi(log_env_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except AmbienteLogicoNameDuplicatedError:
            return self.response_error(173, name)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except (AmbienteError):
            return self.response_error(1)
