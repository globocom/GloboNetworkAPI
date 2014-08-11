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

from networkapi.ambiente.models import Ambiente, AmbienteNotFoundError

from networkapi.admin_permission import AdminPermission

from networkapi.infrastructure.xml_utils import dumps_networkapi

from networkapi.grupo.models import GrupoError

from networkapi.util import is_valid_int_greater_zero_param

from networkapi.exception import InvalidValueError


class HealthcheckExpectResource(RestResource):

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições GET para consulta de HealthCheckExpects.

        Lista as informações dos HealthCheckExpect's de um determinado ambiente.

        URL:  /healthcheckexpect/ambiente/<id_amb>/
        """
        try:
            if not has_perm(user,
                            AdminPermission.HEALTH_CHECK_EXPECT,
                            AdminPermission.READ_OPERATION):
                return self.not_authorized()

            map_list = []

            environment_id = kwargs.get('id_amb')
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'The environment_id parameter is not a valid value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            environment = Ambiente().get_by_pk(environment_id)

            healthcheckexpects = HealthcheckExpect().search(environment_id)

            for healthcheckexpect in healthcheckexpects:
                healthcheckexpect_map = dict()
                healthcheckexpect_map['id'] = healthcheckexpect.id
                healthcheckexpect_map[
                    'expect_string'] = healthcheckexpect.expect_string
                healthcheckexpect_map[
                    'match_list'] = healthcheckexpect.match_list
                healthcheckexpect_map[
                    'id_ambiente'] = healthcheckexpect.ambiente_id

                map_list.append(healthcheckexpect_map)

            return self.response(dumps_networkapi({'healthcheck_expect': map_list}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except (HealthcheckExpectError, GrupoError):
            return self.response_error(1)
