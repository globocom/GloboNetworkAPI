# -*- coding:utf-8 -*-

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


from django.forms.models import model_to_dict
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.rack.models import RackNumberNotFoundError, RackNameDuplicatedError, RackNumberDuplicatedValueError, Rack , RackError, InvalidMacValueError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_string_minsize, is_valid_string_maxsize
from networkapi.equipamento.models import Equipamento


class RackAddResource(RestResource):

    log = Log('RackAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Rack.

        URL: rack/insert/
        """

        try:

            self.log.info("Add Rack")

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            rack_map = networkapi_map.get('rack')
            if rack_map is None:
                return self.response_error(3, u'There is no value to the rack tag  of XML request.')

            # Get XML data
            number = rack_map.get('number')
            name = rack_map.get('name')
            mac_address_sw1 = rack_map.get('mac_address_sw1')
            mac_address_sw2 = rack_map.get('mac_address_sw2')
            mac_address_ilo = rack_map.get('mac_address_ilo')
            id_sw1 = rack_map.get('id_sw1')
            id_sw2 = rack_map.get('id_sw2')
            id_ilo = rack_map.get('id_ilo')

            rack = Rack()

            # set variables
            rack.numero = number
            rack.nome = name
            rack.mac_sw1 = mac_address_sw1
            rack.mac_sw2 = mac_address_sw2
            rack.mac_ilo = mac_address_ilo
            if not id_sw1==None:
                id_sw1 = int(id_sw1)
                rack.id_sw1 = Equipamento(id=id_sw1)
            else:
                rack.id_sw1 = id_sw1
            if not id_sw2==None:
                id_sw2 = int(id_sw2)
                rack.id_sw2 = Equipamento(id=id_sw2)
            else:
                rack.id_sw2 = id_sw2
            if not id_ilo==None:
                id_ilo = int(id_ilo)
                rack.id_ilo = Equipamento(id=id_ilo)
            else:
                rack.id_ilo = id_ilo

            # save 
            rack.insert_new(user)
            
            rack_map = dict()
            rack_map['rack'] = model_to_dict(
                rack, exclude=["numero", "nome","mac_sw1", "mac_sw2","mac_ilo", "id_sw1", "id_sw2", "id_ilo"])

            return self.response(dumps_networkapi(rack_map))

        except InvalidValueError, e:
            return self.response_error(369, e.param, e.value)

        except RackNumberDuplicatedValueError:
            return self.response_error(376, number)

        except RackNameDuplicatedError:
            return self.response_error(381, name)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RackError:
            return self.response_error(1)

        except InvalidMacValueError:
            return self.response_error(377)

