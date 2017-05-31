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
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import Marca
from networkapi.equipamento.models import MarcaModeloNameDuplicatedError
from networkapi.equipamento.models import MarcaNotFoundError
from networkapi.equipamento.models import Modelo
from networkapi.equipamento.models import ModeloNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class ModelAddResource(RestResource):

    log = logging.getLogger('ModelAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Model.

        URL: model/
        """

        try:

            self.log.info('Add Model')

            # User permission
            if not has_perm(user, AdminPermission.BRAND_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            model_map = networkapi_map.get('model')
            if model_map is None:
                return self.response_error(3, u'There is no value to the model tag  of XML request.')

            # Get XML data
            name = model_map.get('name')
            id_brand = model_map.get('id_brand')

            # Valid name
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 100):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            # Valid ID Brand
            if not is_valid_int_greater_zero_param(id_brand):
                self.log.error(
                    u'The id_brand parameter is not a valid value: %s.', id_brand)
                raise InvalidValueError(None, 'id_brand', id_brand)

            # Find Brand by ID to check if it exist
            brand = Marca.get_by_pk(id_brand)

            try:
                Modelo.get_by_name_brand(name, id_brand)
                raise MarcaModeloNameDuplicatedError(
                    None, u'Já existe um modelo com o nome %s com marca %s.' % (name, brand.nome))
            except ModeloNotFoundError:
                pass

            model = Modelo()

            # set variables
            model.nome = name
            model.marca = brand

            try:
                # save Model
                model.save()
            except Exception, e:
                self.log.error(u'Failed to save the Model.')
                raise EquipamentoError(e, u'Failed to save the Model.')

            model_map = dict()
            model_map['model'] = model_to_dict(
                model, exclude=['nome', 'marca'])

            return self.response(dumps_networkapi(model_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except MarcaNotFoundError:
            return self.response_error(167, id_brand)

        except MarcaModeloNameDuplicatedError:
            return self.response_error(252, name, id_brand)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except (EquipamentoError):
            return self.response_error(1)
