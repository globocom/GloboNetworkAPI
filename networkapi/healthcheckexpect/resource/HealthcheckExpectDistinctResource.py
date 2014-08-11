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


class HealthcheckExpectDistinctResource(RestResource):

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições GET para buscar expect_strings do Healthchecks_expects com distinct.

        URL:  /healthcheckexpect/distinct/
        """
        try:
            if not has_perm(user,
                            AdminPermission.HEALTH_CHECK_EXPECT,
                            AdminPermission.READ_OPERATION):
                return self.not_authorized()

            expect_strings = HealthcheckExpect.get_expect_strings()

            map_list = []
            ex = []
            for es in expect_strings:

                if not es.expect_string in ex:
                    map_list.append(
                        {'expect_string': es.expect_string, 'id': es.id})
                    ex.append(es.expect_string)

            return self.response(dumps_networkapi({'healthcheck_expect': map_list}))

        except (HealthcheckExpectError, GrupoError):
            return self.response_error(1)
