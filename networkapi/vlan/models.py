# -*- coding: utf-8 -*-
from __future__ import with_statement

import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import get_model
from django.db.models import Q

from networkapi.filter.models import verify_subnet_and_equip
from networkapi.infrastructure.ipaddr import IPNetwork
from networkapi.models.BaseModel import BaseModel
from networkapi.queue_tools import queue_keys
from networkapi.queue_tools.queue_manager import QueueManager
from networkapi.semaforo.model import Semaforo
from networkapi.util import clone
from networkapi.util.decorators import cached_property


class VlanError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com Vlan."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


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

    id = models.AutoField(primary_key=True, db_column='id_vlan')
    nome = models.CharField(unique=True, max_length=50)
    num_vlan = models.IntegerField(unique=True)
    ambiente = models.ForeignKey('ambiente.Ambiente', db_column='id_ambiente')
    descricao = models.CharField(max_length=200, blank=True)
    acl_file_name = models.CharField(max_length=200, blank=True)
    acl_valida = models.BooleanField()
    acl_file_name_v6 = models.CharField(max_length=200, blank=True)
    acl_valida_v6 = models.BooleanField()
    ativada = models.BooleanField()
    vrf = models.CharField(max_length=100, null=True, db_column='vrf')

    acl_draft = models.TextField(blank=True, null=True, db_column='acl_draft')
    acl_draft_v6 = models.TextField(
        blank=True, null=True, db_column='acl_draft_v6')

    def _get_networks_ipv4(self):
        """Returns networks v4."""
        networkipv4 = self.networkipv4_set.all().select_related()
        return networkipv4

    networks_ipv4 = property(_get_networks_ipv4)

    def _get_networks_ipv6(self):
        """Returns networks v6."""
        networkipv6 = self.networkipv6_set.all().select_related()
        return networkipv6

    networks_ipv6 = property(_get_networks_ipv6)

    class Meta(BaseModel.Meta):
        db_table = u'vlans'
        managed = True
        unique_together = (('nome', 'ambiente'), ('num_vlan', 'ambiente'))

    @cached_property
    def vrfs(self):
        return self.get_vrf().prefetch_related()

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
            return Vlan.objects.filter(num_vlan__range=(min_num, max_num), ambiente__id=environment_id).values_list('num_vlan', flat=True).distinct().order_by('num_vlan')
        except Exception, e:
            self.log.error(u'Failure to search the Vlans.')
            raise VlanError(e, u'Failure to search the Vlans.')

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
        id_equipamentos = EquipamentoAmbiente.objects.filter(equipamento__tipo_equipamento__id__in=[1, 3, 5],
                                                             ambiente__id=self.ambiente_id).values_list('equipamento',
                                                                                                        flat=True)
        # Vlan numbers in others environment but in environment that has equipments found in before
        # filter ('switches', 'roteadores' or 'balanceadores')
        vlans_others_environments = Vlan.objects.exclude(ambiente__id=self.ambiente_id) \
            .filter(ambiente__equipamentoambiente__equipamento__id__in=id_equipamentos) \
            .values_list('num_vlan', flat=True)

        # Clean duplicates numbers and update merge 'vlan_numbers_in_interval'
        # with 'vlans_others_environments'
        vlan_numbers_in_interval = set(vlan_numbers_in_interval)
        vlan_numbers_in_interval.update(vlans_others_environments)

        self.log.info('Interval: %s.', interval)
        self.log.info('VLANs in interval: %s.', vlan_numbers_in_interval)

        # if len(interval) > len(vlan_numbers_in_interval):
        diff_set = set(interval) - set(vlan_numbers_in_interval)
        self.log.info('Difference in the lists: %s.', diff_set)
        if list_available:
            return diff_set
        for num_vlan in diff_set:
            return num_vlan
        return None

    def activate(self, authenticated_user):
        """ Set column ativada = 1"""
        from networkapi.vlan.serializers import VlanSerializer

        try:
            self.ativada = 1
            self.save()
            # Send to Queue
            queue_manager = QueueManager()
            serializer = VlanSerializer(self)
            data_to_queue = serializer.data
            data_to_queue.update({'description': queue_keys.VLAN_ACTIVATE})
            queue_manager.append({'action': queue_keys.VLAN_ACTIVATE,
                                  'kind': queue_keys.VLAN_KEY, 'data': data_to_queue})
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
        from networkapi.vlan.serializers import VlanSerializer

        try:

            self.ativada = 0
            self.save()
            # Send to Queue
            queue_manager = QueueManager()
            serializer = VlanSerializer(self)
            data_to_queue = serializer.data
            data_to_queue.update({'description': queue_keys.VLAN_DEACTIVATE})
            queue_manager.append({'action': queue_keys.VLAN_DEACTIVATE,
                                  'kind': queue_keys.VLAN_KEY, 'data': data_to_queue})
            queue_manager.send()

        except Exception, e:
            self.log.error(u'Falha ao salvar a VLAN.')
            raise VlanError(e, u'Falha ao salvar a VLAN.')

    def create_new(self, authenticated_user, min_num_01, max_num_01, min_num_02, max_num_02):
        """
        Create a Vlan with the new Model

        The fields num_vlan, acl_file_name, acl_valida and ativada will be generated automatically

        @return: nothing
        """
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

        try:
            self.save()
        except Exception, e:
            msg = u'Error persisting a VLAN.'
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
        if (len(vlan_address) == 0):
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

        try:
            self.save()
        except Exception, e:
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
            return Vlan.objects.filter(num_vlan=number, ambiente=environment).uniqueResult()
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
        for env in ambiente.equipamentoambiente_set.all().exclude(equipamento__tipo_equipamento__in=equipment_types):
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
                        None, 'Já existe uma VLAN cadastrada com o número %s com um equipamento compartilhado nesse ambiente' % (self.num_vlan))

        # Name VLAN can not be duplicated in the environment
        if self.exist_vlan_name_in_environment():
            raise VlanNameDuplicatedError(
                None, 'Name VLAN can not be duplicated in the environment.')

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
                        if self.ambiente.filter_id is None or vlan.ambiente.filter_id is None or int(vlan.ambiente.filter_id) != int(self.ambiente.filter_id):
                            raise VlanNumberEnvironmentNotAvailableError(
                                None, 'Já existe uma VLAN cadastrada com o número %s com um equipamento compartilhado nesse ambiente' % (self.num_vlan))

            old_vlan = self.get_by_pk(self.id)
            old_env = old_vlan.ambiente

            # Old env
            if old_env.filter is not None:
                if self.check_env_shared_equipment(old_env):
                    if self.ambiente.filter_id != old_env.filter_id:
                        raise VlanNumberEnvironmentNotAvailableError(
                            None, 'Um dos equipamentos associados com o ambiente desta Vlan também está associado com outro ambiente que tem uma rede com a mesma faixa, adicione filtros nos ambientes se necessário.')

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
        # get all eqpts of environment
        eqpts = self.ambiente.equipamentoambiente_set.all().exclude(
            equipamento__tipo_equipamento__filterequiptype__filter=self.ambiente.filter
        ).distinct().values_list('equipamento')

        eqpts = [equip[0] for equip in eqpts]

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

    def validate_num_vlan_v3(self):
        """
        Validate if number of vlan is duplicated in environment or
        environment assoc with eqpt.
        """
        equips = self.get_eqpt()
        vlan_model = get_model('vlan', 'Vlan')

        # get vlans with same num_vlan
        vlan = vlan_model.objects.filter(
            ambiente__equipamentoambiente__equipamento__in=equips,
            num_vlan=self.num_vlan
        ).exclude(
            id=self.id
        )

        if vlan:
            raise Exception(
                'There is a registered VLAN with the number in '
                'equipments of environment')

    def validate_v3(self):
        """Make validations in values inputted."""
        if self.exist_vlan_num_in_environment(self.id):
            raise Exception(
                'Number Vlan can not be duplicated in the environment.')

        if self.exist_vlan_name_in_environment(self.id):
            raise Exception(
                'Name VLAN can not be duplicated in the environment.')

        # update
        if self.id:
            old_env = self.get_by_pk(self.id)
            if old_env.ativada:
                if old_env.ambiente != self.ambiente:
                    raise Exception(
                        'Environment can not be changed in vlan actived')
                if old_env.num_vlan != self.num_vlan:
                    raise Exception(
                        'Number Vlan can not be changed in vlan actived')

            if old_env.ambiente != self.ambiente:
                netv4_vip = self.networkipv4_set.filter(
                    ambient_vip__isnull=False)
                netv6_vip = self.networkipv6_set.filter(
                    ambient_vip__isnull=False)
                if netv4_vip or netv6_vip:
                    raise NotImplementedError(
                        'Not change vlan when networks are of environment Vip'
                    )
                self.validate_network()

        self.validate_num_vlan_v3()

    def create_v3(self):
        """Create new vlan."""
        self.validate_v3()

        self.save()

    def update_v3(self):
        """Update vlan."""

        self.validate_v3()

        self.save()

    def get_environment_related(self):

        env_model = get_model('ambiente', 'Ambiente')

        envs = env_model.objects.filter(
            # get environment or environment assoc with equipments
            # of current vlan
            equipamentoambiente__equipamento__in=self.get_eqpt()
        ).filter(
            # get vlans with customized vrfs of current vlan
            Q(vlan__vrfvlanequipment__vrf__in=self.get_vrf()) |
            # get environments using vrfs of current vlan
            Q(default_vrf__in=self.get_vrf())
        ).distinct()

        return envs

    def get_networks_related(self, has_netv4=True, has_netv6=True, exclude_current=True):

        vlan_model = get_model('vlan', 'Vlan')

        vlans_env_eqpt = vlan_model.objects.filter(
            # get vlans of environment or environment assoc
            ambiente__equipamentoambiente__equipamento__in=self.get_eqpt()
        ).filter(
            # get vlans with customized vrfs
            Q(vrfvlanequipment__vrf__in=self.get_vrf()) |
            # get vlans using vrf of environment
            Q(ambiente__default_vrf__in=self.get_vrf())
        )

        if exclude_current:
            vlans_env_eqpt = vlans_env_eqpt.exclude(
                # exclude current vlan
                id=self.id
            )
        vlans_env_eqpt = vlans_env_eqpt.distinct()

        self.log.debug('Query vlans: %s' % vlans_env_eqpt.query)

        netv4 = list()
        if has_netv4:
            netv4 = reduce(list.__add__, [
                list(vlan_env.networkipv4_set.all())
                for vlan_env in vlans_env_eqpt if vlan_env.networkipv4_set.all()], [])

        netv6 = list()
        if has_netv6:
            netv6 = reduce(list.__add__, [
                list(vlan_env.networkipv6_set.all())
                for vlan_env in vlans_env_eqpt if vlan_env.networkipv6_set.all()], [])

        return netv4, netv6

    def validate_network(self):

        configs = self.ambiente.configs.all()
        netv4 = self.networkipv4_set.filter()
        netv6 = self.networkipv6_set.filter()

        self.allow_networks_environment(configs, netv4, netv6)

        netv4, netv6 = self.get_networks_related()

        netv4_env, netv6_env = self.prepare_networks(
            netv4,
            netv6
        )

        netv4, netv6 = self.prepare_networks(
            self.networkipv4_set.all(),
            self.networkipv6_set.all()
        )

        v4_interset = self.verify_networks(netv4, netv4_env)
        v6_interset = self.verify_networks(netv6, netv6_env)

        if v4_interset[0] or v6_interset[0]:
            raise Exception(
                'Um dos equipamentos associados com o ambiente desta Vlan '
                'também está associado com outro ambiente que tem uma rede '
                'com a mesma faixa, adicione filtros nos ambientes se necessário.')

    def allow_networks_environment(self, configs, netv4, netv6):
        """
            Verify if networksv4 and networksv6 are permitted in environment
            by way configs settings.
        """

        for net in netv4:
            configsv4 = configs.filter(
                ip_config__type='v4',
                ip_config__network_type=net.network_type
            )

            nts = [IPNetwork(config.ip_config.subnet) for config in configsv4]

            net_ip = [IPNetwork(net.networkv4)]

            if not self.verify_intersect(nts, net.block, net_ip)[0]:
                raise Exception(
                    'Network can not inserted in environment %s because '
                    'network %s are in out of the range of allowed networks ' %
                    (self.ambiente.name, net.networkv4)
                )

        for net in netv6:
            configsv6 = configs.filter(
                ip_config__type='v6',
                ip_config__network_type=net.network_type
            )

            nts = [IPNetwork(config.ip_config.subnet) for config in configsv6]

            net_ip = [IPNetwork(net.networkv6)]

            if not self.verify_intersect(nts, net.block, net_ip)[0]:
                raise Exception(
                    'Network can not inserted in environment %s because '
                    'network %s are in out of the range of allowed networks ' %
                    (self.ambiente.name, net.networkv6)
                )

    def prepare_networks(self, netv4, netv6):
        """
            Make a dict where key is block of network and value is a list
            network with block.
        """

        netv4_dict = dict()
        for net in netv4:
            if not netv4_dict.get(net.block):
                netv4_dict.update({
                    net.block: list()
                })
            nt = IPNetwork(net.networkv4)
            netv4_dict[net.block].append(nt)

        netv6_dict = dict()
        for net in netv6:
            if not netv6_dict.get(net.block):
                netv6_dict.update({
                    net.block: list()
                })
            nt = IPNetwork(net.networkv6)
            netv6_dict[net.block].append(nt)

        return netv4_dict, netv6_dict

    def verify_networks(self, nets1, nets2):
        """
            Verify a list of networks has make intersect with a second list
            and contrariwise.
        """

        vl_net1 = reduce(list.__add__, nets1.values(), [])
        vl_net2 = reduce(list.__add__, nets2.values(), [])

        # has network conflict with same networks
        intersect = list(set(vl_net1) & set(vl_net2))
        if intersect:
            self.log.info('Same network - intersect:%s' % intersect)
            return intersect, intersect

        for block1 in nets1.keys():

            for block2 in nets2.keys():

                # network1 < network2 of environment
                # Example: /23 < /24 = /24 is subnet
                if block1 < block2:
                    # get subnet of network1
                    ret = self.verify_intersect(nets1[block1], block2, vl_net2)

                # network1 >= network2 of environment
                # Example: /24 >= /23 = /24 is subnet
                else:
                    # get subnet of network2
                    ret = self.verify_intersect(nets2[block2], block1, vl_net1)

                if ret[0]:
                    return ret

        return [], []

    def verify_intersect(self, nets, new_prefix, nets2):
        """
            Verify if a item of a list of networks has make intersect
            with a second list.
        """

        for net in nets:
            try:
                subnets = list(net.subnet(new_prefix=new_prefix))
                # has network conflict with subnet of network1

                intersect = list(set(subnets) & set(nets2))
                if intersect:
                    self.log.info(
                        'Subnet intersect:%s, supernet:%s' % (intersect, net))
                    return intersect, net
            except:
                pass

        return [], []
