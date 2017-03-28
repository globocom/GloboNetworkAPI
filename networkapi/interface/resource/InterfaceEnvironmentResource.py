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

from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.interface.models import EnvironmentInterface
from networkapi.interface.models import Interface
from networkapi.interface.models import InterfaceError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError


class InterfaceEnvironmentResource(RestResource):

    log = logging.getLogger('InterfaceEnvironmentResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to add Rack.

        URL: interface/associar-ambiente/
        """
        try:
            self.log.info('Associa interface aos ambientes')

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
            self.log.info('Edita os ambientes associados a uma interface')

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

            # deletar associacoes
            interface_list = EnvironmentInterface.objects.all().filter(interface__exact=interface)
            for var in interface_list:
                var.delete()

            return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except InterfaceError:
            return self.response_error(1)

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to find EnvironmentInterface.

        URLs: int/get-env-by-interface/<id_interface>
        """
        self.log.info('buscando os ambientes associados a uma interface')

        try:

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Get XML data
            interface = kwargs.get('id_interface')

            int_ambiente = EnvironmentInterface.get_by_interface(
                int(interface))

            ambiente_map = []

            for ids in int_ambiente:
                ambiente_map.append(
                    self.get_environment_map(ids.ambiente, ids.vlans))

            return self.response(dumps_networkapi({'ambiente': ambiente_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)
        except InterfaceError:
            return self.response_error(1)

    def get_environment_map(self, environment, vlans):
        environment_map = dict()
        environment_map['id'] = environment.id
        environment_map['divisao_dc_name'] = environment.divisao_dc.nome
        environment_map[
            'ambiente_logico_name'] = environment.ambiente_logico.nome
        environment_map['grupo_l3_name'] = environment.grupo_l3.nome
        if not environment.min_num_vlan_1 is None and not environment.max_num_vlan_2 is None:
            environment_map['range'] = str(
                environment.min_num_vlan_1) + ' - ' + str(environment.max_num_vlan_2)
        else:
            environment_map['range'] = 'Nao definido'
        environment_map['vlans'] = vlans

        return environment_map
