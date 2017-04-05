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
import logging

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.rest import RestResource


class EnvironmentVipGetFinalityResource(RestResource):

    log = logging.getLogger('EnvironmentVipGetFinalityResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to find all finalitys of environment VIP.

        URLs: /vip/get/finality
        """

        self.log.info('Find all finality distinct of environment_vip')

        try:
            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VIPS_REQUEST, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            evip = EnvironmentVip()
            # Business Validations
            evips = evip.list_all_finalitys()

            finality_map = dict()
            finality_list = []

            for evip in evips:
                finality_map['finality'] = evip.get('finalidade_txt')
                finality_list.append(finality_map)
                finality_map = dict()

            return self.response(dumps_networkapi({'finalidade': finality_list}))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except BaseException, e:
            return self.response_error(1)
