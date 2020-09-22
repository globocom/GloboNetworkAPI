# -*- coding: utf-8 -*-
from __future__ import with_statement

import logging
import re

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import get_model
from django.db.models import Q

from networkapi.admin_permission import AdminPermission
from networkapi.distributedlock import LOCK_ENVIRONMENT_ALLOCATES
from networkapi.distributedlock import LOCK_VLAN
from networkapi.filter.models import verify_subnet_and_equip
from networkapi.infrastructure.ipaddr import IPNetwork
from networkapi.models.BaseModel import BaseModel
from networkapi.queue_tools import queue_keys
from networkapi.queue_tools.rabbitmq import QueueManager
from networkapi.semaforo.model import Semaforo
from networkapi.settings import MAX_VLAN_NUMBER_01
from networkapi.settings import MAX_VLAN_NUMBER_02
from networkapi.settings import MIN_VLAN_NUMBER_01
from networkapi.settings import MIN_VLAN_NUMBER_02
from networkapi.util import clone
from networkapi.util import network
from networkapi.util.decorators import cached_property
from networkapi.util.geral import create_lock_with_blocking
from networkapi.util.geral import destroy_lock
from networkapi.util.geral import get_app


class VlanError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com Vlan."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class VlanErrorV3(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


class NetworkTypeNotFoundError(VlanError):

    """Returns exception when trying to get network type by its identifier."""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class NetTypeUsedByNetworkError(VlanError):

    """Return exception when trying to remove network type used by network."""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class NetworkTypeNameDuplicatedError(VlanError):

    """Returns exception when trying to insert/update network type with same name as other."""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class VlanNotFoundError(VlanError):

    """Retorna exceção para pesquisa de vlan por nome ou por chave primária."""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class VlanNumberNotAvailableError(VlanError):

    """Retorna exceção porque não existe um número de VLAN disponível para criar uma nova VLAN."""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class VlanNumberEnvironmentNotAvailableError(VlanError):

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class VlanNetworkAddressNotAvailableError(VlanError):

    """Retorna exceção porque não existe um endereço de rede disponível para criar uma nova VLAN."""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class VlanNameDuplicatedError(VlanError):

    """Retorna exceção porque já existe uma VLAN cadastrada com o mesmo nome."""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class VlanNameInvalid(VlanError):

    """Retorna exceção porque o nome da VLAN tem caracter especial ou quebra de linha."""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class VlanACLDuplicatedError(VlanError):

    """Retorna exceção porque já existe uma VLAN cadastrada com o mesmo nome de arquivo ACL."""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class VlanInactiveError(VlanError):

    """Retorna exceção porque está inativa."""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class VlanNetworkError(VlanError):

    """Retorna exceção caso não consiga remover uma rede"""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class AclNotFoundError(VlanError):

    """Retorna exceção para acl inexistente."""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class VlanCantDeallocate(VlanError):

    """Retorna exceção porque Vlan está ativa e não pode ser excluída."""

    def __init__(self, cause, message=None):
        VlanError.__init__(self, cause, message)


class TipoRedeNotFoundError(VlanError):
    pass


class TipoRedeUsedByVlanError(VlanError):
    pass


class TipoRedeNameDuplicatedError(VlanError):
    pass


class TipoRede(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_tipo_rede')
    tipo_rede = models.CharField(max_length=100)

    log = logging.getLogger('TipoRede')

    class Meta(BaseModel.Meta):
        db_table = u'tipo_rede'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        try:
            return TipoRede.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise NetworkTypeNotFoundError(
                e, u'There is no network type with pk = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failed to get network type.')
            raise VlanError(e, u'Failed to get network type.')

    @classmethod
    def get_by_name(cls, name):
        try:
            tipos = TipoRede.objects.filter(tipo_rede__iexact=name)
            if len(tipos) == 0:
                raise NetworkTypeNotFoundError(
                    None, u'There is no network type with name = %s.' % name)
            return tipos[0]
        except NetworkTypeNotFoundError, e:
            raise e
        except Exception, e:
            cls.log.error(u'Failed to get network type.')
            raise VlanError(e, u'Failed to get network type.')


class Vlan(BaseModel):

    log = logging.getLogger('Vlan')

    id = models.AutoField(
        primary_key=True,
        db_column='id_vlan'
    )
    nome = models.CharField(
        max_length=50
    )
    num_vlan = models.IntegerField()
    ambiente = models.ForeignKey(
        'ambiente.Ambiente',
        db_column='id_ambiente'
    )
    descricao = models.CharField(
        max_length=200,
        blank=True
    )
    acl_file_name = models.CharField(
        max_length=200,
        blank=True
    )
    acl_valida = models.BooleanField()
    acl_file_name_v6 = models.CharField(
        max_length=200,
        blank=True
    )
    acl_valida_v6 = models.BooleanField()
    ativada = models.BooleanField()
    vrf = models.CharField(
        max_length=100,
        null=True,
        db_column='vrf'
    )
    acl_draft = models.TextField(
        blank=True,
        null=True,
        db_column='acl_draft'
    )
    acl_draft_v6 = models.TextField(
        blank=True,
        null=True,
        db_column='acl_draft_v6'
    )
    vxlan = models.NullBooleanField(
        db_column='vxlan',
        default=False,
        null=True,
        blank=True
    )

    def _get_networks_ipv4(self):
        """Returns networks v4."""
        networkipv4 = self.networkipv4_set.all()
        return networkipv4

    networks_ipv4 = property(_get_networks_ipv4)

    def _get_networks_ipv6(self):
        """Returns networks v6."""
        networkipv6 = self.networkipv6_set.all()
        return networkipv6

    networks_ipv6 = property(_get_networks_ipv6)

    class Meta(BaseModel.Meta):
        db_table = u'vlans'
        managed = True
        unique_together = (
            ('nome', 'ambiente'),
            ('num_vlan', 'ambiente')
        )

    @cached_property
    def vrfs(self):
        return self.get_vrf().prefetch_related()

    @cached_property
    def groups_permissions(self):
        ogp_models = get_app('api_ogp', 'models')
        perms = ogp_models.ObjectGroupPermission\
            .get_by_object(self.id, AdminPermission.OBJ_TYPE_VLAN)
        return perms

    def get_by_pk(self, vlan_id):
        """Get Vlan by id.

        @return: Vlan.

        @raise VlanNotFoundError: Vlan is not registered.
        @raise VlanError: Failed to search for the Vlan.
        @raise OperationalError: Lock wait timeout exceed
        """
        try:
            return Vlan.objects.get(id=vlan_id)
        except ObjectDoesNotExist, e:
            raise VlanNotFoundError(
                e, u'Dont there is a Vlan by pk = %s.' % vlan_id)
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def get_vlan_by_acl(self, acl_file):
        try:
            vlan = Vlan.objects.filter(acl_file_name=acl_file).uniqueResult()

            if self.id is not None:
                if vlan.id == self.id:
                    return
            raise VlanACLDuplicatedError(
                None, 'uThere is already an Vlan with the Acl - Ipv4 = %s.' % acl_file)
        except VlanACLDuplicatedError, e:
            raise VlanACLDuplicatedError(e, e.message)
        except ObjectDoesNotExist, e:
            pass
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def get_vlan_by_acl_v6(self, acl_file_v6):
        try:

            vlan = Vlan.objects.filter(
                acl_file_name_v6=acl_file_v6).uniqueResult()

            if self.id is not None:
                if vlan.id == self.id:
                    return

            raise VlanACLDuplicatedError(
                None, 'uThere is already an Vlan with the Acl - Ipv6 = %s.' % acl_file_v6)
        except VlanACLDuplicatedError, e:
            raise VlanACLDuplicatedError(e, e.message)
        except ObjectDoesNotExist, e:
            pass
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def exist_vlan_name_in_environment(self, id_vlan=None):
        try:
            vlans = Vlan.objects.filter(
                nome__iexact=self.nome,
                ambiente__id=self.ambiente.id
            )
            if id_vlan:
                vlans = vlans.exclude(id=id_vlan)

            if vlans:
                return True
            else:
                return False
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def exist_vlan_num_in_environment(self, id_vlan=None):
        try:
            vlans = Vlan.objects.filter(
                num_vlan=self.num_vlan,
                ambiente__id=self.ambiente.id
            )
            if id_vlan:
                vlans = vlans.exclude(id=id_vlan)

            if vlans:
                return True
            else:
                return False
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def search_vlan_numbers(self, environment_id, min_num, max_num):
        try:
            return Vlan.objects.filter(
                num_vlan__range=(min_num, max_num),
                ambiente__id=environment_id
            ).values_list(
                'num_vlan', flat=True
            ).distinct().order_by('num_vlan')
        except Exception, e:
            self.log.error(u'Failure to search the Vlans.')
            raise VlanError(e, u'Failure to search the Vlans.')

    def valid_vlan_name(self, name):

        if name is None or name == '':
            return False

        regex_for_breakline = re.compile('\r|\n\r|\n')
        regex_for_special_characters = re.compile('[@!#$%^&*()<>?/\\\|}{~:]')

        return False if regex_for_breakline.search(name) or regex_for_special_characters.search(name) else True

    def search(self, environment_id=None):
        try:
            v = Vlan.objects.all()

            if environment_id is not None:
                v = v.filter(ambiente__id=environment_id)
            return v
        except Exception, e:
            self.log.error(u'Failure to search the Vlans.')
            raise VlanError(e, u'Failure to search the Vlans.')

    def calculate_vlan_number(self, min_num, max_num, list_available=False):

        from networkapi.equipamento.models import EquipamentoAmbiente
        """
            Caculate if has a number available in range (min_num/max_num) to specified environment

            @param min_num: Minimum number that the vlan can be created.
            @param max_num: Maximum number that the vlan can be created.
            @param list_available: If = True, return the list of numbers availables

            @return: None when hasn't a number available | num_vlan when found a number available
        """
        interval = range(min_num, max_num + 1)

        # Vlan numbers in interval in the same environment
        vlan_numbers_in_interval = self.search_vlan_numbers(
            self.ambiente_id, min_num, max_num)

        # Find equipment's ids from environmnet that is 'switches',
        # 'roteadores' or 'balanceadores'
        id_equipamentos = EquipamentoAmbiente.objects.filter(
            equipamento__tipo_equipamento__id__in=[1, 3, 5],
            ambiente__id=self.ambiente_id
        ).values_list('equipamento', flat=True)
        # Vlan numbers in others environment but in environment that has
        # equipments found in before filter ('switches', 'roteadores' or
        # 'balanceadores')
        vlans_others_environments = Vlan.objects.exclude(
            ambiente__id=self.ambiente_id
        ).filter(
            ambiente__equipamentoambiente__equipamento__id__in=id_equipamentos
        ).values_list('num_vlan', flat=True)

        # Clean duplicates numbers and update merge 'vlan_numbers_in_interval'
        # with 'vlans_others_environments'
        vlan_numbers_in_interval = set(vlan_numbers_in_interval)
        vlan_numbers_in_interval.update(vlans_others_environments)

        self.log.debug('Interval: %s.', interval)
        self.log.debug('VLANs in interval: %s.', vlan_numbers_in_interval)

        # if len(interval) > len(vlan_numbers_in_interval):
        diff_set = set(interval) - set(vlan_numbers_in_interval)
        self.log.debug('Difference in the lists: %s.', diff_set)
        if list_available:
            return diff_set
        for num_vlan in diff_set:
            return num_vlan
        return None

    def activate(self, authenticated_user):
        """ Set column ativada = 1"""

        try:
            self.ativada = 1
            self.save()

            vlan_slz = get_app('api_vlan', 'serializers')

            serializer = vlan_slz.VlanV3Serializer(
                self,
                include=('environment__basic',),
                exclude=(
                    'acl_draft',
                    'acl_draft_v6',
                    'acl_valida_v6',
                    'acl_file_name_v6',
                    'acl_valida',
                    'acl_file_name',
                )
            )

            data_to_queue = serializer.data
            data_to_queue.update({
                'description': queue_keys.VLAN_ACTIVATE
            })

            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            queue_manager.append({
                'action': queue_keys.VLAN_ACTIVATE,
                'kind': queue_keys.VLAN_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

        except Exception, e:
            self.log.error(u'Falha ao salvar a VLAN.')
            raise VlanError(e, u'Falha ao salvar a VLAN.')

    def remove(self, authenticated_user):
        """
            Update status column to 'active = 0'

            @param authenticate_user: User authenticate

            @raise VlanError: Exception
        """
        try:

            self.ativada = 0
            self.save()

            vlan_slz = get_app('api_vlan', 'serializers')

            serializer = vlan_slz.VlanV3Serializer(
                self,
                include=('environment__basic',),
                exclude=(
                    'acl_draft',
                    'acl_draft_v6',
                    'acl_valida_v6',
                    'acl_file_name_v6',
                    'acl_valida',
                    'acl_file_name',
                )
            )

            data_to_queue = serializer.data
            data_to_queue.update({
                'description': queue_keys.VLAN_DEACTIVATE
            })

            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            queue_manager.append({
                'action': queue_keys.VLAN_DEACTIVATE,
                'kind': queue_keys.VLAN_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

        except Exception, e:
            self.log.error(u'Falha ao salvar a VLAN.')
            raise VlanError(e, u'Falha ao salvar a VLAN.')

    def create_new(self, authenticated_user, min_num_01, max_num_01, min_num_02, max_num_02):
        """
        Create a Vlan with the new Model

        The fields num_vlan, acl_file_name, acl_valida and ativada will be
        generated automatically

        @return: nothing
        """

        # Validate Name VLAN
        if not self.valid_vlan_name(self.nome):
            raise VlanNameInvalid(None, 'Name VLAN can not have special characters or breakline.')

        if self.nome is not None:
            self.nome = self.nome.upper()

        # Name VLAN can not be duplicated in the environment
        if self.exist_vlan_name_in_environment():
            raise VlanNameDuplicatedError(
                None, 'Name VLAN can not be duplicated in the environment.')

        # Calculate Number VLAN
        self.num_vlan = self.calculate_vlan_number(min_num_01, max_num_01)
        if self.num_vlan is None:
            self.num_vlan = self.calculate_vlan_number(min_num_02, max_num_02)
            if self.num_vlan is None:
                raise VlanNumberNotAvailableError(
                    None, u'Number VLAN unavailable for environment %d.' % self.ambiente.id)

        # Default values
        self.acl_file_name = self.nome
        self.acl_valida = 0
        self.ativada = 0
        self.vxlan = self.ambiente.vxlan

        try:
            self.save()
        except Exception as e:
            msg = 'Error persisting a VLAN. E: %s' % e
            self.log.error(msg)
            raise VlanError(e, msg)

    def create(self, authenticated_user, min_num_01, max_num_01, min_num_02, max_num_02):
        """Insere uma nova VLAN.

        O valor dos campos num_vlan, rede_oct1, rede_oct2, rede_oct3, rede_oct4, bloco,
        broadcast, masc_oct1, masc_oct2, masc_oct3, masc_oct4, acl_file_name, acl_valida e ativada é gerado internamente.
        Os demais campos devem ser fornecidos.

        @param min_num_01: Valor inicial do intervalo 01 para calcular o número da VLAN.
        @param max_num_01: Valor final do intervalo 01 para calcular o número da VLAN.
        @param min_num_02: Valor inicial do intervalo 02 para calcular o número da VLAN.
        @param max_num_02: Valor final do intervalo 02 para calcular o número da VLAN.

        @return: nothing

        @raise NetworkTypeNotFoundError: Tipo de Rede não cadastrada no banco de dados.

        @raise AmbienteNotFoundError: Ambiente não cadastrado no banco de dados.

        @raise AmbienteError: Falha ao pesquisar o ambiente.

        @raise VlanNameDuplicatedError: Nome da VLAN duplicado.

        @raise VlanNumberNotAvailableError: Não encontra um número de VLAN disponível em um dos intervalos (2 até 1001) ou
        (1006 até 4094) para o ambiente informado.

        @raise VlanNetworkAddressNotAvailableError: Não existe um endereço de rede disponível para VLAN que não seja
        sub-rede ou super-rede de um endereço existe no cadastro de VLANs.

        @raise VlanError: Erro não esperado ao executar o save.
        """

        # Validate Name VLAN
        if not self.valid_vlan_name(self.nome):
            raise VlanNameInvalid(None, 'Name VLAN can not have special characters or breakline.')

        if self.nome is not None:
            self.nome = self.nome.upper()

        # Tipo de Rede
        if self.tipo_rede.id is not None:
            self.tipo_rede = TipoRede().get_by_pk(self.tipo_rede.id)

        # Verificar duplicidade do Nome da VLAN
        if self.exist_vlan_name_in_environment():
            raise VlanNameDuplicatedError(
                None, 'VLAN com nome duplicado dentro do ambiente.')

        Semaforo.lock(Semaforo.ALOCAR_VLAN_ID)

        # Calcular o Numero da VLAN
        self.num_vlan = self.calculate_vlan_number(min_num_01, max_num_01)
        if self.num_vlan is None:
            self.num_vlan = self.calculate_vlan_number(min_num_02, max_num_02)
            if self.num_vlan is None:
                raise VlanNumberNotAvailableError(
                    None, u'Não existe número de VLAN disponível para o ambiente %d.' % self.ambiente.id)

        # Calcular o Endereço de Rede da VLAN
        vlan_address = self.calculate_vlan_address()
        if len(vlan_address) == 0:
            raise VlanNetworkAddressNotAvailableError(
                None, u'Não existe endereço de rede disponível para o cadastro da VLAN.')

        self.rede_oct1, self.rede_oct2, self.rede_oct3, self.rede_oct4 = vlan_address

        # Valores Default
        self.bloco = 24
        self.masc_oct1 = 255
        self.masc_oct2 = 255
        self.masc_oct3 = 255
        self.masc_oct4 = 0
        self.broadcast = '%d.%d.%d.255' % (
            self.rede_oct1, self.rede_oct2, self.rede_oct3)
        self.acl_file_name = self.nome
        self.acl_valida = 0
        self.ativada = 0
        self.vxlan = self.ambiente.vxlan

        try:
            self.save()
        except Exception as e:
            self.log.error(u'Falha ao inserir a VLAN.')
            raise VlanError(e, u'Falha ao inserir a VLAN.')

    def get_by_number_and_environment(self, number, environment):
        """Get Vlan by number.

        @return: Vlan.

        @raise VlanNotFoundError: Vlan is not registered.
        @raise VlanError: Failed to search for the Vlan.
        @raise OperationalError: Lock wait timeout exceed
        """
        try:
            return Vlan.objects.filter(
                num_vlan=number, ambiente=environment).uniqueResult()
        except ObjectDoesNotExist, e:
            raise VlanNotFoundError(
                e, u'Dont there is a Vlan by number = %s.' % number)
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def get_by_number(self, number):
        """Get Vlan by number.

        @return: Vlan.

        @raise VlanNotFoundError: Vlan is not registered.
        @raise VlanError: Failed to search for the Vlan.
        @raise OperationalError: Lock wait timeout exceed
        """
        try:
            return Vlan.objects.filter(num_vlan=number).uniqueResult()
        except ObjectDoesNotExist, e:
            raise VlanNotFoundError(
                e, u'Dont there is a Vlan by number = %s.' % number)
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def get_by_name(self, name):
        """Get Vlan by name.

        @return: Vlan.

        @raise VlanNotFoundError: Vlan is not registered.
        @raise VlanError: Failed to search for the Vlan.
        @raise OperationalError: Lock wait timeout exceed
        """
        try:
            return Vlan.objects.filter(nome=name).uniqueResult()
        except ObjectDoesNotExist, e:
            raise VlanNotFoundError(
                e, u'Dont there is a Vlan by name = %s.' % name)
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def insert_vlan(self, authenticated_user):
        """
        Insere uma nova Vlan.

        @return ID new Vlan.

        @raise VlanNameDuplicatedError: Nome do Vlan já existe.

        @raise VlanNumberEnvironmentNotAvailableError: Numero e Ambiente
                                                       da VLan já existe.

        @raise VlanError: Erro ao cadastrar Vlan.
        """
        from networkapi.equipamento.models import TipoEquipamento

        try:
            self.get_by_number_and_environment(self.num_vlan, self.ambiente)
            ambiente = '%s - %s - %s' % (self.ambiente.divisao_dc.nome,
                                         self.ambiente.ambiente_logico.nome, self.ambiente.grupo_l3.nome)
            raise VlanNumberEnvironmentNotAvailableError(
                None, 'Já existe uma VLAN cadastrada com o número %s no ambiente %s' % (self.num_vlan, ambiente))
        except VlanNotFoundError:
            pass

        ambiente = self.ambiente
        filter = ambiente.filter
        equipment_types = TipoEquipamento.objects.filter(
            filterequiptype__filter=filter)

        equips = list()
        envs = list()
        envs_aux = list()

        # Get all equipments from the environment being tested
        # that are not supposed to be filtered
        # (not the same type of the equipment type of a filter of the environment)
        for env in ambiente.equipamentoambiente_set.all().exclude(
                equipamento__tipo_equipamento__in=equipment_types):
            equips.append(env.equipamento)

        # Get all environment that the equipments above are included
        for equip in equips:
            for env in equip.equipamentoambiente_set.all():
                if env.ambiente_id not in envs_aux:
                    envs.append(env.ambiente)
                    envs_aux.append(env.ambiente_id)

        # Check in all vlans from all environments above
        # if there is a vlan with the same vlan number of the
        # vlan being tested
        for env in envs:
            for vlan in env.vlan_set.all():
                if int(vlan.num_vlan) == int(self.num_vlan):
                    raise VlanNumberEnvironmentNotAvailableError(
                        None, 'Já existe uma VLAN cadastrada com o número %s com um equipamento compartilhado '
                              'nesse ambiente' % (self.num_vlan))

        # Name VLAN can not be duplicated in the environment
        if self.exist_vlan_name_in_environment():
            raise VlanNameDuplicatedError(
                None, 'Name VLAN can not be duplicated in the environment.')

        # Validate Name VLAN
        if not self.valid_vlan_name(self.nome):
            raise VlanNameInvalid(None, 'Name VLAN can not have special characters or breakline.')

        try:
            return self.save()

        except Exception, e:
            self.log.error(u'Falha ao inserir VLAN.')
            raise VlanError(e, u'Falha ao inserir VLAN.')

    def edit_vlan(self, authenticated_user, change_name, change_number_environment):
        """
        Edita uma Vlan.

        @return None.

        @raise VlanNameDuplicatedError: Nome do Vlan já existe.

        @raise VlanNumberEnvironmentNotAvailableError: Numero e Ambiente da VLan já existe.

        @raise VlanError: Erro ao cadastrar Vlan.
        """
        if change_number_environment:
            try:
                self.get_by_number_and_environment(
                    self.num_vlan, self.ambiente)
                ambiente = '%s - %s - %s' % (self.ambiente.divisao_dc.nome,
                                             self.ambiente.ambiente_logico.nome, self.ambiente.grupo_l3.nome)
                raise VlanNumberEnvironmentNotAvailableError(
                    None, 'Já existe uma VLAN cadastrada com o número %s no ambiente %s' % (self.num_vlan, ambiente))
            except VlanNotFoundError:
                pass

        if change_number_environment:
            ambiente = self.ambiente

            equips = list()
            envs = list()

            for env in ambiente.equipamentoambiente_set.all():
                equips.append(env.equipamento)

            for equip in equips:
                for env in equip.equipamentoambiente_set.all():
                    if env not in envs:
                        envs.append(env.ambiente)

            for env in envs:
                for vlan in env.vlan_set.all():
                    if int(vlan.num_vlan) == int(self.num_vlan) and int(vlan.id) != int(self.id):
                        if self.ambiente.filter_id is None or vlan.ambiente.filter_id is None \
                                or int(vlan.ambiente.filter_id) != int(self.ambiente.filter_id):
                            raise VlanNumberEnvironmentNotAvailableError(
                                None, 'Já existe uma VLAN cadastrada com o número %s com um equipamento compartilhado '
                                      'nesse ambiente' % (self.num_vlan))

            old_vlan = self.get_by_pk(self.id)
            old_env = old_vlan.ambiente

            # Old env
            if old_env.filter is not None:
                if self.check_env_shared_equipment(old_env):
                    if self.ambiente.filter_id != old_env.filter_id:
                        raise VlanNumberEnvironmentNotAvailableError(
                            None, 'Um dos equipamentos associados com o ambiente desta Vlan também está associado '
                                  'com outro ambiente que tem uma rede com a mesma faixa, adicione filtros nos '
                                  'ambientes se necessário.')

        if change_name:
            # Name VLAN can not be duplicated in the environment
            if self.exist_vlan_name_in_environment():
                raise VlanNameDuplicatedError(
                    None, 'Name VLAN can not be duplicated in the environment.')

        try:
            return self.save()

        except Exception, e:
            self.log.error(u'Falha ao inserir VLAN.')
            raise VlanError(e, u'Falha ao inserir VLAN.')

    def check_env_shared_equipment(self, old_env):

        # Check if the environment is sharing an equipment by the network

        # Envs using old filter
        envs_old_filter = old_env.filter.ambiente_set.all()

        # Vlans in listed envs
        vlans = list()
        for env_old_filter in envs_old_filter:
            for vlan in env_old_filter.vlan_set.all():
                vlans.append(vlan)

        # Nets in vlan
        nets_ipv4 = list()
        nets_ipv6 = list()
        for vlan in vlans:
            for net in vlan.networkipv4_set.all():
                nets_ipv4.append({'net': net, 'vlan_env': vlan.ambiente})
            for net in vlan.networkipv6_set.all():
                nets_ipv6.append({'net': net, 'vlan_env': vlan.ambiente})

        # Verify subnet ipv4
        for i in range(0, len(nets_ipv4)):
            net = nets_ipv4[i].get('net')
            ip = '%s.%s.%s.%s/%s' % (net.oct1,
                                     net.oct2, net.oct3, net.oct4, net.block)
            network_ip_verify = IPNetwork(ip)

            nets_ipv4_aux = clone(nets_ipv4)
            nets_ipv4_aux.remove(nets_ipv4[i])

            if verify_subnet_and_equip(nets_ipv4_aux, network_ip_verify, 'v4',
                                       net, nets_ipv4[i].get('vlan_env')):
                env_aux_id = nets_ipv4[i].get('vlan_env').id
                if old_env.id == env_aux_id:
                    return True

        # Verify subnet ipv6
        for i in range(0, len(nets_ipv6)):
            net = nets_ipv6[i].get('net')
            ip = '%s:%s:%s:%s:%s:%s:%s:%s/%d' % (net.block1, net.block2, net.block3,
                                                 net.block4, net.block5, net.block6,
                                                 net.block7, net.block8, net.block)
            network_ip_verify = IPNetwork(ip)

            nets_ipv6_aux = clone(nets_ipv6)
            nets_ipv6_aux.remove(nets_ipv6[i])

            if verify_subnet_and_equip(nets_ipv6_aux, network_ip_verify, 'v6',
                                       net, nets_ipv6[i].get('vlan_env')):
                env_aux_id = nets_ipv6[i].get('vlan_env').id
                if old_env.id == env_aux_id:
                    return True

        return False

    def delete(self):
        from networkapi.ip.models import IpCantBeRemovedFromVip
        try:

            if not self.ativada:

                for net4 in self.networkipv4_set.all():
                    net4.delete()

                for net6 in self.networkipv6_set.all():
                    net6.delete()
            else:
                raise VlanCantDeallocate(
                    str(self.nome), 'Cant deallocate all relationships between vlan because its active.')

            super(Vlan, self).delete()

        except IpCantBeRemovedFromVip, e:
            cause = e.cause
            cause['Vlan'] = self.nome
            raise IpCantBeRemovedFromVip(
                cause, 'Esta Vlan possui uma Rede com Requisição Vip apontando para ela, e não pode ser excluída')
        except VlanCantDeallocate, e:
            raise e

    def get_eqpt(self):
        """Returns list of equipments associated with environment."""

        # Get all eqpts of environment
        eqpts = self.ambiente.eqpts

        # Filter of environment
        filenv = self.ambiente.filter

        # Use filter
        if filenv:
            eqpts = eqpts.exclude(equipamento__in=eqpts.filter(
                equipamento__tipo_equipamento__filterequiptype__filter=filenv)
            )

        self.log.debug('Equipments of environment(filtered): %s' % eqpts)

        return eqpts

    def get_vrf(self):

        # get vrf to filter
        vrf = get_model('api_vrf', 'Vrf')
        vrfs = vrf.objects.filter(
            Q(
                Q(vrfvlanequipment__equipment__in=self.get_eqpt()) &
                Q(vrfvlanequipment__vlan__id=self.id)
            ) |
            Q(id=self.ambiente.default_vrf_id)
        )

        return vrfs

    def validate_v3(self):
        """Make validations in values inputted."""

        if self.exist_vlan_num_in_environment(self.id):
            msg = 'Number VLAN can not be duplicated in the environment.'
            self.log.error(msg)
            raise VlanErrorV3(msg)

        if self.exist_vlan_name_in_environment(self.id):
            msg = 'Name VLAN can not be duplicated in the environment.'
            self.log.error(msg)
            raise VlanErrorV3(msg)

        if not self.valid_vlan_name(self.nome):
            msg = 'Name VLAN can not have special characters or breakline.'
            raise VlanErrorV3(msg)

        # Validate Number of vlan in environment related
        equips = self.get_eqpt()

        network.validate_vlan_conflict(equips, self.num_vlan, self.id)

    def create_v3(self, vlan, user):
        """Create new vlan."""

        try:
            env_model = get_model('ambiente', 'Ambiente')
            ogp_models = get_app('api_ogp', 'models')

            self.ambiente = env_model.get_by_pk(vlan.get('environment'))
            self.nome = vlan.get('name').upper()
            self.num_vlan = vlan.get('num_vlan')
            self.descricao = vlan.get('description')
            self.acl_file_name = vlan.get('acl_file_name')
            self.acl_valida = vlan.get('acl_valida', False)
            self.acl_file_name_v6 = vlan.get('acl_file_name_v6')
            self.acl_valida_v6 = vlan.get('acl_valida_v6', False)
            self.ativada = vlan.get('active', False)
            self.vrf = vlan.get('vrf')
            self.acl_draft = vlan.get('acl_draft')
            self.acl_draft_v6 = vlan.get('acl_draft_v6')

            self.vxlan = self.ambiente.vxlan

            # Get environments related
            envs = self.get_environment_related(use_vrf=False)\
                .values_list('id', flat=True)

        except Exception, e:
            raise VlanErrorV3(e)
        else:
            # Create locks for environment
            locks_name = [LOCK_ENVIRONMENT_ALLOCATES % env for env in envs]
            locks_list = create_lock_with_blocking(locks_name)

        try:
            # Allocates 1 number of vlan automatically
            if not self.num_vlan:
                self.allocate_vlan()

            self.validate_v3()

            self.save()

            # Permissions
            perm = ogp_models.ObjectGroupPermission()
            perm.create_perms(
                vlan, self.id, AdminPermission.OBJ_TYPE_VLAN, user)

            # Allocates networkv4
            netv4 = vlan.get('create_networkv4')
            if netv4:
                network_type = vlan.get('create_networkv4').get(
                    'network_type', None)
                prefix = vlan.get('create_networkv4').get('prefix', None)
                environmentvip = vlan.get('create_networkv4').get(
                    'environmentvip', None)

                dict_net = {
                    'network_type': network_type,
                    'prefix': prefix,
                    'vlan': self.id,
                    'environmentvip': environmentvip,
                }

                net4_model = get_model('ip', 'NetworkIPv4')

                netv4_obj = net4_model()

                netv4_obj.create_v3(dict_net, locks_used=locks_name)

            # Allocates networkv6
            if vlan.get('create_networkv6'):

                network_type = vlan.get('create_networkv6').get(
                    'network_type', None)
                prefix = vlan.get('create_networkv6').get('prefix', None)
                environmentvip = vlan.get('create_networkv6').get(
                    'environmentvip', None)

                dict_net = {
                    'network_type': network_type,
                    'prefix': prefix,
                    'vlan': self.id,
                    'environmentvip': environmentvip,
                }

                net6_model = get_model('ip', 'NetworkIPv6')

                netv6_obj = net6_model()

                netv6_obj.create_v3(dict_net, locks_used=locks_name)
        except Exception, e:
            raise VlanErrorV3(e)
        finally:
            # Destroy locks
            destroy_lock(locks_list)

    def update_v3(self, vlan, user):
        """Update vlan."""

        try:
            env_model = get_model('ambiente', 'Ambiente')
            ogp_models = get_app('api_ogp', 'models')

            env = env_model.get_by_pk(vlan.get('environment'))

            self.ambiente = env
            self.nome = vlan.get('name')
            self.num_vlan = vlan.get('num_vlan')
            self.descricao = vlan.get('description')
            self.acl_file_name = vlan.get('acl_file_name')
            self.acl_valida = vlan.get('acl_valida', False)
            self.acl_file_name_v6 = vlan.get('acl_file_name_v6')
            self.acl_valida_v6 = vlan.get('acl_valida_v6', False)
            self.ativada = vlan.get('active', False)
            self.vrf = vlan.get('vrf')
            self.acl_draft = vlan.get('acl_draft')
            self.acl_draft_v6 = vlan.get('acl_draft_v6')

            old_vlan = self.get_by_pk(self.id)
        except Exception, e:
            raise VlanErrorV3(e)

        else:
            # Prepare locks for vlan
            locks_name = [LOCK_VLAN % self.id]

            # If the environment was changed, create lock to validate
            if old_vlan.ambiente != self.ambiente:
                # Get environments related
                envs = self.get_environment_related(use_vrf=False)\
                    .values_list('id', flat=True)

                # Prepare locks for environment
                locks_name += [LOCK_ENVIRONMENT_ALLOCATES % env_id
                               for env_id in envs]

            # Create locks for environment and vlan
            locks_list = create_lock_with_blocking(locks_name)

        try:
            # Activate vlan can not be changed of environment
            if old_vlan.ativada:

                if old_vlan.ambiente != self.ambiente:

                    msg = 'Environment can not be changed in vlan actived.'
                    self.log.error(msg)
                    raise VlanErrorV3(msg)

                if old_vlan.num_vlan != self.num_vlan:

                    msg = 'Number Vlan can not be changed in vlan actived.'
                    self.log.error(msg)
                    raise VlanErrorV3(msg)

                if old_vlan.nome != self.nome:

                    msg = 'Name Vlan can not be changed in vlan actived.'
                    self.log.error(msg)
                    raise VlanErrorV3(msg)

            # If the environment was changed, create lock to validate
            if old_vlan.ambiente != self.ambiente:

                # If vlan has networks of environment, can not be changed
                # of environment
                netv4_vip = self.networkipv4_set.filter(
                    ambient_vip__isnull=False)

                netv6_vip = self.networkipv6_set.filter(
                    ambient_vip__isnull=False)

                if netv4_vip or netv6_vip:

                    msg = u'Not change vlan when networks are of' \
                          ' environment Vip.'
                    self.log.error(msg)
                    raise VlanErrorV3(msg)

                if self.networkipv4_set.all() or self.networkipv6_set.all():
                    # Validate conflicts of network(equal, subnet ou supernet)
                    self.validate_network()

                # Validate name and number
                self.validate_v3()

            self.save()

            # Permissions
            perm = ogp_models.ObjectGroupPermission()
            perm.update_perms(
                vlan, self.id, AdminPermission.OBJ_TYPE_VLAN, user)

        except Exception, e:
            raise VlanErrorV3(e)

        finally:
            # Destroy locks
            destroy_lock(locks_list)

        return self

    def delete_v3(self):
        ogp_models = get_app('api_ogp', 'models')
        ipcantberemovedfromvip = get_model('ip', 'IpCantBeRemovedFromVip')

        id_vlan = self.id

        try:

            if not self.ativada:

                for net4 in self.networkipv4_set.all():
                    net4.delete_v3()

                for net6 in self.networkipv6_set.all():
                    net6.delete_v3()
            else:
                self.log.error(
                    'Cant deallocate all relationships between vlan because '
                    'its active.')
                raise VlanCantDeallocate(
                    str(self.nome),
                    'Cant deallocate all relationships between vlan because '
                    'its active.')

            super(Vlan, self).delete()

        except ipcantberemovedfromvip, e:
            cause = e.cause
            cause['Vlan'] = self.nome
            self.log.error(
                'This Vlan has a Network with Vip Request pointing to it, and '
                'can not be deleted')
            raise ipcantberemovedfromvip(
                cause,
                'This Vlan has a Network with Vip Request pointing to it, and '
                'can not be deleted')
        except VlanCantDeallocate, e:
            raise e

        # Deletes Permissions
        ogp_models.ObjectGroupPermission.objects.filter(
            object_type__name=AdminPermission.OBJ_TYPE_VLAN,
            object_value=id_vlan
        ).delete()

    def activate_v3(self, locks_used):
        """Set column ativada = 1"""

        """
            Send activate notication of network for queue of ACL
                configuration system.
            Update status column  to 'ativada = 1'.

            @raise VlanErrorV3: Error activating a Vlan.
        """

        locks_list = list()
        # Prepare locks for vlan
        lock_name = [LOCK_VLAN % self.id]
        if lock_name not in locks_used:
            # Create locks for environment and vlan
            locks_list = create_lock_with_blocking([lock_name])

        try:

            vlan_slz = get_app('api_vlan', 'serializers')
            self.ativada = 1

            serializer = vlan_slz.VlanV3Serializer(
                self,
                include=('environment__basic',),
                exclude=(
                    'acl_draft',
                    'acl_draft_v6',
                    'acl_valida_v6',
                    'acl_file_name_v6',
                    'acl_valida',
                    'acl_file_name',
                )
            )

            data_to_queue = serializer.data
            data_to_queue.update({
                'description': queue_keys.VLAN_ACTIVATE
            })

            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            queue_manager.append({
                'action': queue_keys.VLAN_ACTIVATE,
                'kind': queue_keys.VLAN_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

            self.save()

        except Exception, e:
            self.log.error(u'Error activating Vlan.: %s' % e)
            raise VlanErrorV3(u'Error activating Vlan.')

        finally:
            if locks_list:
                # Destroy locks
                destroy_lock(locks_list)

    def deactivate_v3(self, locks_used):
        """
            Send activate notication of vlan for queue of ACL
                configuration system.
            Update status column  to 'ativada = 0'.

            @raise VlanErrorV3: Error disabling a Vlan.
        """

        locks_list = list()
        # Prepare locks for vlan
        lock_name = [LOCK_VLAN % self.id]
        if lock_name not in locks_used:
            # Create locks for environment and vlan
            locks_list = create_lock_with_blocking([lock_name])

        try:

            vlan_slz = get_app('api_vlan', 'serializers')
            self.ativada = 0

            serializer = vlan_slz.VlanV3Serializer(
                self,
                include=('environment__basic',),
                exclude=(
                    'acl_draft',
                    'acl_draft_v6',
                    'acl_valida_v6',
                    'acl_file_name_v6',
                    'acl_valida',
                    'acl_file_name',
                )
            )

            data_to_queue = serializer.data
            data_to_queue.update({
                'description': queue_keys.VLAN_DEACTIVATE
            })

            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            queue_manager.append({
                'action': queue_keys.VLAN_DEACTIVATE,
                'kind': queue_keys.VLAN_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

            self.save()

        except Exception, e:
            self.log.error(u'Error disabling Vlan.: %s' % e)
            raise VlanErrorV3(u'Error disabling Vlan.')

        finally:
            if locks_list:
                # Destroy locks
                destroy_lock(locks_list)

    def get_environment_related(self, use_vrf=True):

        env_model = get_model('ambiente', 'Ambiente')

        # get environment or environment assoc with equipments
        # of current vlan
        envs = env_model.objects.filter(
            equipamentoambiente__equipamento__in=self.get_eqpt()
        )

        if use_vrf is True:
            envs = envs.filter(
                # get vlans with customized vrfs of current vlan
                Q(vlan__vrfvlanequipment__vrf__in=self.get_vrf()) |
                # get environments using vrfs of current vlan
                Q(default_vrf__in=self.get_vrf())
            )

        envs = envs.distinct()

        return envs

    # def get_networks_related(self, eqpts=None, has_netv4=True, has_netv6=True,
    #                          exclude_current=True):

    #     if not eqpts:
    #         eqpts = self.get_eqpt()

    #     vlan_model = get_model('vlan', 'Vlan')

    #     vlans_env_eqpt = vlan_model.objects.filter(
    #         # get vlans of environment or environment assoc
    #         ambiente__equipamentoambiente__equipamento__in=eqpts
    #     ).filter(
    #         # get vlans with customized vrfs
    #         Q(vrfvlanequipment__vrf__in=self.get_vrf()) |
    #         # get vlans using vrf of environment
    #         Q(ambiente__default_vrf__in=self.get_vrf())
    #     ).distinct()

    #     if exclude_current:
    #         vlans_env_eqpt = vlans_env_eqpt.exclude(
    #             # exclude current vlan
    #             id=self.id
    #         )
    #     vlans_env_eqpt = vlans_env_eqpt.distinct()

    #     self.log.debug('Query vlans: %s' % vlans_env_eqpt.query)

    #     netv4 = list()
    #     if has_netv4:
    #         netv4 = reduce(list.__add__, [
    #             list(vlan_env.networkipv4_set.all())
    # for vlan_env in vlans_env_eqpt if vlan_env.networkipv4_set.all()], [])

    #     netv6 = list()
    #     if has_netv6:
    #         netv6 = reduce(list.__add__, [
    #             list(vlan_env.networkipv6_set.all())
    # for vlan_env in vlans_env_eqpt if vlan_env.networkipv6_set.all()], [])

    #     return netv4, netv6

    def validate_network(self):

        configs = self.ambiente.configs.all()
        netv4 = self.networkipv4_set.filter()
        netv6 = self.networkipv6_set.filter()

        self.allow_networks_environment(configs, netv4, netv6)

        netv4, netv6 = network.get_networks_related(
            vrfs=self.get_vrf(), eqpts=self.get_eqpt(), exclude=self.id)

        netv4_env_format = [IPNetwork(net.networkv4) for net in netv4]
        netv6_env_format = [IPNetwork(net.networkv6) for net in netv6]

        netv4_format = [IPNetwork(net.networkv4)
                        for net in self.networkipv4_set.all()]
        netv6_format = [IPNetwork(net.networkv6)
                        for net in self.networkipv6_set.all()]

        network.verify_networks(netv4_format, netv4_env_format)
        network.verify_networks(netv6_format, netv6_env_format)

    def allow_networks_environment(self, configs, netv4, netv6):
        """
            Verify if networksv4 and networksv6 are permitted in environment
            by way configs settings.
        """

        for net in netv4:
            configsv4 = configs.filter(
                ip_version='v4'
            )

            nts = [IPNetwork(config.network) for config in configsv4]

            net_ip = [IPNetwork(net.networkv4)]

            if not network.verify_intersect(nts, net_ip)[0]:
                msg = 'Network {} cannot not inserted in environment {} because ' \
                    'it is not within environment network range.'
                msg = msg.format(net.networkv4, self.ambiente.name)
                self.log.error(msg)

                raise VlanErrorV3(msg)

        for net in netv6:
            configsv6 = configs.filter(
                ip_version='v6'
            )

            nts = [IPNetwork(config.network) for config in configsv6]

            net_ip = [IPNetwork(net.networkv6)]

            if not network.verify_intersect(nts, net_ip)[0]:
                msg = 'Network {} cannot not inserted in environment {} because ' \
                    'it is not within environment network range.'
                msg = msg.format(net.networkv6, self.ambiente.name)
                self.log.error(msg)
                raise VlanErrorV3(msg)

    def allocate_vlan(self):
        """Create a Vlan with the new Model

        The fields num_vlan, acl_file_name, acl_valida and ativada will be
        generated automatically

        @return: nothing
        """

        if (self.ambiente.min_num_vlan_1 and self.ambiente.max_num_vlan_1) or \
                (self.ambiente.min_num_vlan_2 and self.ambiente.max_num_vlan_2):

            min_num_01 = self.ambiente.min_num_vlan_1 \
                if self.ambiente.min_num_vlan_1 and self.ambiente.max_num_vlan_1 \
                else self.ambiente.min_num_vlan_2

            max_num_01 = self.ambiente.max_num_vlan_1 \
                if self.ambiente.min_num_vlan_1 and self.ambiente.max_num_vlan_1 \
                else self.ambiente.max_num_vlan_2

            min_num_02 = self.ambiente.min_num_vlan_2 \
                if self.ambiente.min_num_vlan_2 and self.ambiente.max_num_vlan_2 \
                else self.ambiente.min_num_vlan_1

            max_num_02 = self.ambiente.max_num_vlan_2 \
                if self.ambiente.min_num_vlan_2 and self.ambiente.max_num_vlan_2 \
                else self.ambiente.max_num_vlan_1
        else:
            min_num_01 = MIN_VLAN_NUMBER_01
            max_num_01 = MAX_VLAN_NUMBER_01
            min_num_02 = MIN_VLAN_NUMBER_02
            max_num_02 = MAX_VLAN_NUMBER_02

        # Calculate Number VLAN
        self.num_vlan = self.calculate_vlan_number_v3(min_num_01, max_num_01)
        if self.num_vlan is None:
            self.num_vlan = self.calculate_vlan_number_v3(
                min_num_02, max_num_02)
            if self.num_vlan is None:
                raise VlanNumberNotAvailableError(
                    None, u'Number VLAN unavailable for environment %d.'
                    % self.ambiente.id)

    def calculate_vlan_number_v3(self, min_num, max_num, list_available=False):
        """Caculate if has a number available in range (min_num/max_num) to
        specified environment

        @param min_num: Minimum number that the vlan can be created.
        @param max_num: Maximum number that the vlan can be created.
        @param list_available: If = True, return the list of numbers availables

        @return: None when hasn't a number available | num_vlan when found
                 a number available
        """

        interval = range(min_num, max_num + 1)

        # Vlan numbers in interval in the same environment
        vlan_numbers_in_interval = self.search_vlan_numbers(
            self.ambiente_id, min_num, max_num)

        # Find equipment's ids from environmnet that is 'switches',
        # 'roteadores' or 'balanceadores'
        id_equipamentos = self.get_eqpt()

        # Vlan numbers in others environment but in environment that has
        # equipments found in before filter ('switches', 'roteadores' or
        # 'balanceadores')
        vlans_others_environments = Vlan.objects.exclude(
            ambiente__id=self.ambiente_id
        ).filter(
            ambiente__equipamentoambiente__equipamento__id__in=id_equipamentos
        ).values_list('num_vlan', flat=True)

        # Clean duplicates numbers and update merge 'vlan_numbers_in_interval'
        # with 'vlans_others_environments'
        vlan_numbers_in_interval = set(vlan_numbers_in_interval)
        vlan_numbers_in_interval.update(vlans_others_environments)

        self.log.debug('Interval: %s.', interval)
        self.log.debug('VLANs in interval: %s.', vlan_numbers_in_interval)

        diff_set = set(interval) - set(vlan_numbers_in_interval)
        self.log.debug('Difference in the lists: %s.', diff_set)

        if list_available:
            return diff_set
        for num_vlan in diff_set:
            return num_vlan
        return None
