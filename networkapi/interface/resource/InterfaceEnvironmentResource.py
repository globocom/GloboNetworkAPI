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


from __future__ import with_statement
from networkapi.rest import RestResource
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.admin_permission import AdminPermission
from networkapi.log import Log
from networkapi.grupo.models import GrupoError
from networkapi.ambiente.models import Ambiente
from networkapi.interface.models import EnvironmentInterface, Interface
from networkapi.exception import InvalidValueError


class InterfaceEnvironmentResource(RestResource):

    log = Log('InterfaceEnvironmentResource')

    def handle_post(self, request, user, *args, **kwargs):
        #"""Treat requests POST to add Rack.
#
 #       URL: interface/associar-ambiente/
  #      """

        #try:
            self.log.info("Associa interface aos ambientes")

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            # Load XML data
                xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'There is no value to the networkapi tag  of XML request.')

            interface_map = networkapi_map.get('interface')
            if interface_map is None:
                return self.response_error(3, u'There is no value to the interface tag  of XML request.')

            # Get XML data
            envs = interface_map.get('ambientes')
            int = interface_map.get('interface')

            amb_int_list = []
            amb_int = EnvironmentInterface()
            interface = Interface()
            ambiente = Ambiente()
            amb_int.interface = interface.get_by_pk(int)

            # set variables
            for var in envs:
                amb_int.ambiente = ambiente.get_by_pk(str(var))
                #id = amb_int.save(user)
                amb_int_list.append(id)

            amb_int_map = dict()
            amb_int_map['interface_ambiente'] = amb_int_list

            return self.response(dumps_networkapi(amb_int_map))

        #except InvalidValueError, e:
         #   return self.response_error(269, e.param, e.value)
        #except XMLError, x:
         #   self.log.error(u'Erro ao ler o XML da requisição.')
          #  return self.response_error(3, x)
        #except InterfaceError:
         #   return self.response_error(1)
