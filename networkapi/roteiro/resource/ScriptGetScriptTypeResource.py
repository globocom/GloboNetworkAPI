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
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.roteiro.models import Roteiro
from networkapi.roteiro.models import RoteiroError
from networkapi.roteiro.models import TipoRoteiro
from networkapi.roteiro.models import TipoRoteiroNotFoundError
from networkapi.util import is_valid_int_greater_zero_param


class ScriptGetScriptTypeResource(RestResource):

    log = logging.getLogger('ScriptGetScriptTypeResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Script by Script Type.

        URL: script/scripttype/<id_script_type>
        """
        try:

            self.log.info('GET to list all the Script by Script Type')

            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_script_type = kwargs.get('id_script_type')

            # Valid ID Script Type
            if not is_valid_int_greater_zero_param(id_script_type):
                self.log.error(
                    u'The id_script_type parameter is not a valid value: %s.', id_script_type)
                raise InvalidValueError(None, 'id_script_type', id_script_type)

            # Find Script Type by ID to check if it exist
            TipoRoteiro.get_by_pk(id_script_type)

            script_list = []
            for script in Roteiro.objects.filter(tipo_roteiro__id=id_script_type):
                script_map = dict()
                script_map['id'] = script.id
                script_map['nome'] = script.roteiro
                script_map['descricao'] = script.descricao
                script_map['id_tipo_roteiro'] = script.tipo_roteiro_id
                script_list.append(script_map)

            return self.response(dumps_networkapi({'script': script_list}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except TipoRoteiroNotFoundError:
            return self.response_error(158, id_script_type)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RoteiroError:
            return self.response_error(1)
