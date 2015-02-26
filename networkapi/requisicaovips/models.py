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
from django.db import models
from django.db.models.fields import NullBooleanField
from networkapi.log import Log
from networkapi.healthcheckexpect.models import HealthcheckExpect
from networkapi.ip.models import Ip, Ipv6, IpNotFoundByEquipAndVipError
from networkapi.ambiente.models import EnvironmentVip, IP_VERSION, Ambiente
from django.core.exceptions import ObjectDoesNotExist
from _mysql_exceptions import OperationalError
from networkapi.log import Log
from networkapi.models.BaseModel import BaseModel
import re
from string import upper
from networkapi.util import is_valid_ip, is_valid_int_greater_equal_zero_param, is_valid_int_greater_zero_param, is_valid_string_maxsize, is_valid_string_minsize, is_valid_option, is_valid_regex, is_valid_ipv6, is_valid_ipv4, \
    mount_ipv4_string, mount_ipv6_string
from networkapi.exception import InvalidValueError, OptionVipError, OptionVipNotFoundError, OptionVipEnvironmentVipError, OptionVipEnvironmentVipNotFoundError, OptionVipEnvironmentVipDuplicatedError, \
    EnvironmentVipNotFoundError
from networkapi.healthcheckexpect.models import HealthcheckExpectNotFoundError
from networkapi.distributedlock import distributedlock, LOCK_VIP
from networkapi.healthcheckexpect.models import Healthcheck


class RequisicaoVipsError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com requisicao_vips."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class VipRequestBlockAlreadyInRule(RequisicaoVipsError):

    """Retorna exceção ao tentar inserir um bloco que já existe na regra do Vip."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class VipRequestNoBlockInRule(RequisicaoVipsError):

    """Retorna exceção ao buscar a regra associada a requisição vip."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class RequisicaoVipsNotFoundError(RequisicaoVipsError):

    """Retorna exceção ao pesquisar a requisição de vip por chave primária."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class RequisicaoVipsAlreadyCreatedError(RequisicaoVipsError):

    """Retorna exceção ao tentar alterar uma requisição de vip já criada."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidFinalidadeValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável finalidade é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidClienteValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável cliente é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidAmbienteValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável ambiente é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidTimeoutValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável timeout é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidCacheValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável cache é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidMetodoBalValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável metodo_bal é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidPersistenciaValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável persistencia é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidHealthcheckTypeValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável healthcheck_type é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidMaxConValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável maxcon é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidBalAtivoValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável bal_ativo é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidTransbordoValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável transbordo é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidServicePortValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável porta do serviço é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidRealValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável real é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidHealthcheckValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável healthcheck é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidHostNameError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável host é inválido."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidPriorityValueError(RequisicaoVipsError):

    """Returns exception when the value of the priority variable is invalid."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidWeightValueError(RequisicaoVipsError):

    """Returns exception when the value of the weight variable is invalid."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class RequisicaoVips(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id_requisicao_vips'
    )

    validado = models.BooleanField()

    variaveis = models.TextField(
        blank=True
    )

    vip_criado = models.BooleanField()

    ip = models.ForeignKey(
        Ip,
        db_column='ips_id_ip',
        blank=True,
        null=True
    )

    ipv6 = models.ForeignKey(
        Ipv6,
        db_column='ipsv6_id_ipv6',
        blank=True,
        null=True
    )

    l7_filter = models.TextField(
        blank=True,
        null=True,
        db_column='l7_filter_to_apply'
    )

    filter_applied = models.TextField(
        blank=True,
        null=True,
        db_column='l7_filter_current'
    )

    filter_rollback = models.TextField(
        blank=True,
        null=True,
        db_column='l7_filter_rollback'
    )

    filter_valid = models.BooleanField(
        db_column='l7_filter_is_valid'
    )

    applied_l7_datetime = models.DateTimeField(
        db_column='l7_filter_applied_datetime'
    )

    healthcheck_expect = models.ForeignKey(
        HealthcheckExpect,
        null=True,
        db_column='id_healthcheck_expect',
        blank=True
    )

    rule = models.ForeignKey(
        'blockrules.Rule',
        db_column='id_rule',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='rule'
    )

    rule_applied = models.ForeignKey(
        'blockrules.Rule',
        db_column='id_rule_current',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='rule_applied'
    )

    rule_rollback = models.ForeignKey(
        'blockrules.Rule',
        db_column='id_rule_rollback',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='rule_rollback'
    )

    log = Log('RequisicaoVips')

    class Meta(BaseModel.Meta):
        db_table = u'requisicao_vips'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get Request Vip by id.

            @return: Request Vip.

            @raise RequisicaoVipsNotFoundError: Request Vip is not registered.
            @raise RequisicaoVipsError: Failed to search for the Request Vip.
            @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return RequisicaoVips.objects.get(id=id)
        except ObjectDoesNotExist, e:
            raise RequisicaoVipsNotFoundError(
                e, u'Dont there is a request of vips by pk = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the request vip.')
            raise RequisicaoVipsError(e, u'Failure to search the request vip.')

    @classmethod
    def remove(cls, authenticated_user, vip_id):
        '''Pesquisa e remove uma Requisicao VIP.

        @return: Nothing

        @raise RequisicaoVipsNotFoundError: Requisao VIP não cadastrado.

        @raise RequisicaoVipsError: Falha ao remover Requisao VIP.
        '''
        try:
            vip = RequisicaoVips.get_by_pk(vip_id)

            with distributedlock(LOCK_VIP % vip_id):

                vip.delete(authenticated_user)
        except RequisicaoVipsNotFoundError, e:
            cls.log.error(u'Requisao Vip nao encontrada')
            raise RequisicaoVipsNotFoundError(
                e, 'Requisao Vip com id %s nao encontrada' % vip_id)
        except Exception, e:
            cls.log.error(u'Falha ao remover o usuario.')
            raise RequisicaoVipsError(e, u'Falha ao remover requisicao VIP.')

    @classmethod
    def get_all(cls):
        """Get All Request Vip.

            @return: All Request Vip.

            @raise RequisicaoVipsError: Failed to search for all Request Vip.
        """
        try:
            return RequisicaoVips.objects.all()
        except Exception, e:
            cls.log.error(u'Failure to list all Request Vip.')
            raise RequisicaoVipsError(e, u'Failure to list all Request Vip.')

    @classmethod
    def get_by_healthcheck_expect(cls, healthcheck_exp):
        """Get Request Vip associated with heathcheck expect.

            @return: Request Vip with given healthcheck expect.

            @raise RequisicaoVipsError: Failed to search for Request Vip.
        """
        try:
            return RequisicaoVips.objects.filter(healthcheck_expect__id=healthcheck_exp)
        except Exception, e:
            cls.log.error(
                u'Failure to list Request Vip with healthcheck expect.')
            raise RequisicaoVipsError(
                e, u'Failure to list Request Vip with healthcheck expect.')

    @classmethod
    def get_by_ipv4_id(cls, id_ipv4):
        """Get Request Vip associated with ipv4.

            @return: Request Vip with given ipv4.

            @raise RequisicaoVipsError: Failed to search for Request Vip.
        """
        try:
            return RequisicaoVips.objects.filter(ip__id=id_ipv4)
        except Exception, e:
            cls.log.error(u'Failure to list Request Vip by ipv4.')
            raise RequisicaoVipsError(
                e, u'Failure to list Request Vip by ipv4.')

    @classmethod
    def get_by_ipv6_id(cls, id_ipv6):
        """Get Request Vip associated with ipv6.

            @return: Request Vip with given ipv6.

            @raise RequisicaoVipsError: Failed to search for Request Vip.
        """
        try:
            return RequisicaoVips.objects.filter(ipv6__id=id_ipv6)
        except Exception, e:
            cls.log.error(u'Failure to list Request Vip by ipv4.')
            raise RequisicaoVipsError(
                e, u'Failure to list Request Vip by ipv4.')

    @classmethod
    def is_valid_values_reals_priority(cls, reals_priority_map):
        '''Validation when the values ​​of reals_priority.N are all equal, the values ​​should be automatically changed to 0 (zero).

        @param reals_priority_map: List of reals_priority.
        @return: reals_priority_map: List of reals_priority.
        '''
        firstValue = reals_priority_map[0]
        valid_number_map = []
        for reals_priority in reals_priority_map:
            valid_number_map.append(firstValue)

        if reals_priority_map == valid_number_map and len(reals_priority_map) != 1:

            priority_map = []
            for reals_priority in reals_priority_map:
                priority_map.append('0')

            reals_priority_map = {
                'reals_prioritys': {'reals_priority': priority_map}}
        else:
            reals_priority_map = {
                'reals_prioritys': {'reals_priority': reals_priority_map}}

        return reals_priority_map

    def add_variable(self, key, value):
        self.variaveis = self.variaveis + key + '=' + value + '\n'

    def __parse_variables(self):
        map = dict()
        if self.variaveis is not None:
            variaveis = self.variaveis.split('\n')

            for variavel in variaveis:
                try:
                    chave, valor = variavel.split('=', 1)
                    chave = chave.strip()
                    valor = valor.strip()
                    map[chave] = valor
                except:
                    continue

        return map

    def variables_to_map(self):
        map = self.__parse_variables()

        i = 1
        key_portas = '-portas_servico.'
        portas = []
        while map.get(key_portas + str(i)) is not None:
            portas.append(map[key_portas + str(i)])
            del map[key_portas + str(i)]
            i = i + 1
        if len(portas) > 0:
            map['portas_servicos'] = {'porta': portas}
            del map['portas_servicos']

        transbordos = map.get('_transbordo')
        if transbordos is not None:
            transbordos = transbordos.split('|')
            map['transbordos'] = {'transbordo': transbordos}
            del map['_transbordo']
            del map['transbordos']

        i = 1
        key_real_name = '-reals_name.'
        key_real_ip = '-reals_ip.'
        real_maps = []
        while (map.get(key_real_name + str(i)) is not None) and (map.get(key_real_ip + str(i)) is not None):
            real_maps.append(
                {'real_name': map[key_real_name + str(i)], 'real_ip': map[key_real_ip + str(i)]})
            del map[key_real_name + str(i)]
            del map[key_real_ip + str(i)]
            i = i + 1
        if len(real_maps) > 0:
            map['reals'] = {'real': real_maps}
            del map['reals']

        i = 1
        key_reals_priority = '-reals_priority.'
        reals_prioritys = []
        while map.get(key_reals_priority + str(i)) is not None:
            reals_prioritys.append(map[key_reals_priority + str(i)])
            del map[key_reals_priority + str(i)]
            i = i + 1
        if len(reals_prioritys) > 0:
            map['reals_prioritys'] = {'reals_priority': reals_prioritys}
            del map['reals_prioritys']

        i = 1
        key_reals_weight = '-reals_weight.'
        reals_weights = []
        while map.get(key_reals_weight + str(i)) is not None:
            reals_weights.append(map[key_reals_weight + str(i)])
            del map[key_reals_weight + str(i)]
            i = i + 1
        if len(reals_weights) > 0:
            map['reals_weights'] = {'reals_weight': reals_weights}
            del map['reals_weights']

        return map

    def set_variables(self, variables_map):
        '''Constroe e atribui o valor do campo "variaveis" a partir dos dados no mapa.

        @raise EnvironmentVipNotFoundError: Ambiente Vip não encontrado com os valores de finalidade, cliente e ambiente fornecidos.

        @raise InvalidTimeoutValueError: Timeout com valor inválido.

        @raise InvalidCacheValueError: Cache com valor inválido.

        @raise InvalidMetodoBalValueError: Valor do método de balanceamento inválido.

        @raise InvalidPersistenciaValueError: Persistencia com valor inválido.

        @raise InvalidHealthcheckTypeValueError: Healthcheck_Type com valor inválido ou inconsistente em relação ao valor do healthcheck_expect.

        @raise InvalidMaxConValueError: Número máximo de conexões com valor inválido.

        @raise InvalidBalAtivoValueError: Bal_Ativo com valor inválido.

        @raise InvalidTransbordoValueError: Transbordo com valor inválido.

        @raise InvalidServicePortValueError: Porta do Serviço com valor inválido.

        @raise InvalidRealValueError: Valor inválido de um real.

        @raise InvalidHealthcheckValueError: Valor do healthcheck inconsistente em relação ao valor do healthcheck_type.
        '''

        log = Log('insert_vip_request_set_variables')

        self.variaveis = ''

        healthcheck_type = variables_map.get('healthcheck_type')
        if self.healthcheck_expect is not None and healthcheck_type != 'HTTP':
            raise InvalidHealthcheckTypeValueError(
                None, u"Valor do healthcheck_type inconsistente com o valor do healthcheck_expect.")

        finalidade = variables_map.get('finalidade')
        if not is_valid_string_minsize(finalidade, 3) or not is_valid_string_maxsize(finalidade, 50):
            log.error(u'Finality value is invalid: %s.', finalidade)
            raise InvalidValueError(None, 'finalidade', finalidade)

        cliente = variables_map.get('cliente')
        if not is_valid_string_minsize(cliente, 3) or not is_valid_string_maxsize(cliente, 50):
            log.error(u'Client value is invalid: %s.', cliente)
            raise InvalidValueError(None, 'cliente', cliente)

        ambiente = variables_map.get('ambiente')
        if not is_valid_string_minsize(ambiente, 3) or not is_valid_string_maxsize(ambiente, 50):
            log.error(u'Environment value is invalid: %s.', ambiente)
            raise InvalidValueError(None, 'ambiente', ambiente)

        try:
            evip = EnvironmentVip.get_by_values(finalidade, cliente, ambiente)
            self.add_variable('finalidade', finalidade)
            self.add_variable('cliente', cliente)
            self.add_variable('ambiente', ambiente)
        except EnvironmentVipNotFoundError:
            raise EnvironmentVipNotFoundError(
                None, u'Não existe ambiente vip para valores: finalidade %s, cliente %s e ambiente_p44 %s.' % (finalidade, cliente, ambiente))

        balanceamento = variables_map.get('metodo_bal')
        timeout = variables_map.get('timeout')
        grupo_cache = variables_map.get('cache')
        persistencia = variables_map.get('persistencia')

        grupos_cache = [(gc.nome_opcao_txt)
                        for gc in OptionVip.get_all_grupo_cache(evip.id)]
        timeouts = [(t.nome_opcao_txt)
                    for t in OptionVip.get_all_timeout(evip.id)]
        persistencias = [(p.nome_opcao_txt)
                         for p in OptionVip.get_all_persistencia(evip.id)]
        balanceamentos = [(b.nome_opcao_txt)
                          for b in OptionVip.get_all_balanceamento(evip.id)]

        if timeout not in timeouts:
            log.error(
                u'The timeout not in OptionVip, invalid value: %s.', timeout)
            raise InvalidTimeoutValueError(
                None, 'timeout com valor inválido: %s.' % timeout)
        self.add_variable('timeout', timeout)

        if balanceamento not in balanceamentos:
            log.error(
                u'The method_bal not in OptionVip, invalid value: %s.', balanceamento)
            raise InvalidMetodoBalValueError(
                None, 'metodo_bal com valor inválido: %s.' % balanceamento)
        self.add_variable('metodo_bal', balanceamento)

        if grupo_cache not in grupos_cache:
            log.error(
                u'The grupo_cache not in OptionVip, invalid value: %s.', grupo_cache)
            raise InvalidCacheValueError(
                None, 'grupo_cache com valor inválido: %s.' % grupo_cache)
        self.add_variable('cache', grupo_cache)

        if persistencia not in persistencias:
            log.error(
                u'The persistencia not in OptionVip, invalid value: %s.', persistencia)
            raise InvalidPersistenciaValueError(
                None, 'persistencia com valor inválido %s.' % persistencia)
        self.add_variable('persistencia', persistencia)

        environment_vip = EnvironmentVip.get_by_values(
            finalidade, cliente, ambiente)
        healthcheck_is_valid = RequisicaoVips.heathcheck_exist(
            healthcheck_type, environment_vip.id)

        # healthcheck_type
        if not healthcheck_is_valid:
            raise InvalidHealthcheckTypeValueError(
                None, u'Healthcheck_type com valor inválido: %s.' % healthcheck_type)
        self.add_variable('healthcheck_type', healthcheck_type)

        # healthcheck
        healthcheck = variables_map.get('healthcheck')
        if healthcheck is not None:
            if healthcheck_type != 'HTTP':
                raise InvalidHealthcheckValueError(
                    None, u"Valor do healthcheck inconsistente com o valor do healthcheck_type.")
            self.add_variable('healthcheck', healthcheck)

        # Host
        host_name = variables_map.get('host')
        if host_name is not None:
            self.add_variable('host', host_name)

        # maxcon
        maxcon = variables_map.get('maxcon')
        try:
            maxcon_int = int(maxcon)
            self.add_variable('maxcon', maxcon)
        except (TypeError, ValueError):
            raise InvalidMaxConValueError(
                None, u'Maxcon com valor inválido: %s.' % maxcon)

        # dsr
        dsr = variables_map.get('dsr')
        if dsr is not None:
            self.add_variable('dsr', dsr)

        # area negocio
        areanegocio = variables_map.get('areanegocio')
        if areanegocio is not None:
            self.add_variable('areanegocio', areanegocio)

        # nome servico
        nomeservico = variables_map.get('nome_servico')
        if nomeservico is not None:
            self.add_variable('nome_servico', nomeservico)

        # bal_ativo
        bal_ativo = variables_map.get('bal_ativo')
        if finalidade == 'Producao' and cliente == 'Usuario WEB' and ambiente == 'Streaming FE' and dsr == 'dsr' and bal_ativo is not None:
            if bal_ativo not in ('B11A', 'B12'):
                raise InvalidBalAtivoValueError(
                    None, u'Bal_ativo com valor inválido: %s.' % bal_ativo)
        if bal_ativo is not None:
            self.add_variable('bal_ativo', bal_ativo)

        # transbordos
        transbordos_map = variables_map.get('transbordos')
        if (transbordos_map is not None):
            transbordos = transbordos_map.get('transbordo')
            values = ''
            for transbordo in transbordos:
                if (finalidade == "Homologacao" and ambiente == "Homologacao FE-CITTA") or (finalidade == 'Producao' and ambiente in ('Portal FE', 'Aplicativos FE', 'Streaming FE')):
                    if not is_valid_ip(transbordo):
                        raise InvalidTransbordoValueError(None, transbordo)
                values = values + transbordo + '|'
            if values != '':
                values = values[0:len(values) - 1]
                self.add_variable('_transbordo', values)

        """# portas_servicos
        portas_servicos_map = variables_map.get('portas_servicos')
        if portas_servicos_map is not None:
            portas = portas_servicos_map.get('porta')
            if len(portas) == 0:
                raise InvalidServicePortValueError(None, portas)

            i = 1
            for porta in portas:
                try:
                    if re.match('[0-9]+:[0-9]+', porta):
                        [porta1, porta2] = re.split(':', porta)
                        porta1_int = int(porta1)
                        porta2_int = int(porta2)
                    else:
                        porta_int = int(porta)
                except (TypeError, ValueError):
                    raise InvalidServicePortValueError(None, porta)
                self.add_variable('-portas_servico.' + str(i), porta)
                i = i + 1
        else:
            raise InvalidServicePortValueError(None, portas_servicos_map)

        # reals
        reals_map = variables_map.get('reals')
        if (reals_map is not None):
            real_maps = reals_map.get('real')

            if len(real_maps) == 0:
                raise InvalidRealValueError(None, real_maps)

            i = 1
            for real_map in real_maps:
                real_name = real_map.get('real_name')
                real_ip = real_map.get('real_ip')
                if (real_name is None) or (real_ip is None):
                    raise InvalidRealValueError(None, '(%s-%s)' % (real_name, real_ip) )
                self.add_variable('-reals_name.' + str(i), real_name)
                self.add_variable('-reals_ip.' + str(i), real_ip)
                i = i + 1

            # reals_priority
            reals_prioritys_map = variables_map.get('reals_prioritys')
            if (reals_prioritys_map is not None):
                reals_priority_map = reals_prioritys_map.get('reals_priority')

                if len(reals_priority_map) == 0:
                    raise InvalidPriorityValueError(None, reals_priority_map)

                i = 1
                for reals_priority in reals_priority_map:

                    if reals_priority is None:
                        raise InvalidRealValueError(None, '(%s)' % reals_priority )

                    self.add_variable('-reals_priority.' + str(i), reals_priority)
                    i = i + 1
            else:
                raise InvalidPriorityValueError(None, reals_prioritys_map)

            # reals_weight
            if ( str(balanceamento).upper() == "WEIGHTED" ):

                # reals_weight
                reals_weights_map = variables_map.get('reals_weights')
                if (reals_weights_map is not None):
                    reals_weight_map = reals_weights_map.get('reals_weight')

                    if len(reals_weight_map) == 0:
                        raise InvalidPriorityValueError(None, reals_weight_map)

                    i = 1
                    for reals_weight in reals_weight_map:

                        if reals_weight is None:
                            raise InvalidRealValueError(None, '(%s)' % reals_weight )

                        self.add_variable('-reals_weight.' + str(i), reals_weight)
                        i = i + 1
                else:
                    raise InvalidWeightValueError(None, reals_weights_map)"""

        if self.variaveis != '':
            self.variaveis = self.variaveis[0:len(self.variaveis) - 1]

    def update_vip_created(self, authenticated_user, vip_created):
        try:
            self.vip_criado = vip_created
            self.save(authenticated_user)
        except Exception, e:
            self.log.error(
                u'Falha ao atualizar o campo vip_criado da requisição de vip.')
            raise RequisicaoVipsError(
                e, u'Falha ao atualizar o campo vip_criado da requisição de vip.')

    @classmethod
    def update(cls, authenticated_user, pk, variables_map, **kwargs):
        '''Atualiza os dados de uma requisição de VIP.

        Após atualizar os dados o campo "validado" receberá o valor 0(zero).

        Se o campo "vip_criado" da requisição de VIP tem o valor 1 então
        o VIP não poderá ser alterado.

        @return: Nothing.

        @raise RequisicaoVipsNotFoundError: Requisição de VIP não cadastrada.

        @raise RequisicaoVipsError: Falha ao atualizar a requisição de VIP.

        @raise RequisicaoVipsAlreadyCreatedError: Requisição de VIP já foi criada e não poderá ser alterada.

        @raise HealthcheckExpectNotFoundError: HealthcheckExpect não cadastrado.

        @raise HealthcheckExpectError: Falha ao pesquisar o HealthcheckExpect.

        @raise IpError: Falha ao pesquisar o IP.

        @raise IpNotFoundError: IP nao cadastrado.

        @raise InvalidHealthcheckTypeValueError: Healthcheck_Type com valor inválido ou inconsistente em relação ao valor do healthcheck_expect.
        '''
        vip = RequisicaoVips.get_by_pk(pk)

        with distributedlock(LOCK_VIP % pk):

            try:
                ip_id = kwargs['ip_id']
                if vip.ip_id != ip_id:
                    if vip.vip_criado:
                        raise RequisicaoVipsAlreadyCreatedError(
                            None, u'O IP da requisição de VIP %d não pode ser alterado porque o VIP já está criado.' % vip.id)

                    vip.ip = Ip().get_by_pk(ip_id)
            except KeyError:
                pass

            # Valid ports
            variables_map, code = vip.valid_values_ports(variables_map)
            if code is not None:
                return code

        finalidade = variables_map.get('finalidade')
        cliente = variables_map.get('cliente')
        ambiente = variables_map.get('ambiente')

        if not is_valid_string_minsize(finalidade, 3) or not is_valid_string_maxsize(finalidade, 50):
            cls.log.error(u'Finality value is invalid: %s.', finalidade)
            raise InvalidValueError(None, 'finalidade', finalidade)

        if not is_valid_string_minsize(cliente, 3) or not is_valid_string_maxsize(cliente, 50):
            cls.log.error(u'Client value is invalid: %s.', cliente)
            raise InvalidValueError(None, 'cliente', cliente)

        if not is_valid_string_minsize(ambiente, 3) or not is_valid_string_maxsize(ambiente, 50):
            cls.log.error(u'Environment value is invalid: %s.', ambiente)
            raise InvalidValueError(None, 'ambiente', ambiente)

        # get environmentVip dor validation dynamic heathcheck
        environment_vip = EnvironmentVip.get_by_values(
            finalidade, cliente, ambiente)
        # Valid HealthcheckExpect
        variables_map, vip, code = vip.valid_values_healthcheck(
            variables_map, vip, environment_vip)
        if code is not None:
            return code

        vip_variables = vip.variables_to_map()

        # Valid list reals_prioritys
        if variables_map.get('reals_prioritys') is None:
            if vip_variables.get('reals_prioritys') is None:
                priority_map = []
                for __reals in variables_map.get('reals').get('real'):
                    priority_map.append('0')
                variables_map['reals_prioritys'] = {
                    'reals_priority': priority_map}
            else:
                if vip_variables.get('reals_prioritys').get('reals_priority') is None:
                    priority_map = []
                    for __reals in variables_map.get('reals').get('real'):
                        priority_map.append('0')
                    variables_map['reals_prioritys'] = {
                        'reals_priority': priority_map}
                else:
                    variables_map['reals_prioritys'] = vip_variables.get(
                        'reals_prioritys')

        # Valid list reals_weights
        if variables_map.get('reals_weights') is None:
            if vip_variables.get('reals_weights') is None:
                weight_map = []
                for __reals in variables_map.get('reals').get('real'):
                    weight_map.append('0')
                variables_map['reals_weights'] = {'reals_weight': weight_map}
            else:
                if vip_variables.get('reals_weights').get('reals_weight') is None:
                    priority_map = []
                    for __reals in variables_map.get('reals').get('real'):
                        priority_map.append('0')
                    variables_map['reals_weights'] = {
                        'reals_weight': priority_map}
                else:
                    variables_map['reals_weights'] = vip_variables.get(
                        'reals_weights')

        # Valid l7_filter
        if vip.l7_filter is None:
            vip.l7_filter = None

        # Valid transbordos
        if vip_variables.get('transbordos') is None:
            variables_map['transbordos'] = None
        else:
            variables_map['transbordos'] = vip_variables.get('transbordos')

        # Valid bal_ativo
        if vip_variables.get('bal_ativo') is None:
            variables_map['bal_ativo'] = None
        else:
            variables_map['bal_ativo'] = vip_variables.get('bal_ativo')

        vip.__dict__.update(kwargs)
        vip.set_variables(variables_map)

        try:
            vip.save(authenticated_user)
        except Exception, e:
            cls.log.error(u'Falha ao atualizar a requisição de vip.')
            raise RequisicaoVipsError(
                e, u'Falha ao atualizar a requisição de vip.')

    def valida(self, authenticated_user, validado):
        '''Valida uma Requisicao VIP.

        @return: Nothing.

        @raise RequisicaoVipsError: Erro ao validar Requisição de VIP.
        '''
        try:
            self.validado = validado

            self.save(authenticated_user)
        except RequisicaoVipsError, e:
            self.log.error(u'Falha ao validar a requisição de vip.')
            raise RequisicaoVipsError(
                e, u'Falha ao validar a requisição de vip.')

    def create(self, authenticated_user, variables_map):
        ''' Insere uma nova requisição de VIP.

        Os campos validado e vip_criado terão sempre o valor 0.

        @return: Nothing

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

        @raise InvalidMaxConValueError: Número máximo de conexões com valor inválido.

        @raise InvalidBalAtivoValueError: Bal_Ativo com valor inválido.

        @raise InvalidTransbordoValueError: Transbordo com valor inválido.

        @raise InvalidServicePortValueError: Porta do Serviço com valor inválido.

        @raise InvalidRealValueError: Valor inválido de um real.

        @raise InvalidHealthcheckValueError: Valor do healthcheck inconsistente em relação ao valor do healthcheck_type.

        @raise RequisicaoVipsError: Falha ao inserir a requisição de VIP.
        '''
        self.ip = Ip().get_by_pk(self.ip.id)

        # Valid list reals_prioritys
        if variables_map.get('reals_prioritys') is None:
            priority_map = []
            for __reals in variables_map.get('reals').get('real'):
                priority_map.append('0')
            variables_map['reals_prioritys'] = {'reals_priority': priority_map}

        # Valid list reals_weights
        if variables_map.get('reals_weights') is None:

            weight_map = []
            for __reals in variables_map.get('reals').get('real'):
                weight_map.append('0')

            variables_map['reals_weights'] = {'reals_weight': weight_map}

        # Set None transbordo and bal_ativo
        variables_map['transbordos'] = None
        variables_map['bal_ativo'] = None

        if variables_map.get('areanegocio') is None:
            variables_map['areanegocio'] = 'Orquestra'
        if variables_map.get('nome_servico') is None:
            variables_map['nome_servico'] = 'Orquestra'

        # set variables
        self.l7_filter = variables_map.get('l7_filter')
        self.validado = 0
        self.vip_criado = 0
        self.set_variables(variables_map)

        try:
            self.save(authenticated_user)
        except Exception, e:
            self.log.error(u'Falha ao inserir a requisição de vip.')
            raise RequisicaoVipsError(
                e, u'Falha ao inserir a requisição de vip.')

    def valid_values_ports(self, vip_map):
        '''Validation when the values ​​of portas_servicos
        This method accept 'port1:port2' and 'port1' only, when the parameter is port1, the method will understand that it means 'por1:por1'

        @param vip_map: Map with the data of the request..

        @return: On success: vip_map, None
                 In case of error: vip_map, code  (code error message).

        @raise InvalidValueError: Represents an error occurred validating a value.
        '''

        # Valid portas_servicos
        portas_servicos_map = vip_map.get('portas_servicos')
        if (portas_servicos_map is not None):

            port_map = portas_servicos_map.get('porta')
            new_port_map = list()

            if (port_map is not None and port_map != []):

                # Valid values ​​of port
                for port in port_map:
                    port_arr = port.split(':')
                    if len(port_arr) < 2:
                        port = port_arr[0] + ':' + port_arr[0]
                    if not is_valid_regex(port, "[0-9]+:[0-9]+"):
                        self.log.error(
                            u'The port parameter is not a valid value: %s.', port)
                        raise InvalidValueError(None, 'port', port)

                    new_port_map.append(port)

                vip_map['portas_servicos'] = {'porta': new_port_map}
            else:
                self.log.error(
                    u'The ports parameter is not a valid value: %s.', port_map)
                return vip_map, (138, port_map)
        else:
            self.log.error(
                u'The ports parameter is not a valid value: %s.', portas_servicos_map)
            raise InvalidValueError(None, 'ports', portas_servicos_map)

        return vip_map, None

    def valid_values_reals_priority(self, vip_map):
        '''Validation when the values ​​of reals_priority.N

        @param vip_map: Map with the data of the request..

        @return: On success: vip_map, None
                 In case of error: vip_map, code  (code error message).

        @raise InvalidValueError: Represents an error occurred validating a value.
        '''

        # Valid reals_prioritys
        reals_prioritys_map = vip_map.get('reals_prioritys')
        if (reals_prioritys_map is not None):

            reals_priority_map = reals_prioritys_map.get('reals_priority')

            if (reals_priority_map is not None):

                # Validates the size reals list is equal to the size priority
                # list
                if len(vip_map.get('reals').get('real')) != len(vip_map.get('reals_prioritys').get('reals_priority')):
                    self.log.error(
                        u'List the Reals_priority  is higher or lower than list the real_server.')
                    return vip_map, 272

                # Valid values ​​of reals_priority
                for reals_priority in reals_priority_map:
                    if not is_valid_int_greater_equal_zero_param(reals_priority):
                        self.log.error(
                            u'The reals_priority parameter is not a valid value: %s.', reals_priority)
                        raise InvalidValueError(
                            None, 'reals_priority', reals_priority)

                # Valid list reals_prioritys
                vip_map['reals_prioritys'] = self.is_valid_values_reals_priority(
                    vip_map.get('reals_prioritys').get('reals_priority')).get('reals_prioritys')

        else:
            self.log.error(
                u'The reals_priority parameter is not a valid value: %s.', reals_prioritys_map)
            raise InvalidValueError(
                None, 'reals_priority', reals_prioritys_map)

        return vip_map, None

    def valid_values_reals_weight(self, vip_map):
        '''Validation when the values ​​of reals_weight.N

        @param vip_map: Map with the data of the request.

        @return: On success: vip_map, None
                 In case of error: vip_map, code  (code error message).

        @raise InvalidValueError: Represents an error occurred validating a value.
        '''

        # Valid reals_weight
        reals_weights_map = vip_map.get('reals_weights')
        metodo_bal = vip_map.get('metodo_bal')

        if (str(metodo_bal).upper() == "WEIGHTED"):

            if (reals_weights_map is not None):

                reals_weight_map = reals_weights_map.get('reals_weight')

                if (reals_weight_map is not None):

                    # Validates the size reals list is equal to the size
                    # _weight list
                    if len(vip_map.get('reals').get('real')) != len(vip_map.get('reals_weights').get('reals_weight')):
                        self.log.error(
                            u'List of reals_weight is higher or lower than list the real_server.')
                        return vip_map, 274

                    # Valid values ​​of reals_weight
                    for reals_weight in reals_weight_map:
                        if not is_valid_int_greater_equal_zero_param(reals_weight):
                            self.log.error(
                                u'The reals_weight parameter is not a valid value: %s.', reals_weight)
                            raise InvalidValueError(
                                None, 'reals_weight', reals_weight)

                else:
                    # Validates the size reals list is equal to the size
                    # _weight list
                    if len(vip_map.get('reals').get('real')) > 0:
                        self.log.error(
                            u'List of reals_weight is empty but real_server is not.')
                        return vip_map, 274
            else:
                    # Validates the size reals list is equal to the size
                    # _weight list
                if len(vip_map.get('reals').get('real')) > 0:
                    self.log.error(
                        u'List of reals_weight is empty but real_server is not.')
                    return vip_map, 274

        return vip_map, None

    def valid_values_healthcheck(self, vip_map, vip, evironment_vip):
        '''Validation when the values ​​of healthcheck

        @param vip_map: Map with the data of the request.

        @param vip: request VIP.

        @return: On success: vip_map, vip, None
                 In case of error: vip_map, vip, code  (code error message).

        @raise InvalidValueError: Represents an error occurred validating a value.
        @raise ObjectDoesNotExist: Healthcheck does not exist .
        @raise HealthcheckExpectNotFoundError: The id_healthcheck_expect parameter does not exist.

        '''

        # Get XML data
        healthcheck_type = upper(str(vip_map['healthcheck_type']))
        healthcheck = vip_map['healthcheck']
        id_healthcheck_expect = vip_map['id_healthcheck_expect']

        healthcheck_is_valid = RequisicaoVips.heathcheck_exist(
            healthcheck_type, evironment_vip.id)

        if not healthcheck_is_valid:
            self.log.error(u'The healthcheck_type parameter not exist.')
            return vip_map, vip, 275

        if healthcheck_type != 'HTTP':
            if not (id_healthcheck_expect == None and healthcheck == None):
                self.log.error(
                    u'The healthcheck_type parameter is %s, then healthcheck and id_healthcheck_expect must be None.', healthcheck_type)
                return vip_map, vip, 276

        # If healthcheck_type is 'HTTP' id_healthcheck_expect and healthcheck
        # must NOT be None
        elif healthcheck_type == 'HTTP':
            if id_healthcheck_expect == None or healthcheck == None:
                self.log.error(
                    u'The healthcheck_type parameter is HTTP, then healthcheck and id_healthcheck_expect must NOT be None.')
                return vip_map, vip, 277
            else:
                try:

                    # Valid healthcheck_expect ID
                    if not is_valid_int_greater_zero_param(id_healthcheck_expect):
                        self.log.error(
                            u'The id_healthcheck_expect parameter is not a valid value: %s.', id_healthcheck_expect)
                        raise InvalidValueError(
                            None, 'id_healthcheck_expect', id_healthcheck_expect)

                    # Find healthcheck_expect by ID to check if it exist
                    healthcheck_expect = HealthcheckExpect.get_by_pk(
                        id_healthcheck_expect)

                    vip_map['healthcheck'] = healthcheck
                    # Set id_healthcheck_expect
                    vip.healthcheck_expect = healthcheck_expect

                    # Check if healthcheck is a string
                    if not isinstance(healthcheck, basestring):
                        self.log.error(u'The healthcheck must be a string.')
                        raise InvalidValueError(
                            None, 'healthcheck', healthcheck)

                except HealthcheckExpectNotFoundError:
                    self.log.error(
                        'The id_healthcheck_expect parameter does not exist.')
                    raise HealthcheckExpectNotFoundError(None)
        else:
            vip_map['healthcheck'] = None
            # Set id_healthcheck_expect to None
            vip.healthcheck_expect = None

        # Make changes in healthcheck
        # Set healthcheck_type
        vip_map['healthcheck_type'] = healthcheck_type

        return vip_map, vip, None

    @classmethod
    def heathcheck_exist(cls, healthcheck_type, id_evironment_vip):
        healthcheck_is_valid = False
        healthcheck_type = healthcheck_type.upper()

        healthcheck_list = OptionVip.get_all_healthcheck(id_evironment_vip)

        for option_vip_healthcheck in healthcheck_list:
            if str(option_vip_healthcheck.nome_opcao_txt).upper() == healthcheck_type:
                healthcheck_is_valid = True
                break

        return healthcheck_is_valid

    @classmethod
    def valid_real_server(cls, ip, equip, evip, valid=True):
        '''Validation real server

        @param ip:     IPv4 or Ipv6. 'xxx.xxx.xxx.xxx or xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx'
        @param equip:  Equipment
        @param evip:   Environment Vip

        @return: IPv4 or Ipv6, Equipment, Environment Vip

        @raise IpNotFoundByEquipAndVipError:  IP is not related equipment and Environment Vip.
        @raise IpNotFoundError: IP is not registered.
        @raise IpError: Failed to search for the IP.
        '''
        if is_valid_ipv4(ip):

            ip_list = ip.split(".")

            ip = Ip.get_by_octs_and_environment_vip(
                ip_list[0], ip_list[1], ip_list[2], ip_list[3], evip.id, valid)

            lista_ips_equip = list()
            lista_amb_div_4 = list()

            # GET DIVISAO DC AND AMBIENTE_LOGICO OF NET4
            for net in evip.networkipv4_set.select_related().all():

                dict_div_4 = dict()
                dict_div_4['divisao_dc'] = net.vlan.ambiente.divisao_dc_id
                dict_div_4[
                    'ambiente_logico'] = net.vlan.ambiente.ambiente_logico_id

                if dict_div_4 not in lista_amb_div_4:
                    lista_amb_div_4.append(dict_div_4)

            # Get all IPV4's Equipment
            for ipequip in equip.ipequipamento_set.select_related().all():
                if ipequip.ip not in lista_ips_equip:
                    for dict_div_amb in lista_amb_div_4:
                        if ipequip.ip.networkipv4.ambient_vip is not None and ipequip.ip.networkipv4.ambient_vip.id == evip.id:
                            if (ipequip.ip.networkipv4.vlan.ambiente.divisao_dc_id == dict_div_amb.get('divisao_dc') and ipequip.ip.networkipv4.vlan.ambiente.ambiente_logico_id == dict_div_amb.get('ambiente_logico')):
                                lista_ips_equip.append(ipequip.ip)

            if valid == True:
                if not ip in lista_ips_equip:
                    raise IpNotFoundByEquipAndVipError(None, 'Ipv4 não está relacionado com equipamento %s e Ambiente Vip: %s' % (
                        equip.name, evip.show_environment_vip()))

        elif is_valid_ipv6(ip):

            ip_list = ip.split(":")
            ip = Ipv6.get_by_octs_and_environment_vip(ip_list[0], ip_list[1], ip_list[
                                                      2], ip_list[3], ip_list[4], ip_list[5], ip_list[6], ip_list[7], evip.id, valid)

            lista_amb_div_6 = list()
            lista_ipsv6_equip = list()

            # GET DIVISAO DC AND AMBIENTE_LOGICO OF NET6
            for net in evip.networkipv6_set.select_related().all():

                dict_div_6 = dict()
                dict_div_6['divisao_dc'] = net.vlan.ambiente.divisao_dc
                dict_div_6[
                    'ambiente_logico'] = net.vlan.ambiente.ambiente_logico
                if dict_div_6 not in lista_amb_div_6:
                    lista_amb_div_6.append(dict_div_6)

            # Get all IPV6'S Equipment
            for ipequip in equip.ipv6equipament_set.select_related().all():
                if ipequip.ip not in lista_ipsv6_equip:
                    for dict_div_amb in lista_amb_div_6:
                        if ipequip.ip.networkipv6.ambient_vip is not None and ipequip.ip.networkipv6.ambient_vip.id == evip.id:
                            if (ipequip.ip.networkipv6.vlan.ambiente.divisao_dc == dict_div_amb.get('divisao_dc') and ipequip.ip.networkipv6.vlan.ambiente.ambiente_logico == dict_div_amb.get('ambiente_logico')):
                                lista_ipsv6_equip.append(ipequip.ip)

            if valid == True:
                if not ip in lista_ipsv6_equip:
                    raise IpNotFoundByEquipAndVipError(None, 'Ipv6 não está relacionado com equipamento %s e Ambiente Vip: %s' % (
                        equip.name, evip.show_environment_vip()))

        else:
            raise InvalidValueError(None, 'ip', ip)

        return ip, equip, evip

    def save_vips_and_ports(self, vip_map, user):
        # Ports Vip
        ports_vip_map = vip_map.get('portas_servicos')
        ports_vip = ports_vip_map.get('porta')
        reals = list()
        
        # Environment
        finalidade = vip_map.get('finalidade')
        cliente = vip_map.get('cliente')
        ambiente = vip_map.get('ambiente')
        evip = EnvironmentVip.get_by_values(
            finalidade,
            cliente,
            ambiente
        )
        env_query = Ambiente.objects.filter(
            Q(vlan__networkipv4__ambient_vip=evip) |
            Q(vlan__networkipv6__ambient_vip=evip)
        )
        environment_obj = env_query and env_query.uniqueResult() or None
        
        # Reals
        reals_map = vip_map.get('reals')
        if reals_map:
            reals = reals_map.get('real')

            # Prioritys
            reals_priority = vip_map.get('reals_prioritys')
            prioritys = reals_priority.get('reals_priority')

            # Weights
            reals_weights = vip_map.get('reals_weights')
            weights = None

            if reals_weights != None:
                weights = reals_weights.get('reals_weight')

        vip_port_list = list()
        # save ServerPool and VipPortToPool
        for port_vip in ports_vip:

            port_vip = port_vip.split(':')
            default_port = port_vip[1]
            # save ServerPool
            server_pool = ServerPool()
            server_pool.environment = environment_obj
            server_pool.prepare_and_save(default_port, user)

            # save VipPortToPool
            vip_port_to_pool = VipPortToPool()
            vip_port_to_pool.prepare_and_save(
                port_vip[0], server_pool, self, user)

            vip_port_list.append(
                {'port_vip': port_vip[0], 'server_pool': server_pool})

        # save ServerPoolMember
        for i in range(0, len(reals)):

            port_real = reals[i].get('port_real')
            port_vip = reals[i].get('port_vip')

            # Valid port real
            if not is_valid_int_greater_zero_param(port_real):
                self.log.error(
                    u'The reals.port_real parameter is not a valid value: %s.', port_real)
                raise InvalidValueError(None, 'reals.port_real', port_real)

            weight = ''

            for v_port in vip_port_list:
                if v_port['port_vip'] == port_vip:
                    server_pool = v_port['server_pool']

            ip_id = reals[i].get('id_ip')
            # Valid ip_id
            if not is_valid_int_greater_zero_param(ip_id):
                self.log.error(
                    u'The reals.ip_id parameter is not a valid value: %s.', ip_id)
                raise InvalidValueError(None, 'reals.ip_id', ip_id)

            # Check ip type
            if is_valid_ipv4(reals[i].get('real_ip')) == True:
                ip_type = IP_VERSION.IPv4[1]
                ip = Ip().get_by_pk(ip_id)
            else:
                ip_type = IP_VERSION.IPv6[1]
                ip = Ipv6().get_by_pk(ip_id)

            priority = prioritys[i]

            if weights != None:
                if i < len(weights):
                    weight = weights[i]

            server_pool_member = ServerPoolMember()

            # save ServerPoolMember
            server_pool_member.prepare_and_save(
                server_pool, ip, ip_type, priority, weight, port_real, user)

    def get_vips_and_reals(self, id_vip):
        vip_port = VipPortToPool.get_by_vip_id(id_vip)

        vip_port_list = list()
        reals_list = list()
        reals_priority = list()
        reals_weight = list()

        for v_port in vip_port:

            vip_port_list.append(
                str(v_port.port_vip) + ':' + str(v_port.server_pool.default_port))

            members = v_port.server_pool.serverpoolmember_set.all()

            for member in members:
                try:
                    ip_equip = member.ip.ipequipamento_set.get()
                    equip_name = ip_equip.equipamento.nome
                    ip_string = mount_ipv4_string(member.ip)
                    ip_id = member.ip.id
                except:
                    ip_equip = member.ipv6.ipv6equipament_set.get()
                    equip_name = ip_equip.equipamento.nome
                    ip_string = mount_ipv6_string(member.ipv6)
                    ip_id = member.ipv6.id

                vip_port = member.server_pool.vipporttopool_set.get()
                reals_list.append({'real_ip': ip_string, 'real_name': equip_name,
                                   'port_vip': vip_port.port_vip, 'port_real': member.port_real, 'id_ip': ip_id})
                reals_priority.append(member.priority)
                reals_weight.append(member.weight)

        return vip_port_list, reals_list, reals_priority, reals_weight

    def delete_vips_and_reals(self, user):

        vip_ports = VipPortToPool.objects.filter(requisicao_vip=self)
        server_pool_list = list()
        for vip_port in vip_ports:
            server_pool_members = ServerPoolMember.objects.filter(
                server_pool=vip_port.server_pool)
            for server_pool_member in server_pool_members:
                server_pool_member.delete(user)
            vip_port.delete(user)
            server_pool_list.append(vip_port.server_pool)

        for server_pool in server_pool_list:
            server_pool.delete(user)


class OptionVip(BaseModel):
    id = models.AutoField(primary_key=True)
    tipo_opcao = models.CharField(
        max_length=50, blank=False, db_column='tipo_opcao')
    nome_opcao_txt = models.CharField(
        max_length=50, blank=False, db_column='nome_opcao_txt')

    log = Log('OptionVIP')

    class Meta(BaseModel.Meta):
        db_table = u'opcoesvip'
        managed = True

    def valid_option_vip(self, optionvip_map):
        '''Validate the values ​​of option vip

        @param optionvip_map: Map with the data of the request.

        @raise InvalidValueError: Represents an error occurred validating a value.
        '''

        # Get XML data
        tipo_opcao = optionvip_map.get('tipo_opcao')
        nome_opcao_txt = optionvip_map.get('nome_opcao_txt')

        # tipo_opcao can NOT be greater than 50
        if not is_valid_string_maxsize(tipo_opcao, 50, True) or not is_valid_option(tipo_opcao):
            self.log.error(
                u'Parameter tipo_opcao is invalid. Value: %s.', tipo_opcao)
            raise InvalidValueError(None, 'tipo_opcao', tipo_opcao)

        # nome_opcao_txt can NOT be greater than 50
        if not is_valid_string_maxsize(nome_opcao_txt, 50, True) or not is_valid_option(nome_opcao_txt):
            self.log.error(
                u'Parameter nome_opcao_txt is invalid. Value: %s.', nome_opcao_txt)
            raise InvalidValueError(None, 'nome_opcao_txt', nome_opcao_txt)

        # set variables
        self.tipo_opcao = tipo_opcao
        self.nome_opcao_txt = nome_opcao_txt

    @classmethod
    def get_by_pk(cls, id):
        """"Get  Option Vip by id.

        @return: Option Vip.

        @raise OptionVipNotFoundError: Option Vip is not registered.
        @raise OptionVipError: Failed to search for the Option Vip.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return OptionVip.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise OptionVipNotFoundError(
                e, u'Dont there is a option vip by pk = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the option vip.')
            raise OptionVipError(e, u'Failure to search the option vip.')

    @classmethod
    def get_all(cls):
        """Get All Option Vip.

            @return: All Option Vip.

            @raise OperationalError: Failed to search for all Option Vip.
        """
        try:
            return OptionVip.objects.all()
        except Exception, e:
            cls.log.error(u'Failure to list all Option Vip.')
            raise OptionVipError(e, u'Failure to list all Option Vip.')

    @classmethod
    def get_all_timeout(cls, id_environment_vip):
        """Get All Option Vip Timeout by environmentvip_id.

            @return: All Option Vip.

            @raise OperationalError: Failed to search for all Option Vip.
        """
        try:

            ovips = OptionVip.objects.select_related().all()
            ovips = ovips.filter(tipo_opcao__icontains='timeout')
            ovips = ovips.filter(
                optionvipenvironmentvip__environment__id=int(id_environment_vip))

            return ovips

        except Exception, e:
            cls.log.error(u'Failure to list all Option Vip.')
            raise OptionVipError(e, u'Failure to list all Option Vip.')

    @classmethod
    def get_all_balanceamento(cls, id_environment_vip):
        """Get All Option Vip Balancing by environmentvip_id.

            @return: All Option Vip.

            @raise OperationalError: Failed to search for all Option Vip.
        """
        try:

            ovips = OptionVip.objects.select_related().all()
            ovips = ovips.filter(tipo_opcao__icontains='balanceamento')
            ovips = ovips.filter(
                optionvipenvironmentvip__environment__id=int(id_environment_vip))

            return ovips

        except Exception, e:
            cls.log.error(u'Failure to list all Option Vip.')
            raise OptionVipError(e, u'Failure to list all Option Vip.')

    @classmethod
    def get_all_healthcheck(cls, id_environment_vip):
        """Get All Option Vip Healthcheck by environmentvip_id.

            @return: Get All Option Vip Healthcheck.

            @raise OperationalError: Failed to search for all Option Vip Healthcheck.
        """
        try:

            ovips = OptionVip.objects.select_related().all()
            ovips = ovips.filter(tipo_opcao__icontains='HealthCheck')
            ovips = ovips.filter(
                optionvipenvironmentvip__environment__id=int(id_environment_vip))

            return ovips

        except Exception, e:
            cls.log.error(u'Failure to list all Option Vip Healthcheck.')
            raise OptionVipError(
                e, u'Failure to list all Option Vip Healthcheck.')

    @classmethod
    def get_all_persistencia(cls, id_environment_vip):
        """Get All Option Vip Persistence by environmentvip_id.

            @return: All Option Vip.

            @raise OperationalError: Failed to search for all Option Vip.
        """
        try:

            ovips = OptionVip.objects.select_related().all()
            ovips = ovips.filter(tipo_opcao__icontains='persistencia')
            ovips = ovips.filter(
                optionvipenvironmentvip__environment__id=int(id_environment_vip))

            return ovips

        except Exception, e:
            cls.log.error(u'Failure to list all Option Vip.')
            raise OptionVipError(e, u'Failure to list all Option Vip.')

    @classmethod
    def get_all_grupo_cache(cls, id_environment_vip):
        """Get All Option Vip Timeout by environmentvip_id.

            @return: All Option Vip.

            @raise OperationalError: Failed to search for all Option Vip.
        """
        try:

            ovips = OptionVip.objects.select_related().all()
            ovips = ovips.filter(tipo_opcao__icontains='cache')
            ovips = ovips.filter(
                optionvipenvironmentvip__environment__id=int(id_environment_vip))

            return ovips

        except Exception, e:
            cls.log.error(u'Failure to list all Option Vip.')
            raise OptionVipError(e, u'Failure to list all Option Vip.')

    def delete(self, authenticated_user):
        '''Override Django's method to remove option vip

        Before removing the option vip removes all relationships with environment vip.
        '''

        # Remove all EnvironmentVIP OptionVip related
        for option_environment in OptionVipEnvironmentVip.objects.filter(option=self.id):
            option_environment.delete(authenticated_user)

        super(OptionVip, self).delete(authenticated_user)


class OptionVipEnvironmentVip(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id')
    option = models.ForeignKey(OptionVip, db_column='id_opcoesvip')
    environment = models.ForeignKey(EnvironmentVip, db_column='id_ambiente')

    log = Log('OptionVipEnvironmentVip')

    class Meta(BaseModel.Meta):
        db_table = u'opcoesvip_ambiente_xref'
        managed = True
        unique_together = ('option', 'environment')

    def get_by_option_environment(self, option_id, environment_id):
        """Get OptionVipEnvironmentVip by OptionVip and EnvironmentVip.

        @return: OptionVipEnvironmentVip.

        @raise OptionVipEnvironmentVipNotFoundError: Ipv6Equipament is not registered.
        @raise OptionVipEnvironmentVipError: Failed to search for the OptionVipEnvironmentVip.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return OptionVipEnvironmentVip.objects.filter(option__id=option_id, environment__id=environment_id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise OptionVipEnvironmentVipNotFoundError(
                e, u'Dont there is a OptionVipEnvironmentVip by option_id = %s and environment_id = %s' % (option_id, environment_id))
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the OptionVipEnvironmentVip.')
            raise OptionVipEnvironmentVipError(
                e, u'Failure to search the OptionVipEnvironmentVip.')

    def validate(self):
        """Validates whether OptionVip is already associated with EnvironmentVip

            @raise IpEquipamentoDuplicatedError: if OptionVip is already associated with EnvironmentVip
        """
        try:
            OptionVipEnvironmentVip.objects.get(
                option=self.option, environment=self.environment)
            raise OptionVipEnvironmentVipDuplicatedError(
                None, u'Option vip already registered for the environment vip.')
        except ObjectDoesNotExist:
            pass


class ServerPool(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id_server_pool'
    )

    identifier = models.CharField(
        max_length=200
    )

    healthcheck = models.ForeignKey(
        Healthcheck,
        db_column='healthcheck_id_healthcheck'
    )

    default_port = models.IntegerField(
        db_column='default_port'
    )

    pool_created = models.NullBooleanField(
        db_column='pool_criado',
        null=True
    )

    environment = models.ForeignKey(
        Ambiente,
        db_column='ambiente_id_ambiente',
        null=True
    )

    lb_method = models.CharField(
        max_length=50,
        db_column='lb_method',
        null=True
    )

    log = Log('ServerPool')

    class Meta(BaseModel.Meta):
        db_table = u'server_pool'
        managed = True

    def prepare_and_save(self, default_port, user):
        self.default_port = default_port
        self.save(user)


class ServerPoolMember(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_server_pool_member')
    server_pool = models.ForeignKey(ServerPool, db_column='id_server_pool')
    identifier = models.CharField(max_length=200)
    ip = models.ForeignKey(Ip, db_column='ips_id_ip', null=True)
    ipv6 = models.ForeignKey(Ipv6, db_column='ipsv6_id_ipv6', null=True)
    priority = models.IntegerField()
    weight = models.IntegerField(db_column='weight')
    limit = models.IntegerField()
    port_real = models.IntegerField(db_column='port')
    healthcheck = models.ForeignKey(
        Healthcheck, db_column='healthcheck_id_healthcheck')

    class Meta(BaseModel.Meta):
        db_table = u'server_pool_member'
        managed = True

    def prepare_and_save(self, server_pool, ip, ip_type, priority, weight, port_real, user, commit=False):

        self.server_pool = server_pool

        if ip_type == IP_VERSION.IPv4[1]:
            self.ip = ip
        else:
            self.ipv6 = ip

        self.priority = priority

        if weight != '':
            self.weight = weight
        else:
            self.weight = 0

        self.limit = 0
        self.port_real = port_real

        self.save(user, commit=commit)

    def save_with_default_port(self, vip_id, ip, ip_version, user):
        """
            Old calls hasn't a port real, save with deafult_port specified in server pool
            Save with commit = True
        """

        server_pools = ServerPool.objects.filter(
            vipporttopool__requisicao_vip__id=vip_id)

        for server_pool in server_pools:
            server_pool_member = ServerPoolMember()
            server_pool_member.prepare_and_save(
                server_pool, ip, ip_version, 0, 1, server_pool.default_port, user, commit=True)

    def save_specified_port(self, vip_id, port_vip, ip, ip_version, port_real, user):
        """ Save with commit = True """
        vipporttopool = VipPortToPool.objects.filter(
            requisicao_vip__id=vip_id, port_vip=port_vip)
        if vipporttopool:
            vipporttopool = vipporttopool[0]
            ServerPoolMember().prepare_and_save(
                vipporttopool.server_pool, ip, ip_version, 0, 1, port_real, user, commit=True)


class VipPortToPool(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_vip_port_to_pool')
    requisicao_vip = models.ForeignKey(
        RequisicaoVips, db_column='id_requisicao_vips')
    server_pool = models.ForeignKey(ServerPool, db_column='id_server_pool')
    port_vip = models.IntegerField(db_column='vip_port')

    class Meta(BaseModel.Meta):
        db_table = u'vip_port_to_pool'
        managed = True

    def prepare_and_save(self, port_vip, server_pool, vip, user):

        self.requisicao_vip = vip
        self.server_pool = server_pool
        self.port_vip = port_vip

        self.save(user)

    @classmethod
    def get_by_vip_id(cls, id_vip):
        """Get Request VipPortToPool associated with id_vip.

            @return: Request VipPortToPool with given id_vip.

            @raise RequisicaoVipsError: Failed to search for VipPortToPool.
        """
        try:
            return VipPortToPool.objects.filter(requisicao_vip__id=id_vip)
        except Exception, e:
            cls.log.error(u'Failure to list Request VipPortToPool by id_vip.')
            raise RequisicaoVipsError(
                e, u'Failure to list Request VipPortToPool by id_vip.')
