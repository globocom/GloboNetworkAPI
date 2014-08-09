# -*- coding:utf-8 -*-
'''
Title: Infrastructure NetworkAPI
Author: globo.com / TQI
Copyright: ( c )  2009 globo.com todos os direitos reservados.
'''
from __future__ import with_statement
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from networkapi.log import Log
from networkapi.semaforo.model import Semaforo
from networkapi.models.BaseModel import BaseModel
from _mysql_exceptions import OperationalError
from networkapi.infrastructure.ipaddr import IPNetwork
from networkapi.util import clone
from networkapi.filter.models import verify_subnet_and_equip


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


class TipoRede(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_tipo_rede')
    tipo_rede = models.CharField(max_length=100)

    log = Log('TipoRede')

    class Meta(BaseModel.Meta):
        db_table = u'tipo_rede'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        try:
            return TipoRede.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise NetworkTypeNotFoundError(e, u'There is no network type with pk = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failed to get network type.')
            raise VlanError(e, u'Failed to get network type.')

    @classmethod
    def get_by_name(cls, name):
        try:
            tipos = TipoRede.objects.filter(tipo_rede__iexact=name)
            if len(tipos) == 0:
                raise NetworkTypeNotFoundError(None, u'There is no network type with name = %s.' % name)
            return tipos[0]
        except NetworkTypeNotFoundError, e:
            raise e
        except Exception, e:
            cls.log.error(u'Failed to get network type.')
            raise VlanError(e, u'Failed to get network type.')


class Vlan(BaseModel):

    from networkapi.ambiente.models import Ambiente

    log = Log('Vlan')

    id = models.AutoField(primary_key=True, db_column='id_vlan')
    nome = models.CharField(unique=True, max_length=50)
    num_vlan = models.IntegerField(unique=True)
    ambiente = models.ForeignKey(Ambiente, db_column='id_ambiente')
    descricao = models.CharField(max_length=200, blank=True)
    acl_file_name = models.CharField(max_length=200, blank=True)
    acl_valida = models.BooleanField()
    acl_file_name_v6 = models.CharField(max_length=200, blank=True)
    acl_valida_v6 = models.BooleanField()
    ativada = models.BooleanField()

    class Meta(BaseModel.Meta):
        db_table = u'vlans'
        managed = True
        unique_together = (('nome', 'ambiente'), ('num_vlan', 'ambiente'))

    def get_by_pk(self, id):
        '''Get Vlan by id.

        @return: Vlan.

        @raise VlanNotFoundError: Vlan is not registered.
        @raise VlanError: Failed to search for the Vlan.
        @raise OperationalError: Lock wait timeout exceed
        '''
        try:
            return Vlan.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise VlanNotFoundError(e, u'Dont there is a Vlan by pk = %s.' % id)
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def get_vlan_by_acl(self, acl_file):
        try:
            vlan = Vlan.objects.filter(acl_file_name=acl_file).uniqueResult()

            if self.id is  not None:
                if vlan.id == self.id:
                    return
            raise VlanACLDuplicatedError(None, 'uThere is already an Vlan with the Acl - Ipv4 = %s.' % acl_file)
        except VlanACLDuplicatedError, e:
            raise VlanACLDuplicatedError(e, e.message)
        except ObjectDoesNotExist, e:
            pass
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def get_vlan_by_acl_v6(self, acl_file_v6):
        try:

            vlan = Vlan.objects.filter(acl_file_name_v6=acl_file_v6).uniqueResult()

            if self.id is  not None:
                if vlan.id == self.id:
                    return

            raise VlanACLDuplicatedError(None, 'uThere is already an Vlan with the Acl - Ipv6 = %s.' % acl_file_v6)
        except VlanACLDuplicatedError, e:
            raise VlanACLDuplicatedError(e, e.message)
        except ObjectDoesNotExist, e:
            pass
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def existVlanNameInEnvironment(self):
        try:
            Vlan.objects.get(nome__iexact=self.nome, ambiente__id=self.ambiente.id)
            return True
        except ObjectDoesNotExist:
            return False
        except Exception, e:
            self.log.error(u'Falha ao pesquisar a VLAN.')
            raise VlanError(e, u'Falha ao pesquisar a VLAN.')

    def search_vlan_numbers(self, environment_id, min_num, max_num):
        try:
            return Vlan.objects.filter(num_vlan__range=(min_num, max_num), ambiente__id=environment_id).values_list('num_vlan', flat=True).distinct().order_by('num_vlan')
        except Exception, e:
            self.log.error(u'Falha ao pesquisar as VLANs.')
            raise VlanError(e, u'Falha ao pesquisar as VLANs.')

    def search(self, environment_id=None):
        try:
            v = Vlan.objects.all()

            if environment_id is not None:
                v = v.filter(ambiente__id=environment_id)
            return v
        except Exception, e:
            self.log.error(u'Falha ao pesquisar as VLANs.')
            raise VlanError(e, u'Falha ao pesquisar as VLANs.')

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
        vlan_numbers_in_interval = self.search_vlan_numbers(self.ambiente_id, min_num, max_num)

        # Find equipment's ids from environmnet that is 'switches', 'roteadores' or 'balanceadores'
        id_equipamentos = EquipamentoAmbiente.objects.filter(equipamento__tipo_equipamento__id__in=[1, 3, 5],
                                                             ambiente__id=self.ambiente_id).values_list('equipamento',
                                                                                                        flat=True)
        # Vlan numbers in others environment but in environment that has equipments found in before
        # filter ('switches', 'roteadores' or 'balanceadores')
        vlans_others_environments = Vlan.objects.exclude(ambiente__id=self.ambiente_id) \
            .filter(ambiente__equipamentoambiente__equipamento__id__in=id_equipamentos) \
                .values_list('num_vlan', flat=True)

        # Clean duplicates numbers and update merge 'vlan_numbers_in_interval' with 'vlans_others_environments'
        vlan_numbers_in_interval = set(vlan_numbers_in_interval)
        vlan_numbers_in_interval.update(vlans_others_environments)

        self.log.info("Interval: %s.", interval)
        self.log.info("VLANs in interval: %s.", vlan_numbers_in_interval)

        # if len(interval) > len(vlan_numbers_in_interval):
        diff_set = set(interval) - set(vlan_numbers_in_interval)
        self.log.info("Difference in the lists: %s.", diff_set)
        if list_available:
            return diff_set
        for num_vlan in diff_set:
            return num_vlan
        return None

    def activate(self, authenticated_user):
        """ Set column ativada = 1"""
        try:
            self.ativada = 1
            self.save(authenticated_user)
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
            self.save(authenticated_user)
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
        if self.existVlanNameInEnvironment():
            raise VlanNameDuplicatedError(None, 'Name VLAN can not be duplicated in the environment.')


        # Calculate Number VLAN
        self.num_vlan = self.calculate_vlan_number(min_num_01, max_num_01)
        if self.num_vlan is None:
            self.num_vlan = self.calculate_vlan_number(min_num_02, max_num_02)
            if self.num_vlan is None:
                raise VlanNumberNotAvailableError(None, u'Number VLAN unavailable for environment %d.' % self.ambiente.id)

        # Default values
        self.acl_file_name = self.nome
        self.acl_valida = 0
        self.ativada = 0

        try:
            self.save(authenticated_user)
        except Exception, e:
            msg = u'Error persisting a VLAN.'
            self.log.error(msg)
            raise VlanError(e, msg)

    def create(self, authenticated_user, min_num_01, max_num_01, min_num_02, max_num_02):
        '''Insere uma nova VLAN.

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
        '''
        if self.nome is not None:
            self.nome = self.nome.upper()

        # Tipo de Rede
        if self.tipo_rede.id is not None:
            self.tipo_rede = TipoRede().get_by_pk(self.tipo_rede.id)

        # Verificar duplicidade do Nome da VLAN
        if self.existVlanNameInEnvironment():
            raise VlanNameDuplicatedError(None, 'VLAN com nome duplicado dentro do ambiente.')

        Semaforo.lock(Semaforo.ALOCAR_VLAN_ID)

        # Calcular o Numero da VLAN
        self.num_vlan = self.calculate_vlan_number(min_num_01, max_num_01)
        if self.num_vlan is None:
            self.num_vlan = self.calculate_vlan_number(min_num_02, max_num_02)
            if self.num_vlan is None:
                raise VlanNumberNotAvailableError(None, u'Não existe número de VLAN disponível para o ambiente %d.' % self.ambiente.id)

        # Calcular o Endereço de Rede da VLAN
        vlan_address = self.calculate_vlan_address()
        if (len(vlan_address) == 0):
            raise VlanNetworkAddressNotAvailableError(None, u'Não existe endereço de rede disponível para o cadastro da VLAN.')

        self.rede_oct1, self.rede_oct2, self.rede_oct3, self.rede_oct4 = vlan_address

        # Valores Default
        self.bloco = 24
        self.masc_oct1 = 255
        self.masc_oct2 = 255
        self.masc_oct3 = 255
        self.masc_oct4 = 0
        self.broadcast = '%d.%d.%d.255' % (self.rede_oct1, self.rede_oct2, self.rede_oct3)
        self.acl_file_name = self.nome
        self.acl_valida = 0
        self.ativada = 0

        try:
            self.save(authenticated_user)
        except Exception, e:
            self.log.error(u'Falha ao inserir a VLAN.')
            raise VlanError(e, u'Falha ao inserir a VLAN.')

    def get_by_number_and_environment(self, number, environment):
        '''Get Vlan by number.

        @return: Vlan.

        @raise VlanNotFoundError: Vlan is not registered.
        @raise VlanError: Failed to search for the Vlan.
        @raise OperationalError: Lock wait timeout exceed
        '''
        try:
            return Vlan.objects.filter(num_vlan=number, ambiente=environment).uniqueResult()
        except ObjectDoesNotExist, e:
            raise VlanNotFoundError(e, u'Dont there is a Vlan by number = %s.' % number)
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def get_by_number(self, number):
        '''Get Vlan by number.

        @return: Vlan.

        @raise VlanNotFoundError: Vlan is not registered.
        @raise VlanError: Failed to search for the Vlan.
        @raise OperationalError: Lock wait timeout exceed
        '''
        try:
            return Vlan.objects.filter(num_vlan=number).uniqueResult()
        except ObjectDoesNotExist, e:
            raise VlanNotFoundError(e, u'Dont there is a Vlan by number = %s.' % number)
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def get_by_name(self, name):
        '''Get Vlan by name.

        @return: Vlan.

        @raise VlanNotFoundError: Vlan is not registered.
        @raise VlanError: Failed to search for the Vlan.
        @raise OperationalError: Lock wait timeout exceed
        '''
        try:
            return Vlan.objects.filter(nome=name).uniqueResult()
        except ObjectDoesNotExist, e:
            raise VlanNotFoundError(e, u'Dont there is a Vlan by name = %s.' % name)
        except OperationalError, e:
            self.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            self.log.error(u'Failure to search the Vlan.')
            raise VlanError(e, u'Failure to search the Vlan.')

    def insert_vlan(self, authenticated_user):
        """
        Insere uma nova Vlan

        @return ID new Vlan

        @raise VlanNameDuplicatedError: Nome do Vlan já existe.

        @raise VlanNumberEnvironmentNotAvailableError: Numero e Ambiente da VLan já existe.

        @raise VlanError: Erro ao cadastrar Vlan
        """

        try:
            self.get_by_number_and_environment(self.num_vlan, self.ambiente)
            ambiente = "%s - %s - %s" % (self.ambiente.divisao_dc.nome, self.ambiente.ambiente_logico.nome, self.ambiente.grupo_l3.nome)
            raise VlanNumberEnvironmentNotAvailableError(None, "Já existe uma VLAN cadastrada com o número %s no ambiente %s" % (self.num_vlan, ambiente))
        except VlanNotFoundError:
            pass

        ambiente = self.ambiente

        equips = list()
        envs = list()

        for env in ambiente.equipamentoambiente_set.all():
            equips.append(env.equipamento)

        for equip in equips:
            for env in equip.equipamentoambiente_set.all():
                if not env in envs:
                    envs.append(env.ambiente)

        for env in envs:
            for vlan in env.vlan_set.all():
                if int(vlan.num_vlan) == int(self.num_vlan):
                    if self.ambiente.filter_id == None or vlan.ambiente.filter_id == None or int(vlan.ambiente.filter_id) != int(self.ambiente.filter_id):
                        raise VlanNumberEnvironmentNotAvailableError(None, "Já existe uma VLAN cadastrada com o número %s com um equipamento compartilhado nesse ambiente" % (self.num_vlan))

        try:
            self.get_by_name(self.nome)
            raise VlanNameDuplicatedError(None, "Já existe uma VLAN cadastrada com o nome %s" % self.nome)
        except VlanNotFoundError:
            pass

        try:
            return self.save(authenticated_user)

        except Exception, e:
            self.log.error(u'Falha ao inserir VLAN.')
            raise VlanError(e, u'Falha ao inserir VLAN.')

    def edit_vlan(self, authenticated_user, change_name, change_number_environment):
        """
        Edita uma Vlan

        @return None

        @raise VlanNameDuplicatedError: Nome do Vlan já existe.

        @raise VlanNumberEnvironmentNotAvailableError: Numero e Ambiente da VLan já existe.

        @raise VlanError: Erro ao cadastrar Vlan
        """

        if change_number_environment:
            try:
                self.get_by_number_and_environment(self.num_vlan, self.ambiente)
                ambiente = "%s - %s - %s" % (self.ambiente.divisao_dc.nome, self.ambiente.ambiente_logico.nome, self.ambiente.grupo_l3.nome)
                raise VlanNumberEnvironmentNotAvailableError(None, "Já existe uma VLAN cadastrada com o número %s no ambiente %s" % (self.num_vlan, ambiente))
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
                    if not env in envs:
                        envs.append(env.ambiente)

            for env in envs:
                for vlan in env.vlan_set.all():
                    if int(vlan.num_vlan) == int(self.num_vlan) and int(vlan.id) != int(self.id):
                        if self.ambiente.filter_id == None or vlan.ambiente.filter_id == None or int(vlan.ambiente.filter_id) != int(self.ambiente.filter_id):
                            raise VlanNumberEnvironmentNotAvailableError(None, "Já existe uma VLAN cadastrada com o número %s com um equipamento compartilhado nesse ambiente" % (self.num_vlan))

            old_vlan = self.get_by_pk(self.id)
            old_env = old_vlan.ambiente

            # Old env
            if old_env.filter != None:
                if self.check_env_shared_equipment(old_env):
                    if self.ambiente.filter_id != old_env.filter_id:
                        raise VlanNumberEnvironmentNotAvailableError(None, "Um dos equipamentos associados com o ambiente desta Vlan também está associado com outro ambiente que tem uma rede com a mesma faixa, adicione filtros nos ambientes se necessário.")

        if change_name:
            try:
                self.get_by_name(self.nome)
                raise VlanNameDuplicatedError(None, "Já existe uma VLAN cadastrada com o nome %s" % self.nome)
            except VlanNotFoundError:
                pass

        try:
            return self.save(authenticated_user)

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
            ip = "%s.%s.%s.%s/%s" % (net.oct1, net.oct2, net.oct3, net.oct4, net.block)
            network_ip_verify = IPNetwork(ip)

            nets_ipv4_aux = clone(nets_ipv4)
            nets_ipv4_aux.remove(nets_ipv4[i])

            if verify_subnet_and_equip(nets_ipv4_aux, network_ip_verify, 'v4', net, nets_ipv4[i].get('vlan_env')):
                env_aux_id = nets_ipv4[i].get('vlan_env').id
                if old_env.id == env_aux_id:
                    return True

        # Verify subnet ipv6
        for i in range(0, len(nets_ipv6)):
            net = nets_ipv6[i].get('net')
            ip = "%s:%s:%s:%s:%s:%s:%s:%s/%d" % (net.block1, net.block2, net.block3, net.block4, net.block5, net.block6, net.block7, net.block8, net.block)
            network_ip_verify = IPNetwork(ip)

            nets_ipv6_aux = clone(nets_ipv6)
            nets_ipv6_aux.remove(nets_ipv6[i])

            if verify_subnet_and_equip(nets_ipv6_aux, network_ip_verify, 'v6', net, nets_ipv6[i].get('vlan_env')):
                env_aux_id = nets_ipv6[i].get('vlan_env').id
                if old_env.id == env_aux_id:
                    return True

        return False

    def delete(self, authenticated_user):
        from networkapi.ip.models import IpCantBeRemovedFromVip
        try:

            if not self.ativada:

                for net4 in self.networkipv4_set.all():
                    net4.delete(authenticated_user)

                for net6 in self.networkipv6_set.all():
                    net6.delete(authenticated_user)
            else:
                raise VlanCantDeallocate(str(self.nome), 'Cant deallocate all relationships between vlan because its active.')

            super(Vlan, self).delete(authenticated_user)

        except IpCantBeRemovedFromVip, e:
            cause = e.cause
            cause['Vlan'] = self.nome
            raise IpCantBeRemovedFromVip(cause, "Esta Vlan possui uma Rede com Requisição Vip apontando para ela, e não pode ser excluída")
        except VlanCantDeallocate, e:
            raise e
