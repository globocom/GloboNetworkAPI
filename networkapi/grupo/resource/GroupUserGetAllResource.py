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
from networkapi.grupo.models import GrupoError
from networkapi.grupo.models import UGrupo
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError


class GroupUserGetAllResource(RestResource):

    log = logging.getLogger('GroupUserGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the user groups.

        URL: ugroup/all
        """
        try:

            self.log.info('GET to list all the GroupUser')

            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            ugroup_list = []
            for ugrp in UGrupo.objects.all():
                ugroup_list.append(model_to_dict(ugrp))

            return self.response(dumps_networkapi({'user_group': ugroup_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except GrupoError:
            return self.response_error(1)
