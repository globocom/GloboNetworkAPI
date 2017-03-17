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

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.interface.models import TipoInterface
from networkapi.rest import RestResource


class InterfaceTypeGetAllResource(RestResource):

    log = logging.getLogger('InterfaceTypeGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all .
        URL: interface/get-type/
        """
        try:

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()

            lista_tipo_interface = []

            tipos_interface = TipoInterface.objects.all()

            for tipo in tipos_interface:
                lista_tipo_interface.append(tipo)

            lists = self.get_envs(lista_tipo_interface)

            # Return XML
            interface_list = dict()
            interface_list['tipo_interface'] = lists
            return self.response(dumps_networkapi(interface_list))

        except GrupoError:
            return self.response_error(1)

        except InvalidValueError, e:
            return self.response_error(369, e.param, e.value)

    def get_envs(self, tipos_interface):

        lists = []

        for tipo in tipos_interface:
            tipo_map = model_to_dict(tipo)
            tipo_map['id'] = tipo.id
            tipo_map['tipo'] = tipo.tipo
            lists.append(tipo_map)

        return lists
