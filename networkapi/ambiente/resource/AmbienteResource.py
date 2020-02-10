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

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteDuplicatedError
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteLogico
from networkapi.ambiente.models import AmbienteLogicoNotFoundError
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.ambiente.models import AmbienteUsedByEquipmentVlanError
from networkapi.ambiente.models import ConfigEnvironment
from networkapi.ambiente.models import ConfigEnvironmentDuplicateError
from networkapi.ambiente.models import DivisaoDc
from networkapi.ambiente.models import DivisaoDcNotFoundError
from networkapi.ambiente.models import Filter
from networkapi.ambiente.models import FilterNotFoundError
from networkapi.ambiente.models import GroupL3NotFoundError
from networkapi.ambiente.models import GrupoL3
from networkapi.ambiente.models import IPConfig
from networkapi.ambiente.models import IPConfigNotFoundError
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_DC_DIVISION
from networkapi.distributedlock import LOCK_ENVIRONMENT
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.filter.models import CannotDissociateFilterError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotFoundError
from networkapi.rest import RestResource
from networkapi.util import destroy_cache_function
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_regex
from networkapi.util import is_valid_string_maxsize
from networkapi.vlan.models import Vlan


def get_environment_map(environment):
    environment_map = dict()
    environment_map['id'] = environment.id
    environment_map['link'] = environment.link
    environment_map['id_divisao'] = environment.divisao_dc.id
    environment_map['nome_divisao'] = environment.divisao_dc.nome
    environment_map['id_ambiente_logico'] = environment.ambiente_logico.id
    environment_map['nome_ambiente_logico'] = environment.ambiente_logico.nome
    environment_map['id_grupo_l3'] = environment.grupo_l3.id
    environment_map['nome_grupo_l3'] = environment.grupo_l3.nome
    environment_map['ambiente_rede'] = environment.divisao_dc.nome + ' - ' + \
        environment.ambiente_logico.nome + ' - ' + \
        environment.grupo_l3.nome

    if environment.filter is not None:
        environment_map['id_filter'] = environment.filter.id
        environment_map['filter_name'] = environment.filter.name

    if environment.vrf is not None:
        environment_map['vrf'] = environment.vrf
    return environment_map


class AmbienteResource(RestResource):

    """Classe que recebe as requisições relacionadas com a tabela 'ambiente'."""

    log = logging.getLogger('AmbienteResource')

    CODE_MESSAGE_CONFIG_ENVIRONMENT_ALREADY_EXISTS = 302

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições de GET para consulta de ambientes.

        Permite a consulta de todos os ambientes, ambientes filtrados por divisao_dc,
        ambientes filtrados por divisão_dc e por ambiente_logico

        URLs: /ambiente/,
              /ambiente/divisao_dc/<id_divisao_dc>/,
              /ambiente/divisao_dc/<id_divisao_dc>/ambiente_logico/<id_amb_logico>/,
        """
        try:
            if not has_perm(user, AdminPermission.ENVIRONMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                return self.not_authorized()
        
            environment_list = []
        
            division_id = kwargs.get('id_divisao_dc')
            environment_logical_id = kwargs.get('id_amb_logico')
        
            if division_id is not None:
                if not is_valid_int_greater_zero_param(division_id):
                    self.log.error(
                        u'The division_id parameter is not a valid value: %s.', division_id)
                    raise InvalidValueError(None, 'division_id', division_id)
                else:
                    division_dc = DivisaoDc.get_by_pk(division_id)
        
            if environment_logical_id is not None:
                if not is_valid_int_greater_zero_param(environment_logical_id):
                    self.log.error(
                        u'The environment_logical_id parameter is not a valid value: %s.', environment_logical_id)
                    raise InvalidValueError(
                        None, 'environment_logical_id', environment_logical_id)
                else:
                    loc_env = AmbienteLogico.get_by_pk(environment_logical_id)
        
            environments = Ambiente().search(
                division_id, environment_logical_id).select_related('grupo_l3', 'ambiente_logico', 'divisao_dc', 'filter')
            for environment in environments:
                environment_list.append(get_environment_map(environment))
        
            return self.response(dumps_networkapi({'ambiente': environment_list}))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except DivisaoDcNotFoundError:
            return self.response_error(164, division_id)
        except AmbienteLogicoNotFoundError:
            return self.response_error(162, environment_logical_id)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except (AmbienteError, GrupoError):
            return self.response_error(1)

    def handle_post(self, request, user, *args, **kwargs):
        """Trata requisições POST para inserir novo Ambiente.

        URL: ambiente/ or ambiente/ipconfig/
        """
        
        try:

            if not has_perm(user,
                            AdminPermission.ENVIRONMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION):
                return self.not_authorized()
        
            xml_map, attrs_map = loads(request.raw_post_data)
        
            self.log.debug('XML_MAP: %s', xml_map)
        
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')
        
            environment_map = networkapi_map.get('ambiente')
            if environment_map is None:
                return self.response_error(3, u'Não existe valor para a tag ambiente do XML de requisição.')
        
            link = environment_map.get('link')
            if not is_valid_string_maxsize(link, 200, False):
                self.log.error(u'Parameter link is invalid. Value: %s', link)
                raise InvalidValueError(None, 'link', link)
        
            l3_group_id = environment_map.get('id_grupo_l3')
            if not is_valid_int_greater_zero_param(l3_group_id):
                self.log.error(
                    u'The l3_group_id parameter is not a valid value: %s.', l3_group_id)
                raise InvalidValueError(None, 'l3_group_id', l3_group_id)
            else:
                l3_group_id = int(l3_group_id)
        
            logic_environment_id = environment_map.get('id_ambiente_logico')
            if not is_valid_int_greater_zero_param(logic_environment_id):
                self.log.error(
                    u'The logic_environment_id parameter is not a valid value: %s.', logic_environment_id)
                raise InvalidValueError(
                    None, 'logic_environment_id', logic_environment_id)
            else:
                logic_environment_id = int(logic_environment_id)
        
            dc_division_id = environment_map.get('id_divisao')
            if not is_valid_int_greater_zero_param(dc_division_id):
                self.log.error(
                    u'The dc_division_id parameter is not a valid value: %s.', dc_division_id)
                raise InvalidValueError(None, 'dc_division_id', dc_division_id)
            else:
                dc_division_id = int(dc_division_id)
        
            filter_id = environment_map.get('id_filter')
            if filter_id is not None:
                if not is_valid_int_greater_zero_param(filter_id):
                    self.log.error(
                        u'Parameter filter_id is invalid. Value: %s.', filter_id)
                    raise InvalidValueError(None, 'filter_id', filter_id)
        
            acl_path = environment_map.get('acl_path')
            if not is_valid_string_maxsize(acl_path, 250, False):
                self.log.error(
                    u'Parameter acl_path is invalid. Value: %s', acl_path)
                raise InvalidValueError(None, 'acl_path', acl_path)
        
            ipv4_template = environment_map.get('ipv4_template')
            if not is_valid_string_maxsize(ipv4_template, 250, False):
                self.log.error(
                    u'Parameter ipv4_template is invalid. Value: %s', ipv4_template)
                raise InvalidValueError(None, 'ipv4_template', ipv4_template)
        
            ipv6_template = environment_map.get('ipv6_template')
            if not is_valid_string_maxsize(ipv6_template, 250, False):
                self.log.error(
                    u'Parameter ipv6_template is invalid. Value: %s', ipv6_template)
                raise InvalidValueError(None, 'ipv6_template', ipv6_template)
        
            max_num_vlan_1 = environment_map.get('max_num_vlan_1')
            min_num_vlan_1 = environment_map.get('min_num_vlan_1')
            max_num_vlan_2 = environment_map.get('max_num_vlan_2')
            min_num_vlan_2 = environment_map.get('min_num_vlan_2')
            # validate  max_num_vlan_1 and min_num_vlan_1
            if (max_num_vlan_1 is not None and min_num_vlan_1 is None) or (min_num_vlan_1 is not None and max_num_vlan_1 is None):
                self.log.error(
                    u'Parameters min_num_vlan_1, max_num_vlan_1  is invalid. Values: %s, %s', (min_num_vlan_1, max_num_vlan_1))
                raise InvalidValueError(
                    None, 'min_num_vlan_1, max_num_vlan_1', min_num_vlan_1 + ',' + max_num_vlan_1)
        
            if max_num_vlan_1 is not None and min_num_vlan_1 is not None:
                max_num_vlan_1 = int(max_num_vlan_1)
                min_num_vlan_1 = int(min_num_vlan_1)
        
                if max_num_vlan_1 < 1 or min_num_vlan_1 < 1:
                    self.log.error(
                        u'Parameters min_num_vlan_1, max_num_vlan_1  is invalid. Values: %s, %s', (min_num_vlan_1, max_num_vlan_1))
                    raise InvalidValueError(
                        None, 'min_num_vlan_1, max_num_vlan_1', min_num_vlan_1 + ',' + max_num_vlan_1)
                if max_num_vlan_1 <= min_num_vlan_1:
                    self.log.error(
                        u'Parameters min_num_vlan_1, max_num_vlan_1  is invalid. Values: %s, %s', (min_num_vlan_1, max_num_vlan_1))
                    raise InvalidValueError(
                        None, 'min_num_vlan_1, max_num_vlan_1', min_num_vlan_1 + ',' + max_num_vlan_1)
            else:
                max_num_vlan_1 = max_num_vlan_2
                min_num_vlan_1 = min_num_vlan_2
            # validate  max_num_vlan_1 and min_num_vlan_1
        
            # validate  max_num_vlan_2 and min_num_vlan_2
            if (max_num_vlan_2 is not None and min_num_vlan_2 is None) or (min_num_vlan_2 is not None and max_num_vlan_2 is None):
                self.log.error(
                    u'Parameters min_num_vlan_2, max_num_vlan_2  is invalid. Values: %s, %s', (min_num_vlan_2, max_num_vlan_2))
                raise InvalidValueError(
                    None, 'min_num_vlan_2, max_num_vlan_2', min_num_vlan_2 + ',' + max_num_vlan_1)
        
            if max_num_vlan_2 is not None and min_num_vlan_2 is not None:
                max_num_vlan_2 = int(max_num_vlan_2)
                min_num_vlan_2 = int(min_num_vlan_2)
        
                max_num_vlan_1 = int(max_num_vlan_1)
                min_num_vlan_1 = int(min_num_vlan_1)
        
                if max_num_vlan_2 < 1 or min_num_vlan_2 < 1:
                    self.log.error(
                        u'Parameters min_num_vlan_2, max_num_vlan_2  is invalid. Values: %s, %s', (min_num_vlan_2, max_num_vlan_2))
                    raise InvalidValueError(
                        None, 'min_num_vlan_2, max_num_vlan_2', min_num_vlan_2 + ',' + max_num_vlan_1)
        
                if max_num_vlan_2 <= min_num_vlan_2:
                    self.log.error(
                        u'Parameters min_num_vlan_2, max_num_vlan_2  is invalid. Values: %s, %s', (min_num_vlan_2, max_num_vlan_2))
                    raise InvalidValueError(
                        None, 'min_num_vlan_2, max_num_vlan_2', min_num_vlan_2 + ',' + max_num_vlan_1)
            else:
                max_num_vlan_2 = max_num_vlan_1
                min_num_vlan_2 = min_num_vlan_1
            # validate  max_num_vlan_2 and min_num_vlan_2
        
            vrf = environment_map.get('vrf')
            if not is_valid_string_maxsize(vrf, 100, False):
                self.log.error(u'Parameter vrf is invalid. Value: %s', vrf)
                raise InvalidValueError(None, 'link', vrf)
        
            environment = Ambiente()
            environment.grupo_l3 = GrupoL3()
            environment.ambiente_logico = AmbienteLogico()
            environment.divisao_dc = DivisaoDc()
            environment.grupo_l3.id = l3_group_id
            environment.ambiente_logico.id = logic_environment_id
            environment.divisao_dc.id = dc_division_id
            environment.acl_path = fix_acl_path(acl_path)
            environment.ipv4_template = ipv4_template
            environment.ipv6_template = ipv6_template
            environment.max_num_vlan_1 = max_num_vlan_1
            environment.min_num_vlan_1 = min_num_vlan_1
            environment.max_num_vlan_2 = max_num_vlan_2
            environment.min_num_vlan_2 = min_num_vlan_2
            environment.vrf = vrf
        
            if filter_id is not None:
                environment.filter = Filter()
                environment.filter.id = filter_id
        
            environment.link = link
        
            environment.create(user)
        
            # IP Config
            ip_config = kwargs.get('ip_config')
        
            # If ip config is set
            if ip_config:
        
                # Add this to environment
                id_ip_config = environment_map.get('id_ip_config')
        
                # Valid ip config
                if not is_valid_int_greater_zero_param(id_ip_config):
                    raise InvalidValueError(None, 'id_ip_config', id_ip_config)
        
                # Ip config must exists
                ip_conf = IPConfig().get_by_pk(id_ip_config)
        
                # Makes the relationship
                config = ConfigEnvironment()
                config.environment = environment
                config.ip_config = ip_conf
        
                config.save()
        
            environment_map = dict()
            environment_map['id'] = environment.id
        
            return self.response(dumps_networkapi({'ambiente': environment_map}))
        
        except GrupoError:
            return self.response_error(1)
        
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)
        
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        
        except FilterNotFoundError, e:
            return self.response_error(339)
        
        except IPConfigNotFoundError, e:
            return self.response_error(301)
        
        except GrupoL3.DoesNotExist:
            return self.response_error(160, l3_group_id)
        
        except AmbienteLogicoNotFoundError:
            return self.response_error(162, logic_environment_id)
        
        except AmbienteDuplicatedError:
            return self.response_error(219)
        
        except DivisaoDcNotFoundError:
            return self.response_error(164, dc_division_id)
        
        except ConfigEnvironmentDuplicateError, e:
            return self.response_error(self.CODE_MESSAGE_CONFIG_ENVIRONMENT_ALREADY_EXISTS)
        
        except AmbienteError:
            return self.response_error(1)

    def handle_put(self, request, user, *args, **kwargs):
        """Trata requisições PUT para alterar um Ambiente.

        URL: ambiente/<id_ambiente>/
        """

        try:
        
            environment_id = kwargs.get('id_ambiente')
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'The environment_id parameter is not a valid value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)
        
            if not has_perm(user,
                            AdminPermission.ENVIRONMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION):
                return self.not_authorized()
        
            xml_map, attrs_map = loads(request.raw_post_data)
        
            self.log.debug('XML_MAP: %s', xml_map)
        
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')
        
            environment_map = networkapi_map.get('ambiente')
            if environment_map is None:
                return self.response_error(3, u'Não existe valor para a tag ambiente do XML de requisição.')
        
            l3_group_id = environment_map.get('id_grupo_l3')
            if not is_valid_int_greater_zero_param(l3_group_id):
                self.log.error(
                    u'The l3_group_id parameter is not a valid value: %s.', l3_group_id)
                raise InvalidValueError(None, 'l3_group_id', l3_group_id)
            else:
                l3_group_id = int(l3_group_id)
        
            GrupoL3.get_by_pk(l3_group_id)
        
            logic_environment_id = environment_map.get('id_ambiente_logico')
            if not is_valid_int_greater_zero_param(logic_environment_id):
                self.log.error(
                    u'The logic_environment_id parameter is not a valid value: %s.', logic_environment_id)
                raise InvalidValueError(
                    None, 'logic_environment_id', logic_environment_id)
            else:
                logic_environment_id = int(logic_environment_id)
        
            AmbienteLogico.get_by_pk(logic_environment_id)
        
            dc_division_id = environment_map.get('id_divisao')
            if not is_valid_int_greater_zero_param(dc_division_id):
                self.log.error(
                    u'The dc_division_id parameter is not a valid value: %s.', dc_division_id)
                raise InvalidValueError(None, 'dc_division_id', dc_division_id)
            else:
                dc_division_id = int(dc_division_id)
        
            DivisaoDc.get_by_pk(dc_division_id)
        
            link = environment_map.get('link')
            if not is_valid_string_maxsize(link, 200, False):
                self.log.error(u'Parameter link is invalid. Value: %s', link)
                raise InvalidValueError(None, 'link', link)
        
            vrf = environment_map.get('vrf')
            if not is_valid_string_maxsize(link, 100, False):
                self.log.error(u'Parameter vrf is invalid. Value: %s', vrf)
                raise InvalidValueError(None, 'vrf', vrf)
        
            filter_id = environment_map.get('id_filter')
            if filter_id is not None:
                if not is_valid_int_greater_zero_param(filter_id):
                    self.log.error(
                        u'Parameter filter_id is invalid. Value: %s.', filter_id)
                    raise InvalidValueError(None, 'filter_id', filter_id)
        
                filter_id = int(filter_id)
                # Filter must exist
                Filter.get_by_pk(filter_id)
        
            acl_path = environment_map.get('acl_path')
            if not is_valid_string_maxsize(acl_path, 250, False):
                self.log.error(
                    u'Parameter acl_path is invalid. Value: %s', acl_path)
                raise InvalidValueError(None, 'acl_path', acl_path)
        
            ipv4_template = environment_map.get('ipv4_template')
            if not is_valid_string_maxsize(ipv4_template, 250, False):
                self.log.error(
                    u'Parameter ipv4_template is invalid. Value: %s', ipv4_template)
                raise InvalidValueError(None, 'ipv4_template', ipv4_template)
        
            ipv6_template = environment_map.get('ipv6_template')
            if not is_valid_string_maxsize(ipv6_template, 250, False):
                self.log.error(
                    u'Parameter ipv6_template is invalid. Value: %s', ipv6_template)
                raise InvalidValueError(None, 'ipv6_template', ipv6_template)
        
            max_num_vlan_1 = environment_map.get('max_num_vlan_1')
            min_num_vlan_1 = environment_map.get('min_num_vlan_1')
            max_num_vlan_2 = environment_map.get('max_num_vlan_2')
            min_num_vlan_2 = environment_map.get('min_num_vlan_2')
            # validate  max_num_vlan_1 and min_num_vlan_1
            if (max_num_vlan_1 is not None and min_num_vlan_1 is None) or (min_num_vlan_1 is not None and max_num_vlan_1 is None):
                self.log.error(
                    u'Parameters min_num_vlan_1, max_num_vlan_1  is invalid. Values: %s, %s', (min_num_vlan_1, max_num_vlan_1))
                raise InvalidValueError(
                    None, 'min_num_vlan_1, max_num_vlan_1', min_num_vlan_1 + ',' + max_num_vlan_1)
        
            if max_num_vlan_1 is not None and min_num_vlan_1 is not None:
                max_num_vlan_1 = int(max_num_vlan_1)
                min_num_vlan_1 = int(min_num_vlan_1)
        
                if max_num_vlan_1 < 1 or min_num_vlan_1 < 1:
                    self.log.error(
                        u'Parameters min_num_vlan_1, max_num_vlan_1  is invalid. Values: %s, %s', (min_num_vlan_1, max_num_vlan_1))
                    raise InvalidValueError(
                        None, 'min_num_vlan_1, max_num_vlan_1', min_num_vlan_1 + ',' + max_num_vlan_1)
                if max_num_vlan_1 <= min_num_vlan_1:
                    self.log.error(
                        u'Parameters min_num_vlan_1, max_num_vlan_1  is invalid. Values: %s, %s', (min_num_vlan_1, max_num_vlan_1))
                    raise InvalidValueError(
                        None, 'min_num_vlan_1, max_num_vlan_1', min_num_vlan_1 + ',' + max_num_vlan_1)
            else:
                max_num_vlan_1 = max_num_vlan_2
                min_num_vlan_1 = min_num_vlan_2
            # validate  max_num_vlan_1 and min_num_vlan_1
        
            # validate  max_num_vlan_2 and min_num_vlan_2
            if (max_num_vlan_2 is not None and min_num_vlan_2 is None) or (min_num_vlan_2 is not None and max_num_vlan_2 is None):
                self.log.error(
                    u'Parameters min_num_vlan_2, max_num_vlan_2  is invalid. Values: %s, %s', (min_num_vlan_2, max_num_vlan_2))
                raise InvalidValueError(
                    None, 'min_num_vlan_2, max_num_vlan_2', min_num_vlan_2 + ',' + max_num_vlan_1)
        
            if max_num_vlan_2 is not None and min_num_vlan_2 is not None:
                max_num_vlan_2 = int(max_num_vlan_2)
                min_num_vlan_2 = int(min_num_vlan_2)
        
                max_num_vlan_1 = int(max_num_vlan_1)
                min_num_vlan_1 = int(min_num_vlan_1)
        
                if max_num_vlan_2 < 1 or min_num_vlan_2 < 1:
                    self.log.error(
                        u'Parameters min_num_vlan_2, max_num_vlan_2  is invalid. Values: %s, %s', (min_num_vlan_2, max_num_vlan_2))
                    raise InvalidValueError(
                        None, 'min_num_vlan_2, max_num_vlan_2', min_num_vlan_2 + ',' + max_num_vlan_1)
        
                if max_num_vlan_2 <= min_num_vlan_2:
                    self.log.error(
                        u'Parameters min_num_vlan_2, max_num_vlan_2  is invalid. Values: %s, %s', (min_num_vlan_2, max_num_vlan_2))
                    raise InvalidValueError(
                        None, 'min_num_vlan_2, max_num_vlan_2', min_num_vlan_2 + ',' + max_num_vlan_1)
            else:
                max_num_vlan_2 = max_num_vlan_1
                min_num_vlan_2 = min_num_vlan_1
            # validate  max_num_vlan_2 and min_num_vlan_2
        
            with distributedlock(LOCK_ENVIRONMENT % environment_id):
        
                # Delete vlan's cache
                key_list_db = Vlan.objects.filter(ambiente__pk=environment_id)
                key_list = []
                for key in key_list_db:
                    key_list.append(key.id)
        
                destroy_cache_function(key_list)
        
                # Destroy equipment's cache
                equip_id_list = []
                envr = Ambiente.get_by_pk(environment_id)
                for equipment in envr.equipamentoambiente_set.all():
                    equip_id_list.append(equipment.equipamento_id)
        
                destroy_cache_function(equip_id_list, True)
        
                Ambiente.update(user,
                                environment_id,
                                grupo_l3_id=l3_group_id,
                                ambiente_logico_id=logic_environment_id,
                                divisao_dc_id=dc_division_id,
                                filter_id=filter_id,
                                link=link,
                                vrf=vrf,
                                acl_path=fix_acl_path(acl_path),
                                ipv4_template=ipv4_template,
                                ipv6_template=ipv6_template,
                                max_num_vlan_1=max_num_vlan_1,
                                min_num_vlan_1=min_num_vlan_1,
                                max_num_vlan_2=max_num_vlan_2,
                                min_num_vlan_2=min_num_vlan_2)
        
                return self.response(dumps_networkapi({}))
        
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except FilterNotFoundError, e:
            return self.response_error(339)
        except GroupL3NotFoundError:
            return self.response_error(160, l3_group_id)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except AmbienteLogicoNotFoundError:
            return self.response_error(162, logic_environment_id)
        except AmbienteDuplicatedError:
            return self.response_error(219)
        except DivisaoDcNotFoundError:
            return self.response_error(164, dc_division_id)
        except CannotDissociateFilterError, e:
            return self.response_error(349, e.cause)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)
        except (AmbienteError, GrupoError):
            return self.response_error(1)

    def handle_delete(self, request, user, *args, **kwargs):
        """Trata requisições DELETE para remover um Ambiente.

        URL: ambiente/<id_ambiente>/
        """

        try:
        
            environment_id = kwargs.get('id_ambiente')
        
            # Valid ID Environment
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'The environment_id parameter is not a valid value: %s.', environment_id)
                raise InvalidValueError(None, 'environment_id', environment_id)
        
            if not has_perm(user,
                            AdminPermission.ENVIRONMENT_MANAGEMENT,
                            AdminPermission.WRITE_OPERATION):
                return self.not_authorized()
        
            with distributedlock(LOCK_ENVIRONMENT % environment_id):
        
                # Delete vlan's cache
                key_list_db = Vlan.objects.filter(ambiente__pk=environment_id)
                key_list = []
                for key in key_list_db:
                    key_list.append(key.id)
        
                destroy_cache_function(key_list)
        
                # Destroy equipment's cache
                equip_id_list = []
                envr = Ambiente.get_by_pk(environment_id)
                for equipment in envr.equipamentoambiente_set.all():
                    equip_id_list.append(equipment.equipamento_id)
        
                destroy_cache_function(equip_id_list, True)
        
                Ambiente.remove(user, environment_id)
        
                return self.response(dumps_networkapi({}))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except AmbienteUsedByEquipmentVlanError, e:
            # dict sent when a vlan cant be removed because of vip request
            # created
            if type(e.cause) is dict:
                return self.response_error(323, environment_id, e.cause['Net'], e.cause['Vlan'], e.cause['ReqVip'])
            # str sent when a vlan cant be removed because its active
            elif type(e.cause) is str:
                return self.response_error(324, environment_id, e.cause)
            else:
                return self.response_error(220, environment_id)
        except (GrupoError, AmbienteError):
            return self.response_error(1)


class AmbienteEquipamentoResource(RestResource):

    """Classe que recebe as requisições relacionadas com a tabela 'ambiente'."""

    log = logging.getLogger('AmbienteEquipamentoResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições de GET para consulta de um ambiente.

        Consulta o ambiente de um IP associado a um Equipamento.

        URL: /ambiente/equipamento/<nome_equip>/ip/<x1>.<x2>.<x3>.<x4>/
        """
        equipment_name = kwargs.get('nome_equip')
        oct1 = kwargs.get('x1')
        oct2 = kwargs.get('x2')
        oct3 = kwargs.get('x3')
        oct4 = kwargs.get('x4')

        if equipment_name is None or oct1 is None or oct2 is None or oct3 is None or oct4 is None:
            return super(AmbienteEquipamentoResource, self).handle_get(request, user, *args, **kwargs)

        self.log.debug('nome_equip = %s', equipment_name)
        self.log.debug('x1 = %s', oct1)
        self.log.debug('x2 = %s', oct2)
        self.log.debug('x3 = %s', oct3)
        self.log.debug('x4 = %s', oct4)

        try:
            equip = Equipamento().get_by_name(equipment_name)

            if not has_perm(user,
                            AdminPermission.ENVIRONMENT_MANAGEMENT,
                            AdminPermission.READ_OPERATION,
                            None,
                            equip.id,
                            AdminPermission.EQUIP_READ_OPERATION):
                return self.not_authorized()

            ip = Ip().get_by_octs_equipment(oct1, oct2, oct3, oct4, equip.id)

            environment_map = get_environment_map(ip.vlan.ambiente)
            map = dict()
            map['ambiente'] = environment_map

            return self.response(dumps_networkapi(map))

        except EquipamentoNotFoundError:
            return self.response_error(117, equipment_name)
        except IpNotFoundError:
            return self.response_error(118, oct1 + '.' + oct2 + '.' + oct3 + '.' + oct4, equip.id)
        except (IpError, EquipamentoError, GrupoError):
            return self.response_error(1)


def fix_acl_path(acl_path):
    path = acl_path
    if path:
        if is_valid_regex(path, r'^.*[\\\\:*?"<>|].*$'):
            raise InvalidValueError(None, 'acl_path', acl_path)
        try:
            while path[0] == '/':
                path = path[1:]

            while path[-1] == '/':
                path = path[:-1]
        except IndexError:
            raise InvalidValueError(None, 'acl_path', acl_path)

    return path


if __name__ == '__main__':
    pass
