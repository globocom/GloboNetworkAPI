# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging

from django.forms.models import model_to_dict

from networkapi import settings
from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_ENVIRONMENT
from networkapi.equipamento.models import Equipamento
from networkapi.exception import InvalidValueError
from networkapi.filterequiptype.models import FilterEquipType
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.util import is_valid_vlan_name
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanNameDuplicatedError
from networkapi.vlan.models import VlanNumberNotAvailableError


class VlanAllocateResource(RestResource):

    log = logging.getLogger('VlanAllocateResource')

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
            vrf = vlan_map.get('vrf')

            # Name must NOT be none and 50 is the maxsize
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 50):
                self.log.error(u'Parameter name is invalid. Value: %s.', name)
                raise InvalidValueError(None, 'name', name)

            if not is_valid_vlan_name(name):
                self.log.error(
                    u'Parameter %s is invalid because is using special characters and/or breaklines.', name)
                raise InvalidValueError(None, 'name', name)

            # Description can NOT be greater than 200
            if not is_valid_string_minsize(description, 3, False) or not is_valid_string_maxsize(description, 200, False):
                self.log.error(
                    u'Parameter description is invalid. Value: %s.', description)
                raise InvalidValueError(None, 'description', description)

            # vrf can NOT be greater than 100
            if not is_valid_string_maxsize(vrf, 100, False):
                self.log.error(
                    u'Parameter vrf is invalid. Value: %s.', vrf)
                raise InvalidValueError(None, 'vrf', vrf)

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

            # To avoid allocation same vlan number twice for different environments in same equipments
            # Lock all environments related to this environment when allocating vlan number
            # select all equipments from this environment that are not part of a filter
            # and them selects all environments from all these equipments and
            # lock them out
            filtered_equipment_type_ids = list()

            env_filter = None
            try:
                env_filter = env.filter.id
            except:
                pass

            for fet in FilterEquipType.objects.filter(filter=env_filter):
                filtered_equipment_type_ids.append(fet.equiptype.id)

            filtered_environment_equips = Equipamento.objects.filter(equipamentoambiente__ambiente=env).exclude(
                tipo_equipamento__in=filtered_equipment_type_ids)

            # select all environments from the equips that were not filtered
            locks_list = list()
            environments_list = Ambiente.objects.filter(
                equipamentoambiente__equipamento__in=filtered_environment_equips).distinct().order_by('id')
            for environment in environments_list:
                lock = distributedlock(LOCK_ENVIRONMENT % environment.id)
                lock.__enter__()
                locks_list.append(lock)

            # Persist
            try:
                vlan.create_new(user,
                                min_num_01,
                                max_num_01,
                                min_num_02,
                                max_num_02
                                )
            except Exception, e:
                # release all the locks if failed
                for lock in locks_list:
                    lock.__exit__('', '', '')
                raise e

            for lock in locks_list:
                lock.__exit__('', '', '')

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
