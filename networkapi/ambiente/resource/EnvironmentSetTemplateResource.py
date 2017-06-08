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
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.ambiente.models import IP_VERSION
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_equal_zero_param


class EnvironmentSetTemplateResource(RestResource):

    log = logging.getLogger('EnvironmentSetTemplateResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Handle POST requests to get Environments by template name.

            URLs: /environment/get_env_template/,
        """

        try:

            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()

            environment_list = list()

            xml_map, attrs_map = loads(request.raw_post_data)

            self.log.debug('XML_MAP: %s', xml_map)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            map = networkapi_map.get('map')
            if map is None:
                return self.response_error(3, u'Não existe valor para a tag ambiente do XML de requisição.')

            name = map.get('name')
            network = map.get('network')

            if network == IP_VERSION.IPv4[1]:
                environments = Ambiente.objects.filter(ipv4_template=name)
            elif network == IP_VERSION.IPv6[1]:
                environments = Ambiente.objects.filter(ipv6_template=name)
            else:
                return self.response_error(269, 'network', network)

            if environments:
                for env in environments:
                    environment_list.append(
                        env.divisao_dc.nome + '-' + env.ambiente_logico.nome + '-' + env.grupo_l3.nome)

            return self.response(dumps_networkapi({'ambiente': environment_list}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)
        except (AmbienteError, GrupoError, Exception), e:
            return self.response_error(1)

    def handle_post(self, request, user, *args, **kwargs):
        """Handle POST requests to set Environment template

            URLs: /environment/set_template/<environment_id>/
        """

        try:

            environment_id = kwargs.get('environment_id')
            if not is_valid_int_greater_equal_zero_param(environment_id):
                self.log.error(
                    u'The environment_id parameter is not a valid value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)

            if not has_perm(user,
                            AdminPermission.VLAN_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            xml_map, attrs_map = loads(request.raw_post_data)

            self.log.debug('XML_MAP: %s', xml_map)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            environment_map = networkapi_map.get('environment')
            if environment_map is None:
                return self.response_error(3, u'Não existe valor para a tag ambiente do XML de requisição.')

            name = environment_map.get('name')
            network = environment_map.get('network')

            if int(environment_id) != 0:

                Ambiente().get_by_pk(environment_id)

                if network == IP_VERSION.IPv4[1]:
                    Ambiente.objects.filter(
                        id=environment_id).update(ipv4_template=name)
                elif network == IP_VERSION.IPv6[1]:
                    Ambiente.objects.filter(
                        id=environment_id).update(ipv6_template=name)
                else:
                    return self.response_error(269, 'network', network)
            else:
                if network == IP_VERSION.IPv4[1]:
                    Ambiente.objects.filter(
                        ipv4_template=name).update(ipv4_template='')
                elif network == IP_VERSION.IPv6[1]:
                    Ambiente.objects.filter(
                        ipv6_template=name).update(ipv6_template='')
                else:
                    return self.response_error(269, 'network', network)

            return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)
        except (AmbienteError, GrupoError, Exception), e:
            return self.response_error(1)


if __name__ == '__main__':
    pass
