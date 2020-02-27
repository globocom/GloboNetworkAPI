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

from django.conf import settings

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import ConfigEnvironmentInvalidError
from networkapi.ip.models import NetworkIPv6
from networkapi.ip.models import NetworkIPv6AddressNotAvailableError
from networkapi.ip.models import NetworkIPv6Error
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.util import is_valid_vlan_name
from networkapi.vlan.models import NetworkTypeNotFoundError
from networkapi.vlan.models import TipoRede
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanNameDuplicatedError
from networkapi.vlan.models import VlanNetworkAddressNotAvailableError
from networkapi.vlan.models import VlanNotFoundError
from networkapi.vlan.models import VlanNumberNotAvailableError


class VlanAllocateIPv6Resorce(RestResource):

    log = logging.getLogger('VlanAllocateIPv6Resorce')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to allocate a new VLAN IPv6.

        URL: vlan/ipv6/
        """

        self.log.info('Allocate a new VLAN IPv6')

        try:
            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            vlan_map = networkapi_map.get('vlan')
            if vlan_map is None:
                return self.response_error(3, u'There is no value to the vlan tag  of XML request.')

            # Get XML data
            environment = vlan_map.get('id_environment')
            network_type = vlan_map.get('id_network_type')
            name = vlan_map.get('name')
            description = vlan_map.get('description')
            environment_vip = vlan_map.get('id_environment_vip')

            # Name must NOT be none and NOT be greater than 50
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
                    u'Parameter descricao is invalid. Value: %s.', description)
                raise InvalidValueError(None, 'descricao', description)

            # Environment

            # Valid environment ID
            if not is_valid_int_greater_zero_param(environment):
                self.log.error(
                    u'Parameter id_environment is invalid. Value: %s.', environment)
                raise InvalidValueError(None, 'id_environment', environment)

            # Find environment by ID to check if it exist
            env = Ambiente.get_by_pk(environment)

            # Environment Vip

            if environment_vip is not None:

                # Valid environment_vip ID
                if not is_valid_int_greater_zero_param(environment_vip):
                    self.log.error(
                        u'Parameter id_environment_vip is invalid. Value: %s.', environment_vip)
                    raise InvalidValueError(
                        None, 'id_environment_vip', environment_vip)

                # Find Environment VIP by ID to check if it exist
                evip = EnvironmentVip.get_by_pk(environment_vip)

            else:
                evip = None

            # Network Type

            # Valid network_type ID
            if not is_valid_int_greater_zero_param(network_type):
                self.log.error(
                    u'Parameter id_network_type is invalid. Value: %s.', network_type)
                raise InvalidValueError(None, 'id_network_type', network_type)

            # Find network_type by ID to check if it exist
            net = TipoRede.get_by_pk(network_type)

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

            # New NetworkIPv6
            network_ipv6 = NetworkIPv6()
            vlan_map = network_ipv6.add_network_ipv6(user, vlan.id, net, evip)

            # Return XML
            return self.response(dumps_networkapi(vlan_map))

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except ConfigEnvironmentInvalidError:
            return self.response_error(294)
        except NetworkIPv6AddressNotAvailableError:
            return self.response_error(296)
        except NetworkTypeNotFoundError:
            return self.response_error(111)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except VlanNotFoundError:
            return self.response_error(116)
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except VlanNameDuplicatedError:
            return self.response_error(108)
        except VlanNumberNotAvailableError:
            return self.response_error(109, min_num_01, max_num_01, min_num_02, max_num_02)
        except VlanNetworkAddressNotAvailableError:
            return self.response_error(150)
        except (VlanError, AmbienteError, NetworkIPv6Error, GrupoError, VlanError):
            return self.response_error(1)
