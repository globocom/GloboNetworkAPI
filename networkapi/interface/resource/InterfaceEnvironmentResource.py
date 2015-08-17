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
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import loads, XMLError, dumps_networkapi
from networkapi.admin_permission import AdminPermission
from networkapi.log import Log
from networkapi.ambiente.models import Ambiente
from networkapi.interface.models import EnvironmentInterface, Interface, InterfaceError
from networkapi.exception import InvalidValueError



class InterfaceEnvironmentResource(RestResource):

    log = Log('InterfaceEnvironmentResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Rack.

        URL: interface/associar-ambiente/
        """
        try:
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
            env = interface_map.get('ambiente')
            interface = interface_map.get('interface')

            amb_int = EnvironmentInterface()
            interfaces = Interface()
            amb = Ambiente()

            amb_int.interface = interfaces.get_by_pk(int(interface))
            amb_int.ambiente = amb.get_by_pk(int(env))

            amb_int.create(user)

            amb_int_map = dict()
            amb_int_map['interface_ambiente'] = amb_int

            return self.response(dumps_networkapi(amb_int_map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except InterfaceError:
           return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests POST to add Rack.

        URL: interface/associar-ambiente/
        """
        try:
            self.log.info("Edita os ambientes associados a uma interface")

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
            interface = interface_map.get('interface')
            interface = int(interface)

            #deletar associacoes
            interface_list = EnvironmentInterface.objects.all().filter(interface__exact=interface)
            for var in interface_list:
                var.delete(user)

            return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except InterfaceError:
           return self.response_error(1)
