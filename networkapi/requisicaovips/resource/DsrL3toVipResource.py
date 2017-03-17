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
from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.exception import OptionVipError
from networkapi.exception import OptionVipNotFoundError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.requisicaovips.models import DsrL3_to_Vip
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class DsrL3toVipResource(RestResource):

    """Class that receives requests related to the table 'DsrL3_to_Vip'."""

    log = logging.getLogger('DsrL3toVipResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to get Option VIP.

        URL: vip/dsrl3/<id_dsrl3_vip>/
        """

        try:

            self.log.info('Get DSRL3 id from VIP by ID')

            id_dsrl3_vip = kwargs.get('id_dsrl3_vip')

            # User permission
            if not has_perm(user, AdminPermission.OPTION_VIP, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Valid Option VIP ID
            if not is_valid_int_greater_zero_param(id_dsrl3_vip):
                self.log.error(
                    u'The id_dsrl3_vip parameter is not a valid value: %s.', id_dsrl3_vip)
                raise InvalidValueError(None, 'id_option_vip', id_dsrl3_vip)

            try:

                # Find Option VIP by ID to check if it exist
                dsrl3 = DsrL3_to_Vip.objects.get(id=id_dsrl3_vip)

            except ObjectDoesNotExist, e:
                self.log.error(
                    u'There is no dsrl3 with pk = %s.', id_dsrl3_vip)
                return self.response_error(289)

            option_map = dict()
            option_map['dsrl3'] = model_to_dict(dsrl3)

            return self.response(dumps_networkapi(option_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except OptionVipNotFoundError:
            return self.response_error(289)

        except OptionVipError:
            return self.response_error(1)
