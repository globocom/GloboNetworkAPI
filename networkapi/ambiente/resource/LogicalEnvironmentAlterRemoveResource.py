# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from __future__ import with_statement
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock, LOCK_LOGICAL_ENVIRONMENT
from networkapi.exception import InvalidValueError
from networkapi.ambiente.models import AmbienteLogico, AmbienteLogicoNameDuplicatedError, AmbienteError, AmbienteLogicoNotFoundError, AmbienteLogicoUsedByEnvironmentError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param, is_valid_string_minsize, is_valid_string_maxsize, is_valid_regex


class LogicalEnvironmentAlterRemoveResource(RestResource):

    log = Log('LogicalEnvironmentAlterRemoveResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to edit Logical Environment.

        URL: logicalenvironment/<id_logicalenvironment>/
        """
        try:

            self.log.info("Edit Logical Environment")

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.ENVIRONMENT_MANAGEMENT,
                    AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_logicalenvironment = kwargs.get('id_logicalenvironment')

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(
                    3,
                    u'There is no value to the networkapi tag  of XML request.')

            logical_environment_map = networkapi_map.get('logical_environment')
            if logical_environment_map is None:
                return self.response_error(
                    3,
                    u'There is no value to the logical_environment tag  of XML request.')

            # Get XML data
            name = logical_environment_map.get('name')

            # Valid ID Logical Environment
            if not is_valid_int_greater_zero_param(id_logicalenvironment):
                self.log.error(
                    u'The id_logicalenvironment parameter is not a valid value: %s.',
                    id_logicalenvironment)
                raise InvalidValueError(
                    None,
                    'id_logicalenvironment',
                    id_logicalenvironment)

            # Valid name
            if not is_valid_string_minsize(
                name,
                2) or not is_valid_string_maxsize(
                name,
                80) or not is_valid_regex(
                name,
                    '^[-0-9a-zA-Z]+$'):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            # Find Logical Environment by ID to check if it exist
            loc_env = AmbienteLogico.get_by_pk(id_logicalenvironment)

            with distributedlock(LOCK_LOGICAL_ENVIRONMENT % id_logicalenvironment):

                try:
                    if loc_env.nome.lower() != name.lower():
                        AmbienteLogico.get_by_name(name)
                        raise AmbienteLogicoNameDuplicatedError(
                            None,
                            u'Já existe um Ambiente Lógico com o valor name %s.' %
                            name)
                except AmbienteLogicoNotFoundError:
                    pass

                # set variables
                loc_env.nome = name

                try:
                    # update Logical Environment
                    loc_env.save(user)
                except Exception as e:
                    self.log.error(
                        u'Failed to update the Logical Environment.')
                    raise AmbienteError(
                        e,
                        u'Failed to update the Logical Environment.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except AmbienteLogicoNotFoundError:
            return self.response_error(162, id_logicalenvironment)

        except AmbienteLogicoNameDuplicatedError:
            return self.response_error(173, name)

        except AmbienteError:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to remove Logical Environment.

        URL: logicalenvironment/<id_logicalenvironment>/
        """
        try:

            self.log.info("Remove Logical Environment")

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.ENVIRONMENT_MANAGEMENT,
                    AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_logicalenvironment = kwargs.get('id_logicalenvironment')

            # Valid ID Logical Environment
            if not is_valid_int_greater_zero_param(id_logicalenvironment):
                self.log.error(
                    u'The id_logicalenvironment parameter is not a valid value: %s.',
                    id_logicalenvironment)
                raise InvalidValueError(
                    None,
                    'id_logicalenvironment',
                    id_logicalenvironment)

            # Find Logical Environment by ID to check if it exist
            loc_env = AmbienteLogico.get_by_pk(id_logicalenvironment)

            with distributedlock(LOCK_LOGICAL_ENVIRONMENT % id_logicalenvironment):

                try:

                    if loc_env.ambiente_set.count() > 0:
                        raise AmbienteLogicoUsedByEnvironmentError(
                            None,
                            u"O Ambiente Lógico %s tem ambiente associado." %
                            loc_env.id)

                    # remove Logical Environment
                    loc_env.delete(user)

                except AmbienteLogicoUsedByEnvironmentError as e:
                    raise e
                except Exception as e:
                    self.log.error(
                        u'Failed to remove the Logical Environment.')
                    raise AmbienteError(
                        e,
                        u'Failed to remove the Logical Environment.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except AmbienteLogicoNotFoundError:
            return self.response_error(162, id_logicalenvironment)

        except AmbienteLogicoUsedByEnvironmentError:
            return self.response_error(217, id_logicalenvironment)

        except AmbienteError:
            return self.response_error(1)
