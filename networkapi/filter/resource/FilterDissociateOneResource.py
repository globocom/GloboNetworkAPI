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

from django.core.exceptions import ObjectDoesNotExist

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.equipamento.models import TipoEquipamento
from networkapi.equipamento.models import TipoEquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.filter.models import Filter
from networkapi.filter.models import FilterError
from networkapi.filter.models import FilterNotFoundError
from networkapi.filterequiptype.models import CantDissociateError
from networkapi.filterequiptype.models import FilterEquipType
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class FilterDissociateOneResource(RestResource):

    """Class that receives requests to remove association between Filter and TipoEquipamento."""

    log = logging.getLogger('FilterDissociateOneResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Treat PUT requests to dissociate Filter and TipoEquipamento.

        URL: filter/<id_filter>/dissociate/<id_equip_type>
        """

        try:
            self.log.info('')
            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            if not is_valid_int_greater_zero_param(kwargs['id_filter']):
                self.log.error(
                    u'Parameter id_filter is invalid. Value: %s.', kwargs['id_filter'])
                raise InvalidValueError(None, 'id_filter', kwargs['id_filter'])
            else:
                # Check existence
                fil = Filter().get_by_pk(kwargs['id_filter'])

            if not is_valid_int_greater_zero_param(kwargs['id_equip_type']):
                self.log.error(
                    u'Parameter id_equip_type is invalid. Value: %s.', kwargs['id_equip_type'])
                raise InvalidValueError(
                    None, 'id_equip_type', kwargs['id_equip_type'])
            else:
                # Check existence
                eq_tp = TipoEquipamento().get_by_pk(kwargs['id_equip_type'])

            # Delete association
            try:
                association = FilterEquipType.objects.get(
                    filter=fil.id, equiptype=eq_tp.id)

                ## Only delete if there's no conflicts ##
                association.delete()

            except ObjectDoesNotExist, e:
                # Association doesn't exist, ok
                self.log.error(e)
                pass

            return self.response(dumps_networkapi({}))

        except CantDissociateError, e:
            return self.response_error(348, e.cause['equiptype'], e.cause['filter_name'])
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except TipoEquipamentoNotFoundError, e:
            return self.response_error(100)
        except FilterNotFoundError, e:
            return self.response_error(339)
        except FilterError, e:
            return self.response_error(1)
        except BaseException, e:
            return self.response_error(1)
