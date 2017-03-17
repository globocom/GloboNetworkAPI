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
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.interface.models import BackLinkNotFoundError
from networkapi.interface.models import FrontLinkNotFoundError
from networkapi.interface.models import Interface
from networkapi.interface.models import InterfaceError
from networkapi.interface.models import InterfaceForEquipmentDuplicatedError
from networkapi.interface.models import InterfaceNotFoundError
from networkapi.interface.models import InterfaceUsedByOtherInterfaceError
from networkapi.rest import RestResource


def get_new_interface_map(interface_sw):

    int_map = model_to_dict(interface_sw)

    int_map['equipamento_nome'] = interface_sw.equipamento.nome
    int_map['interface'] = interface_sw.interface
    if interface_sw.ligacao_front is not None:
        int_map['nome_ligacao_front'] = interface_sw.ligacao_front.interface
        int_map['nome_equip_l_front'] = interface_sw.ligacao_front.equipamento.nome
    if interface_sw.ligacao_back is not None:
        int_map['nome_ligacao_back'] = interface_sw.ligacao_back.interface
        int_map['nome_equip_l_back'] = interface_sw.ligacao_back.equipamento.nome

    return int_map


class InterfaceGetSwRouterResource(RestResource):

    log = logging.getLogger('InterfaceGetSwRouterResource')

    def handle_get(self, request, user, *args, **kwargs):

        try:

            self.log.info('INTERFACE')

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Get XML data
            equip_id = kwargs.get('id_equipamento')

            interface = Interface()
            equip_interface = interface.search(equip_id)
            interface_list = []

            for var in equip_interface:
                try:
                    interface_list.append(get_new_interface_map(
                        var.get_switch_and_router_interface_from_host_interface(None)))
                except:
                    pass

            if len(interface_list) == 0:
                raise InterfaceNotFoundError(
                    None, 'Erro: O servidor deve estar conectado aos uplinks')

            return self.response(dumps_networkapi({'map': interface_list}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)
        except InterfaceNotFoundError:
            return self.response_error(141)
        except (EquipamentoError, GrupoError, InterfaceError):
            return self.response_error(1)
