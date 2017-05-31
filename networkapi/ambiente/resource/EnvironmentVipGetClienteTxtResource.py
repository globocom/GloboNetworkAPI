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
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.exception import EnvironmentVipError
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.util import is_valid_text


class EnvironmentVipGetClienteTxtResource(RestResource):

    """Class that receives requests related to the table 'EnvironmentVip'."""

    log = logging.getLogger('EnvironmentVipGetClienteTxtResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests Post to search cliente_txt of  Environment VIP by finalidade_txt

        URL: environmentvip/search/
        """

        try:

            self.log.info(
                'Search cliente_txt Environment VIP by finalidade_txt')

            # User permission
            if not has_perm(user, AdminPermission.ENVIRONMENT_VIP, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag of XML request.')

            environmentvip_map = networkapi_map.get('vip')
            if environmentvip_map is None:
                return self.response_error(3, u'There is no value to the vip tag of XML request.')

            # Get XML data
            finalidade = environmentvip_map.get('finalidade_txt')
            if not is_valid_string_maxsize(finalidade, 50) or not is_valid_string_minsize(finalidade, 3) or not is_valid_text(finalidade):
                self.log.error(
                    u'The finalidade_txt parameter is not a valid value: %s.', finalidade)
                raise InvalidValueError(None, 'finalidade_txt', finalidade)

            environmentVip = EnvironmentVip()

            evip_values = environmentVip.list_all_clientes_by_finalitys(
                finalidade)

            evips = dict()
            evips_list = []

            for evip in evip_values:
                evips['finalidade_txt'] = finalidade
                evips['cliente_txt'] = evip.get('cliente_txt')
                evips_list.append(evips)
                evips = dict()

            return self.response(dumps_networkapi({'cliente_txt': evips_list}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)

        except EnvironmentVipNotFoundError:
            return self.response_error(283)

        except EnvironmentVipError:
            return self.response_error(1)

        except Exception, e:
            return self.response_error(1)
