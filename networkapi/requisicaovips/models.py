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
from string import upper

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import get_model
from django.db.models import Q

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import EnvironmentVip
from networkapi.ambiente.models import IP_VERSION
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_VIP
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.exception import OptionVipEnvironmentVipDuplicatedError
from networkapi.exception import OptionVipEnvironmentVipError
from networkapi.exception import OptionVipEnvironmentVipNotFoundError
from networkapi.exception import OptionVipError
from networkapi.exception import OptionVipNotFoundError
from networkapi.models.BaseModel import BaseModel
from networkapi.util import is_valid_int_greater_equal_zero_param
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_ip
from networkapi.util import is_valid_ipv4
from networkapi.util import is_valid_ipv6
from networkapi.util import is_valid_option
from networkapi.util import is_valid_regex
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.util import mount_ipv4_string
from networkapi.util import mount_ipv6_string
from networkapi.util.decorators import cached_property
from networkapi.util.geral import get_app

# from networkapi.api_pools.exceptions import PoolError

Ip = get_model('ip', 'Ip')
IpNotFoundByEquipAndVipError = get_model('ip', 'IpNotFoundByEquipAndVipError')
Ipv6 = get_model('ip', 'Ipv6')

# Healthcheck = get_model('healthcheckexpect', 'Healthcheck')
# HealthcheckExpect = get_model('healthcheckexpect', 'HealthcheckExpect')
# HealthcheckExpectNotFoundError = get_model(
#     'healthcheckexpect', 'HealthcheckExpectNotFoundError')


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


class RequisicaoVipsMissingDSRL3idError(RequisicaoVipsError):

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


class InvalidTrafficReturnValueError(RequisicaoVipsError):

    """Retorna exceção quando o valor da variável traffic return é inválido."""

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


class RequestVipWithoutServerPoolError(RequisicaoVipsError):

    """Return exception when no one exisitir server pool to request VIP."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class InvalidWeightValueError(RequisicaoVipsError):

    """Returns exception when the value of the weight variable is invalid."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class RequestVipServerPoolConstraintError(RequisicaoVipsError):

    """Return exception when delete server pool related with other request VIP."""

    def __init__(self, cause, message=None):
        RequisicaoVipsError.__init__(self, cause, message)


class OptionVip(BaseModel):
    id = models.AutoField(primary_key=True)
    tipo_opcao = models.CharField(
        max_length=50,
        blank=False,
        db_column='tipo_opcao'
    )
    nome_opcao_txt = models.CharField(
        max_length=50,
        blank=False,
        db_column='nome_opcao_txt'
    )

    log = logging.getLogger('OptionVIP')

    class Meta(BaseModel.Meta):
        db_table = u'opcoesvip'
        managed = True

    def valid_option_vip(self, optionvip_map):
        """Validate the values ​​of option vip

        @param optionvip_map: Map with the data of the request.

        @raise InvalidValueError: Represents an error occurred validating a value.
        """

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

            ovips = OptionVip.objects.all()
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

            ovips = OptionVip.objects.all()
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

            ovips = OptionVip.objects.all()
            ovips = ovips.filter(tipo_opcao__icontains='HealthCheck')
            ovips = ovips.filter(
                optionvipenvironmentvip__environment__id=int(id_environment_vip))

            return ovips

        except Exception, e:
            cls.log.error(u'Failure to list all Option Vip Healthcheck.')
            raise OptionVipError(
                e, u'Failure to list all Option Vip Healthcheck.')

    @classmethod
    def get_all_trafficreturn(cls, id_environment_vip):
        """Get All Option Vip Traffic Return by environmentvip_id.

            @return: Get All Option Vip Traffic Return.

            @raise OperationalError: Failed to search for all Option Vip Traffic Return.
        """
        # log = logging.getLogger('get_all_trafficreturn')

        try:

            ovips = OptionVip.objects.all()

            ovips = ovips.filter(tipo_opcao__icontains='trafego')

            # log.info(str(ovips))

            ovips = ovips.filter(
                optionvipenvironmentvip__environment__id=int(id_environment_vip))

            return ovips

        except Exception, e:
            cls.log.error(u'Failure to list all Option Vip Traffic Return.')
            raise OptionVipError(
                e, u'Failure to list all Option Vip Traffic Return.')

    @classmethod
    def get_all_persistencia(cls, id_environment_vip):
        """Get All Option Vip Persistence by environmentvip_id.

            @return: All Option Vip.

            @raise OperationalError: Failed to search for all Option Vip.
        """
        try:

            ovips = OptionVip.objects.all()
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

            ovips = OptionVip.objects.all()
            ovips = ovips.filter(tipo_opcao__icontains='cache')
            ovips = ovips.filter(
                optionvipenvironmentvip__environment__id=int(id_environment_vip))

            return ovips

        except Exception, e:
            cls.log.error(u'Failure to list all Option Vip.')
            raise OptionVipError(e, u'Failure to list all Option Vip.')

    def delete(self, authenticated_user):
        """Override Django's method to remove option vip

        Before removing the option vip removes all relationships with environment vip.
        """

        # Remove all EnvironmentVIP OptionVip related
        for option_environment in OptionVipEnvironmentVip.objects.filter(option=self.id):
            option_environment.delete(authenticated_user)

        super(OptionVip, self).delete(authenticated_user)


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
        'ip.Ip',
        db_column='ips_id_ip',
        blank=True,
        null=True
    )

    ipv6 = models.ForeignKey(
        'ip.Ipv6',
        db_column='ipsv6_id_ipv6',
        blank=True,
        null=True
    )

    trafficreturn = models.ForeignKey(
        'requisicaovips.OptionVip',
        db_column='id_traffic_return',
        default=12, blank=True, null=True
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
        db_column='l7_filter_applied_datetime',
        null=True,
        blank=True
    )

    healthcheck_expect = models.ForeignKey(
        'healthcheckexpect.HealthcheckExpect',
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

    log = logging.getLogger('RequisicaoVips')

    class Meta(BaseModel.Meta):
        db_table = u'requisicao_vips'
        managed = True

    @cached_property
    def dsrl3id(self):

        return DsrL3_to_Vip.objects.filter(requisicao_vip=self)

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
        """Pesquisa e remove uma Requisicao VIP.

        @return: Nothing

        @raise RequisicaoVipsNotFoundError: Requisao VIP não cadastrado.

        @raise RequisicaoVipsError: Falha ao remover Requisao VIP.
        """
        try:
            vip = RequisicaoVips.get_by_pk(vip_id)

            try:
                dsrl3 = DsrL3_to_Vip.get_by_vip_id(vip_id)
                dsrl3.delete(authenticated_user)
            except ObjectDoesNotExist, e:
                pass
            except RequisicaoVipsMissingDSRL3idError, e:
                cls.log.error(
                    u'Requisao Vip nao possui id DSRL3 correspondente cadastrado no banco')
                raise RequisicaoVipsMissingDSRL3idError(
                    e, 'Requisao Vip com id %s possui DSRl3 id não foi encontrado' % vip_id)

            vip.delete()

        except RequisicaoVipsNotFoundError, e:
            cls.log.error(u'Requisao Vip nao encontrada')
            raise RequisicaoVipsNotFoundError(
                e, 'Requisao Vip com id %s nao encontrada' % vip_id)
        except Exception, e:
            cls.log.error(u'Falha ao remover requisicao VIP.')
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
        """Validation when the values ​​of reals_priority.N are all equal, the values ​​should be automatically changed to 0 (zero).

        @param reals_priority_map: List of reals_priority.
        @return: reals_priority_map: List of reals_priority.
        """
        first_value = reals_priority_map[0]
        valid_number_map = []
        for reals_priority in reals_priority_map:
            valid_number_map.append(first_value)

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
        self.variaveis = self.variaveis + str(key) + '=' + str(value) + '\n'

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

    def set_new_variables(self, data):

        Healthcheck = get_model('healthcheckexpect', 'Healthcheck')

        log = logging.getLogger('insert_vip_request_set_new_variables')

        self.variaveis = ''

        finalidade = data.get('finalidade')
        if not is_valid_string_minsize(finalidade, 3) or not is_valid_string_maxsize(finalidade, 50):
            log.error(u'Finality value is invalid: %s.', finalidade)
            raise InvalidValueError(None, 'finalidade', finalidade)

        cliente = data.get('cliente')
        if not is_valid_string_minsize(cliente, 3) or not is_valid_string_maxsize(cliente, 50):
            log.error(u'Client value is invalid: %s.', cliente)
            raise InvalidValueError(None, 'cliente', cliente)

        ambiente = data.get('ambiente')
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
                None, u'Não existe ambiente vip para valores: finalidade %s, cliente %s e ambiente_p44 %s.' % (
                    finalidade, cliente, ambiente))

        timeout = data.get('timeout')
        grupo_cache = data.get('cache')
        persistencia = data.get('persistencia')
        traffic = data.get('trafficreturn')
        if traffic is None:
            traffic = '12'

        trafficint = int(traffic)

        grupos_cache = [(gc.nome_opcao_txt)
                        for gc in OptionVip.get_all_grupo_cache(evip.id)]
        timeouts = [(t.nome_opcao_txt)
                    for t in OptionVip.get_all_timeout(evip.id)]
        persistencias = [(p.nome_opcao_txt)
                         for p in OptionVip.get_all_persistencia(evip.id)]
        traffics = [(tr.id)
                    for tr in OptionVip.get_all_trafficreturn(evip.id)]

        if timeout not in timeouts:
            log.error(
                u'The timeout not in OptionVip, invalid value: %s.', timeout)
            raise InvalidTimeoutValueError(
                None, 'timeout com valor inválido: %s.' % timeout)
        self.add_variable('timeout', timeout)

        if grupo_cache not in grupos_cache:
            log.error(
                u'The grupo_cache is not in OptionVip, invalid value: %s.', grupo_cache)
            raise InvalidCacheValueError(
                None, u'grupo_cache com valor inválido: %s.' % grupo_cache)
        self.add_variable('cache', grupo_cache)

        if persistencia not in persistencias:
            log.error(
                u'The persistencia is not in OptionVip, invalid value: %s.', persistencia)
            raise InvalidPersistenciaValueError(
                None, u'persistencia com valor inválido %s.' % persistencia)
        self.add_variable('persistencia', persistencia)

        if trafficint not in traffics:
            log.error(
                u'The traffic return is not in OptionVip, invalid value: %s.', traffic)
            raise InvalidTrafficReturnValueError(
                None, u'traffic return com valor inválido %s.' % traffic)
        self.add_variable('trafficreturn', traffic)

        priority_pools = []

        # Define priority for Healthcheck
        priority_keys = {'HTTP': 1, 'TCP': 2, 'UDP': 3}

        if self.id:
            pools = ServerPool.objects.filter(
                vipporttopool__requisicao_vip=self)

        else:
            pool_ids = []
            for port_to_pool in data.get('vip_ports_to_pools', []):
                pool_ids.append(port_to_pool.get('server_pool'))

            pools = ServerPool.objects.filter(id__in=pool_ids)

        for pool in pools:

            try:
                # Avoid Pool without Old Healthcheck Data From Database
                healthcheck = pool.healthcheck
            except Healthcheck.DoesNotExist:
                continue

            priority = priority_keys.get(healthcheck.healthcheck_type, 2)
            priority_pools.append((priority, pool.id, pool))

        if priority_pools:
            priority_number, priority_pool_id, priority_pool = min(
                priority_pools, key=lambda itens: itens[0])
            healthcheck_type = priority_pool.healthcheck.healthcheck_type
            # TODO: verify if it is not healthcheck_request instead of
            # healthcheck_expect
            healthcheck = priority_pool.healthcheck.healthcheck_expect
            maxcon = str(priority_pool.default_limit)
            method_bal = priority_pool.lb_method
            self.add_variable('healthcheck_type', healthcheck_type)
            self.add_variable('metodo_bal', method_bal)
            self.add_variable('maxcon', maxcon)
            if healthcheck:
                self.add_variable('healthcheck', healthcheck)

        # Host
        host_name = data.get('host')
        if host_name is not None:
            self.add_variable('host', host_name)

        # dsr
        dsr = data.get('dsr')
        if dsr is not None:
            self.add_variable('dsr', dsr)

        # area negocio
        areanegocio = data.get('areanegocio')
        if areanegocio is not None:
            self.add_variable('areanegocio', areanegocio)

        # nome servico
        nomeservico = data.get('nome_servico')
        if nomeservico is not None:
            self.add_variable('nome_servico', nomeservico)

        if self.variaveis != '':
            self.variaveis = self.variaveis[0:len(self.variaveis) - 1]

    def set_variables(self, variables_map):
        """Constroe e atribui o valor do campo "variaveis" a partir dos dados no mapa.

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
        """

        log = logging.getLogger('insert_vip_request_set_variables')

        self.variaveis = ''

        healthcheck_type = variables_map.get('healthcheck_type')
        if self.healthcheck_expect is not None and healthcheck_type != 'HTTP':
            raise InvalidHealthcheckTypeValueError(
                None, u'Valor do healthcheck_type inconsistente com o valor do healthcheck_expect.')

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
                None, u'Não existe ambiente vip para valores: finalidade %s, cliente %s e ambiente_p44 %s.' % (
                    finalidade, cliente, ambiente))

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
                    None, u'Valor do healthcheck inconsistente com o valor do healthcheck_type.')
            self.add_variable('healthcheck', healthcheck)

        # Host
        host_name = variables_map.get('host')
        if host_name is not None:
            self.add_variable('host', host_name)

        # maxcon
        maxcon = variables_map.get('maxcon')
        try:
            # maxcon_int = int(maxcon)
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
                if (finalidade == 'Homologacao' and ambiente == 'Homologacao FE-CITTA') or (
                        finalidade == 'Producao' and ambiente in ('Portal FE', 'Aplicativos FE', 'Streaming FE')):
                    if not is_valid_ip(transbordo):
                        raise InvalidTransbordoValueError(None, transbordo)
                values = values + transbordo + '|'
            if values != '':
                values = values[0:len(values) - 1]
                self.add_variable('_transbordo', values)

        # # portas_servicos
        # portas_servicos_map = variables_map.get('portas_servicos')
        # if portas_servicos_map is not None:
        #     portas = portas_servicos_map.get('porta')
        #     if len(portas) == 0:
        #         raise InvalidServicePortValueError(None, portas)

        #     i = 1
        #     for porta in portas:
        #         try:
        #             if re.match('[0-9]+:[0-9]+', porta):
        #                 [porta1, porta2] = re.split(':', porta)
        #                 porta1_int = int(porta1)
        #                 porta2_int = int(porta2)
        #             else:
        #                 porta_int = int(porta)
        #         except (TypeError, ValueError):
        #             raise InvalidServicePortValueError(None, porta)
        #         self.add_variable('-portas_servico.' + str(i), porta)
        #         i = i + 1
        # else:
        #     raise InvalidServicePortValueError(None, portas_servicos_map)

        # # reals
        # reals_map = variables_map.get('reals')
        # if (reals_map is not None):
        #     real_maps = reals_map.get('real')

        #     if len(real_maps) == 0:
        #         raise InvalidRealValueError(None, real_maps)

        #     i = 1
        #     for real_map in real_maps:
        #         real_name = real_map.get('real_name')
        #         real_ip = real_map.get('real_ip')
        #         if (real_name is None) or (real_ip is None):
        #             raise InvalidRealValueError(None, '(%s-%s)' % (real_name, real_ip) )
        #         self.add_variable('-reals_name.' + str(i), real_name)
        #         self.add_variable('-reals_ip.' + str(i), real_ip)
        #         i = i + 1

        #     # reals_priority
        #     reals_prioritys_map = variables_map.get('reals_prioritys')
        #     if (reals_prioritys_map is not None):
        #         reals_priority_map = reals_prioritys_map.get('reals_priority')

        #         if len(reals_priority_map) == 0:
        #             raise InvalidPriorityValueError(None, reals_priority_map)

        #         i = 1
        #         for reals_priority in reals_priority_map:

        #             if reals_priority is None:
        #                 raise InvalidRealValueError(None, '(%s)' % reals_priority )

        #             self.add_variable('-reals_priority.' + str(i), reals_priority)
        #             i = i + 1
        #     else:
        #         raise InvalidPriorityValueError(None, reals_prioritys_map)

        #     # reals_weight
        #     if ( str(balanceamento).upper() == "WEIGHTED" ):

        #         # reals_weight
        #         reals_weights_map = variables_map.get('reals_weights')
        #         if (reals_weights_map is not None):
        #             reals_weight_map = reals_weights_map.get('reals_weight')

        #             if len(reals_weight_map) == 0:
        #                 raise InvalidPriorityValueError(None, reals_weight_map)

        #             i = 1
        #             for reals_weight in reals_weight_map:

        #                 if reals_weight is None:
        #                     raise InvalidRealValueError(None, '(%s)' % reals_weight )

        #                 self.add_variable('-reals_weight.' + str(i), reals_weight)
        #                 i = i + 1
        #         else:
        #             raise InvalidWeightValueError(None, reals_weights_map)

        if self.variaveis != '':
            self.variaveis = self.variaveis[0:len(self.variaveis) - 1]

    @classmethod
    def update(cls, authenticated_user, pk, variables_map, **kwargs):
        """Atualiza os dados de uma requisição de VIP.

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
        """
        vip = RequisicaoVips.get_by_pk(pk)

        with distributedlock(LOCK_VIP % pk):

            try:
                ip_id = kwargs['ip_id']
                if vip.ip_id != ip_id:
                    if vip.vip_criado:
                        raise RequisicaoVipsAlreadyCreatedError(
                            None,
                            u'O IP da requisição de VIP %d não pode ser alterado porque o VIP já está criado.' % vip.id)

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
        """Valida uma Requisicao VIP.

        @return: Nothing.

        @raise RequisicaoVipsError: Erro ao validar Requisição de VIP.
        """
        try:
            self.validado = validado

            self.save()
        except RequisicaoVipsError, e:
            self.log.error(u'Falha ao validar a requisição de vip.')
            raise RequisicaoVipsError(
                e, u'Falha ao validar a requisição de vip.')

    def create(self, authenticated_user, variables_map):
        """ Insere uma nova requisição de VIP.

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
        """
        self.ip = Ip().get_by_pk(self.ip.id)

        self.trafficreturn = OptionVip.get_by_pk(self.trafficreturn.id)

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
            self.save()
        except Exception, e:
            self.log.error(u'Falha ao inserir a requisição de vip.')
            raise RequisicaoVipsError(
                e, u'Falha ao inserir a requisição de vip.')

    def valid_values_ports(self, vip_map):
        """Validation when the values ​​of portas_servicos
        This method accept 'port1:port2' and 'port1' only, when the parameter is port1, the method will understand that it means 'por1:por1'

        @param vip_map: Map with the data of the request..

        @return: On success: vip_map, None
                 In case of error: vip_map, code  (code error message).

        @raise InvalidValueError: Represents an error occurred validating a value.
        """

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
                    if not is_valid_regex(port, '[0-9]+:[0-9]+'):
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
        """Validation when the values ​​of reals_priority.N

        @param vip_map: Map with the data of the request..

        @return: On success: vip_map, None
                 In case of error: vip_map, code  (code error message).

        @raise InvalidValueError: Represents an error occurred validating a value.
        """

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
        """Validation when the values ​​of reals_weight.N

        @param vip_map: Map with the data of the request.

        @return: On success: vip_map, None
                 In case of error: vip_map, code  (code error message).

        @raise InvalidValueError: Represents an error occurred validating a value.
        """

        # Valid reals_weight
        reals_weights_map = vip_map.get('reals_weights')
        metodo_bal = vip_map.get('metodo_bal')

        if (str(metodo_bal).upper() == 'WEIGHTED'):

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
        """Validation when the values ​​of healthcheck

        @param vip_map: Map with the data of the request.

        @param vip: request VIP.

        @return: On success: vip_map, vip, None
                 In case of error: vip_map, vip, code  (code error message).

        @raise InvalidValueError: Represents an error occurred validating a value.
        @raise ObjectDoesNotExist: Healthcheck does not exist .
        @raise HealthcheckExpectNotFoundError: The id_healthcheck_expect parameter does not exist.

        """

        HealthcheckExpect = get_model('healthcheckexpect', 'HealthcheckExpect')
        HealthcheckExpectNotFoundError = get_model(
            'healthcheckexpect', 'HealthcheckExpectNotFoundError')

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
            if not (id_healthcheck_expect is None and healthcheck is None):
                self.log.error(
                    u'The healthcheck_type parameter is %s, then healthcheck and id_healthcheck_expect must be None.',
                    healthcheck_type)
                return vip_map, vip, 276
            else:
                vip_map['healthcheck'] = None
                # Set id_healthcheck_expect to None
                vip.healthcheck_expect = None

        # If healthcheck_type is 'HTTP' id_healthcheck_expect and healthcheck
        # must NOT be None
        elif healthcheck_type == 'HTTP':
            if id_healthcheck_expect is None or healthcheck is None:
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

        # Make changes in healthcheck
        # Set healthcheck_type
        vip_map['healthcheck_type'] = healthcheck_type

        return vip_map, vip, None

    @classmethod
    def heathcheck_exist(cls, healthcheck_type, id_evironment_vip):

        health_type_upper = healthcheck_type.upper()

        env_query = Ambiente.objects.filter(
            Q(vlan__networkipv4__ambient_vip__id=id_evironment_vip) |
            Q(vlan__networkipv6__ambient_vip__id=id_evironment_vip)
        )

        environment = env_query and env_query.uniqueResult() or None

        options_pool_environment = environment.opcaopoolambiente_set.all()

        for option_pool_env in options_pool_environment:
            if option_pool_env.opcao_pool.description.upper() == health_type_upper:
                return True

        return False

    @classmethod
    def valid_real_server(cls, ip, equip, evip, valid=True):
        """Validation real server

        @param ip:     IPv4 or Ipv6. 'xxx.xxx.xxx.xxx or xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx:xxxx'
        @param equip:  Equipment
        @param evip:   Environment Vip

        @return: IPv4 or Ipv6, Equipment, Environment Vip

        @raise IpNotFoundByEquipAndVipError:  IP is not related equipment and Environment Vip.
        @raise IpNotFoundError: IP is not registered.
        @raise IpError: Failed to search for the IP.
        """

        Ip = get_model('ip', 'Ip')
        IpNotFoundByEquipAndVipError = get_model(
            'ip', 'IpNotFoundByEquipAndVipError')
        Ipv6 = get_model('ip', 'Ipv6')

        if is_valid_ipv4(ip):

            ip_list = ip.split('.')

            ip = Ip.get_by_octs_and_environment_vip(
                ip_list[0], ip_list[1], ip_list[2], ip_list[3], evip.id, valid)

            lista_ips_equip = list()
            lista_amb_div_4 = list()

            # GET DIVISAO DC AND AMBIENTE_LOGICO OF NET4
            for net in evip.networkipv4_set.all():

                dict_div_4 = dict()
                dict_div_4['divisao_dc'] = net.vlan.ambiente.divisao_dc_id
                dict_div_4[
                    'ambiente_logico'] = net.vlan.ambiente.ambiente_logico_id

                if dict_div_4 not in lista_amb_div_4:
                    lista_amb_div_4.append(dict_div_4)

            # Get all IPV4's Equipment
            for ipequip in equip.ipequipamento_set.all():
                if ipequip.ip not in lista_ips_equip:
                    for dict_div_amb in lista_amb_div_4:
                        if ipequip.ip.networkipv4.ambient_vip is not None and ipequip.ip.networkipv4.ambient_vip.id == evip.id:
                            if (ipequip.ip.networkipv4.vlan.ambiente.divisao_dc_id == dict_div_amb.get(
                                'divisao_dc') and ipequip.ip.networkipv4.vlan.ambiente.ambiente_logico_id == dict_div_amb.get(
                                    'ambiente_logico')):
                                lista_ips_equip.append(ipequip.ip)

            if valid is True:
                if ip not in lista_ips_equip:
                    raise IpNotFoundByEquipAndVipError(None,
                                                       'Ipv4 não está relacionado com equipamento %s e Ambiente Vip: %s' % (
                                                           equip.name, evip.show_environment_vip()))

        elif is_valid_ipv6(ip):

            ip_list = ip.split(':')
            ip = Ipv6.get_by_octs_and_environment_vip(ip_list[0], ip_list[1], ip_list[
                2], ip_list[3], ip_list[4], ip_list[5], ip_list[6], ip_list[7], evip.id, valid)

            lista_amb_div_6 = list()
            lista_ipsv6_equip = list()

            # GET DIVISAO DC AND AMBIENTE_LOGICO OF NET6
            for net in evip.networkipv6_set.all():

                dict_div_6 = dict()
                dict_div_6['divisao_dc'] = net.vlan.ambiente.divisao_dc
                dict_div_6[
                    'ambiente_logico'] = net.vlan.ambiente.ambiente_logico
                if dict_div_6 not in lista_amb_div_6:
                    lista_amb_div_6.append(dict_div_6)

            # Get all IPV6'S Equipment
            for ipequip in equip.ipv6equipament_set.all():
                if ipequip.ip not in lista_ipsv6_equip:
                    for dict_div_amb in lista_amb_div_6:
                        if ipequip.ip.networkipv6.ambient_vip is not None and ipequip.ip.networkipv6.ambient_vip.id == evip.id:
                            if (ipequip.ip.networkipv6.vlan.ambiente.divisao_dc == dict_div_amb.get(
                                'divisao_dc') and ipequip.ip.networkipv6.vlan.ambiente.ambiente_logico == dict_div_amb.get(
                                    'ambiente_logico')):
                                lista_ipsv6_equip.append(ipequip.ip)

            if valid is True:
                if ip not in lista_ipsv6_equip:
                    raise IpNotFoundByEquipAndVipError(None,
                                                       'Ipv6 não está relacionado com equipamento %s e Ambiente Vip: %s' % (
                                                           equip.name, evip.show_environment_vip()))

        else:
            raise InvalidValueError(None, 'ip', ip)

        return ip, equip, evip

    def save_vips_and_ports(self, vip_map, user):
        Healthcheck = get_model('healthcheckexpect', 'Healthcheck')

        HealthcheckExpect = get_model('healthcheckexpect', 'HealthcheckExpect')

        # Ports Vip
        ports_vip_map = vip_map.get('portas_servicos')
        ports_vip = ports_vip_map.get('porta')
        reals = list()

        # Check if one of the req pools is marked as created. Raises an error
        # if so.
        vip_ports_pks = []
        for port_vip in ports_vip:
            vip_ports_pks.append(port_vip.split(':')[0])

        server_pools_antes = ServerPool.objects.filter(vipporttopool__requisicao_vip=self,
                                                       vipporttopool__port_vip__in=vip_ports_pks)

        for server_pool in server_pools_antes:
            if server_pool.pool_created:
                raise RequestVipServerPoolConstraintError(
                    None,
                    'ServerPool %s ja esta indicado como criado no equipamento nao pode ser alterado.' % server_pool.identifier)

        vip_port_list = list()
        # pool_member_pks_removed = list()

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

        lb_method = vip_map.get('metodo_bal', '')

        try:
            healthcheck_type = vip_map.get('healthcheck_type', '')
            healthcheck_type_upper = healthcheck_type.upper()
            healthcheck_request = vip_map.get('healthcheck', '')
            healthcheck_expect = ''
            id_healthcheck_expect = vip_map.get('id_healthcheck_expect', '')

            if id_healthcheck_expect and id_healthcheck_expect != '':
                healthcheck_expect = HealthcheckExpect.get_by_pk(
                    id_healthcheck_expect).match_list

            if healthcheck_request is None:
                healthcheck_request = ''
            healthcheck_request = healthcheck_request.replace(
                chr(10), '\\n').replace(chr(13), '\\r')
            if healthcheck_expect is None:
                healthcheck_expect = ''
            healthcheck_expect = healthcheck_expect.replace(
                chr(10), '\\n').replace(chr(13), '\\r')

            # look for a HT with the given values
            healthcheck_query = Healthcheck.objects.filter(
                healthcheck_type=healthcheck_type_upper,
                healthcheck_request=healthcheck_request,
                healthcheck_expect=healthcheck_expect,
                destination='*:*'
            )

            healthcheck_obj = healthcheck_query.uniqueResult()

        except ObjectDoesNotExist:
            # O codigo acima procura um HT ja existente, mas nao acha.
            # Neste caso, é preciso criar um novo HT na tabela e usar este novo
            # id.
            self.log.debug(
                'Criando um novo Healthcheck, pois o desejado ainda não existe')
            healthcheck_obj = Healthcheck()
            healthcheck_obj.healthcheck_type = healthcheck_type_upper
            healthcheck_obj.healthcheck_request = healthcheck_request
            healthcheck_obj.healthcheck_expect = healthcheck_expect
            healthcheck_obj.destination = '*:*'

            healthcheck_obj.save()

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

            if reals_weights is not None:
                weights = reals_weights.get('reals_weight')

        # save ServerPool and VipPortToPool
        for port_vip in ports_vip:

            port_to_vip = port_vip.split(':')
            default_port = port_to_vip[1]
            vip_port = port_to_vip[0]
            # ip_vip = self.ip or self.ipv6

            # Procura se já existe o pool
            server_pools = ServerPool.objects.filter(vipporttopool__requisicao_vip=self,
                                                     vipporttopool__port_vip=vip_port)

            if server_pools.count() == 0:
                server_pool = ServerPool()

                # Try to get a unique identifier for server pool
                server_pool.identifier = 'VIP' + \
                    str(self.id) + '_pool_' + vip_port
                if ServerPool.objects.filter(identifier=server_pool.identifier):
                    name_not_found = 1
                    retry = 2
                    while name_not_found:
                        server_pool.identifier = 'VIP' + \
                            str(self.id) + '_pool_' + \
                            str(retry) + '_' + vip_port
                        retry += 1
                        if not ServerPool.objects.filter(identifier=server_pool.identifier):
                            name_not_found = 0

                server_pool.environment = environment_obj
                server_pool.pool_created = False

                vip_port_to_pool = VipPortToPool()
                vip_port_to_pool.requisicao_vip = self
                vip_port_to_pool.port_vip = vip_port

            elif server_pools.count() == 1:
                server_pool = server_pools.uniqueResult()
                vip_port_to_pool = VipPortToPool.objects.filter(
                    server_pool=server_pool,
                    requisicao_vip=self
                ).uniqueResult()

            else:
                raise RequisicaoVipsError(
                    None, u'Unexpected error while searching for existing pool.')

            server_pool.default_port = default_port
            server_pool.default_limit = vip_map.get('maxcon')

            if healthcheck_obj is not None:
                server_pool.healthcheck = healthcheck_obj
            server_pool.lb_method = lb_method

            server_pool.save()

            vip_port_to_pool.server_pool = server_pool
            vip_port_to_pool.save()

            vip_port_list.append(
                {'port_vip': vip_port, 'server_pool': server_pool})

        # delete Pools not in port_vip provided above
        vip_ports_pks = []
        for v_port in vip_port_list:
            vip_ports_pks.append(v_port['port_vip'])

        server_pools_to_remove = ServerPool.objects.filter(vipporttopool__requisicao_vip=self).exclude(
            vipporttopool__port_vip__in=vip_ports_pks)
        for sp in server_pools_to_remove:
            self.log.debug('Removendo pool da porta %s' % sp.default_port)
            vip_port_to_pool = VipPortToPool.objects.filter(
                server_pool=sp,
                requisicao_vip=self
            ).uniqueResult()

            vip_port_to_pool.delete()

            # Removing unused ServerPool
            # Safe to remove because server pools are not created (tested
            # earlier)
            vip_port_to_pool = VipPortToPool.objects.filter(
                server_pool=sp)
            if not vip_port_to_pool:
                self.log.info('Removing unused ServerPool %s %s' %
                              (sp.id, sp.identifier))
                sp.delete()

        # save ServerPoolMember
        server_pool_member_pks = []
        for i in range(0, len(reals)):

            weight = ''
            port_real = reals[i].get('port_real')
            port_vip = reals[i].get('port_vip')
            ip_id = reals[i].get('id_ip')

            # Valid port real
            if not is_valid_int_greater_zero_param(port_real):
                self.log.error(
                    u'The reals.port_real parameter is not a valid value: %s.', port_real)
                raise InvalidValueError(None, 'reals.port_real', port_real)

            # Valid ip_id
            if not is_valid_int_greater_zero_param(ip_id):
                self.log.error(
                    u'The reals.ip_id parameter is not a valid value: %s.', ip_id)
                raise InvalidValueError(None, 'reals.ip_id', ip_id)

            for v_port in vip_port_list:
                if v_port['port_vip'] == port_vip:
                    server_pool = v_port['server_pool']

            ipv4 = None
            ipv6 = None
            # Check ip type
            if is_valid_ipv4(reals[i].get('real_ip')):
                ipv4 = Ip().get_by_pk(ip_id)
            else:
                ipv6 = Ipv6().get_by_pk(ip_id)

            priority = prioritys[i]

            if weights is not None:
                if i < len(weights):
                    weight = weights[i]

            # procura se já existe o member
            if server_pool.id is not None:
                server_pool_members = ServerPoolMember.objects.filter(ip=ip_id, port_real=port_real,
                                                                      server_pool=server_pool.id)

            if server_pool_members.count() == 0:
                server_pool_member = ServerPoolMember()
                server_pool_member.server_pool = server_pool
                server_pool_member.ip = ipv4
                server_pool_member.ipv6 = ipv6

            elif server_pool_members.count() == 1:
                server_pool_member = server_pool_members.uniqueResult()
            else:
                raise RequisicaoVipsError(
                    None, u'Unexpected error while searching for existing pool.')

            server_pool_member.port_real = port_real
            server_pool_member.priority = priority
            server_pool_member.weight = weight or 0
            server_pool_member.limit = 0 or vip_map.get('maxcon')

            server_pool_member.save()

            server_pool_member_pks.append(server_pool_member.id)

        # delete members
        server_pool_members_to_delete = ServerPoolMember.objects.filter(server_pool__in=server_pools_antes).exclude(
            id__in=server_pool_member_pks)
        for spm in server_pool_members_to_delete:
            self.log.debug('Removendo server_pool_member %s' % spm.ip)
            spm.delete()

    def get_vips_and_reals(self, id_vip):

        vip_ports = VipPortToPool.get_by_vip_id(id_vip)

        vip_port_list = list()
        reals_list = list()
        reals_priority = list()
        reals_weight = list()

        for v_port in vip_ports:
            full_port = str(v_port.port_vip) + ':' + \
                str(v_port.server_pool.default_port)

            if full_port not in vip_port_list:
                vip_port_list.append(full_port)

            members = v_port.server_pool.serverpoolmember_set.all()

            for member in members:
                try:
                    ip_equip = member.ip.ipequipamento_set.all().uniqueResult()
                    equip_name = ip_equip.equipamento.nome
                    ip_string = mount_ipv4_string(member.ip)
                    ip_id = member.ip.id
                except:
                    ip_equip = member.ipv6.ipv6equipament_set.all().uniqueResult()
                    equip_name = ip_equip.equipamento.nome
                    ip_string = mount_ipv6_string(member.ipv6)
                    ip_id = member.ipv6.id

                real_raw = {
                    'real_ip': ip_string,
                    'real_name': equip_name,
                    'port_vip': v_port.port_vip,
                    'port_real': member.port_real,
                    'id_ip': ip_id
                }

                if real_raw not in reals_list:
                    reals_list.append(real_raw)

                reals_priority.append(member.priority)
                reals_weight.append(member.weight)

        return vip_port_list, reals_list, reals_priority, reals_weight

    def delete_vips_and_reals(self, user):

        vip_ports = VipPortToPool.objects.filter(requisicao_vip=self)
        server_pool_list = list()

        for vip_port in vip_ports:
            # Only deletes pool if it is not in use in any other vip request
            server_pools_still_used = VipPortToPool.objects.filter(server_pool=vip_port.server_pool).exclude(
                requisicao_vip=self)

            if not server_pools_still_used:
                server_pool_members = ServerPoolMember.objects.filter(
                    server_pool=vip_port.server_pool)
                for server_pool_member in server_pool_members:
                    server_pool_member.delete()
                vip_port.delete()
                server_pool_list.append(vip_port.server_pool)

        for server_pool in server_pool_list:
            server_pool.delete()


class OptionVipEnvironmentVip(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id')
    option = models.ForeignKey(OptionVip, db_column='id_opcoesvip')
    environment = models.ForeignKey(EnvironmentVip, db_column='id_ambiente')

    log = logging.getLogger('OptionVipEnvironmentVip')

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
            return OptionVipEnvironmentVip.objects.filter(option__id=option_id,
                                                          environment__id=environment_id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise OptionVipEnvironmentVipNotFoundError(
                e, u'Dont there is a OptionVipEnvironmentVip by option_id = %s and environment_id = %s' % (
                    option_id, environment_id))
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
        max_length=200,
        db_column='identifier'
    )

    healthcheck = models.ForeignKey(
        'healthcheckexpect.Healthcheck',
        db_column='healthcheck_id_healthcheck',
        default=1,
        null=True  # This attribute is here to not raise a exception
    )

    servicedownaction = models.ForeignKey(
        'api_pools.OptionPool',
        db_column='service-down-action_id',
        default=5
    )

    default_port = models.IntegerField(
        db_column='default_port'
    )

    default_limit = models.IntegerField(
        db_column='default_limit'
    )

    pool_created = models.NullBooleanField(
        db_column='pool_criado',
        default=False,
        null=True
    )

    environment = models.ForeignKey(
        Ambiente,
        db_column='ambiente_id_ambiente',
    )

    lb_method = models.CharField(
        max_length=50,
        db_column='lb_method',
    )

    log = logging.getLogger('ServerPool')

    class Meta(BaseModel.Meta):
        db_table = u'server_pool'
        managed = True

    def __str__(self):
        return '{} - {}'.format(self.identifier, self.environment)

    def prepare_and_save(self, default_port, user):
        self.default_port = default_port
        self.save()

    @cached_property
    def vip_ports(self):
        return self.vipporttopool_set.all()

    @cached_property
    def vips(self):
        vips = self.get_vips_related(self.id)

        return vips

    @cached_property
    def dscp(self):
        ports_assoc = self.viprequestportpool_set.select_related('vip_request')
        for poolport in ports_assoc:
            dscp = poolport.vip_request_port.vip_request.viprequestdscp_set.all()
            if dscp:
                return dscp.uniqueResult()
        return None

    @cached_property
    def server_pool_members(self):
        members = self.serverpoolmember_set.all()
        return members

    @cached_property
    def groups_permissions(self):
        ogp_models = get_app('api_ogp', 'models')
        perms = ogp_models.ObjectGroupPermission\
            .get_by_object(self.id, AdminPermission.OBJ_TYPE_POOL)
        return perms

    def get_vips_related(self, pool_id):
        vip_model = get_app('api_vip_request', 'models')

        vips = vip_model.VipRequest.objects.filter(
            viprequestport__viprequestportpool__server_pool__id=pool_id
        )

        return vips

    @classmethod
    def get_by_pk(cls, id):
        """Get ServerPool by id.
            @return: ServerPool.
            @raise ServerPoolNotFoundError: ServerPool is not registered.
            @raise PoolError: Failed to search for the ServerPool.
            @raise OperationalError: Lock wait timeout exceeded.
        """

        exceptions = get_app('api_pools', 'exceptions')

        try:
            return ServerPool.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            cls.log.exception(u'There is no ServerPool with pk = %s.' % id)
            raise exceptions.PoolDoesNotExistException(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the ServerPool.')
            raise exceptions.PoolError(e, u'Failure to search the ServerPool.')

    def create_v3(self, pool, user):
        pool_models = get_app('api_pools', 'models')
        ogp_models = get_app('api_ogp', 'models')
        env_models = get_app('ambiente', 'models')
        hc_models = get_app('healthcheckexpect', 'models')

        # Validate
        self.validate_v3(pool)

        self.identifier = pool.get('identifier')
        self.default_port = pool.get('default_port')
        self.lb_method = pool.get('lb_method')
        self.default_limit = pool.get('default_limit')
        self.pool_created = False

        # Environment
        self.environment = env_models.Ambiente.get_by_pk(
            pool.get('environment'))
        # ServiceDownAction
        self.servicedownaction = pool_models.OptionPool().get_option_pool(
            pool.get('servicedownaction').get('name'),
            'ServiceDownAction'
        )

        # Healthcheck
        healthcheck = {
            'identifier': pool.get('healthcheck')
            .get('identifier'),
            'healthcheck_expect': pool.get('healthcheck')
            .get('healthcheck_expect'),
            'healthcheck_type': pool.get('healthcheck')
            .get('healthcheck_type'),
            'healthcheck_request': pool.get('healthcheck')
            .get('healthcheck_request'),
            'destination': pool.get('healthcheck')
            .get('destination'),
        }

        self.healthcheck = hc_models.Healthcheck()\
            .get_create_healthcheck(healthcheck)

        self.save()

        # Server Pool Members
        for server_pool_member in pool['server_pool_members']:
            server_pool_member['server_pool'] = self.id
            sp = ServerPoolMember()
            sp.create_v3(server_pool_member)

        # Permissions
        perm = ogp_models.ObjectGroupPermission()
        perm.create_perms(pool, self.id, AdminPermission.OBJ_TYPE_POOL, user)

    def update_v3(self, pool, user, permit_created=False):

        pool_models = get_app('api_pools', 'models')
        pool_exceptions = get_app('api_pools', 'models')
        ogp_models = get_app('api_ogp', 'models')
        env_models = get_app('ambiente', 'models')
        hc_models = get_app('healthcheckexpect', 'models')

        if self.dscp:
            if self.default_port != pool.get('default_port'):
                raise pool_exceptions.PoolError(
                    'DRSL3 Restriction: Pool {} cannot change port'.format(
                        str(self)
                    )
                )

        # Validate
        self.validate_v3(pool, permit_created)

        self.identifier = pool.get('identifier')
        self.default_port = pool.get('default_port')
        self.lb_method = pool.get('lb_method')
        self.default_limit = pool.get('default_limit')

        # Environment
        self.environment = env_models.Ambiente.get_by_pk(
            pool.get('environment'))
        # ServiceDownAction
        self.servicedownaction = pool_models.OptionPool().get_option_pool(
            pool.get('servicedownaction').get('name'),
            'ServiceDownAction'
        )

        # Healthcheck
        healthcheck = {
            'identifier': pool.get('healthcheck')
            .get('identifier'),
            'healthcheck_expect': pool.get('healthcheck')
            .get('healthcheck_expect'),
            'healthcheck_type': pool.get('healthcheck')
            .get('healthcheck_type'),
            'healthcheck_request': pool.get('healthcheck')
            .get('healthcheck_request'),
            'destination': pool.get('healthcheck')
            .get('destination'),
        }
        self.healthcheck = hc_models.Healthcheck()\
            .get_create_healthcheck(healthcheck)

        self.save()

        # Server Pool Members to delete
        members_ids = [member['id'] for member in pool['server_pool_members']
                       if member['id']]
        for server_pool_member in self.serverpoolmember_set.all():
            if server_pool_member.id not in members_ids:
                sp = ServerPoolMember.get_by_pk(server_pool_member.id)
                sp.delete()

        # Server Pool Members to create
        for server_pool_member in pool['server_pool_members']:
            if server_pool_member.get('id', None) is None:
                server_pool_member['server_pool'] = self.id
                spm = ServerPoolMember()
                spm.create_v3(server_pool_member)

        # Server Pool Members to update
        for server_pool_member in pool['server_pool_members']:
            if server_pool_member.get('id', None) is not None:
                server_pool_member['server_pool'] = self.id
                spm = ServerPoolMember.get_by_pk(server_pool_member.get('id'))
                spm.update_v3(server_pool_member)

        # Permissions
        perm = ogp_models.ObjectGroupPermission()
        perm.update_perms(pool, self.id, AdminPermission.OBJ_TYPE_POOL, user)

    def delete_v3(self):
        ogp_models = get_app('api_ogp', 'models')
        pools_exceptions = get_app('api_pools', 'exceptions')

        id_pool = self.id

        if self.pool_created:
            raise pools_exceptions.PoolConstraintCreatedException()

        if self.vips:
            raise pools_exceptions.PoolError('Pool has related with VIPs')

        # Deletes Server Pool Members
        ServerPoolMember.objects.filter(server_pool=id_pool).delete()

        self.delete()

        # Deletes Permissions
        ogp_models.ObjectGroupPermission.objects.filter(
            object_type__name=AdminPermission.OBJ_TYPE_POOL,
            object_value=id_pool
        ).delete()

    def validate_v3(self, pool, permit_created=False):

        pool_exceptions = get_app('api_pools', 'exceptions')

        has_identifier = ServerPool.objects.filter(
            identifier=pool['identifier'],
            environment=pool['environment']
        )

        if pool.get('id'):
            server_pool = ServerPool.objects.get(id=pool['id'])
            if server_pool.pool_created:
                if not permit_created:
                    raise pool_exceptions\
                        .CreatedPoolValuesException(
                            'Pool: %s' % str(server_pool))

                # identifier changed
                if server_pool.identifier != pool['identifier']:
                    raise pool_exceptions\
                        .PoolNameChange('Pool: %s' % str(server_pool))

                # Environment changed
                if server_pool.environment_id != pool['environment']:
                    raise pool_exceptions\
                        .PoolEnvironmentChange('Pool: %s' %
                                               str(server_pool))

            # members_db = [spm.id for spm in server_pool.serverpoolmember_set.
            # all()]
            has_identifier = has_identifier.exclude(id=pool['id'])

        # Name duplicated
        if has_identifier.count() > 0:
            raise pool_exceptions.InvalidIdentifierAlreadyPoolException()

        for member in pool['server_pool_members']:

            amb = Ambiente.objects.filter(Q(
                environmentenvironmentvip__environment_vip__in=EnvironmentVip.
                objects.filter(
                    networkipv4__vlan__ambiente=pool['environment']
                )) | Q(
                environmentenvironmentvip__environment_vip__in=EnvironmentVip.
                objects.filter(
                    networkipv6__vlan__ambiente=pool['environment']
                ))
            ).distinct()

            if member.get('ip', None) is not None:
                amb = amb.filter(
                    vlan__networkipv4__ip=member['ip']['id']
                )
                # Ip not found environment
                if not amb:
                    raise pool_exceptions.IpNotFoundByEnvironment(
                        'Environment of IP:%s and different of environment '
                        'of server pool: %s' %
                        (member['ip']['id'], pool['identifier'])
                    )

            if member.get('ipv6', None) is not None:
                amb = amb.filter(
                    vlan__networkipv6__ipv6=member['ipv6']['id']
                )

                # Ip not found environment
                if not amb:
                    raise pool_exceptions.IpNotFoundByEnvironment(
                        'Environment of IP:%s and different of environment '
                        'of server pool: %s' %
                        (member['ipv6']['id'], pool['identifier'])
                    )


class ServerPoolMember(BaseModel):
    id = models.AutoField(
        primary_key=True,
        db_column='id_server_pool_member'
    )

    server_pool = models.ForeignKey(
        ServerPool,
        db_column='id_server_pool'
    )

    identifier = models.CharField(
        max_length=200
    )

    ip = models.ForeignKey(
        'ip.Ip',
        db_column='ips_id_ip',
        null=True
    )

    ipv6 = models.ForeignKey(
        'ip.Ipv6',
        db_column='ipsv6_id_ipv6',
        null=True
    )

    priority = models.IntegerField()

    weight = models.IntegerField(
        db_column='weight'
    )

    limit = models.IntegerField()

    port_real = models.IntegerField(
        db_column='port'
    )

    healthcheck = models.ForeignKey(
        'healthcheckexpect.Healthcheck',
        db_column='healthcheck_id_healthcheck',
        null=True
    )

    member_status = models.IntegerField(
        db_column='status',
        default=3
    )

    last_status_update = models.DateTimeField(
        null=True
    )

    log = logging.getLogger('ServerPoolMember')

    class Meta(BaseModel.Meta):
        db_table = u'server_pool_member'
        managed = True

    def __str__(self):
        spm = '{}:{}'.format(
            (self.ip.ip_formated if self.ip else self.ipv6.ip_formated),
            self.port_real)
        return spm

    @classmethod
    def get_spm_by_eqpt_id(cls, eqpts_id):

        spm = ServerPoolMember.objects.filter(
            Q(ip__ipequipamento__equipamento__id__in=eqpts_id) |
            Q(ipv6__ipv6equipament__equipamento__id__in=eqpts_id)
        )

        return spm

    @cached_property
    def equipment(self):
        ipv4 = self.ip
        ipv6 = self.ipv6

        ip_equipment_set = ipv4 and ipv4.ipequipamento_set or ipv6 and ipv6.ipv6equipament_set

        for ipequip in ip_equipment_set.select_related('equipamento'):
            if ipequip.equipamento.nome == self.identifier:
                return ipequip.equipamento

        ip_equipment_obj = ip_equipment_set.select_related(
            'equipamento').uniqueResult()
        equipamento = ip_equipment_obj.equipamento

        return equipamento

    @cached_property
    def equipments(self):
        eqpts = list()
        if self.ip:
            eqpts = self.ip.ipequipamento_set.all()\
                .select_related('equipamento')
        if self.ipv6:
            eqpts |= self.ipv6.ipv6equipament_set.all()\
                .select_related('equipamento')
        eqpts = [eqpt.equipamento for eqpt in eqpts]
        return eqpts

    @cached_property
    def last_status_update_formated(self):
        formated = None
        if self.last_status_update:
            formated = self.last_status_update.strftime('%d/%m/%Y %H:%M:%S')

        return formated

    @classmethod
    def get_by_pk(cls, id):
        """Get ServerPoolMember by id.
            @return: ServerPoolMember.
            @raise PoolMemberDoesNotExistException: ServerPoolMember is not registered.
            @raise PoolError: Failed to search for the ServerPoolMember.
            @raise OperationalError: Lock wait timeout exceeded.
        """

        exceptions = get_app('api_pools', 'exceptions')

        try:
            return ServerPoolMember.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            cls.log.exception(
                u'There is no ServerPoolMember with pk = %s.' % id)
            raise exceptions.PoolMemberDoesNotExistException(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the ServerPoolMember.')
            raise exceptions.PoolError(
                e, u'Failure to search the ServerPoolMember.')

    def prepare_and_save(self, server_pool, ip, ip_type, priority,
                         weight, port_real, user, commit=False):

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

        if server_pools.count() == 0:
            raise RequestVipWithoutServerPoolError(
                None, "Vip's request has no registered server pool")

        for server_pool in server_pools:
            server_pool_member = ServerPoolMember()
            server_pool_member.prepare_and_save(
                server_pool, ip, ip_version, 0, 1, server_pool.default_port, user, commit=True)

    def save_specified_port(self, vip_id, port_vip, ip, ip_version, port_real, user):
        """ Save with commit = True """
        vipporttopool = VipPortToPool.objects.filter(
            requisicao_vip__id=vip_id, port_vip=port_vip)

        if vipporttopool.count() == 0:
            raise RequestVipWithoutServerPoolError(
                None, "Vip's request has no registered server pool")

        if vipporttopool:
            vipporttopool = vipporttopool[0]
            ServerPoolMember().prepare_and_save(
                vipporttopool.server_pool, ip, ip_version, 0, 1, port_real, user, commit=True)

    def create_v3(self, member):
        """
        Creates pool member.

        @raise ServerPoolNotFoundError
        @raise PoolError
        @raise OperationalError
        @raise IpNotFoundError
        @raise IpError
        """

        model_ip = get_model('ip', 'Ip')
        model_ipv6 = get_model('ip', 'Ipv6')
        pools_exceptions = get_app('api_pools', 'exceptions')

        # Server Pool
        self.server_pool = ServerPool.get_by_pk(member['server_pool'])
        # Ip
        self.ip = model_ip.get_by_pk(member['ip']['id']) \
            if member['ip'] else None
        # Ipv6
        self.ipv6 = model_ipv6.get_by_pk(member['ipv6']['id']) \
            if member['ipv6'] else None

        identifier = self.ip.ip_formated if self.ip else self.ipv6.ip_formated
        self.identifier = identifier
        self.weight = member['weight']
        self.priority = member['priority']
        self.port_real = member['port_real']
        self.member_status = member['member_status']
        self.limit = member['limit']
        # vip with dsrl3 using pool
        if self.server_pool.dscp:

            mbs = self.get_spm_by_eqpt_id(self.equipments)

            # check all the pools related to this pool vip request to filter
            # dscp value
            related_viprequestports = self.server_pool.vips[0]\
                .viprequestport_set.all()
            vippools = [p.viprequestportpool_set.all()[0].server_pool_id
                        for p in related_viprequestports]

            sps = ServerPool.objects.filter(
                serverpoolmember__in=mbs).exclude(id__in=vippools)
            dscps = [sp.dscp for sp in sps]

            if self.server_pool.dscp in dscps:
                raise pools_exceptions.PoolError(
                    'DRSL3 Restriction: Pool Member {} cannot be insert'
                    ' in Pool {}, because already in other pool'.format(
                        str(self), str(self.server_pool)
                    )
                )

            if self.port_real != self.server_pool.default_port:
                raise pools_exceptions.PoolError(
                    'DRSL3 Restriction: Pool Member {} cannot have different'
                    ' port of Pool {}'.format(
                        str(self), str(self.server_pool)
                    )
                )

        self.save()

    def update_v3(self, member):
        """
        Creates pool member.

        @raise ServerPoolNotFoundError
        @raise PoolError
        @raise OperationalError
        @raise IpNotFoundError
        @raise IpError
        """

        model_ip = get_model('ip', 'Ip')
        model_ipv6 = get_model('ip', 'Ipv6')
        pools_exceptions = get_app('api_pools', 'exceptions')

        # Ip
        self.ip = model_ip.get_by_pk(member['ip']['id']) \
            if member['ip'] else None
        # Ipv6
        self.ipv6 = model_ipv6.get_by_pk(member['ipv6']['id']) \
            if member['ipv6'] else None

        self.weight = member['weight']
        self.priority = member['priority']
        self.port_real = member['port_real']
        self.member_status = member['member_status']
        self.limit = member['limit']
        self.save()

        if self.server_pool.dscp:
            if self.port_real != self.server_pool.default_port:

                raise pools_exceptions.PoolError(
                    'DRSL3 Restriction: Pool Member {} cannot have different'
                    ' port of Pool {}'.format(
                        str(self), str(self.server_pool)
                    )
                )


class VipPortToPool(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_vip_port_to_pool')

    requisicao_vip = models.ForeignKey(
        RequisicaoVips, db_column='id_requisicao_vips')

    server_pool = models.ForeignKey(ServerPool, db_column='id_server_pool')

    port_vip = models.IntegerField(db_column='vip_port')

    identifier = models.CharField(
        max_length=255,
        db_column='identifier',
        null=True
    )

    class Meta(BaseModel.Meta):
        db_table = u'vip_port_to_pool'
        managed = True

    def prepare_and_save(self, port_vip, server_pool, vip, user):

        self.requisicao_vip = vip
        self.server_pool = server_pool
        self.port_vip = port_vip

        self.save()

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


class DsrL3_to_Vip(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_dsrl3_to_vip')

    requisicao_vip = models.ForeignKey(
        RequisicaoVips, db_column='id_requisicao_vips')

    id_dsrl3 = models.IntegerField(db_column='id_dsrl3')

    log = logging.getLogger('DsrL3_to_Vip')

    class Meta(BaseModel.Meta):
        db_table = u'dsrl3_to_vip'
        managed = True

    def prepare_and_save(self, id_dsrl3, vip, user):

        self.requisicao_vip = vip
        self.id_dsrl3 = id_dsrl3

        self.save(user)

    def get_dsrl3(self, id_vip, user):

        dscp = 4
        dscp_exists = 1
        while dscp_exists:
            dscp_exists = DsrL3_to_Vip.objects.filter(id_dsrl3=dscp)
            if dscp_exists:
                dscp = dscp + 1

        self.prepare_and_save(dscp, id_vip, user)

        return dscp

    @classmethod
    def get_by_vip_id(cls, id_vip):
        """Get Request VipPortToPool associated with id_vip.

            @return: Request VipPortToPool with given id_vip.

            @raise RequisicaoVipsError: Failed to search for VipPortToPool.
        """
        try:
            return DsrL3_to_Vip.objects.filter(
                requisicao_vip__id=id_vip).uniqueResult()
        except ObjectDoesNotExist, e:
            raise ObjectDoesNotExist(
                e, u'There is not DSRL3 entry for vip = %s.' % id_vip)
        except Exception, e:
            cls.log.error(u'Failure to list id of DSR L3 by id_vip.')
            raise RequisicaoVipsError(
                e, u'Failure to list Request DsrL3_to_Vip by id_vip.')

    @classmethod
    def get_all(cls):
        """Get All Option Vip.

            @return: All Option Vip.

            @raise OperationalError: Failed to search for all Option Vip.
        """
        try:
            return DsrL3_to_Vip.objects.all()
        except Exception, e:
            cls.log.error(u'Failure to list all DsrL3_to_Vip .')
            raise OptionVipError(e, u'Failure to list all DsrL3_to_Vip.')
