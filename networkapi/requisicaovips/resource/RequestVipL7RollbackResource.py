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
from datetime import datetime

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_VIP
from networkapi.exception import InvalidValueError
from networkapi.exception import RequestVipsNotBeenCreatedError
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.script_utils import ScriptError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import clone
from networkapi.util import is_valid_int_greater_equal_zero_param
from networkapi.util import is_valid_int_greater_zero_param


class RequestVipL7RollbackResource(RestResource):

    log = logging.getLogger('RequestVipL7RollbackResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Rollback of the filter

        URLs: /vip/l7/<id_vip>/rollback/
        """

        self.log.info('Applies the last working filter to VIP')

        try:
            id_vip = kwargs.get('id_vip')

            # User is authorized
            if not has_perm(user, AdminPermission.VIP_ALTER_SCRIPT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Vip ID
            if not is_valid_int_greater_zero_param(id_vip):
                self.log.error(
                    u'The vip_id parameter is not a valid value: %s.', id_vip)
                raise InvalidValueError(None)

            # Get VIP data
            vip = RequisicaoVips.get_by_pk(id_vip)

            with distributedlock(LOCK_VIP % id_vip):
                # backup do vip
                vip_old = clone(vip)

                # Vip must be created
                if not vip.vip_criado:
                    self.log.error(
                        u'Filter can not be applied because VIP has not been created yet.')
                    raise RequestVipsNotBeenCreatedError(None)

                # salva data do rollback, rollback para aplicado, passa o
                # aplicado para l7
                vip.applied_l7_datetime = datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S')

                # Set Applied With Rollback
                vip.filter_applied = vip_old.filter_rollback
                vip.rule_applied = vip_old.rule_rollback

                # Set Rollback With Applied
                vip.filter_rollback = vip_old.filter_applied
                vip.rule_rollback = vip_old.rule_applied

                vip.save(user, commit=True)

                # roda script
                command = 'gerador_vips -i %d --l7_filter_current' % vip.id
                code, stdout, stderr = exec_script(command)

                # code 0 = executou com sucesso
                if code == 0:
                    success_map = dict()
                    success_map['codigo'] = '%04d' % code
                    success_map['descricao'] = {
                        'stdout': stdout, 'stderr': stderr}

                    map = dict()
                    map['sucesso'] = success_map
                    return self.response(dumps_networkapi(map))
                else:
                    # pega os dados anteriores e os salva no banco
                    vip_old.save(user, commit=True)
                    return self.response_error(2, stdout + stderr)

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)

        except ScriptError, s:
            return self.response_error(2, s)

        except UserNotAuthorizedError:
            return self.not_authorized()
