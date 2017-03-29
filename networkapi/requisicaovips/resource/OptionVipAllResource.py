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
from networkapi.exception import OptionVipError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.requisicaovips.models import OptionVip
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError


class OptionVipAllResource(RestResource):

    log = logging.getLogger('OptionVipAllResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to list all the Option VIP.

        URL: optionvip/all'
        """

        try:

            self.log.info('GET to list all the Option VIP')

            # User permission
            if not has_perm(user, AdminPermission.OPTION_VIP, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Find All Option VIP
            option_vips = OptionVip.get_all()

            ovips = []

            for ov in option_vips:
                ovips.append(model_to_dict(ov))

            return self.response(dumps_networkapi({'option_vip': ovips}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except OptionVipError:
            return self.response_error(1)
