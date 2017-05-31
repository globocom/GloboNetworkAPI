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
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource


class EquipmentListResource(RestResource):

    log = logging.getLogger('EquipmentListResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to list all equipment.

        URLs: equipamento/list/
        """

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Rules

            equip_list = Equipamento.objects.raw(
                'SELECT e.* \
                  FROM equipamentos e \
                   LEFT JOIN equip_do_grupo edg on e.id_equip = edg.id_equip \
                   LEFT JOIN grupos_equip ge on edg.id_egrupo = ge.id \
                   LEFT JOIN direitos_grupoequip dg on ge.id = dg.id_egrupo \
                   LEFT JOIN grupos g on dg.id_ugrupo = g.id \
                   LEFT JOIN usuarios_do_grupo udg on g.id = udg.id_grupo \
                   LEFT JOIN usuarios u on udg.id_user = u.id_user \
                  WHERE u.id_user = %s \
                   AND dg.leitura = 1',
                [user.id]
            )

            map_dicts = set()
            for equip in equip_list:
                map_dicts.add(equip.nome)

            equip_map = dict()
            equip_map['equipamentos'] = list(map_dicts)

            # Return XML
            return self.response(dumps_networkapi(equip_map))

        except (EquipamentoError, GrupoError):
            return self.response_error(1)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
