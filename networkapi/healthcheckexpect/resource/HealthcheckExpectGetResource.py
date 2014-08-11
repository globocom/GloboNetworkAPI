# -*- coding:utf-8 -*-

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


from networkapi.rest import RestResource

from networkapi.auth import has_perm

from networkapi.healthcheckexpect.models import HealthcheckExpect, HealthcheckExpectError

from networkapi.admin_permission import AdminPermission

from networkapi.infrastructure.xml_utils import dumps_networkapi

from networkapi.grupo.models import GrupoError
from django.forms.models import model_to_dict
from networkapi.healthcheckexpect.models import HealthcheckExpectNotFoundError

from networkapi.util import is_valid_int_greater_zero_param

from networkapi.exception import InvalidValueError


class HealthcheckExpectGetResource(RestResource):

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições GET para consulta de HealthCheckExpects por id.

        Lista as informações de um HealthCheckExpect por id.

        URL:  /healthcheckexpect/get/<id_healthcheck_expect>/
        """
        try:
            if not has_perm(user,
                            AdminPermission.HEALTH_CHECK_EXPECT,
                            AdminPermission.READ_OPERATION):
                return self.not_authorized()

            id_healthcheck = kwargs.get('id_healthcheck')

            if not is_valid_int_greater_zero_param(id_healthcheck):
                self.log.error(
                    u'The id_healthcheck parameter is not a valid value: %s.', id_healthcheck)
                raise InvalidValueError(None, 'id_healthcheck', id_healthcheck)

            heal = HealthcheckExpect.get_by_pk(id_healthcheck)

            healthcheckexpect_map = model_to_dict(heal)

            return self.response(dumps_networkapi({'healthcheck_expect': healthcheckexpect_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except HealthcheckExpectNotFoundError:
            return self.response_error(124)
        except (HealthcheckExpectError, GrupoError):
            return self.response_error(1)
