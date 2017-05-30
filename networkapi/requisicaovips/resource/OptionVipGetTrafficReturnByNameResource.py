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
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.exception import OptionVipError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.requisicaovips.models import OptionVip
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class OptionVipGetTrafficReturnByNameResource(RestResource):

    log = logging.getLogger('OptionVipGetTrafficReturnByEVipResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests GET to list all traffic return of the Option VIP by Environment Vip.

        URL: environment-vip/get/trafficreturn/<id_evip>
        """

        try:

            self.log.info('Search Traffic Return by name')

            # User permission
            if not has_perm(user, AdminPermission.OPTION_VIP, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            trafficreturn_map = networkapi_map.get('trafficreturn_opt')
            if trafficreturn_map is None:
                return self.response_error(3, u'There is no value to the trafficreturn_opt tag  of XML request.')

            # Get XML data
            name_trafficreturn = trafficreturn_map.get('trafficreturn')

            # Valid Parameters is none
            if name_trafficreturn is None:
                self.log.error(
                    u'Missing traffic return option name')
                return self.response_error(287)

            # New Queryset by Environment Vip
            queryset = OptionVip.objects.filter()

            if name_trafficreturn is not None:

                tipo_opcao = 'Retorno de trafego'
                queryset = queryset.filter(tipo_opcao=tipo_opcao)
                queryset = queryset.filter(nome_opcao_txt=name_trafficreturn)

                # Checks if there Vip Environment and all other  parameters are
                # null
                if len(queryset) == 0:
                    raise OptionVipError(None)

            # self.log.info(str(environment_vip))

            evips = []
            for evip in queryset:
                request_evip_map = {}
                request_evip_map['id'] = evip.id
                request_evip_map['tipo_opcao'] = evip.tipo_opcao
                request_evip_map['nome_opcao'] = evip.nome_opcao_txt
                evips.append(request_evip_map)

            self.log.info(str(evips))

            # self.log.info(str(ovips))

            return self.response(dumps_networkapi({'trafficreturn': evips}))

        except UserNotAuthorizedError:
            return self.not_authorized()

        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(1, x)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except OptionVipError:
            return self.response_error(1)

        except Exception, e:
            return self.response_error(1)
