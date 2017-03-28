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
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import Modelo
from networkapi.equipamento.models import ModeloRoteiro
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError


class ModelGetAllResource(RestResource):

    log = logging.getLogger('ModelGetAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Model.

        URL: model/all
        """
        try:

            self.log.info('GET to list all the Model')

            script_id = kwargs.get('script_id')

            # User permission
            if not has_perm(user, AdminPermission.BRAND_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            model_list = []

            if script_id is not None:
                models = ModeloRoteiro.objects.filter(
                    roteiro__id=int(script_id))
                for i in models:
                    model_list.append(self.model_map(i.modelo))
                return self.response(dumps_networkapi({'model': model_list}))

            for model in Modelo.objects.all():
                model_list.append(self.model_map(model))
            return self.response(dumps_networkapi({'model': model_list}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except EquipamentoError:
            return self.response_error(1)

    def model_map(self, model):
        model_map = dict()
        model_map['id'] = model.id
        model_map['nome'] = model.nome
        model_map['id_marca'] = model.marca.id
        model_map['nome_marca'] = model.marca.nome

        return model_map
