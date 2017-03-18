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
from __future__ import with_statement

import logging

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_EQUIPMENT_ACCESS
from networkapi.equipamento.models import EquipamentoAccessDuplicatedError
from networkapi.equipamento.models import EquipamentoAccessNotFoundError
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.equipamento.models import EquipamentoError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.tipoacesso.models import AccessTypeNotFoundError
from networkapi.tipoacesso.models import TipoAcesso
from networkapi.tipoacesso.models import TipoAcessoError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class EquipAccessEditResource(RestResource):

    log = logging.getLogger('EquipAccessEditResource')

    def handle_post(self, request, auth, *args, **kwargs):
        """Handles POST requests to update Equipment Access by id.

        URLs: /equipmentaccess/edit/
        """

        self.log.info('Update EquipmentAccess by id')

        try:

            # Commons Validations

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            equipmentaccess_map = networkapi_map.get('equipamento_acesso')
            if equipmentaccess_map is None:
                msg = u'There is no value to the equipamento_acesso tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            user = equipmentaccess_map.get('user')
            password = equipmentaccess_map.get('pass')
            fqdn = equipmentaccess_map.get('fqdn')
            enable_pass = equipmentaccess_map.get('enable_pass')
            type_access = equipmentaccess_map.get('id_tipo_acesso')
            equip_access = equipmentaccess_map.get('id_equip_acesso')

            # Password must NOT be none and 20 is the maxsize and 3 is the
            # minsize
            if not is_valid_string_maxsize(password, 150) or not is_valid_string_minsize(password, 3):
                self.log.error(u'Parameter pass is invalid.')
                raise InvalidValueError(None, 'pass', '****')

            # Enable Pass must NOT be none and 20 is the maxsize and 3 is the
            # minsize
            if not is_valid_string_maxsize(enable_pass, 150) or not is_valid_string_minsize(enable_pass, 3):
                self.log.error(u'Parameter enable_pass is invalid.')
                raise InvalidValueError(None, 'enable_pass', '****')

            # User must NOT be none and 20 is the maxsize and 3 is the minsize
            if not is_valid_string_maxsize(user, 20) or not is_valid_string_minsize(user, 3):
                self.log.error(u'Parameter user is invalid. Value: %s.', user)
                raise InvalidValueError(None, 'user', user)

            # Host must NOT be none and 100 is the maxsize and 4 is the minsize
            if not is_valid_string_maxsize(fqdn, 100) or not is_valid_string_minsize(fqdn, 4):
                self.log.error(u'Parameter fqdn is invalid. Value: %s.', fqdn)
                raise InvalidValueError(None, 'fqdn', fqdn)

            # Type Access
            # Valid type access ID
            if not is_valid_int_greater_zero_param(type_access):
                self.log.error(
                    u'Parameter type_access_id is invalid. Value: %s.', type_access)
                raise InvalidValueError(None, 'type_access_id', type_access)

            type_access = TipoAcesso.get_by_pk(type_access)

            # Business Rules
            equip_access = EquipamentoAcesso.get_by_pk(equip_access)

            # User permission
            if not has_perm(auth, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip_access.equipamento.id, AdminPermission.EQUIP_WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            with distributedlock(LOCK_EQUIPMENT_ACCESS % type_access.id):

                # valid duplicate association
                if not (int(type_access.id) == int(equip_access.tipo_acesso.id)):
                    if EquipamentoAcesso.objects.filter(equipamento=equip_access.equipamento, tipo_acesso=type_access).count() > 0:
                        raise EquipamentoAccessDuplicatedError(
                            None, u'Já existe esta associação de equipamento e tipo de acesso cadastrada.')

                equip_access.__dict__.update(
                    fqdn=fqdn, user=user, password=password, enable_pass=enable_pass)
                equip_access.tipo_acesso = type_access

                equip_access.save(auth)

                # update
                equipmentaccess_map = dict()
                equipmentaccess_map[
                    'equipamento_acesso'] = model_to_dict(equip_access)

                # Return XML
                return self.response(dumps_networkapi(equipmentaccess_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EquipamentoAccessNotFoundError, e:
            return self.response_error(303)
        except EquipamentoAccessDuplicatedError, e:
            return self.response_error(242, equip_access.equipamento.id, type_access.id)
        except AccessTypeNotFoundError, e:
            return self.response_error(304)
        except (TipoAcessoError, EquipamentoError):
            return self.response_error(1)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
