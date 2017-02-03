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

from django.db.models import get_model
from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError


class EquipmentTypeGetAllResource(RestResource):

    log = logging.getLogger('EquipmentTypeGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all Equipment Type.

        URL: equipmenttype/all
        """
        try:
            TipoEquipamento = get_model('equipamento', 'TipoEquipamento')
            EquipamentoError = get_model('equipamento', 'EquipamentoError')

            self.log.info('GET to list all Equipment Type')

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            map_list = []
            for equipment_type in TipoEquipamento.objects.all():
                eq_tp = {
                    'id': equipment_type.id, 'nome': equipment_type.tipo_equipamento}
                map_list.append(eq_tp)

            return self.response(dumps_networkapi({'equipment_type': map_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except EquipamentoError:
            return self.response_error(1)
