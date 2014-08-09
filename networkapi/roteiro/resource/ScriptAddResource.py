# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: masilva / S2IT
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from django.forms.models import model_to_dict
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.roteiro.models import Roteiro, TipoRoteiro, RoteiroNameDuplicatedError, RoteiroNotFoundError, RoteiroError, TipoRoteiroNotFoundError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_string_minsize, is_valid_string_maxsize, is_valid_int_greater_zero_param


class ScriptAddResource(RestResource):

    log = Log('ScriptAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Script.

        URL: script/
        """

        try:

            self.log.info("Add Script")

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.SCRIPT_MANAGEMENT,
                    AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(
                    3,
                    u'There is no value to the networkapi tag  of XML request.')

            script_map = networkapi_map.get('script')
            if script_map is None:
                return self.response_error(
                    3,
                    u'There is no value to the script tag  of XML request.')

            # Get XML data
            script = script_map.get('script')
            id_script_type = script_map.get('id_script_type')
            description = script_map.get('description')

            # Valid Script
            if not is_valid_string_minsize(
                    script,
                    3) or not is_valid_string_maxsize(
                    script,
                    40):
                self.log.error(
                    u'Parameter script is invalid. Value: %s',
                    script)
                raise InvalidValueError(None, 'script', script)

            # Valid ID Script Type
            if not is_valid_int_greater_zero_param(id_script_type):
                self.log.error(
                    u'The id_script_type parameter is not a valid value: %s.',
                    id_script_type)
                raise InvalidValueError(None, 'id_script_type', id_script_type)

            # Valid description
            if not is_valid_string_minsize(
                    description,
                    3) or not is_valid_string_maxsize(
                    description,
                    100):
                self.log.error(
                    u'Parameter description is invalid. Value: %s',
                    description)
                raise InvalidValueError(None, 'description', description)

            # Find Script Type by ID to check if it exist
            script_type = TipoRoteiro.get_by_pk(id_script_type)

            try:
                Roteiro.get_by_name_script(script, id_script_type)
                raise RoteiroNameDuplicatedError(
                    None, u'Já existe um roteiro com o nome %s com tipo de roteiro %s.' %
                    (script, script_type.tipo))
            except RoteiroNotFoundError:
                pass

            scr = Roteiro()

            # set variables
            scr.roteiro = script
            scr.tipo_roteiro = script_type
            scr.descricao = description

            try:
                # save Script
                scr.save(user)
            except Exception as e:
                self.log.error(u'Failed to save the Script.')
                raise RoteiroError(e, u'Failed to save the Script.')

            script_map = dict()
            script_map['script'] = model_to_dict(
                scr,
                exclude=[
                    "roteiro",
                    "tipo_roteiro",
                    "descricao"])

            return self.response(dumps_networkapi(script_map))

        except InvalidValueError as e:
            return self.response_error(269, e.param, e.value)

        except TipoRoteiroNotFoundError:
            return self.response_error(158, id_script_type)

        except RoteiroNameDuplicatedError:
            return self.response_error(250, script, script_type.tipo)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RoteiroError:
            return self.response_error(1)
