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
"""
"""
from __future__ import with_statement

import logging

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_VIP
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsError
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param


class RequestVipValidateResource(RestResource):

    log = logging.getLogger('RequestVipValidateResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles get requests to validate Vip Requests by id.

        URLs: /vip/validate/<id_vip>/
        """

        self.log.info('Validate Vip Request by id')

        try:
            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VIP_VALIDATION, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            id_vip = kwargs.get('id_vip')

            # Valid vip id
            if not is_valid_int_greater_zero_param(id_vip):
                self.log.error(
                    u'Parameter id_vip is invalid. Value: %s.', id_vip)
                raise InvalidValueError(None, 'id_vip', id_vip)

            vip = RequisicaoVips.get_by_pk(id_vip)

            with distributedlock(LOCK_VIP % id_vip):
                vip.validado = True
                vip.save()

            return self.response(dumps_networkapi({}))

        except RequisicaoVipsNotFoundError:
            return self.response_error(152)
        except RequisicaoVipsError:
            return self.response_error(150, 'Failed to validate vip request.')
        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except BaseException, e:
            return self.response_error(1)
