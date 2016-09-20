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
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.query_utils import Q
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict

from networkapi.exception import EnvironmentEnvironmentVipDuplicatedError
from networkapi.exception import EnvironmentEnvironmentVipError
from networkapi.exception import EnvironmentEnvironmentVipNotFoundError
from networkapi.exception import EnvironmentVipError
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.filter.models import CannotDissociateFilterError
from networkapi.filter.models import Filter
from networkapi.filter.models import FilterNotFoundError
from networkapi.models.BaseModel import BaseModel
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.util import is_valid_text


class AmbienteError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com ambiente."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class AmbienteNotFoundError(AmbienteError):

    """Retorna exceção para pesquisa de ambiente por chave primária."""

    def __init__(self, cause, message=None):
        AmbienteError.__init__(self, cause, message)


class AmbienteDuplicatedError(AmbienteError):

    """Retorna exceção porque existe um Ambiente cadastrada com os mesmos nomes
       de grupo layer 3, ambiente lógico e divisão DC."""

    def __init__(self, cause, message=None):
        AmbienteError.__init__(self, cause, message)


class AmbienteUsedByEquipmentVlanError(AmbienteError):

    """Retorna exceção se houver tentativa de exclusão de um Ambiente utilizado
       por algum equipamento ou alguma VLAN."""

    def __init__(self, cause, message=None):
        AmbienteError.__init__(self, cause, message)


class IPConfigError(Exception):

    """Generic exception for everything related to IPConfig."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Caused by: %s, Message: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class IPConfigNotFoundError(IPConfigError):

    """Exception generated when IPConfig was not found in database"""

    def __init__(self, cause, message=None):
        IPConfigError.__init__(self, cause, message)


class ConfigEnvironmentError(Exception):

    """Generic exception for everything related to ConfigEnvironment."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Caused by: %s, Message: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class ConfigEnvironmentNotFoundError(ConfigEnvironmentError):

    """Exception generated when ConfigEnvironment was not found in database"""

    def __init__(self, cause, message=None):
        ConfigEnvironmentError.__init__(self, cause, message)


class ConfigEnvironmentInvalidError(ConfigEnvironmentError):

    """Exception generated when ConfigEnvironment was not found in database"""

    def __init__(self, cause, message=None):
        ConfigEnvironmentError.__init__(self, cause, message)


class ConfigEnvironmentDuplicateError(ConfigEnvironmentError):

    """Exception generated when ConfigEnvironment Duplicate Environment and IpConfig"""

    def __init__(self, cause, message=None):
        ConfigEnvironmentError.__init__(self, cause, message)


class DivisaoDcNotFoundError(AmbienteError):

    """Retorna exceção para pesquisa de Divisão DataCenter pelo nome."""

    def __init__(self, cause, message=None):
        AmbienteError.__init__(self, cause, message)


class DivisaoDcNameDuplicatedError(AmbienteError):

    """Retorna exceção porque existe uma Divisão DataCenter cadastrada com o mesmo nome."""

    def __init__(self, cause, message=None):
        AmbienteError.__init__(self, cause, message)


class DivisaoDcUsedByEnvironmentError(AmbienteError):

    """Retorna exceção se houver tentativa de exclusão de uma Divisão DC utilizada por algum ambiente."""

    def __init__(self, cause, message=None):
        AmbienteError.__init__(self, cause, message)


class GrupoL3NameDuplicatedError(AmbienteError):

    """Retorna exceção porque existe um GrupoL3 cadastrada com o mesmo nome."""

    def __init__(self, cause, message=None):
        AmbienteError.__init__(self, cause, message)


class GrupoL3UsedByEnvironmentError(AmbienteError):

    """Retorna exceção se houver tentativa de exclusão de um GrupoL3 utilizado por algum ambiente."""

    def __init__(self, cause, message=None):
        AmbienteError.__init__(self, cause, message)


class AmbienteLogicoNotFoundError(AmbienteError):

    """Retorna exceção para pesquisa de ambiente lógico por chave primária."""

    def __init__(self, cause, message=None):
        AmbienteError.__init__(self, cause, message)


class AmbienteLogicoNameDuplicatedError(AmbienteError):

    """Retorna exceção porque existe uma Divisão DataCenter cadastrada com o mesmo nome."""

    def __init__(self, cause, message=None):
        AmbienteError.__init__(self, cause, message)


class AmbienteLogicoUsedByEnvironmentError(AmbienteError):

    """Retorna exceção se houver tentativa de exclusão de um Ambiente Lógico utilizado por algum ambiente."""

    def __init__(self, cause, message=None):
        AmbienteError.__init__(self, cause, message)


class GroupL3NotFoundError(AmbienteError):

    """Exception generated when GroupL3 was not found in database"""

    def __init__(self, cause, message=None):
        AmbienteError.__init__(self, cause, message)


class GrupoL3(BaseModel):
    CITTA_CD = 'CITTA CORE/DENSIDADE'
    id = models.AutoField(primary_key=True, db_column='id_grupo_l3')
    nome = models.CharField(unique=True, max_length=80)

    log = logging.getLogger('GrupoL3')

    class Meta(BaseModel.Meta):
        db_table = u'grupo_l3'
        managed = True

    @classmethod
    def get_by_name(cls, name):
        """"Get Group L3 by name.

        @return: Group L3.

        @raise GroupL3NotFoundError: Group L3 is not registered.
        @raise AmbienteError: Failed to search for the Group L3.
        """
        try:
            return GrupoL3.objects.get(nome__iexact=name)
        except ObjectDoesNotExist, e:
            raise GroupL3NotFoundError(
                e, u'Dont there is a Group L3 by name = %s.' % name)
        except Exception, e:
            cls.log.error(u'Failure to search the Group L3.')
            raise AmbienteError(e, u'Failure to search the Group L3.')

    @classmethod
    def get_by_pk(cls, idt):
        """"Get  Group L3 by id.

        @return: Group L3.

        @raise GroupL3NotFoundError: Group L3 is not registered.
        @raise AmbienteError: Failed to search for the Group L3.
        """
        try:
            return GrupoL3.objects.filter(id=idt).uniqueResult()
        except ObjectDoesNotExist, e:
            raise GroupL3NotFoundError(
                e, u'Dont there is a Group L3 by pk = %s.' % idt)
        except Exception, e:
            cls.log.error(u'Failure to search the Group L3.')
            raise AmbienteError(e, u'Failure to search the Group L3.')


class DivisaoDc(BaseModel):
    BE = 'BE'
    FE = 'FE'

    id = models.AutoField(primary_key=True, db_column='id_divisao')
    nome = models.CharField(unique=True, max_length=100)

    log = logging.getLogger('DivisaoDc')

    class Meta(BaseModel.Meta):
        db_table = u'divisao_dc'
        managed = True

    @classmethod
    def get_by_pk(cls, idt):
        """"Get Division Dc by id.

        @return: Division Dc.

        @raise DivisaoDcNotFoundError: Division Dc is not registered.
        @raise AmbienteError: Failed to search for the Division Dc.
        """
        try:
            return DivisaoDc.objects.filter(id=idt).uniqueResult()
        except ObjectDoesNotExist, e:
            raise DivisaoDcNotFoundError(
                e, u'Dont there is a Division Dc by pk = %s.' % idt)
        except Exception, e:
            cls.log.error(u'Failure to search the Division Dc.')
            raise AmbienteError(e, u'Failure to search the Division Dc.')

    @classmethod
    def get_by_name(cls, name):
        """"Get Division Dc by name.

        @return:Division Dc.

        @raise AmbienteLogicoNotFoundError: Division Dc is not registered.
        @raise AmbienteError: Failed to search for the Division Dc.
        """
        try:
            return DivisaoDc.objects.get(nome__iexact=name)
        except ObjectDoesNotExist, e:
            raise DivisaoDcNotFoundError(
                e, u'Dont there is a Division Dc by name = %s.' % name)
        except Exception, e:
            cls.log.error(u'Failure to search the Division Dc.')
            raise AmbienteError(e, u'Failure to search the Division Dc.')


class AmbienteLogico(BaseModel):
    HOMOLOGACAO = 'HOMOLOGACAO'

    id = models.AutoField(primary_key=True, db_column='id_ambiente_logic')
    nome = models.CharField(unique=True, max_length=80)

    log = logging.getLogger('AmbienteLogico')

    class Meta(BaseModel.Meta):
        db_table = u'ambiente_logico'
        managed = True

    @classmethod
    def get_by_pk(cls, idt):
        """"Get Logical Environment by id.

        @return: Logical Environment.

        @raise AmbienteLogicoNotFoundError: Logical Environment is not registered.
        @raise AmbienteError: Failed to search for the Logical Environment.
        """
        try:
            return AmbienteLogico.objects.filter(id=idt).uniqueResult()
        except ObjectDoesNotExist, e:
            raise AmbienteLogicoNotFoundError(
                e, u'Dont there is a Logical Environment by pk = %s.' % idt)
        except Exception, e:
            cls.log.error(u'Failure to search the Logical Environment.')
            raise AmbienteError(
                e, u'Failure to search the Logical Environment.')

    @classmethod
    def get_by_name(cls, name):
        """"Get Logical Environment by name.

        @return: Logical Environment.

        @raise AmbienteLogicoNotFoundError: Logical Environment is not registered.
        @raise AmbienteError: Failed to search for the Logical Environment.
        """
        try:
            return AmbienteLogico.objects.get(nome__iexact=name)
        except ObjectDoesNotExist, e:
            raise AmbienteLogicoNotFoundError(
                e, u'Dont there is a Logical Environment by name = %s.' % name)
        except Exception, e:
            cls.log.error(u'Failure to search the Logical Environment.')
            raise AmbienteError(
                e, u'Failure to search the Logical Environment.')


class EnvironmentVip(BaseModel):

    id = models.AutoField(
        primary_key=True
    )

    finalidade_txt = models.CharField(
        max_length=50,
        blank=False,
        db_column='finalidade_txt'
    )

    cliente_txt = models.CharField(
        max_length=50,
        blank=False,
        db_column='cliente_txt'
    )

    ambiente_p44_txt = models.CharField(
        max_length=50,
        blank=False,
        db_column='ambiente_p44_txt'
    )

    description = models.CharField(
        max_length=50,
        blank=False,
        db_column='description'
    )

    conf = models.TextField(
        blank=False,
        db_column='conf'
    )

    log = logging.getLogger('EnvironmentVip')

    class Meta(BaseModel.Meta):
        db_table = u'ambientevip'
        managed = True

    def _get_name(self):
        "Returns complete name for environment."
        return '%s - %s - %s' % (self.finalidade_txt, self.cliente_txt, self.ambiente_p44_txt)

    name = property(_get_name)

    @classmethod
    def get_by_pk(cls, id):
        """"Get  Environment Vip by id.

        @return: Environment Vip.

        @raise EnvironmentVipNotFoundError: Environment Vip is not registered.
        @raise EnvironmentVipError: Failed to search for the Environment Vip.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return EnvironmentVip.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise EnvironmentVipNotFoundError(
                e, u'There is no environment vip by pk = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the request vip.')
            raise EnvironmentVipError(
                e, u'Failure to search the environment vip.')

    @classmethod
    def get_by_values(cls, finalidade, cliente, ambiente_p44):
        """"Get  Environment Vip by id.

        @return: Environment Vip.

        @raise EnvironmentVipNotFoundError: Environment Vip is not registered.
        @raise EnvironmentVipError: Failed to search for the Environment Vip.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return EnvironmentVip.objects.filter(
                finalidade_txt=finalidade,
                cliente_txt=cliente,
                ambiente_p44_txt=ambiente_p44
            ).uniqueResult()
        except ObjectDoesNotExist, e:
            raise EnvironmentVipNotFoundError(
                e, u'Dont there is a request of environment vip by values = %s,%s,%s.' % (finalidade, cliente, ambiente_p44))
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the request vip.')
            raise EnvironmentVipError(
                e, u'Failure to search the environment vip.')

    def list_all_finalitys(self):
        """Get  all finalidade_txt of environment VIPs with distinct.

        @return: Environment Vip.

        @raise EnvironmentVipNotFoundError: Environment Vip is not registered.
        @raise EnvironmentVipError: Failed to search for the Environment Vip.
        @raise OperationalError: Lock wait timeout exceeded.
        """

        try:

            return EnvironmentVip.objects.values(
                'finalidade_txt'
            ).order_by(
                'finalidade_txt'
            ).distinct()

        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the request vip.')
            raise EnvironmentVipError(
                e, u'Failure to search the environment vip.')

    def list_all_clientes_by_finalitys(self, finalidade):
        """Get cliente_txt by finalidade_txt with distinct.

        @return: Environment Vip.

        @raise EnvironmentVipNotFoundError: Environment Vip is not registered.
        @raise EnvironmentVipError: Failed to search for the Environment Vip.
        @raise OperationalError: Lock wait timeout exceeded.
        """

        try:

            return EnvironmentVip.objects.filter(
                finalidade_txt__iexact=finalidade
            ).values(
                'cliente_txt'
            ).order_by(
                'cliente_txt'
            ).distinct()

        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the request vip.')
            raise EnvironmentVipError(
                e, u'Failure to search the environment vip.')

    def list_all_ambientep44_by_finality_and_cliente(self, finalidade, cliente_txt):
        """Get  Environment Vip by id.

        @return: Environment Vip.

        @raise EnvironmentVipNotFoundError: Environment Vip is not registered.
        @raise EnvironmentVipError: Failed to search for the Environment Vip.
        @raise OperationalError: Lock wait timeout exceeded.
        """

        try:

            return EnvironmentVip.objects.filter(
                finalidade_txt__iexact=finalidade,
                cliente_txt__iexact=cliente_txt
            ).order_by(
                'finalidade_txt',
                'cliente_txt',
                'ambiente_p44_txt'
            )

        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the request vip.')
            raise EnvironmentVipError(
                e, u'Failure to search the environment vip.')

    def valid_environment_vip(self, environmentvip_map):
        '''Validate the values ​​of environment vip

        @param environmentvip_map: Map with the data of the request.

        @raise InvalidValueError: Represents an error occurred validating a value.
        '''

        # Get XML data
        finalidade_txt = environmentvip_map.get('finalidade_txt')
        cliente_txt = environmentvip_map.get('cliente_txt')
        ambiente_p44_txt = environmentvip_map.get('ambiente_p44_txt')
        description = environmentvip_map.get('description')

        # finalidade_txt can NOT be greater than 50 or lesser than 3
        if not is_valid_string_maxsize(finalidade_txt, 50, True) or not is_valid_string_minsize(finalidade_txt, 3, True) or not is_valid_text(finalidade_txt):
            self.log.error(
                u'Parameter finalidade_txt is invalid. Value: %s.', finalidade_txt)
            raise InvalidValueError(None, 'finalidade_txt', finalidade_txt)

        # cliente_txt can NOT be greater than 50 or lesser than 3
        if not is_valid_string_maxsize(cliente_txt, 50, True) or not is_valid_string_minsize(cliente_txt, 3, True) or not is_valid_text(cliente_txt):
            self.log.error(
                u'Parameter cliente_txt is invalid. Value: %s.', cliente_txt)
            raise InvalidValueError(None, 'cliente_txt', cliente_txt)

        # ambiente_p44_txt can NOT be greater than 50 or lesser than 3
        if not is_valid_string_maxsize(ambiente_p44_txt, 50, True) or not is_valid_string_minsize(ambiente_p44_txt, 3, True) or not is_valid_text(ambiente_p44_txt):
            self.log.error(
                u'Parameter ambiente_p44_txt is invalid. Value: %s.', ambiente_p44_txt)
            raise InvalidValueError(None, 'ambiente_p44_txt', ambiente_p44_txt)

        if not is_valid_string_maxsize(description, 50, True) or not is_valid_string_minsize(description, 3, True) or not is_valid_text(description):
            self.log.error(
                u'Parameter description is invalid. Value: %s.', description)
            raise InvalidValueError(None, 'description', description)

        # set variables
        self.finalidade_txt = finalidade_txt
        self.cliente_txt = cliente_txt
        self.ambiente_p44_txt = ambiente_p44_txt
        self.description = description

    def delete(self):
        '''Override Django's method to remove environment vip

        Before removing the environment vip removes all relationships with option vip.
        '''
        from networkapi.requisicaovips.models import OptionVipEnvironmentVip

        # Remove all EnvironmentVIP OptionVip related
        for option_environment in OptionVipEnvironmentVip.objects.filter(environment=self.id):
            option_environment.delete()

        super(EnvironmentVip, self).delete()

    def show_environment_vip(self):
        return "%s - %s - %s" % (self.finalidade_txt, self.cliente_txt, self.ambiente_p44_txt)

    def available_evips(self, evips, id_vlan):
        # The model couldn't be imported in the top of the file. It is a UWSGI bug, where
        # the installed apps in settings.py are imported alphabetically instead of the order
        # defined in INSTALLED_APPS. So, the NetworkAPI does not run if this import is placed
        # in the begin of this file.
        from networkapi.vlan.models import Vlan
        from networkapi.ip.models import NetworkIPv4, NetworkIPv6
        evip_list = []
        vlan = Vlan.objects.get(id=id_vlan)
        environment = vlan.ambiente

        for evip in evips:
            networkipv4 = NetworkIPv4.objects.filter(ambient_vip=evip.id)
            networkipv6 = NetworkIPv6.objects.filter(ambient_vip=evip.id)
            if not networkipv4:
                if not networkipv6:
                    evip_list = self.__append_list(evip, evip_list)
                else:
                    for rede in networkipv6:
                        if rede.vlan.ambiente.id == environment.id:
                            evip_list = self.__append_list(evip, evip_list)
            else:
                for rede in networkipv4:
                    if rede.vlan.ambiente.id == environment.id:
                        evip_list = self.__append_list(evip, evip_list)
                for rede in networkipv6:
                    if rede.vlan.ambiente.id == environment.id:
                        evip_list = self.__append_list(evip, evip_list)

        return evip_list

    def __append_list(self, evip, evip_list):
        if model_to_dict(evip) not in evip_list:
            evip_list.append(model_to_dict(evip))

        return evip_list

    @classmethod
    def get_environment_vips_by_environment_id(cls, environment_id):
        environment_vip_list_id = EnvironmentVip.objects.filter(
            Q(networkipv4__vlan__ambiente__id=environment_id) |
            Q(networkipv6__vlan__ambiente__id=environment_id)).distinct()

        return environment_vip_list_id


class Ambiente(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id_ambiente'
    )
    grupo_l3 = models.ForeignKey(
        GrupoL3,
        db_column='id_grupo_l3'
    )
    ambiente_logico = models.ForeignKey(
        AmbienteLogico,
        db_column='id_ambiente_logic'
    )
    divisao_dc = models.ForeignKey(
        DivisaoDc,
        db_column='id_divisao'
    )
    filter = models.ForeignKey(
        Filter,
        db_column='id_filter',
        null=True
    )
    acl_path = models.CharField(
        max_length=250,
        db_column='acl_path',
        null=True
    )
    ipv4_template = models.CharField(
        max_length=250,
        db_column='ipv4_template',
        null=True
    )
    ipv6_template = models.CharField(
        max_length=250,
        db_column='ipv6_template',
        null=True
    )
    link = models.CharField(
        max_length=200,
        blank=True
    )
    min_num_vlan_1 = models.IntegerField(
        blank=True,
        null=True,
        db_column='min_num_vlan_1'
    )
    max_num_vlan_1 = models.IntegerField(
        blank=True,
        null=True,
        db_column='max_num_vlan_1'
    )
    min_num_vlan_2 = models.IntegerField(
        blank=True,
        null=True,
        db_column='min_num_vlan_2'
    )
    max_num_vlan_2 = models.IntegerField(
        blank=True,
        null=True,
        db_column='max_num_vlan_2'
    )
    vrf = models.CharField(
        max_length=100,
        null=True,
        default='',
        db_column='vrf'
    )
    father_environment = models.ForeignKey(
        'self',
        null=True,
        db_column='id_father_environment'
    )

    log = logging.getLogger('Ambiente')

    class Meta(BaseModel.Meta):
        db_table = u'ambiente'
        managed = True
        unique_together = ('grupo_l3', 'ambiente_logico', 'divisao_dc')

    def _get_name(self):
        "Returns complete name for environment."
        return '%s - %s - %s' % (self.divisao_dc.nome, self.ambiente_logico.nome, self.grupo_l3.nome)

    name = property(_get_name)

    @classmethod
    def get_by_pk(cls, id):
        """Efetua a consulta de Ambiente pelo seu id.

        @return: Um Ambiente.

        @raise AmbienteError: Falha ao pesquisar o Ambiente.

        @raise AmbienteNotFoundError: Não existe um Ambiente para o id pesquisado.
        """
        try:
            return Ambiente.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise AmbienteNotFoundError(
                e, u'Não existe um ambiente com o id = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar o ambiente.')
            raise AmbienteError(e, u'Falha ao pesquisar o ambiente.')

    def search(self, divisao_dc_id=None, ambiente_logico_id=None):
        try:
            a = Ambiente.objects.all()
            if divisao_dc_id is not None:
                a = a.filter(divisao_dc__id=divisao_dc_id)
            if ambiente_logico_id is not None:
                a = a.filter(ambiente_logico__id=ambiente_logico_id)

            return a
        except Exception, e:
            self.log.error(u'Falha ao pesquisar os ambientes.')
            raise AmbienteError(e, u'Falha ao pesquisar os ambientes.')

    def create(self, authenticated_user):
        """Efetua a inclusão de um novo o Ambiente.

        @return: Id new Environment

        @raise AmbienteError: Falha ao inserir um Ambiente.

        @raise AmbienteLogicoNotFoundError: Não existe um Ambiente Lógico para a pk pesquisada.

        @raise GrupoL3.DoesNotExist: Não existe um Grupo Layer 3 para a pk pesquisada.

        @raise DivisaoDcNotFoundError: Não existe uma Divisão DataCenter para a pk pesquisada.

        @raise AmbienteDuplicatedError: Ambiente duplicado.

        @raise FilterNotFoundError: Não existe o filtro para a pk pesquisada.
        """

        self.ambiente_logico = AmbienteLogico.get_by_pk(
            self.ambiente_logico.id)
        self.divisao_dc = DivisaoDc.get_by_pk(self.divisao_dc.id)

        try:
            self.grupo_l3 = GrupoL3.objects.get(pk=self.grupo_l3.id)

            try:
                Ambiente.objects.get(grupo_l3=self.grupo_l3,
                                     ambiente_logico=self.ambiente_logico,
                                     divisao_dc=self.divisao_dc)
                raise AmbienteDuplicatedError(None, u'Ambiente duplicado.')
            except Ambiente.DoesNotExist:
                self.log.debug('Ambiente não duplicado.')

            if self.filter is not None:
                try:
                    self.filter = Filter.objects.get(pk=self.filter.id)
                except Filter.DoesNotExist:
                    raise FilterNotFoundError(
                        None, u'There is no Filter with pk = %s.' % self.filter.id)

            return self.save()

        except FilterNotFoundError, e:
            raise e
        except AmbienteDuplicatedError, e:
            raise e
        except GrupoL3.DoesNotExist, e:
            raise e
        except Exception:
            self.log.error(u'Falha ao inserir um Ambiente.')
            raise AmbienteError('Falha ao inserir um Ambiente.')

    @classmethod
    def update(cls, authenticated_user, pk, **kwargs):
        """Efetua a alteração de um Ambiente.

        @return: Nothing

        @raise AmbienteDuplicatedError: Ambiente duplicado.

        @raise AmbienteError: Falha ao alterar o Ambiente.

        @raise AmbienteNotFoundError: Não existe um Ambiente para a pk pesquisada.

        @raise AmbienteLogicoNotFoundError: Não existe um Ambiente Lógico para a pk pesquisada.

        @raise GrupoL3.DoesNotExist: Não existe um Grupo Layer 3 para a pk pesquisada.

        @raise DivisaoDcNotFoundError: Não existe uma Divisão DataCenter para a pk pesquisada.

        @raise CannotDissociateFilterError: Filter in use, can't be dissociated.
        """
        environment = Ambiente().get_by_pk(pk)

        old_logic_environment_id = environment.ambiente_logico_id
        try:
            logic_environment_id = kwargs['ambiente_logico_id']
            if (logic_environment_id != environment.ambiente_logico_id):
                environment.ambiente_logico = AmbienteLogico.get_by_pk(
                    logic_environment_id)
        except (KeyError):
            logic_environment_id = environment.ambiente_logico_id
            pass

        old_dc_division_id = environment.divisao_dc_id
        try:
            dc_division_id = kwargs['divisao_dc_id']
            if dc_division_id != environment.divisao_dc_id:
                environment.divisao_dc = DivisaoDc.get_by_pk(dc_division_id)
        except (KeyError):
            dc_division_id = environment.divisao_dc_id
            pass

        old_l3_group_id = environment.grupo_l3_id
        try:
            l3_group_id = kwargs['grupo_l3_id']
            if l3_group_id != environment.grupo_l3_id:
                environment.grupo_l3 = GrupoL3.get_by_pk(l3_group_id)
        except (KeyError):
            l3_group_id = environment.grupo_l3_id
            pass

        try:
            try:
                if not (l3_group_id == old_l3_group_id and
                        logic_environment_id == old_logic_environment_id and
                        dc_division_id == old_dc_division_id):

                    Ambiente.objects.get(grupo_l3__id=l3_group_id,
                                         ambiente_logico__id=logic_environment_id,
                                         divisao_dc__id=dc_division_id)
                    raise AmbienteDuplicatedError(None, u'Ambiente duplicado.')
            except Ambiente.DoesNotExist:
                pass

            from networkapi.filter.models import check_filter_use

            filter_id = kwargs.get('filter_id')
            if filter_id != environment.filter_id:
                environment = check_filter_use(filter_id, environment)

            environment.__dict__.update(kwargs)
            environment.save(authenticated_user)

        except AmbienteDuplicatedError, e:
            raise e

        except CannotDissociateFilterError, e:
            raise CannotDissociateFilterError(e.cause, e.message)

        except Exception, e:
            cls.log.error(u'Falha ao alterar Ambiente.')
            raise AmbienteError(u'Falha ao alterar Ambiente.')

    @classmethod
    def remove(cls, authenticated_user, pk):
        """Efetua a remoção de um Ambiente.

        @return: Nothing

        @raise AmbienteError: Falha ao remover um HealthCheckExpect ou Ambiente Config associado ou o Ambiente.

        @raise AmbienteNotFoundError: Não existe um Ambiente para a pk pesquisada.

        @raise AmbienteUsedByEquipmentVlanError: Existe Equipamento ou Vlan associado ao ambiente que não pode ser removido.
        """
        environment = Ambiente().get_by_pk(pk)

        from networkapi.ip.models import IpCantBeRemovedFromVip
        from networkapi.vlan.models import VlanCantDeallocate
        from networkapi.equipamento.models import EquipamentoAmbiente, EquipamentoAmbienteNotFoundError, EquipamentoError
        from networkapi.healthcheckexpect.models import HealthcheckExpect, HealthcheckExpectError

        # Remove every vlan associated with this environment
        for vlan in environment.vlan_set.all():
            try:
                if vlan.ativada:
                    vlan.remove(authenticated_user)
                vlan.delete()
            except VlanCantDeallocate, e:
                raise AmbienteUsedByEquipmentVlanError(e.cause, e.message)
            except IpCantBeRemovedFromVip, e:
                raise AmbienteUsedByEquipmentVlanError(e.cause, e.message)

        # Remove every association between equipment and this environment
        for equip_env in environment.equipamentoambiente_set.all():
            try:
                EquipamentoAmbiente.remove(
                    authenticated_user, equip_env.equipamento_id, equip_env.ambiente_id)
            except EquipamentoAmbienteNotFoundError, e:
                raise AmbienteUsedByEquipmentVlanError(e, e.message)
            except EquipamentoError, e:
                raise AmbienteUsedByEquipmentVlanError(e, e.message)

        # Dissociate or remove healthcheck expects
        try:
            HealthcheckExpect.dissociate_environment_and_delete(
                authenticated_user, pk)
        except HealthcheckExpectError, e:
            cls.log.error(u'Falha ao desassociar algum HealthCheckExpect.')
            raise AmbienteError(
                e, u'Falha ao desassociar algum HealthCheckExpect.')

        # Remove ConfigEnvironments associated with environment
        try:
            ConfigEnvironment.remove_by_environment(authenticated_user, pk)
        except (ConfigEnvironmentError, OperationalError, ConfigEnvironmentNotFoundError), e:
            cls.log.error(u'Falha ao remover algum Ambiente Config.')
            raise AmbienteError(e, u'Falha ao remover algum Ambiente Config.')

        # Remove the environment
        try:
            environment.delete()
        except Exception, e:
            cls.log.error(u'Falha ao remover o Ambiente.')
            raise AmbienteError(e, u'Falha ao remover o Ambiente.')

    def show_environment(self):
        environment = "%s - %s - %s" % (self.divisao_dc.nome,
                                        self.ambiente_logico.nome, self.grupo_l3.nome)
        return environment


class IP_VERSION:
    IPv6 = ('v6', 'IPv6')
    IPv4 = ('v4', 'IPv4')
    List = (IPv4, IPv6)


class IPConfig(BaseModel):

    from networkapi.vlan.models import TipoRede

    id = models.AutoField(
        primary_key=True,
        db_column='id_ip_config'
    )
    subnet = models.CharField(
        max_length=45,
        blank=False
    )
    new_prefix = models.CharField(
        max_length=3,
        blank=False
    )
    type = models.CharField(
        max_length=2,
        blank=False,
        choices=IP_VERSION.List
    )
    network_type = models.ForeignKey(
        TipoRede,
        null=True,
        db_column='network_type'
    )

    log = logging.getLogger('IPConfig')

    class Meta(BaseModel.Meta):
        db_table = u'ip_config'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Search IPConfig by your primary key

        @return: IPConfig

        @raise IPConfigError: Error finding IPConfig by primary key.
        @raise IPConfigNotFoundError: IPConfig not found in database.
        """
        try:
            return IPConfig.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise IPConfigNotFoundError(
                e, u'Can not find a IPConfig with id = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Error finding IPConfig.')
            raise IPConfigError(e, u'Error finding IPConfig.')

    @staticmethod
    def get_by_environment(cls, environment_id):
        """Search all ConfigEnvironment by Environment ID

        @return: all ConfigEnvironment

        @raise ConfigEnvironmentError: Error finding ConfigEnvironment by Environment ID.
        @raise ConfigEnvironmentNotFoundError: ConfigEnvironment not found in database.
        """
        try:

            config_environment = ConfigEnvironment.objects.filter(
                environment=environment_id
            ).values('ip_config').query

            return IPConfig.objects.filter(id__in=config_environment)

            return
        except ObjectDoesNotExist, e:
            raise ConfigEnvironmentNotFoundError(
                e, u'Can not find a ConfigEnvironment with Environment ID = %s.' % environment_id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Error finding ConfigEnvironment.')
            raise ConfigEnvironmentError(
                e, u'Error finding ConfigEnvironment.')

    @staticmethod
    def remove(cls, authenticated_user, environment_id, configuration_id):
        """Search all IpConfig by ID and remove them

        @raise IPConfigError: Error removeing IPConfig by ID.
        @raise IPConfigNotFoundError: IPConfig not found in database.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:

            ip_config = IPConfig.objects.filter(id=configuration_id)
            config_environment = ConfigEnvironment.objects.filter(
                ip_config=ip_config, environment=environment_id)

            config_environment.get().delete()

            ip_config.get().delete()

            return ip_config

        except ObjectDoesNotExist, e:
            raise IPConfigNotFoundError(
                e, u'Can not find a IpConfig with ID = %s.' % configuration_id)

        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')

        except Exception, e:
            cls.log.error(u'Error removing IpConfig.')
            raise IPConfigError(e, u'Error removing IpConfig.')


class ConfigEnvironment(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_config_do_ambiente')
    environment = models.ForeignKey(Ambiente, db_column='id_ambiente')
    ip_config = models.ForeignKey(IPConfig, db_column='id_ip_config')

    log = logging.getLogger('ConfigEnvironment')

    class Meta(BaseModel.Meta):
        db_table = u'config_do_ambiente'
        managed = True

    @classmethod
    def get_by_pk(cls, id_environment, id_ip_config):
        """Search ConfigEnvironment by your primary key

        @return: ConfigEnvironment

        @raise ConfigEnvironmentError: Error finding ConfigEnvironment by primary key.
        @raise ConfigEnvironmentNotFoundError: ConfigEnvironment not found in database.
        """
        try:
            return ConfigEnvironment.objects.filter(
                environment=id_environment,
                ip_config=id_ip_config).uniqueResult()
        except ObjectDoesNotExist, e:
            raise ConfigEnvironmentNotFoundError(
                e, u'Can not find a ConfigEnvironment with id = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Error finding ConfigEnvironment.')
            raise ConfigEnvironmentError(
                e, u'Error finding ConfigEnvironment.')

    @classmethod
    def get_by_environment(cls, id_environment):
        """Search all ConfigEnvironment by Environment ID

        @return: all ConfigEnvironment

        @raise ConfigEnvironmentError: Error finding ConfigEnvironment by Environment ID.
        @raise ConfigEnvironmentNotFoundError: ConfigEnvironment not found in database.
        """
        try:
            return ConfigEnvironment.objects.filter(environment=id_environment)
        except ObjectDoesNotExist, e:
            raise ConfigEnvironmentNotFoundError(
                e, u'Can not find a ConfigEnvironment with Environment ID = %s.' % id_environment)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Error finding ConfigEnvironment.')
            raise ConfigEnvironmentError(
                e, u'Error finding ConfigEnvironment.')

    @classmethod
    def get_by_ip_config(cls, id_ip_config):
        """Search all ConfigEnvironment by IPConfig ID

        @return: all ConfigEnvironment

        @raise ConfigEnvironmentError: Error finding ConfigEnvironment by IPConfig ID.
        @raise ConfigEnvironmentNotFoundError: ConfigEnvironment not found in database.
        """
        try:
            return ConfigEnvironment.objects.filter(ip_config=id_ip_config)
        except ObjectDoesNotExist, e:
            raise ConfigEnvironmentNotFoundError(
                e, u'Can not find a ConfigEnvironment with IPConfig ID = %s.' % id_ip_config)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Error finding ConfigEnvironment.')
            raise ConfigEnvironmentError(
                e, u'Error finding ConfigEnvironment.')

    @classmethod
    def remove_by_environment(cls, authenticated_user, id_environment):
        """Search all ConfigEnvironment by Environment ID and remove them

        @raise ConfigEnvironmentError: Error finding ConfigEnvironment by Environment ID.
        @raise ConfigEnvironmentNotFoundError: ConfigEnvironment not found in database.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            ces = ConfigEnvironment.objects.filter(environment=id_environment)
            for ce in ces:
                ce.delete()
        except ObjectDoesNotExist, e:
            raise ConfigEnvironmentNotFoundError(
                e, u'Can not find a ConfigEnvironment with Environment ID = %s.' % id_environment)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Error removing ConfigEnvironment.')
            raise ConfigEnvironmentError(
                e, u'Error removing ConfigEnvironment.')

    def save(self):
        '''
            Save ConfigEnvironment

            @raise ConfigEnvironmentDuplicateError: ConfigEnvironment Duplicate
        '''
        try:

            super(ConfigEnvironment, self).save()

        except IntegrityError, e:
            self.log.error(u'Error saving ConfigEnvironment: %r' % str(e))
            raise ConfigEnvironmentDuplicateError(
                e, u'Error saving duplicate Environment Configuration.')


class EnvironmentEnvironmentVip(BaseModel):

    environment = models.ForeignKey(Ambiente)
    environment_vip = models.ForeignKey(EnvironmentVip)

    log = logging.getLogger('EnvironmentEnvironmentVip')

    class Meta(BaseModel.Meta):
        db_table = u'environment_environment_vip'
        managed = True
        unique_together = ('environment', 'environment_vip')

    @classmethod
    def get_by_environment_environment_vip(cls, environment_id, environment_vip_id):
        """Search all EnvironmentEnvironmentVip by Environment ID and EnvironmentVip ID

        @return: all EnvironmentEnvironmentVip

        @raise EnvironmentEnvironmentVipError: Error finding EnvironmentEnvironmentVipError by Environment ID and EnvironmentVip ID.
        @raise EnvironmentEnvironmentVipNotFoundError: ConfigEnvironment not found in database.
        @raise OperationalError: Error when made find.

        """
        try:
            return EnvironmentEnvironmentVip.objects.filter(
                environment__id=environment_id,
                environment_vip__id=environment_vip_id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise EnvironmentEnvironmentVipNotFoundError(
                e, u'Can not find a EnvironmentEnvironmentVipNotFoundError with Environment ID = {} and EnvironmentVIP ID = {}'.format(environment_id, environment_vip_id))
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Error finding ConfigEnvironment.')
            raise EnvironmentEnvironmentVipError(
                e, u'Error finding EnvironmentEnvironmentVipError.')

    def validate(self):
        """Validates whether Environment is already associated with EnvironmentVip

            @raise EnvironmentEnvironmentVipDuplicatedError: if Environment is already associated with EnvironmentVip
        """
        try:
            EnvironmentEnvironmentVip.objects.get(
                environment=self.environment,
                environment_vip=self.environment_vip)
        except ObjectDoesNotExist:
            pass
        except MultipleObjectsReturned:
            raise EnvironmentEnvironmentVipDuplicatedError(None, u'Environment already registered for the environment vip.')

    @classmethod
    def get_server_pool_by_environment_environment_vip(cls, environment_environment_vip):

        from networkapi.requisicaovips.models import VipPortToPool

        environment = environment_environment_vip.environment
        environment_vip = environment_environment_vip.environment_vip

        vipporttopool_list = VipPortToPool.objects.filter(
            Q(requisicao_vip__ip__networkipv4__ambient_vip=environment_vip) |
            Q(requisicao_vip__ipv6__networkipv6__ambient_vip=environment_vip),
            server_pool__environment=environment
        )

        server_pool_list = []
        for vipporttopool in vipporttopool_list:
            server_pool_list.append(vipporttopool.server_pool)

        return server_pool_list

    @classmethod
    def get_environment_list_by_environment_vip_list(cls, environment_vip_list):
        env_envivip_list = EnvironmentEnvironmentVip.objects.filter(
            environment_vip__in=environment_vip_list).distinct()
        environment_list = [env_envivip.environment for env_envivip in env_envivip_list]
        return environment_list

    @classmethod
    def get_environment_list_by_environment_vip(cls, environment_vip):
        env_envivip_list = EnvironmentEnvironmentVip.objects.filter(
            environment_vip=environment_vip)
        environment_list = [env_envivip.environment for env_envivip in env_envivip_list]
        return environment_list
