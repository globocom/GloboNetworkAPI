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
from networkapi.grupo.models import GrupoError
from networkapi.grupo.models import UGrupo
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.usuario.models import Usuario
from networkapi.usuario.models import UsuarioError
from networkapi.usuario.models import UsuarioGrupo


class UsuarioGetResource(RestResource):
    log = logging.getLogger('UsuarioGetResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições de GET para listar Usuarios.

        URLs: usuario/get/$
        """

        try:
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.READ_OPERATION):
                return self.not_authorized()

            list_groups = []
            user_groups_list = []

            map_list = []
            for user in Usuario.objects.all():
                user_map = dict()
                user_map['id'] = user.id
                user_map['user'] = user.user
                user_map['nome'] = user.nome
                user_map['ativo'] = user.ativo
                user_map['email'] = user.email
                groups = None

                groups = UsuarioGrupo.list_by_user_id(user.id)

                if groups is not None and len(groups) > 0:
                    for group in groups:
                        user_groups_list.append(
                            UGrupo.get_by_pk(group.ugrupo_id))

                    for user_group in user_groups_list:
                        list_groups.append(user_group.nome)

                if (len(list_groups) > 3):
                    user_map['is_more'] = True
                else:
                    user_map['is_more'] = False

                user_map['grupos'] = list_groups if len(
                    list_groups) > 0 else [None]
                list_groups = []
                user_groups_list = []

                map_list.append(user_map)

            return self.response(dumps_networkapi({'usuario': map_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except (UsuarioError, GrupoError):
            return self.response_error(1)
