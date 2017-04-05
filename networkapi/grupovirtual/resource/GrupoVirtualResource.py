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

from networkapi.ambiente.models import EnvironmentVip
from networkapi.api_vip_request.syncs import old_to_new
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_GROUP_VIRTUAL
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNameDuplicatedError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.equipamento.models import InvalidGroupToEquipmentTypeError
from networkapi.equipamento.models import ModeloNotFoundError
from networkapi.equipamento.models import TipoEquipamentoNotFoundError
from networkapi.equipamento.resource.EquipamentoResource import insert_equipment
from networkapi.equipamento.resource.EquipamentoResource import remove_equipment
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import EGrupoNotFoundError
from networkapi.grupo.models import GrupoError
from networkapi.healthcheckexpect.models import HealthcheckExpectError
from networkapi.healthcheckexpect.models import HealthcheckExpectNotFoundError
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.script_utils import ScriptError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import IpEquipamentoDuplicatedError
from networkapi.ip.models import IpEquipmentNotFoundError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import IpNotFoundByEquipAndVipError
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.resource.IpResource import insert_ip
from networkapi.ip.resource.IpResource import insert_ip_equipment
from networkapi.ip.resource.IpResource import remove_ip_equipment
from networkapi.requisicaovips.models import EnvironmentVipNotFoundError
from networkapi.requisicaovips.models import InvalidAmbienteValueError
from networkapi.requisicaovips.models import InvalidBalAtivoValueError
from networkapi.requisicaovips.models import InvalidCacheValueError
from networkapi.requisicaovips.models import InvalidClienteValueError
from networkapi.requisicaovips.models import InvalidFinalidadeValueError
from networkapi.requisicaovips.models import InvalidHealthcheckTypeValueError
from networkapi.requisicaovips.models import InvalidHealthcheckValueError
from networkapi.requisicaovips.models import InvalidHostNameError
from networkapi.requisicaovips.models import InvalidMaxConValueError
from networkapi.requisicaovips.models import InvalidMetodoBalValueError
from networkapi.requisicaovips.models import InvalidPersistenciaValueError
from networkapi.requisicaovips.models import InvalidRealValueError
from networkapi.requisicaovips.models import InvalidServicePortValueError
from networkapi.requisicaovips.models import InvalidTimeoutValueError
from networkapi.requisicaovips.models import InvalidTransbordoValueError
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsError
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.requisicaovips.resource.RequisicaoVipsResource import insert_vip_request
from networkapi.requisicaovips.resource.RequisicaoVipsResource import update_vip_request
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.settings import VIP_REMOVE
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanNotFoundError


class GroupVirtualResource(RestResource):

    log = logging.getLogger('GroupVirtualResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """Trata as requisições de PUT para remover um grupo virtual.

        URL: /grupovirtual/
        """

        try:
            xml_map, attrs_map = loads(
                request.raw_post_data, ['vip', 'equipamento', 'id_equipamento'])
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)

        networkapi_map = xml_map.get('networkapi')
        if networkapi_map is None:
            return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

        vips_map = networkapi_map.get('vips')

        try:
            equipments_map = networkapi_map['equipamentos']
        except KeyError:
            return self.response_error(3, u'XML de requisição inválido.')

        try:

            with distributedlock(LOCK_GROUP_VIRTUAL):

                # Vips
                if vips_map is not None:
                    try:
                        vip_maps = vips_map['vip']
                        for vip_map in vip_maps:
                            balanceadores_map = vip_map['balanceadores']
                            if balanceadores_map is None:
                                return self.response_error(3, u'Valor da tag balanceadores do XML de requisição inválido.')

                            ip_id = vip_map['id_ip']
                            try:
                                ip_id = int(ip_id)
                            except (TypeError, ValueError), e:
                                self.log.error(
                                    u'Valor do id_ip inválido: %s.', ip_id)
                                raise IpNotFoundError(
                                    e, u'Valor do id_ip inválido: %s.' % ip_id)

                            vip_s = RequisicaoVips.get_by_ipv4_id(ip_id)
                            # Run scripts to remove vips
                            for vip in vip_s:
                                # Make command
                                command = VIP_REMOVE % (vip.id)
                                # Execute command
                                code, stdout, stderr = exec_script(command)
                                if code == 0:
                                    vip.vip_criado = 0
                                    vip.save()

                                    # SYNC_VIP
                                    old_to_new(vip)
                                else:
                                    return self.response_error(2, stdout + stderr)

                            equipment_ids = balanceadores_map['id_equipamento']
                            for equip_id in equipment_ids:
                                try:
                                    equip_id = int(equip_id)
                                except (TypeError, ValueError), e:
                                    self.log.error(
                                        u'Valor do id_equipamento inválido: %s.', equip_id)
                                    raise EquipamentoNotFoundError(
                                        e, u'Valor do id_equipamento inválido: %s.' % equip_id)

                                remove_ip_equipment(ip_id, equip_id, user)
                    except KeyError:
                        return self.response_error(3, u'Valor das tags vips/vip do XML de requisição inválido.')

                # Equipamentos
                if equipments_map is not None:
                    try:
                        equipment_maps = equipments_map['equipamento']

                        for equipment_map in equipment_maps:
                            equip_id = equipment_map['id']
                            try:
                                equip_id = int(equip_id)
                            except (TypeError, ValueError), e:
                                self.log.error(
                                    u'Valor do id do equipamento inválido: %s.', equip_id)
                                raise EquipamentoNotFoundError(
                                    e, u'Valor do id do equipamento inválido: %s.' % equip_id)

                            remove_equipment(equip_id, user)
                    except KeyError:
                        return self.response_error(3, u'Valor das tags equipamentos/equipamento do XML de requisição inválido.')

                return self.response(dumps_networkapi({}))

        except IpNotFoundError:
            return self.response_error(119)
        except IpEquipmentNotFoundError:
            return self.response_error(118, ip_id, equip_id)
        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except ScriptError, s:
            return self.response_error(2, s)
        except (IpError, EquipamentoError, GrupoError, RequisicaoVipsError) as e:
            self.log.error(e)
            return self.response_error(1)

    def __treat_response_error(self, response):
        """Trata as repostas de erro no formato de uma tupla.

        Formato da tupla:
             (<codigo da mensagem de erro>, <argumento 01 da mensagem>, <argumento 02 da mensagem>, ...)

        @return: HttpResponse com a mensagem de erro.
        """
        if len(response) > 1:
            return self.response_error(response[0], response[1:len(response)])
        return self.response_error(response[0])

    def __post_virtual_group_equipment(self, equipment_maps, vip_maps, user, resp_equipment_maps, vip_equipment_ip_map):
        try:
            for equipment_map in equipment_maps:
                equipment_prefixo = equipment_map.get('prefixo')
                if equipment_prefixo is None:
                    return self.response_error(105)

                name = Equipamento.get_next_name_by_prefix(equipment_prefixo)
                equipment_map['nome'] = name

                response = insert_equipment(equipment_map, user)
                if response[0] == 0:
                    equip_id = response[2].id

                    ip_map = equipment_map.get('ip')
                    if ip_map is None:
                        return self.response_error(3, u'Não existe valor para a tag ip do equipamento %s do XML de requisição.' % equipment_map.get('nome'))

                    ip_map['id_equipamento'] = equip_id

                    response_ip = insert_ip(ip_map, user)
                    if response_ip[0] == 0:

                        # Insere um IP para cada VIP e o relacionamento dele
                        # com equipamento
                        resp_vip_maps = []
                        for vip_map in vip_maps:
                            ip_vip_map = vip_map.get('ip_real', dict())
                            ip_vip_map['id_equipamento'] = equip_id

                            response_ip_vip = insert_ip(ip_vip_map, user)
                            if (response_ip_vip[0] == 0):
                                resp_vip_maps.append({'id': vip_map.get('id'),
                                                      'ip': response_ip_vip[1]})

                                ip = str(response_ip_vip[1].get('oct1')) + '.' + str(response_ip_vip[1].get('oct2')) + '.' + str(
                                    response_ip_vip[1].get('oct3')) + '.' + str(response_ip_vip[1].get('oct4'))

                                equipment_ip_map = {
                                    'ip': ip, 'nome_equipamento': equipment_map.get('nome')}

                                equipment_ip_maps = vip_equipment_ip_map.get(
                                    vip_map.get('id'))
                                if equipment_ip_maps is None:
                                    equipment_ip_maps = [equipment_ip_map]
                                else:
                                    equipment_ip_maps.append(equipment_ip_map)

                                vip_equipment_ip_map[
                                    vip_map.get('id')] = equipment_ip_maps
                            else:
                                return self.__treat_response_error(response_ip_vip)

                        resp_equipment_maps.append({'id': equip_id,
                                                    'nome': name,
                                                    'ip': response_ip[1],
                                                    'vips': {'vip': resp_vip_maps}})

                    else:
                        return self.__treat_response_error(response_ip)
                else:
                    return self.__treat_response_error(response)

        except InvalidGroupToEquipmentTypeError:
            return self.response_error(107)
        except TipoEquipamentoNotFoundError:
            return self.response_error(100)
        except ModeloNotFoundError:
            return self.response_error(101)
        except EquipamentoNameDuplicatedError:
            return self.response_error(149)
        except EGrupoNotFoundError:
            return self.response_error(102)

        return

    def __post_virtual_group_vip(self, vip_maps, user, vip_equipment_ip_map, resp_vip_maps):
        try:
            for vip_map in vip_maps:
                resp_vip_map = dict()

                vip_id = vip_map.get('id')

                resp_vip_map['id'] = vip_id

                id_vip_request_map = vip_map.get('requisicao_vip')

                ip_map = vip_map.get('ip')

                # Somente insere o IP do VIP se a requisição de VIP ainda não foi criada
                # (id_vip_request_map is None).

                if (ip_map is not None) and (id_vip_request_map is None):

                    # Insere o IP do VIP e o associa aos balanceadores

                    balanceadores_map = vip_map.get('balanceadores')
                    if balanceadores_map is None:
                        return self.response_error(3, u'Não existe valor para a tag balanceadors do vip %s do XML de requisição.' % vip_id)

                    equipments_ids = balanceadores_map.get('id_equipamento')
                    if len(equipments_ids) == 0:
                        return self.response_error(3, u'Não existe valor para a tag id_equipamento do vip %s do XML de requisição.' % vip_id)

                    # Insere um IP e o relacionamento dele com o primeiro
                    # balanceador
                    equip_id = equipments_ids[0]
                    ip_map['id_equipamento'] = equip_id
                    response_ip = insert_ip(ip_map, user)
                    if response_ip[0] != 0:
                        return self.__treat_response_error(response_ip)

                    # Insere o relacionamento entre o IP e os demais
                    # balanceadores
                    for equip_id in equipments_ids[1:len(equipments_ids)]:
                        insert_ip_equipment(
                            response_ip[1].get('id'), equip_id, user)

                    resp_vip_map['ip'] = response_ip[1]

                    vip_map['id_ip'] = response_ip[1].get('id')

                # Constroe o reals

                # Obtem os reals já criados e que foram enviados no XML de
                # requisição
                reals_map = vip_map.get('reals')
                if reals_map is not None:
                    real_maps = reals_map.get('real', [])
                else:
                    real_maps = []

                # Adiciona os novos reals para os equipamentos criados
                equipment_ip_maps = vip_equipment_ip_map.get(vip_id)
                if equipment_ip_maps is not None:
                    for equipment_ip_map in equipment_ip_maps:
                        real_name = equipment_ip_map.get(
                            'nome_equipamento')  # + sufix
                        real_ip = equipment_ip_map.get('ip')
                        real_maps.append(
                            {'real_name': real_name, 'real_ip': real_ip})

                vip_map['reals'] = {'real': real_maps}

                reals_priority_map = vip_map.get('reals_prioritys')
                if reals_priority_map is not None:
                    reals_priority_map = reals_priority_map.get(
                        'reals_priority')
                    if reals_priority_map is None:
                        reals_priority_map = ['0' for __real in real_maps]
                else:
                    reals_priority_map = ['0' for __real in real_maps]

                vip_map['reals_prioritys'] = {
                    'reals_priority': reals_priority_map}

                reals_weight_map = vip_map.get('reals_weights')
                if reals_weight_map is not None:
                    reals_weight_map = reals_weight_map.get('reals_weight')
                    if reals_weight_map is None:
                        reals_weight_map = ['0' for __real in real_maps]
                else:
                    reals_weight_map = ['0' for __real in real_maps]

                vip_map['reals_weights'] = {'reals_weight': reals_weight_map}

                # Valid real names and real ips of real server
                if vip_map.get('reals') is not None:

                    evip = EnvironmentVip.get_by_values(
                        vip_map.get('finalidade'), vip_map.get('cliente'), vip_map.get('ambiente'))

                    for real in vip_map.get('reals').get('real'):
                        ip_aux_error = real.get('real_ip')
                        equip_id = real.get('real_name')
                        if equip_id is not None:
                            equip = Equipamento.get_by_name(equip_id)
                        else:
                            self.log.error(
                                u'The real_name parameter is not a valid value: None.')
                            raise InvalidValueError(None, 'real_name', 'None')

                        # Valid Real
                        RequisicaoVips.valid_real_server(
                            ip_aux_error, equip, evip, False)

                        vip_map, code = RequisicaoVips().valid_values_reals_priority(
                            vip_map)
                        if code is not None:
                            return self.response_error(code)

                        vip_map, code = RequisicaoVips().valid_values_reals_weight(
                            vip_map)
                        if code is not None:
                            return self.response_error(code)

                # Insere ou atualiza a requisição de VIP
                if (id_vip_request_map is not None):

                    resp_vip_map['requisicao_vip'] = id_vip_request_map

                    if not is_valid_int_greater_zero_param(id_vip_request_map.get('id')):
                        self.log.error(
                            u'The requisicao_vip.id parameter is not a valid value: %s.', id_vip_request_map.get('id'))
                        raise InvalidValueError(
                            None, 'requisicao_vip.id', id_vip_request_map.get('id'))

                    vip_request = RequisicaoVips.get_by_pk(
                        id_vip_request_map.get('id'))

                    vip_map['id_ip'] = vip_request.ip_id
                    if vip_request.validado:
                        vip_map['validado'] = '1'
                    else:
                        vip_map['validado'] = '0'
                    if vip_request.vip_criado:
                        vip_map['vip_criado'] = '1'
                    else:
                        vip_map['vip_criado'] = '0'

                    response_vip = update_vip_request(
                        vip_request.id, vip_map, user)
                    if (response_vip != 0):
                        return self.response_error(response_vip)

                else:
                    """This condition is used to attend a requisite from 'Orquestra',
                       because in some points the VIP doesn't have cache option and
                       the value can be 'None'"""
                    if vip_map['cache'] is None:
                        vip_map['cache'] = '(nenhum)'

                    response_vip = insert_vip_request(vip_map, user)
                    if (response_vip[0] != 0):
                        if response_vip[0] not in (275, 276, 277):
                            return self.__treat_response_error(response_vip)
                        else:
                            return self.__treat_response_error([response_vip[0]])

                    resp_vip_map['requisicao_vip'] = {'id': response_vip[1].id}

                resp_vip_maps.append(resp_vip_map)

        except EnvironmentVipNotFoundError:
            return self.response_error(316, vip_map['finalidade'], vip_map['cliente'], vip_map['ambiente'])
        except RequisicaoVipsNotFoundError:
            return self.response_error(152)
        except HealthcheckExpectNotFoundError:
            return self.response_error(124)
        except InvalidFinalidadeValueError:
            return self.response_error(125)
        except InvalidClienteValueError:
            return self.response_error(126)
        except InvalidAmbienteValueError:
            return self.response_error(127)
        except InvalidCacheValueError:
            return self.response_error(128)
        except InvalidMetodoBalValueError:
            return self.response_error(131)
        except InvalidPersistenciaValueError:
            return self.response_error(132)
        except InvalidHealthcheckTypeValueError:
            return self.response_error(133)
        except InvalidHealthcheckValueError:
            return self.response_error(134)
        except InvalidTimeoutValueError:
            return self.response_error(135)
        except InvalidHostNameError:
            return self.response_error(136)
        except InvalidMaxConValueError:
            return self.response_error(137)
        except InvalidBalAtivoValueError:
            return self.response_error(129)
        except InvalidTransbordoValueError, t:
            transbordo = 'nulo'
            if t.message is not None:
                transbordo = t.message
            return self.response_error(130, transbordo)
        except InvalidServicePortValueError, s:
            porta = 'nulo'
            if s.message is not None:
                porta = s.message
            return self.response_error(138, porta)
        except InvalidRealValueError, r:
            real = 'nulo'
            if r.message is not None:
                real = r.message
            return self.response_error(151, real)
        except IpNotFoundError:
            return self.response_error(119)
        except IpEquipamentoDuplicatedError:
            return self.response_error(120)
        except EquipamentoNotFoundError:
            return self.response_error(117, equip_id)
        except IpNotFoundByEquipAndVipError:
            return self.response_error(334)

        return

    def handle_post(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para inserir um Grupo Virtual.

        URL: /grupovirtual/
        """

        try:
            xml_map, attrs_map = loads(request.raw_post_data, [
                                       'vip', 'equipamento', 'id_equipamento', 'reals_weight', 'reals_priority', 'real', 'transbordo', 'porta'])
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisicao.')
            return self.response_error(3, x)

        self.log.debug('XML_MAP: %s', xml_map)

        networkapi_map = xml_map.get('networkapi')
        if networkapi_map is None:
            return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

        equipments_map = networkapi_map.get('equipamentos')
        if equipments_map is None:
            return self.response_error(3, u'Não existe valor para a tag equipamentos do XML de requisição.')

        equipment_maps = equipments_map.get('equipamento')
        if len(equipment_maps) == 0:
            return self.response_error(3, u'Não existe valor para a tag equipamento do XML de requisição.')

        vips_map = networkapi_map.get('vips')
        if vips_map is not None:
            vip_maps = vips_map.get('vip')
        else:
            vip_maps = []

        try:

            with distributedlock(LOCK_GROUP_VIRTUAL):

                # for nos equipamentos
                resp_equipment_maps = []
                vip_equipment_ip_map = dict()
                response = self.__post_virtual_group_equipment(
                    equipment_maps, vip_maps, user, resp_equipment_maps, vip_equipment_ip_map)
                if response is not None:
                    return response

                # for nos vips
                resp_vip_maps = []
                response = self.__post_virtual_group_vip(
                    vip_maps, user, vip_equipment_ip_map, resp_vip_maps)
                if response is not None:
                    return response

                # Mapa final
                map = dict()
                map['equipamentos'] = {'equipamento': resp_equipment_maps}
                map['vips'] = {'vip': resp_vip_maps}
                return self.response(dumps_networkapi(map))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except VlanNotFoundError:
            return self.response_error(116)
        except IpNotAvailableError, e:
            return self.response_error(150, e)
        except (IpError, VlanError, EquipamentoError, GrupoError, RequisicaoVipsError, HealthcheckExpectError):
            return self.response_error(1)
