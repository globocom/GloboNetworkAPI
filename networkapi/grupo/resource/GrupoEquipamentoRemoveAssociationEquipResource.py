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
from networkapi.distributedlock import LOCK_EQUIPMENT_GROUP
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoGrupo
from networkapi.equipamento.models import EquipamentoGrupoNotFoundError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import EGrupo
from networkapi.grupo.models import EGrupoNotFoundError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class GrupoEquipamentoRemoveAssociationEquipResource(RestResource):

    log = logging.getLogger('GrupoEquipamentoRemoveAssociationEquipResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições de GET remover a associação entre um grupo de equipamento e um equipamento.

        URL: egrupo/equipamento/id_equip/egrupo/id_egrupo/
        """
        try:

            id_equip = kwargs.get('id_equipamento')
            id_egrupo = kwargs.get('id_egrupo')

            if not is_valid_int_greater_zero_param(id_egrupo):
                raise InvalidValueError(None, 'id_egrupo', id_egrupo)

            if not is_valid_int_greater_zero_param(id_equip):
                raise InvalidValueError(None, 'id_equip', id_equip)

            equip = Equipamento.get_by_pk(id_equip)
            EGrupo.get_by_pk(id_egrupo)

            if not has_perm(user,
                            AdminPermission.EQUIPMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION,
                            id_egrupo,
                            id_equip,
                            AdminPermission.EQUIP_WRITE_OPERATION):
                raise UserNotAuthorizedError(
                    None, u'User does not have permission to perform the operation.')

            with distributedlock(LOCK_EQUIPMENT_GROUP % id_egrupo):

                EquipamentoGrupo.remove(user, equip.id, id_egrupo)

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except EquipamentoGrupoNotFoundError, e:
            return self.response_error(185, id_equip, id_egrupo)
        except EquipamentoNotFoundError, e:
            return self.response_error(117, id_equip)
        except EGrupoNotFoundError, e:
            return self.response_error(102)
        except EquipamentoError, e:
            return self.response_error(1)
        except (XMLError):
            return self.response_error(1)
