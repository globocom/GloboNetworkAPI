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
# from _ast import For
import logging

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import EnvironmentVip
from networkapi.api_vip_request.syncs import old_to_new
from networkapi.auth import has_perm
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.healthcheckexpect.models import HealthcheckExpectError
from networkapi.healthcheckexpect.models import HealthcheckExpectNotFoundError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotFoundByEquipAndVipError
from networkapi.ip.models import IpNotFoundError
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
from networkapi.requisicaovips.models import OptionVip
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsAlreadyCreatedError
from networkapi.requisicaovips.models import RequisicaoVipsError
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import convert_boolean_to_int
from networkapi.util import is_valid_int_greater_equal_zero_param
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
# from django.forms.models import model_to_dict


def insert_vip_request(vip_map, user):
    """Insere uma requisição de VIP.

    @param vip_map: Mapa com os dados da requisição.
    @param user: Usuário autenticado.

    @return: Em caso de sucesso: tupla (0, <requisição de VIP>).
             Em caso de erro: tupla (código da mensagem de erro, argumento01, argumento02, ...)

    @raise IpNotFoundError: IP não cadastrado.

    @raise IpError: Falha ao pesquisar o IP.

    @raise HealthcheckExpectNotFoundError: HealthcheckExpect não cadastrado.

    @raise HealthcheckExpectError: Falha ao pesquisar o HealthcheckExpect.

    @raise InvalidFinalidadeValueError: Finalidade com valor inválido.

    @raise InvalidClienteValueError: Cliente com valor inválido.

    @raise InvalidAmbienteValueError: Ambiente com valor inválido.

    @raise InvalidCacheValueError: Cache com valor inválido.

    @raise InvalidMetodoBalValueError: Valor do método de balanceamento inválido.

    @raise InvalidPersistenciaValueError: Persistencia com valor inválido.

    @raise InvalidHealthcheckTypeValueError: Healthcheck_Type com valor inválido ou inconsistente em relação ao valor do healthcheck_expect.

    @raise InvalidTimeoutValueError: Timeout com valor inválido.

    @raise InvalidHostNameError: Host não cadastrado.

    @raise EquipamentoError: Falha ao pesquisar o equipamento.

    @raise InvalidMaxConValueError: Número máximo de conexões com valor inválido.

    @raise InvalidBalAtivoValueError: Bal_Ativo com valor inválido.

    @raise InvalidTransbordoValueError: Transbordo com valor inválido.

    @raise InvalidServicePortValueError: Porta do Serviço com valor inválido.

    @raise InvalidRealValueError: Valor inválido de um real.

    @raise InvalidHealthcheckValueError: Valor do healthcheck inconsistente em relação ao valor do healthcheck_type.

    @raise RequisicaoVipsError: Falha ao inserir a requisição de VIP.

    @raise UserNotAuthorizedError:
    """

    log = logging.getLogger('insert_vip_request')

    if not has_perm(user, AdminPermission.VIPS_REQUEST, AdminPermission.WRITE_OPERATION):
        raise UserNotAuthorizedError(
            None, u'Usuário não tem permissão para executar a operação.')

    ip_id = vip_map.get('id_ip')
    if not is_valid_int_greater_zero_param(ip_id):
        log.error(u'The ip_id parameter is not a valid value: %s.', ip_id)
        raise InvalidValueError(None, 'ip_id', ip_id)
    else:
        ip_id = int(ip_id)

    vip = RequisicaoVips()
    vip.ip = Ip()
    vip.ip.id = ip_id

    # Valid ports
    vip_map, code = vip.valid_values_ports(vip_map)
    if code is not None:
        return code, vip

    # get environmentVip for validation dynamic heathcheck

    finalidade = vip_map.get('finalidade')
    cliente = vip_map.get('cliente')
    ambiente = vip_map.get('ambiente')

    if not is_valid_string_minsize(finalidade, 3) or not is_valid_string_maxsize(finalidade, 50):
        log.error(u'Finality value is invalid: %s.', finalidade)
        raise InvalidValueError(None, 'finalidade', finalidade)

    if not is_valid_string_minsize(cliente, 3) or not is_valid_string_maxsize(cliente, 50):
        log.error(u'Client value is invalid: %s.', cliente)
        raise InvalidValueError(None, 'cliente', cliente)

    if not is_valid_string_minsize(ambiente, 3) or not is_valid_string_maxsize(ambiente, 50):
        log.error(u'Environment value is invalid: %s.', ambiente)
        raise InvalidValueError(None, 'ambiente', ambiente)

    try:
        environment_vip = EnvironmentVip.get_by_values(
            finalidade, cliente, ambiente)
    except Exception, e:
        raise EnvironmentVipNotFoundError(
            e, 'The fields finality or client or ambiente is None')

    # Valid HealthcheckExpect
    vip_map, vip, code = vip.valid_values_healthcheck(
        vip_map, vip, environment_vip)
    if code is not None:
        return code, vip

    # get traffic return
    # traffic_return=OptionVip.objects.filter(nome_opcao_txt=traffic)
    traffic_id = vip_map.get('trafficreturn')
    if traffic_id is None:
        traffic = OptionVip.get_all_trafficreturn(environment_vip.id)
        traffic = traffic.filter(nome_opcao_txt='Normal')
        traffic_id = traffic.id
    vip.trafficreturn = OptionVip()
    vip.trafficreturn.id = traffic_id

    # Valid maxcon
    if not is_valid_int_greater_equal_zero_param(vip_map.get('maxcon')):
        log.error(
            u'The maxcon parameter is not a valid value: %s.', vip_map.get('maxcon'))
        raise InvalidValueError(None, 'maxcon', vip_map.get('maxcon'))

    if vip_map.get('reals') is not None:

        for real in vip_map.get('reals').get('real'):
            ip_aux_error = real.get('real_ip')
            equip_aux_error = real.get('real_name')

            if equip_aux_error is not None:
                equip = Equipamento.get_by_name(equip_aux_error)
            else:
                raise InvalidValueError(None, 'real_name', 'None')

            RequisicaoVips.valid_real_server(
                ip_aux_error, equip, environment_vip)

    vip.create(user, vip_map)

    # SYNC_VIP
    old_to_new(vip)

    return 0, vip


def update_vip_request(vip_id, vip_map, user):

    log = logging.getLogger('update_vip_request')

    if not has_perm(user,
                    AdminPermission.VIPS_REQUEST,
                    AdminPermission.WRITE_OPERATION):
        raise UserNotAuthorizedError(
            None, u'Usuário não tem permissão para executar a operação.')

    healthcheck_expect_id = vip_map.get('id_healthcheck_expect')
    if healthcheck_expect_id is not None:
        if not is_valid_int_greater_zero_param(healthcheck_expect_id):
            log.error(
                u'The healthcheck_expect_id parameter is not a valid value: %s.', healthcheck_expect_id)
            raise InvalidValueError(
                None, 'healthcheck_expect_id', healthcheck_expect_id)
        else:
            healthcheck_expect_id = int(healthcheck_expect_id)

    ip_id = vip_map.get('id_ip')
    if not is_valid_int_greater_zero_param(ip_id):
        log.error(u'The ip_id parameter is not a valid value: %s.', ip_id)
        raise InvalidValueError(None, 'ip_id', ip_id)
    else:
        ip_id = int(ip_id)

    traffic_id = vip_map.get('trafficreturn')
    if not is_valid_int_greater_zero_param(traffic_id):
        log.error(u'The traffic_id parameter is not a valid value: %s.', traffic_id)
        raise InvalidValueError(None, 'trafficreturn', traffic_id)
    else:
        traffic_id = int(traffic_id)

    validated = vip_map.get('validado')
    if validated is None:
        return 246
    if validated == '0':
        validated = False
    elif validated == '1':
        validated = True
    else:
        return 244

    vip_created = vip_map.get('vip_criado')
    if vip_created is None:
        return 247
    if vip_created == '0':
        vip_created = False
    elif vip_created == '1':
        vip_created = True
    else:
        return 245

    # Valid maxcon
    if not is_valid_int_greater_equal_zero_param(vip_map.get('maxcon')):
        log.error(
            u'The maxcon parameter is not a valid value: %s.', vip_map.get('maxcon'))
        raise InvalidValueError(None, 'maxcon', vip_map.get('maxcon'))

    code = RequisicaoVips.update(user,
                                 vip_id,
                                 vip_map,
                                 healthcheck_expect_id=healthcheck_expect_id,
                                 ip_id=ip_id,
                                 vip_criado=vip_created,
                                 validado=validated,
                                 traffic_return_id=traffic_id)

    if code is not None:
        return code

    # SYNC_VIP
    vip = RequisicaoVips.get_by_pk(vip_id)
    old_to_new(vip)

    return 0


class RequisicaoVipsResource(RestResource):

    log = logging.getLogger('RequisicaoVipsResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Trata as requisições de POST para inserir uma requisição de VIP."""

        try:
            xml_map, attrs_map = loads(
                request.raw_post_data, ['transbordo', 'porta', 'real'])
        except XMLError, x:
            self.log.error(u'Erro ao ler o XML da requisição.')
            return self.response_error(3, x)

        networkapi_map = xml_map.get('networkapi')
        if networkapi_map is None:
            return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

        vip_map = networkapi_map.get('vip')
        if vip_map is None:
            return self.response_error(3, u'Não existe valor para a tag vip do XML de requisição.')

        try:
            response = insert_vip_request(vip_map, user)
            if (response[0] == 0):

                vip_map = dict()
                vip_map['id'] = response[1].id

                return self.response(dumps_networkapi({'requisicao_vip': vip_map}))
            else:
                return self.response_error(response[0])

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except EnvironmentVipNotFoundError:
            return self.response_error(316, vip_map['finalidade'], vip_map['cliente'], vip_map['ambiente'])
        except IpNotFoundError:
            return self.response_error(119)
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
        except UserNotAuthorizedError:
            return self.not_authorized()
        except (RequisicaoVipsError, EquipamentoError, IpError, HealthcheckExpectError, GrupoError):
            return self.response_error(1)
        except IpNotFoundByEquipAndVipError, e:
            return self.response_error(334, e.message)

    def handle_get(self, request, user, *args, **kwargs):
        """Trata as requisições de GET para listar uma requisição de VIP.

        Filtra a requisição de VIP por chave primária.

        URL: vip/id_vip
        """

        try:
            if kwargs.get('id_vip') is None:
                return super(RequisicaoVipsResource, self).handle_get(request, user, *args, **kwargs)

            if not has_perm(user,
                            AdminPermission.VIPS_REQUEST,
                            AdminPermission.READ_OPERATION):
                return self.not_authorized()

            # Valid Ip ID
            if not is_valid_int_greater_zero_param(kwargs.get('id_vip')):
                self.log.error(
                    u'The id_vip parameter is not a valid value: %s.', kwargs.get('id_vip'))
                raise InvalidValueError(None, 'id_vip', kwargs.get('id_vip'))

            request_vip = RequisicaoVips.get_by_pk(kwargs.get('id_vip'))

            request_vip_map = request_vip.variables_to_map()

            """"""
            vip_port_list, reals_list, reals_priority, reals_weight = request_vip.get_vips_and_reals(
                request_vip.id)

            if reals_list:
                request_vip_map['reals'] = {'real': reals_list}
                request_vip_map['reals_prioritys'] = {
                    'reals_priority': reals_priority}
                request_vip_map['reals_weights'] = {
                    'reals_weight': reals_weight}

            request_vip_map['portas_servicos'] = {'porta': vip_port_list}

            """"""

            request_vip_map['id'] = request_vip.id
            request_vip_map['validado'] = convert_boolean_to_int(
                request_vip.validado)
            request_vip_map['vip_criado'] = convert_boolean_to_int(
                request_vip.vip_criado)
            request_vip_map['id_ip'] = request_vip.ip_id
            request_vip_map['id_ipv6'] = request_vip.ipv6_id
            request_vip_map[
                'id_healthcheck_expect'] = request_vip.healthcheck_expect_id
            request_vip_map['l7_filter'] = request_vip.l7_filter
            request_vip_map['rule_id'] = request_vip.rule_id

            return self.response(dumps_networkapi({'vip': request_vip_map}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except (RequisicaoVipsNotFoundError):
            return self.response_error(152)
        except (RequisicaoVipsError, GrupoError):
            return self.response_error(1)

    def __update_vip(self, vip_id, request, user):
        try:
            try:
                xml_map, attrs_map = loads(
                    request.raw_post_data, ['transbordo', 'porta', 'real'])
            except XMLError, x:
                self.log.error(u'Erro ao ler o XML da requisição.')
                return self.response_error(3, x)

            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                return self.response_error(3, u'Não existe valor para a tag networkapi do XML de requisição.')

            vip_map = networkapi_map.get('vip')
            if vip_map is None:
                return self.response_error(3, u'Não existe valor para a tag vip do XML de requisição.')

            response = update_vip_request(vip_id, vip_map, user)
            if (response != 0):
                return self.response_error(response)

            return self.response(dumps_networkapi({}))

        except UserNotAuthorizedError:
            return self.not_authorized()
        except IpNotFoundError:
            return self.response_error(119)
        except EnvironmentVipNotFoundError:
            return self.response_error(316, vip_map['finalidade'], vip_map['cliente'], vip_map['ambiente'])
        except RequisicaoVipsAlreadyCreatedError:
            return self.response_error(186, vip_id)
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

    def handle_put(self, request, user, *args, **kwargs):
        """Trata as requisições de PUT para atualizar/criar uma requisição de VIP.

        URLs: vip/<id_vip>/
        """
        try:
            vip_id = kwargs.get('id_vip')

            if not is_valid_int_greater_zero_param(vip_id):
                self.log.error(
                    u'The vip_id parameter is not a valid value: %s.', vip_id)
                raise InvalidValueError(None, 'vip_id', vip_id)

            if not has_perm(user,
                            AdminPermission.VIPS_REQUEST,
                            AdminPermission.WRITE_OPERATION):
                return self.not_authorized()

            return self.__update_vip(vip_id, request, user)

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except (RequisicaoVipsNotFoundError):
            return self.response_error(152)
        except (RequisicaoVipsError, GrupoError, HealthcheckExpectError, EquipamentoError, IpError):
            return self.response_error(1)
