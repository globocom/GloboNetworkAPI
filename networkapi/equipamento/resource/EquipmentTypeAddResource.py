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

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import TipoEquipamento
from networkapi.equipamento.models import TipoEquipamentoDuplicateNameError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_regex
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class EquipmentTypeAddResource(RestResource):

    log = logging.getLogger('EquipmentTypeAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to insert a Equipment Type.

        URL: equipmenttype/
        """

        try:

            self.log.info('Add Equipment Script')

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.body)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            equipment_type_map = networkapi_map.get('equipment_type')
            if equipment_type_map is None:
                msg = u'There is no value to the equipment_type tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            name = equipment_type_map.get('name')

            # Valid Name
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 100) or not is_valid_regex(name, '^[A-Za-z0-9 -]+$'):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            # Business Rules
            equipment_type = TipoEquipamento()

            # save Equipment Type
            equipment_type.insert_new(user, name)

            etype_dict = dict()
            etype_dict['id'] = equipment_type.id

            return self.response(dumps_networkapi({'equipment_type': etype_dict}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except TipoEquipamentoDuplicateNameError, e:
            return self.response_error(312, name)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except EquipamentoError, e:
            return self.response_error(1)

        except XMLError, e:
            self.log.exception(e)
            return self.response_error(1)
