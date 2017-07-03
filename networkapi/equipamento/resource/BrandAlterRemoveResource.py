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

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_BRAND
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import Marca
from networkapi.equipamento.models import MarcaNameDuplicatedError
from networkapi.equipamento.models import MarcaNotFoundError
from networkapi.equipamento.models import MarcaUsedByModeloError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class BrandAlterRemoveResource(RestResource):

    log = logging.getLogger('BrandAlterRemoveResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat requests PUT to edit Brand.

        URL: brand/<id_brand>/
        """
        try:

            self.log.info('Edit Brand')

            # User permission
            if not has_perm(user, AdminPermission.BRAND_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_brand = kwargs.get('id_brand')

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

            # Valid ID Brand
            if not is_valid_int_greater_zero_param(id_brand):
                self.log.error(
                    u'The id_brand parameter is not a valid value: %s.', id_brand)
                raise InvalidValueError(None, 'id_brand', id_brand)

            # Valid name
            if not is_valid_string_minsize(name, 3) or not is_valid_string_maxsize(name, 100):
                self.log.error(u'Parameter name is invalid. Value: %s', name)
                raise InvalidValueError(None, 'name', name)

            # Find Brand by ID to check if it exist
            brand = Marca.get_by_pk(id_brand)

            with distributedlock(LOCK_BRAND % id_brand):

                try:
                    if brand.nome.lower() != name.lower():
                        Marca.get_by_name(name)
                        raise MarcaNameDuplicatedError(
                            None, u'Marca com o nome %s já cadastrada.' % name)
                except MarcaNotFoundError:
                    pass

                # set variables
                brand.nome = name

                try:
                    # update Brand
                    brand.save()
                except Exception, e:
                    self.log.error(u'Failed to update the Brand.')
                    raise EquipamentoError(e, u'Failed to update the Brand.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except MarcaNotFoundError:
            return self.response_error(167, id_brand)

        except MarcaNameDuplicatedError:
            return self.response_error(251, name)

        except EquipamentoError:
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests DELETE to remove Brand.

        URL: brand/<id_brand>/
        """
        try:

            self.log.info('Remove Brand')

            # User permission
            if not has_perm(user, AdminPermission.BRAND_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            id_brand = kwargs.get('id_brand')

            # Valid ID Brand
            if not is_valid_int_greater_zero_param(id_brand):
                self.log.error(
                    u'The id_brand parameter is not a valid value: %s.', id_brand)
                raise InvalidValueError(None, 'id_brand', id_brand)

            # Find Brand by ID to check if it exist
            brand = Marca.get_by_pk(id_brand)

            with distributedlock(LOCK_BRAND % id_brand):

                try:

                    if brand.modelo_set.count() > 0:
                        raise MarcaUsedByModeloError(
                            None, u'A marca %d tem modelo associado.' % brand.id)

                    # remove Brand
                    brand.delete()

                except MarcaUsedByModeloError, e:
                    raise e
                except Exception, e:
                    self.log.error(u'Failed to remove the Brand.')
                    raise EquipamentoError(e, u'Failed to remove the Brand.')

                return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except MarcaNotFoundError:
            return self.response_error(167, id_brand)

        except MarcaUsedByModeloError:
            return self.response_error(199, id_brand)

        except EquipamentoError:
            return self.response_error(1)
