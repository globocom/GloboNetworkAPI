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
from networkapi.equipamento.models import Marca
from networkapi.equipamento.models import MarcaNotFoundError
from networkapi.equipamento.models import Modelo
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class ModelGetByBrandResource(RestResource):

    log = logging.getLogger('ModelGetByBrandResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Model by Brand.

        URL: model/brand/<id_brand>/
        """
        try:

            self.log.info('GET to list all the Model by Brand')

            # User permission
            if not has_perm(user, AdminPermission.BRAND_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_brand = kwargs.get('id_brand')

            # Valid ID Brand
            if not is_valid_int_greater_zero_param(id_brand):
                self.log.error(
                    u'The id_brand parameter is not a valid value: %s.', id_brand)
                raise InvalidValueError(None, 'id_groupl3', id_brand)

            # Find Brand by ID to check if it exist
            Marca.get_by_pk(id_brand)

            model_list = []
            for model in Modelo.get_by_brand(id_brand):
                model_map = dict()
                model_map['id'] = model.id
                model_map['nome'] = model.nome
                model_map['id_marca'] = model.marca.id
                model_map['nome_marca'] = model.marca.nome
                model_list.append(model_map)

            return self.response(dumps_networkapi({'model': model_list}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except MarcaNotFoundError:
            return self.response_error(167, id_brand)

        except EquipamentoError:
            return self.response_error(1)
