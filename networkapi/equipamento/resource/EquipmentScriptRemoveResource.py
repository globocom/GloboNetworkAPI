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

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_EQUIPMENT_SCRIPT
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.equipamento.models import EquipamentoRoteiroNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.roteiro.models import Roteiro
from networkapi.roteiro.models import RoteiroError
from networkapi.roteiro.models import RoteiroNotFoundError
from networkapi.util import is_valid_int_greater_zero_param


class EquipmentScriptRemoveResource(RestResource):

    log = logging.getLogger('EquipmentScriptRemoveResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to remove Equipment Script.

        URL: equipmentscript/<id_equipment>/<id_script>/
        """
        try:
            self.log.info('Remove Equipment Script')

            id_equipment = kwargs.get('id_equipment')
            id_script = kwargs.get('id_script')

            # Valid ID Equipment
            if not is_valid_int_greater_zero_param(id_equipment):
                self.log.error(
                    u'The id_equipment parameter is not a valid value: %s.', id_equipment)
                raise InvalidValueError(None, 'id_equipment', id_equipment)

            # Valid ID Script
            if not is_valid_int_greater_zero_param(id_script):
                self.log.error(
                    u'The id_script parameter is not a valid value: %s.', id_script)
                raise InvalidValueError(None, 'id_script', id_script)

            # Find Equipment by ID to check if it exist
            Equipamento.get_by_pk(id_equipment)

            # Find Script by ID to check if it exist
            Roteiro.get_by_pk(id_script)

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, id_equipment, AdminPermission.EQUIP_WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            with distributedlock(LOCK_EQUIPMENT_SCRIPT % id_script):

                EquipamentoRoteiro.remove(user, id_equipment, id_script)
                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RoteiroNotFoundError:
            return self.response_error(165, id_script)

        except EquipamentoNotFoundError:
            return self.response_error(117, id_equipment)

        except EquipamentoRoteiroNotFoundError:
            return self.response_error(190, id_script, id_equipment)

        except (EquipamentoError, RoteiroError):
            return self.response_error(1)
