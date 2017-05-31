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
from networkapi.equipamento.models import MarcaNameDuplicatedError
from networkapi.equipamento.models import MarcaNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class BrandAddResource(RestResource):

    log = logging.getLogger('BrandAddResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Brand.

        URL: brand/
        """

        try:

            self.log.info('Add Brand')

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

            brand_map = networkapi_map.get('brand')
            if brand_map is None:
                return self.response_error(3, u'There is no value to the brand tag  of XML request.')

            # Get XML data
            name = brand_map.get('name')

            # Valid name
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 100):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            try:
                Marca.get_by_name(name)
                raise MarcaNameDuplicatedError(
                    None, u'Marca com o nome %s já cadastrada.' % name)
            except MarcaNotFoundError:
                pass

            brand = Marca()

            # set variables
            brand.nome = name

            try:
                # save Brand
                brand.save()
            except Exception, e:
                self.log.error(u'Failed to save the Brand.')
                raise EquipamentoError(e, u'Failed to save the Brand.')

            brand_map = dict()
            brand_map['brand'] = model_to_dict(brand, exclude=['nome'])

            return self.response(dumps_networkapi(brand_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except MarcaNameDuplicatedError:
            return self.response_error(251, name)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except (EquipamentoError):
            return self.response_error(1)
