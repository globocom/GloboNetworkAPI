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

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.healthcheckexpect.models import HealthcheckEqualError
from networkapi.healthcheckexpect.models import HealthcheckExpect
from networkapi.healthcheckexpect.models import HealthcheckExpectError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize


class HealthcheckAddResource(RestResource):

    log = logging.getLogger('HealthcheckAddResource.')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add a HeltcheckExpect.

        URL: healthcheckexpect/add/
        """

        try:
            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            healthcheck_map = networkapi_map.get('healthcheck')
            if healthcheck_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            match_list = healthcheck_map.get('match_list')
            expect_string = healthcheck_map.get('expect_string')
            environment_id = healthcheck_map.get('id_ambiente')

            # Valid equip_id
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'Parameter environment_id is invalid. Value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            if expect_string is not None:
                if not is_valid_string_maxsize(expect_string, 50) or not is_valid_string_minsize(expect_string, 2):
                    self.log.error(
                        u'Parameter expect_string is invalid. Value: %s.', expect_string)
                    raise InvalidValueError(
                        None, 'expect_string', expect_string)
            else:
                raise InvalidValueError(None, 'expect_string', expect_string)

            if match_list is not None:
                if not is_valid_string_maxsize(match_list, 50) or not is_valid_string_minsize(match_list, 2):
                    self.log.error(
                        u'Parameter match_list is invalid. Value: %s.', match_list)
                    raise InvalidValueError(None, 'match_list', match_list)
            else:
                raise InvalidValueError(None, 'expect_string', expect_string)

            # User permission
            if not has_perm(user,
                            AdminPermission.HEALTH_CHECK_EXPECT,
                            AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            healthcheck = HealthcheckExpect()

            ambiente = Ambiente.get_by_pk(environment_id)

            healthcheck.insert(user, match_list, expect_string, ambiente)

            healtchcheck_dict = dict()
            healtchcheck_dict['id'] = healthcheck.id

            return self.response(dumps_networkapi({'healthcheck_expect': healtchcheck_dict}))

        except AmbienteNotFoundError, e:
            return self.response_error(112)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except HealthcheckEqualError, e:
            return self.response_error(313, e.message)

        except HealthcheckExpectError, e:
            return self.response_error(1)

        except XMLError, e:
            return self.response_error(1)
