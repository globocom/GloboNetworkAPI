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

from django.db.utils import IntegrityError

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_IP_EQUIPMENT
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.ipaddr import IPAddress
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpCantBeRemovedFromVip
from networkapi.ip.models import IpCantRemoveFromServerPool
from networkapi.ip.models import IpEquipamento
from networkapi.ip.models import IpEquipamentoDuplicatedError
from networkapi.ip.models import IpEquipCantDissociateFromVip
from networkapi.ip.models import IpEquipmentNotFoundError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import NetworkIPv4NotFoundError
from networkapi.requisicaovips.models import ServerPoolMember
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import destroy_cache_function
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_ipv4
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.util import mount_ipv4_string
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanNotFoundError


def insert_ip(ip_map, user):
    """Insere um IP e o relacionamento entre o IP e o equipamento.

    @param ip_map: Map com as chaves: id_equipamento, id_vlan e descricao
    @param user: Usuário autenticado na API.

    @return Em caso de erro retorna a tupla: (código da mensagem de erro, argumento01, argumento02, ...)
            Em caso de sucesso retorna a tupla: (0, <mapa com os dados do IP>)

    @raise VlanNotFoundError: VLAN não cadastrada.
    @raise VlanError: Falha ao pesquisar a VLAN.
    @raise EquipamentoNotFoundError: Equipamento não cadastrado.
    @raise EquipamentoError: Falha ao pesquisar o Equipamento.
    @raise IpNotAvailableError: Não existe um IP disponível para a VLAN.
    @raise IpError: Falha ao inserir no banco de dados.
    @raise UserNotAuthorizedError: Usuário sem autorização para executar a operação.

    """
    log = logging.getLogger('insert_ip')

    equip_id = ip_map.get('id_equipamento')
    if not is_valid_int_greater_zero_param(equip_id):
        log.error(
            u'The equip_id parameter is not a valid value: %s.', equip_id)
        raise InvalidValueError(None, 'equip_id', equip_id)
    else:
        equip_id = int(equip_id)

    if not has_perm(user,
                    AdminPermission.IPS,
                    AdminPermission.WRITE_OPERATION,
                    None,
                    equip_id,
                    AdminPermission.EQUIP_WRITE_OPERATION):
        raise UserNotAuthorizedError(
            None, u'Usuário não tem permissão para executar a operação.')

    vlan_id = ip_map.get('id_vlan')
    if not is_valid_int_greater_zero_param(vlan_id):
        log.error(u'The vlan_id parameter is not a valid value: %s.', vlan_id)
        raise InvalidValueError(None, 'vlan_id', vlan_id)
    else:
        vlan_id = int(vlan_id)

    desc_ip = ip_map.get('descricao')
    if desc_ip is not None:
        if not is_valid_string_maxsize(desc_ip, 100) or not is_valid_string_minsize(desc_ip, 3):
            log.error(u'Parameter desc_ip is invalid. Value: %s.', desc_ip)
            raise InvalidValueError(None, 'desc_ip', desc_ip)

    ip = Ip()
    ip.descricao = desc_ip

    ip.create(user, equip_id, vlan_id, False)

    ip_map = dict()
    ip_map['id'] = ip.id
    ip_map['id_redeipv4'] = ip.networkipv4.id
    ip_map['oct4'] = ip.oct4
    ip_map['oct3'] = ip.oct3
    ip_map['oct2'] = ip.oct2
    ip_map['oct1'] = ip.oct1
    ip_map['descricao'] = ip.descricao

    return 0, ip_map


def insert_ip_equipment(ip_id, equip_id, user):
    """Insere o relacionamento entre o IP e o equipamento.

    @param ip_id: Identificador do IP.
    @param equip_id: Identificador do equipamento.
    @param user: Usuário autenticado.

    @return: O ip_equipamento criado.

    @raise IpError: Falha ao inserir.
    @raise EquipamentoNotFoundError: Equipamento não cadastrado.
    @raise IpNotFoundError: Ip não cadastrado.
    @raise IpEquipamentoDuplicatedError: IP já cadastrado para o equipamento.
    @raise EquipamentoError: Falha ao pesquisar o equipamento.
    @raise UserNotAuthorizedError: Usuário sem autorização para executar a operação.
    """
    if not has_perm(user,
                    AdminPermission.IPS,
                    AdminPermission.WRITE_OPERATION,
                    None,
                    equip_id,
                    AdminPermission.EQUIP_WRITE_OPERATION):
        raise UserNotAuthorizedError(
            None, u'Usuário não tem permissão para executar a operação.')

    ip_equipment = IpEquipamento()
    ip_equipment.create(user, ip_id, equip_id)

    return ip_equipment


def remove_ip_equipment(ip_id, equipment_id, user):
    """ Remove o relacionamento entre um ip e um equipamento.

    @param ip_id: Identificador do IP.
    @param equipment_id: Identificador do equipamento.
    @param user: Usuário autenticado.

    @return: Nothing.

    @raise IpEquipmentNotFoundError: Relacionamento não cadastrado.
    @raise IpEquipCantDissociateFromVip: Equip is the last balancer in a created Vip Request, the relationship cannot be removed.
    @raise EquipamentoNotFoundError: Equipamento não cadastrado.
    @raise IpError, GrupoError: Falha na pesquisa dos dados ou na operação de remover.
    @raise UserNotAuthorizedError: Usuário sem autorização para executar a operação.
    """
    if not has_perm(user,
                    AdminPermission.IPS,
                    AdminPermission.WRITE_OPERATION,
                    None,
                    equipment_id,
                    AdminPermission.EQUIP_WRITE_OPERATION):
        raise UserNotAuthorizedError(
            None, u'Usuário não tem permissão para executar a operação.')

    IpEquipamento().remove(user, ip_id, equipment_id)
    return


class IpResource(RestResource):
    log = logging.getLogger('IpResource')

    def handle_put(self, request, user, *args, **kwargs):
        """Trata as requisições de PUT para inserir o relacionamento entre IP e Equipamento.

        URL: ip/<id_ip>/equipamento/<id_equipamento>/$
        """
        try:

            ip_id = kwargs.get('id_ip')
            equip_id = kwargs.get('id_equipamento')

            if not is_valid_int_greater_zero_param(ip_id):
                self.log.error(
                    u'The ip_id parameter is not a valid value: %s.', ip_id)
                raise InvalidValueError(None, 'ip_id', ip_id)

            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'The equip_id parameter is not a valid value: %s.', equip_id)
                raise InvalidValueError(None, 'equip_id', equip_id)

            Ip.get_by_pk(ip_id)

            with distributedlock(LOCK_IP_EQUIPMENT % (ip_id, equip_id)):

                ip_equipment = insert_ip_equipment(ip_id, equip_id, user)

                ipequipamento_map = dict()
                ipequipamento_map['id'] = ip_equipment.id
                map = dict()
                map['ip_equipamento'] = ipequipamento_map

                return self.response(dumps_networkapi(map))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError:
            return self.response_error(119)
        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)
        except IpEquipamentoDuplicatedError:
            return self.response_error(120)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except (IpError, EquipamentoError, GrupoError):
            return self.response_error(1)

    def handle_post(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para inserir um IP e associá-lo a um equipamento.

        URL: ip/
        """

        try:
            xml_map, attrs_map = loads(request.raw_post_data)
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)

        networkapi_map = xml_map.get('networkapi')
        if networkapi_map is None:
            return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

        ip_map = networkapi_map.get('ip')
        if ip_map is None:
            return self.response_error(3, u'Não existe valor para a tag ip do XML de requisição.')

        try:
            response = insert_ip(ip_map, user)
            if response[0] == 0:
                return self.response(dumps_networkapi({'ip': response[1]}))
            else:
                return self.response_error(response[0])
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except VlanNotFoundError:
            return self.response_error(116)
        except NetworkIPv4NotFoundError, e:
            return self.response_error(281)
        except EquipamentoNotFoundError:
            return self.response_error(117, ip_map.get('id_equipamento'))
        except IpNotAvailableError, e:
            return self.response_error(150, e.message)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except (IpError, VlanError, EquipamentoError, GrupoError), e:
            return self.response_error(1, e)
        except Exception, e:
            return self.response_error(1, e)

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat DELETE requests to remove IP and Equipment relationship.

        URL: ip/<id_ip>/equipamento/<id_equipamento>/$
        """
        try:

            ip_id = kwargs.get('id_ip')
            equip_id = kwargs.get('id_equipamento')

            if not is_valid_int_greater_zero_param(ip_id):
                self.log.error(
                    u'The ip_id parameter is not a valid value: %s.', ip_id)
                raise InvalidValueError(None, 'ip_id', ip_id)

            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'The equip_id parameter is not a valid value: %s.', equip_id)
                raise InvalidValueError(None, 'equip_id', equip_id)

            Ip.get_by_pk(ip_id)
            Equipamento.get_by_pk(equip_id)

            with distributedlock(LOCK_IP_EQUIPMENT % (ip_id, equip_id)):

                ipv4 = Ip.get_by_pk(ip_id)
                equipament = Equipamento.get_by_pk(equip_id)

                # Delete vlan's cache
                destroy_cache_function([ipv4])

                # delete equipment's cache
                destroy_cache_function([equip_id], True)

                server_pool_member_list = ServerPoolMember.objects.filter(
                    ip=ipv4)

                if server_pool_member_list.count() != 0:
                    # IP associated with Server Pool

                    server_pool_name_list = set()

                    for member in server_pool_member_list:
                        item = '{}: {}'.format(
                            member.server_pool.id, member.server_pool.identifier)
                        server_pool_name_list.add(item)

                    server_pool_name_list = list(server_pool_name_list)
                    server_pool_identifiers = ', '.join(server_pool_name_list)

                    raise IpCantRemoveFromServerPool({'ip': mount_ipv4_string(ipv4), 'equip_name': equipament.nome, 'server_pool_identifiers': server_pool_identifiers},
                                                     'Ipv4 não pode ser disassociado do equipamento %s porque ele está sendo utilizando nos Server Pools (id:identifier) %s' % (equipament.nome, server_pool_identifiers))

                remove_ip_equipment(ip_id, equip_id, user)

                return self.response(dumps_networkapi({}))

        except IpCantRemoveFromServerPool, e:
            return self.response_error(385, e.cause.get('ip'), e.cause.get('equip_name'), e.cause.get('server_pool_identifiers'))
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EquipamentoNotFoundError, e:
            return self.response_error(117, e.message)
        except IpEquipmentNotFoundError:
            return self.response_error(118, ip_id, equip_id)
        except IpNotFoundError:
            return self.response_error(119)
        except IpCantBeRemovedFromVip, e:
            return self.response_error(319, 'ip', 'ipv4', ip_id)
        except IpEquipCantDissociateFromVip, e:
            return self.response_error(352, e.cause['ip'], e.cause['equip_name'], e.cause['vip_id'])
        except UserNotAuthorizedError:
            return self.not_authorized()
        except (IpError, GrupoError, EquipamentoError, IntegrityError), e:
            if isinstance(e.cause, IntegrityError):
                # IP associated VIP
                self.log.error(u'Failed to update the request vip.')
                return self.response_error(354, ip_id)
            else:
                return self.response_error(1)

    def handle_get(self, request, user, *args, **kwargs):
        """Treat requests GET to verify that the IP belongs to environment.

        URLs:  /ip/x1.x2.x3.x4/ambiente/<id_amb>
        URLs:  /ip/<ip>/ambiente/<id_amb>
        """

        self.log.info('GET to verify that the IP belongs to environment')

        try:

            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            environment_id = kwargs.get('id_amb')

            # Valid Environment ID
            if not is_valid_int_greater_zero_param(environment_id):
                self.log.error(
                    u'The id_environment parameter is not a valid value: %s.', environment_id)
                raise InvalidValueError(None, 'id_environment', environment_id)

            ip = kwargs.get('ip')

            # Valid IP
            if not is_valid_ipv4(ip):
                self.log.error(u'Parameter ip is invalid. Value: %s.', ip)
                raise InvalidValueError(None, 'ip', ip)

            # Find Environment by ID to check if it exist
            Ambiente.get_by_pk(environment_id)

            # Existing IP
            octs = str(IPAddress(ip, 4).exploded).split('.')
            ip = Ip.get_by_octs_and_environment(
                octs[0], octs[1], octs[2], octs[3], environment_id)

            # Build dictionary return
            ip_map = dict()
            ip_map['id'] = ip.id
            ip_map['id_vlan'] = ip.networkipv4.vlan.id
            ip_map['oct4'] = ip.oct4
            ip_map['oct3'] = ip.oct3
            ip_map['oct2'] = ip.oct2
            ip_map['oct1'] = ip.oct1
            ip_map['descricao'] = ip.descricao

            return self.response(dumps_networkapi({'ip': ip_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except IpNotFoundError:
            return self.response_error(119)
        except AmbienteNotFoundError:
            return self.response_error(112)
        except (IpError, GrupoError):
            return self.response_error(1)
