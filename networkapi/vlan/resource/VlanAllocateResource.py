# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: avanzolin / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi, loads, XMLError
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param, is_valid_string_maxsize, is_valid_string_minsize
from networkapi.vlan.models import Vlan, VlanError, VlanNameDuplicatedError, VlanNumberNotAvailableError
from networkapi.exception import InvalidValueError
from networkapi.ambiente.models import Ambiente, AmbienteNotFoundError, AmbienteError
from networkapi import settings
from django.forms.models import model_to_dict


class VlanAllocateResource(RestResource):

    log = Log('VlanAllocateResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to create new VLAN without add NetworkIPv4.

        URLs: /vlan/no-network/
        """

        self.log.info('Create new VLAN without add NetworkIPv4')

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            vlan_map = networkapi_map.get('vlan')
            if vlan_map is None:
                msg = u'There is no value to the vlan tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            environment = vlan_map.get('environment_id')
            name = vlan_map.get('name')
            description = vlan_map.get('description')

            # Name must NOT be none and 50 is the maxsize
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 50):
                self.log.error(u'Parameter name is invalid. Value: %s.', name)
                raise InvalidValueError(None, 'name', name)

            # Description can NOT be greater than 200
            if not is_valid_string_minsize(description, 3, False) or not is_valid_string_maxsize(description, 200, False):
                self.log.error(
                    u'Parameter description is invalid. Value: %s.', description)
                raise InvalidValueError(None, 'description', description)

            # Environment
            try:

                # Valid environment ID
                if not is_valid_int_greater_zero_param(environment):
                    self.log.error(
                        u'Parameter environment_id is invalid. Value: %s.', environment)
                    raise InvalidValueError(
                        None, 'environment_id', environment)

                # Find environment by ID to check if it exist
                env = Ambiente.get_by_pk(environment)

            except AmbienteNotFoundError, e:
                self.log.error(u'The environment parameter does not exist.')
                return self.response_error(112)

            # Business Rules

            # New Vlan
            vlan = Vlan()
            vlan.nome = name
            vlan.descricao = description
            vlan.ambiente = env

            # Check if environment has min/max num_vlan value or use the value
            # thas was configured in settings
            if (vlan.ambiente.min_num_vlan_1 and vlan.ambiente.max_num_vlan_1) or (vlan.ambiente.min_num_vlan_2 and vlan.ambiente.max_num_vlan_2):
                min_num_01 = vlan.ambiente.min_num_vlan_1 if vlan.ambiente.min_num_vlan_1 and vlan.ambiente.max_num_vlan_1 else vlan.ambiente.min_num_vlan_2
                max_num_01 = vlan.ambiente.max_num_vlan_1 if vlan.ambiente.min_num_vlan_1 and vlan.ambiente.max_num_vlan_1 else vlan.ambiente.max_num_vlan_2
                min_num_02 = vlan.ambiente.min_num_vlan_2 if vlan.ambiente.min_num_vlan_2 and vlan.ambiente.max_num_vlan_2 else vlan.ambiente.min_num_vlan_1
                max_num_02 = vlan.ambiente.max_num_vlan_2 if vlan.ambiente.min_num_vlan_2 and vlan.ambiente.max_num_vlan_2 else vlan.ambiente.max_num_vlan_1
            else:
                min_num_01 = settings.MIN_VLAN_NUMBER_01
                max_num_01 = settings.MAX_VLAN_NUMBER_01
                min_num_02 = settings.MIN_VLAN_NUMBER_02
                max_num_02 = settings.MAX_VLAN_NUMBER_02

            # Persist
            vlan.create_new(user,
                            min_num_01,
                            max_num_01,
                            min_num_02,
                            max_num_02
                            )

            vlan_map = dict()
            vlan_map['vlan'] = model_to_dict(vlan)

            # Return XML
            return self.response(dumps_networkapi(vlan_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except GrupoError:
            return self.response_error(1)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except VlanNameDuplicatedError:
            return self.response_error(108)
        except VlanNumberNotAvailableError:
            return self.response_error(109, min_num_01, max_num_01, min_num_02, max_num_02)
        except (VlanError, AmbienteError):
            return self.response_error(1)
