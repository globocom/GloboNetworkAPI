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
from networkapi.eventlog.models import EventLog
from networkapi.eventlog.models import EventLogError
from networkapi.eventlog.models import Functionality
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.usuario.models import Usuario


def ValuesQuerySetToList(vqs):
    data = list()
    for item in vqs:
        data += item
    return data


def FunctionalitiesList(fl):
    data = list()
    for item in fl:
        func = dict()
        func['f_value'] = item.nome
        func['f_name'] = item.nome
        data.append(func)
    data.insert(0, {'f_value': '0', 'f_name': '-'})
    return data


def UsersList(ul):
    data = list()
    for item in ul:
        user = dict()
        user['id_usuario'] = item.id
        user['nome'] = item.nome
        user['usuario'] = item.user
        data.append(user)
    data.insert(0, {'id_usuario': '0', 'nome': '-', 'usuario': '-'})
    return data


class EventLogChoiceResource(RestResource):
    log = logging.getLogger('EventLogFindResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to find all logs by search parameters.

        URLs: /eventlog/find/
        """

        self.log.info('find all logs')

        try:
            # Common validations

            # User permission
            if not has_perm(user, AdminPermission.USER_ADMINISTRATION, AdminPermission.READ_OPERATION):
                self.log.error(
                    'User does not have permission to perform this operation.')
                return self.not_authorized()

            # Business Validations

            # Here starts the stuff

            functionalities = Functionality.objects

            acoes = ['Alterar', 'Cadastrar', 'Remover']
            usuarios = Usuario.uniqueUsers()

            funcionalidades = functionalities.all()

            usuarios = UsersList(usuarios)
            funcionalidades = FunctionalitiesList(funcionalidades)

            choices_map = dict()

            choices_map['usuario'] = usuarios
            choices_map['acao'] = acoes
            choices_map['funcionalidade'] = funcionalidades

            return self.response(dumps_networkapi(choices_map))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except (EventLogError):
            return self.response_error(1)
        except BaseException, e:
            return self.response_error(1)
