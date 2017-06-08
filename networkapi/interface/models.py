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
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.ambiente.models import Ambiente
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import TipoEquipamento
from networkapi.exception import InvalidValueError
from networkapi.models.BaseModel import BaseModel
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_regex


class InterfaceError(Exception):

    """Representa um erro ocorrido durante acesso à tabela interfaces."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class InterfaceInvalidBackFrontError(InterfaceError):

    """Exception thrown when try to remove connection between interfaces"""

    def __init__(self, cause, message=None):
        InterfaceError.__init__(self, cause, message)


class InterfaceNotFoundError(InterfaceError):

    """Retorna exceção quando não encontra a interface através da pesquisa por chave primária ou chave única."""

    def __init__(self, cause, message=None):
        InterfaceError.__init__(self, cause, message)


class InvalidValueForProtectedError(InterfaceError):

    """Retorna exceção quando o valor informado para o atributo "protegida" da interface for inválido."""

    def __init__(self, cause, message=None):
        InterfaceError.__init__(self, cause, message)


class FrontLinkNotFoundError(InterfaceError):

    """Retorna exceção quando ligacao_front informada for inexistente."""

    def __init__(self, cause, message=None):
        InterfaceError.__init__(self, cause, message)


class BackLinkNotFoundError(InterfaceError):

    """Retorna exceção quando ligacao_back informada for inexistente."""

    def __init__(self, cause, message=None):
        InterfaceError.__init__(self, cause, message)


class InterfaceForEquipmentDuplicatedError(InterfaceError):

    """Retorna exceção quando já existir uma interface com o mesmo nome para o equipamento informado."""

    def __init__(self, cause, message=None):
        InterfaceError.__init__(self, cause, message)


class InterfaceUsedByOtherInterfaceError(InterfaceError):

    """Retorna exceção quando a interface a ser removida for utilizada por outra interface."""

    def __init__(self, cause, message=None):
        InterfaceError.__init__(self, cause, message)


class InterfaceProtectedError(InterfaceError):

    """Retorna exceção quando a interface tem o status protegida diferente do pesquisado."""

    def __init__(self, cause, message=None):
        InterfaceError.__init__(self, cause, message)


class TipoInterface(BaseModel):

    id = models.AutoField(primary_key=True, db_column='id_tipo_interface')
    tipo = models.CharField(unique=True, max_length=20)

    log = logging.getLogger('Tipo de Interface')

    class Meta(BaseModel.Meta):
        db_table = u'tipo_interface'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        try:
            return TipoInterface.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise InterfaceNotFoundError(
                e, u'Can not find a TipoInterface with id = %s.' % id)
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar o tipo de interface.')
            raise InterfaceError(e, u'Falha ao pesquisar o tipo de interface.')

    @classmethod
    def get_by_name(cls, name):
        """"Get TipoInterface by tipo.
        @return: TipoInterface.
        """
        try:
            return TipoInterface.objects.get(tipo__iexact=name)
        except ObjectDoesNotExist, e:
            raise InterfaceNotFoundError(
                e, u'Can not find a TipoInterface with tipo = %s.' % name)
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar o tipo de interface.')
            raise InterfaceError(e, u'Falha ao pesquisar o tipo de interface.')


class PortChannel(BaseModel):

    log = logging.getLogger('PortChannel')

    id = models.AutoField(primary_key=True, db_column='id_port_channel')
    nome = models.CharField(max_length=10, unique=True)
    lacp = models.BooleanField(default=1)

    class Meta(BaseModel.Meta):
        db_table = u'port_channel'
        managed = True

    def create(self, authenticated_user):
        """Add new port channel"""

        # Checks if name is valid
        try:
            if not is_valid_int_greater_zero_param(self.nome):
                raise InvalidValueError(None, 'nome', self.nome)
        except Exception, e:
            raise InvalidValueError(None, e.param, e.value)

        try:
            return self.save()
        except Exception, e:
            self.log.error(u'Failed to add port channel.')
            raise InterfaceError(e, u'Failed to add port channel.')

    @classmethod
    def get_by_pk(cls, id):
        try:
            return PortChannel.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise InterfaceNotFoundError(
                e, u'Can not find a Channel with id = %s.' % id)
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar o Channel.')
            raise InterfaceError(e, u'Falha ao pesquisar o interface.')

    @classmethod
    def get_by_name(cls, name):
        try:
            return PortChannel.objects.filter(nome=name)
        except ObjectDoesNotExist, e:
            raise InterfaceNotFoundError(
                e, u'Can not find a Channel with name = %s.' % id)
        except Exception, e:
            cls.log.error(u'Failure to search the Group L3.')
            raise InterfaceError(e, u'Failure to search the Group L3.')

    def delete(self, user):
        """Override Django method to remove port channel.
        """
        id = self.id
        interfaces = Interface.objects.all().filter(channel=id)
        for interface in interfaces:
            interface.channel = None
            interface.save(user)
        super(PortChannel, self).delete()

    def list_interfaces(self):
        """Override Django method to remove port channel.
        """
        try:
            return Interface.objects.all().filter(channel=self)
        except ObjectDoesNotExist, e:
            raise InterfaceNotFoundError(
                e, u'Can not find interfaces for channel: %s.' % self.id)


class Interface(BaseModel):
    equipamento = models.ForeignKey(Equipamento, db_column='id_equip')
    interface = models.CharField(unique=True, max_length=20)
    protegida = models.BooleanField()
    descricao = models.CharField(max_length=200, blank=True)
    id = models.AutoField(primary_key=True, db_column='id_interface')
    ligacao_front = models.ForeignKey(
        'self', null=True, db_column='id_ligacao_front', blank=True, related_name='interfaces_front')
    ligacao_back = models.ForeignKey(
        'self', null=True, db_column='id_ligacao_back', blank=True, related_name='interfaces_back')
    vlan_nativa = models.CharField(
        max_length=200, blank=True, null=True, db_column='vlan_nativa', default=1)
    tipo = models.ForeignKey(
        TipoInterface, db_column='id_tipo_interface', blank=True, default=1)
    channel = models.ForeignKey(
        PortChannel, db_column='id_channel', blank=True, null=True)

    log = logging.getLogger('Interface')

    class Meta(BaseModel.Meta):
        db_table = u'interfaces'
        managed = True
        unique_together = ('interface', 'equipamento')

    @classmethod
    def get_by_interface_equipment(cls, interface, equipment_id):
        try:
            return Interface.objects.get(interface__iexact=interface, equipamento__id=equipment_id)
        except ObjectDoesNotExist, e:
            raise InterfaceNotFoundError(
                e, u'Interface com nome %s e equipamento %s não cadastrada.' % (interface, equipment_id))
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar a interface.')
            raise InterfaceError(e, u'Falha ao pesquisar a interface.')

    @classmethod
    def get_by_pk(cls, id):
        try:
            return Interface.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise InterfaceNotFoundError(
                e, u'Can not find a Interface with id = %s.' % id)
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar a interface.')
            raise InterfaceError(e, u'Falha ao pesquisar a interface.')

    def search_interfaces(self, from_interface):
        """Retorna a interface e as todas as interfaces ligadas no front ou no back da mesma.

        Se a interface do front é a interface "from_interface" então deverá seguir a ligação pelo back,
        caso contrário, deverá seguir pelo front.

        A busca encerra quando não tem mais ligação ou quando encontra um "loop" por erro
        na configuração do banco de dados.

        @param from_interface: Interface de origem da consulta.

        @return: Lista de interfaces.

        @raise InterfaceError: Falha na consulta de interfaces.
        """
        interfaces = []

        try:
            interface = self
            while (interface is not None):
                interfaces.append(interface)

                if (interface.ligacao_back is not None) and (from_interface.id != interface.ligacao_back_id):
                    from_interface = interface
                    interface = interface.ligacao_back
                elif (interface.ligacao_front is not None) and (from_interface.id != interface.ligacao_front_id):
                    from_interface = interface
                    interface = interface.ligacao_front
                else:
                    interface = None

                if (interface is not None) and (interface in interfaces):
                    break
        except Exception, e:
            self.log.error(
                u'Falha ao pesquisar as interfaces de uma interface.')
            raise InterfaceError(
                e, u'Falha ao pesquisar as interfaces de uma interface.')

        return interfaces

    def search_front_back_interfaces(self):
        """Busca todas as interfaces ligadas no front e no back da interface.

        Retorna um set vazio se não tiver nenhuma interface nas ligações.

        @return: Set de interfaces.

        @raise InterfaceError: Falha na consulta de interfaces.
        """
        interfaces = set()

        try:
            if self.ligacao_front is not None:
                interfaces.update(self.ligacao_front.search_interfaces(self))

            if self.ligacao_back is not None:
                interfaces.update(self.ligacao_back.search_interfaces(self))
        except Exception, e:
            self.log.error(
                u'Falha ao pesquisar as interfaces da ligação front e back.')
            raise InterfaceError(
                e, u'Falha ao pesquisar as interfaces da ligação front e back.')

        return interfaces

    def get_server_switch_or_router_interface_from_host_interface(self, protegida=None):
        """A partir da ligacao_front da interface local busca uma interface ligada a um equipamento do tipo SWITCH.

        @param protegida: Indicação do campo 'protegida' da interface do switch.

        @return: Interface ligada a um equipamento do tipo SWITCH.

        @raise InterfaceError: Falha ao pesquisar a interface do switch

        @raise InterfaceNotFoundError: Interface do switch não encontrada.

        @raise InterfaceProtectedError: A interface do switch está com o campo protegida diferente do parâmetro.
        """

        interface_ids = []
        from_interface = self
        interface = self.ligacao_front
        try:
            while (interface is not None) and (interface.equipamento.tipo_equipamento_id != TipoEquipamento.TIPO_EQUIPAMENTO_SWITCH) \
                    and (interface.equipamento.tipo_equipamento_id != TipoEquipamento.TIPO_EQUIPAMENTO_ROUTER)\
                    and (interface.equipamento.tipo_equipamento_id != TipoEquipamento.TIPO_EQUIPAMENTO_SERVIDOR):
                interface_ids.append(interface.id)

                if (interface.ligacao_back is not None) and (from_interface.id != interface.ligacao_back_id):
                    from_interface = interface
                    interface = interface.ligacao_back
                elif (interface.ligacao_front is not None) and (from_interface.id != interface.ligacao_front_id):
                    from_interface = interface
                    interface = interface.ligacao_front
                else:
                    interface = None

                if interface is not None:
                    if interface.id in interface_ids:
                        raise InterfaceNotFoundError(
                            None, u'Interface do tipo switch não encontrada a partir do front da interface %d.' % self.id)
        except InterfaceNotFoundError, e:
            raise e
        except Exception, e:
            self.log.error(u'Falha ao pesquisar a interface do switch.')
            raise InterfaceError(
                e, u'Falha ao pesquisar a interface do switch.')

        if (interface is None):
            raise InterfaceNotFoundError(
                None, u'Interface do tipo switch não encontrada a partir do front da interface %d.' % self.id)

        if ((protegida is not None) and (interface.protegida != protegida)):
            raise InterfaceProtectedError(
                None, u'Interface do switch com o campo protegida diferente de %s.' % protegida)

        return interface

    def get_switch_and_router_interface_from_host_interface(self, protegida=None):
        """A partir da ligacao_front da interface local busca uma interface ligada a um equipamento do tipo SWITCH.

        @param protegida: Indicação do campo 'protegida' da interface do switch.

        @return: Interface ligada a um equipamento do tipo SWITCH.

        @raise InterfaceError: Falha ao pesquisar a interface do switch

        @raise InterfaceNotFoundError: Interface do switch não encontrada.

        @raise InterfaceProtectedError: A interface do switch está com o campo protegida diferente do parâmetro.
        """

        interface_ids = []
        from_interface = self
        interface = self.ligacao_front
        try:
            while (interface is not None) and (interface.equipamento.tipo_equipamento_id != TipoEquipamento.TIPO_EQUIPAMENTO_SWITCH) and (interface.equipamento.tipo_equipamento_id != TipoEquipamento.TIPO_EQUIPAMENTO_ROUTER):
                interface_ids.append(interface.id)

                if (interface.ligacao_back is not None) and (from_interface.id != interface.ligacao_back_id):
                    from_interface = interface
                    interface = interface.ligacao_back
                elif (interface.ligacao_front is not None) and (from_interface.id != interface.ligacao_front_id):
                    from_interface = interface
                    interface = interface.ligacao_front
                else:
                    interface = None

                if interface is not None:
                    if interface.id in interface_ids:
                        raise InterfaceNotFoundError(
                            None, u'Interface do tipo switch não encontrada a partir do front da interface %d.' % self.id)
        except InterfaceNotFoundError, e:
            raise e
        except Exception, e:
            self.log.error(u'Falha ao pesquisar a interface do switch.')
            raise InterfaceError(
                e, u'Falha ao pesquisar a interface do switch.')

        if (interface is None):
            raise InterfaceNotFoundError(
                None, u'Interface do tipo switch não encontrada a partir do front da interface %d.' % self.id)

        if ((protegida is not None) and (interface.protegida != protegida)):
            raise InterfaceProtectedError(
                None, u'Interface do switch com o campo protegida diferente de %s.' % protegida)

        return interface

    def get_switch_interface_from_host_interface(self, protegida=None):
        """A partir da ligacao_front da interface local busca uma interface ligada a um equipamento do tipo SWITCH.
        @param protegida: Indicação do campo 'protegida' da interface do switch
        @return: Interface ligada a um equipamento do tipo SWITCH.
        @raise InterfaceError: Falha ao pesquisar a interface do switch
        @raise InterfaceNotFoundError: Interface do switch não encontrada.
        @raise InterfaceProtectedError: A interface do switch está com o campo protegida diferente do parâmetr
        """
        interface_ids = []
        from_interface = self
        interface = self.ligacao_front
        try:
            while (interface is not None) and (interface.equipamento.tipo_equipamento_id != TipoEquipamento.TIPO_EQUIPAMENTO_SWITCH):
                interface_ids.append(interface.id)

                if (interface.ligacao_back is not None) and (from_interface.id != interface.ligacao_back_id):
                    from_interface = interface
                    interface = interface.ligacao_back
                elif (interface.ligacao_front is not None) and (from_interface.id != interface.ligacao_front_id):
                    from_interface = interface
                    interface = interface.ligacao_front
                else:
                    interface = None

                if interface is not None:
                    if interface.id in interface_ids:
                        raise InterfaceNotFoundError(
                            None, u'Interface do tipo switch não encontrada a partir do front da interface %d.' % self.id)
        except InterfaceNotFoundError, e:
            raise e
        except Exception, e:
            self.log.error(u'Falha ao pesquisar a interface do switch.')
            raise InterfaceError(
                e, u'Falha ao pesquisar a interface do switch.')

        if (interface is None):
            raise InterfaceNotFoundError(
                None, u'Interface do tipo switch não encontrada a partir do front da interface %d.' % self.id)

        if ((protegida is not None) and (interface.protegida != protegida)):
            raise InterfaceProtectedError(
                None, u'Interface do switch com o campo protegida diferente de %s.' % protegida)

        return interface

    @classmethod
    def search(cls, equipment_id=None):
        try:
            interfaces = Interface.objects.all()
            if equipment_id is not None:
                interfaces = interfaces.filter(equipamento__id=equipment_id)

            return interfaces
        except Exception, e:
            cls.log.error(u'Failed to search interfaces.')
            raise InterfaceError(e, u'Failed to search interfaces.')

    def create(self, authenticated_user):
        """Add new interface

        @return: Interface instance

        @raise EquipamentoNotFoundError: Equipment doesn't exist
        @raise EquipamentoError: Failed to find equipment
        @raise FrontLinkNotFoundError: FrontEnd interface doesn't exist
        @raise BackLinkNotFoundError: BackEnd interface doesn't exist
        @raise InterfaceForEquipmentDuplicatedError: An interface with the same name on the same equipment already exists
        @raise InterfaceError: Failed to add new interface
        """

        # Valid equipment
        self.equipamento = Equipamento.get_by_pk(self.equipamento.id)

        marca = self.equipamento.modelo.marca.id if self.equipamento.tipo_equipamento.id != 2 else 0

        if marca == 0:
            regex = '^([a-zA-Z0-9-_/ ]+(:)?){1,6}$'
        elif marca == 2:
            regex = '^(Int)\s[0-9]+$'
        elif marca == 3:
            regex = '^(Fa|Gi|Te|Serial|Eth|mgmt)\s?[0-9]+(/[0-9]+(/[0-9]+)?)?$'
        elif marca == 4:
            regex = '^(interface)\s[0-9a-zA-Z]+(/[0-9a-zA-Z])+([0-9a-zA-Z-.]+)?$'
        elif marca == 5:
            regex = '^(eth)[0-9]+(/[0-9]+)?$'
        elif marca == 8:
            regex = '^[0-9]+$'
        else:
            regex = ''

        # Checks if name is valid according to the brand
        if not is_valid_regex(self.interface, regex):
            raise InvalidValueError(None, 'nome', self.interface)

        # Check front end interface existence
        if self.ligacao_front is not None:
            try:
                self.ligacao_front = Interface.get_by_pk(self.ligacao_front.id)
            except InterfaceNotFoundError, e:
                raise FrontLinkNotFoundError(
                    e, u'Frontend interface does not exist')

        # Check back end interface existence
        if self.ligacao_back is not None:
            try:
                self.ligacao_back = Interface.get_by_pk(self.ligacao_back.id)
            except InterfaceNotFoundError, e:
                raise BackLinkNotFoundError(
                    e, u'Backend interface does not exist')

        if self.vlan_nativa is None:
            self.vlan_nativa = 1
        elif int(self.vlan_nativa) < 1 or 3967 < int(self.vlan_nativa) < 4048 or int(self.vlan_nativa) == 4096:
            raise InvalidValueError(
                None, 'Vlan Nativa', 'Intervalo reservado: 3968-4047 e 4094')

        try:
            # Check if interface name already exists for this equipment
            if Interface.objects.filter(equipamento=self.equipamento, interface__iexact=self.interface).count() > 0:
                raise InterfaceForEquipmentDuplicatedError(
                    None, u'An interface with the same name on the same equipment already exists')

            return self.save()

        except InterfaceForEquipmentDuplicatedError, e:
            raise e
        except Exception, e:
            self.log.error(u'Failed to add interface for the equipment.')
            raise InterfaceError(
                e, u'Failed to add interface for the equipment.')

    @classmethod
    def update(cls, authenticated_user, id_interface, **kwargs):
        """Update interface according to arguments

        @param id_interface: Interface identifier

        @return: Interface instance

        @raise InterfaceNotFoundError: Interface doesn't exist
        @raise FrontLinkNotFoundError: FrontEnd connection Interface doesn't exist
        @raise BackLinkNotFoundError: BackEnd connection Interface doesn't exist
        @raise InterfaceForEquipmentDuplicatedError: An interface with the same name on the same equipment already exists
        @raise InterfaceError: Failed to update interface
        """

        # Get interface
        interface = Interface.get_by_pk(id_interface)
        nome = kwargs['interface']
        marca = interface.equipamento.modelo.marca.id if interface.equipamento.tipo_equipamento.id != 2 else 0

        if marca == 0:
            regex = '^([a-zA-Z0-9-_/ ]+(:)?){1,6}$'
        elif marca == 2:
            regex = '^(Int)\s[0-9]+$'
        elif marca == 3:
            regex = '^(Fa|Gi|Te|Serial|Eth|mgmt)\s?[0-9]+(/[0-9]+(/[0-9]+)?)?$'
        elif marca == 4:
            regex = '^(interface)\s[0-9]+(/[0-9]+.[0-9]+)?$'
        elif marca == 5:
            regex = '^(eth)[0-9]+(/[0-9]+)?$'
        elif marca == 8:
            regex = '^[0-9]+$'
        else:
            regex = ''

        # Checks if name is valid according to the brand
        if not is_valid_regex(nome, regex):
            raise InvalidValueError(None, 'nome', nome)
        # Valid ligacao_front_id
        try:
            id_ligacao_front = kwargs['ligacao_front_id']
            if id_ligacao_front is not None:
                if (interface.ligacao_front_id != id_ligacao_front):
                    interface.ligacao_front = Interface.get_by_pk(
                        id_ligacao_front)
            else:
                interface.ligacao_front = None
        except InterfaceNotFoundError, e:
            raise FrontLinkNotFoundError(
                e, u'Frontend interface does not exist')
        except KeyError:
            pass
        # Valid ligacao_back_id
        try:
            id_ligacao_back = kwargs['ligacao_back_id']
            if id_ligacao_back is not None:
                if (interface.ligacao_back_id != id_ligacao_back):
                    interface.ligacao_back = Interface.get_by_pk(
                        id_ligacao_back)
            else:
                interface.ligacao_back = None
        except InterfaceNotFoundError, e:
            raise BackLinkNotFoundError(
                e, u'Backend interface does not exist.')
        except KeyError:
            pass

        try:
            # Check if interface name already exists for this equipment
            try:
                nome = kwargs['interface']
                if Interface.objects.filter(equipamento=interface.equipamento, interface__iexact=nome).exclude(id=interface.id).count() > 0:
                    raise InterfaceForEquipmentDuplicatedError(
                        None, u'An interface with the same name on the same equipment already exists')
            except KeyError:
                pass
            interface.interface = nome
            interface.descricao = kwargs['descricao']
            interface.protegida = kwargs['protegida']
            try:
                interface.tipo = kwargs['tipo']
            except:
                pass
            interface.vlan_nativa = kwargs['vlan_nativa']
            if interface.vlan_nativa is not None:
                if int(interface.vlan_nativa) < 1 or int(interface.vlan_nativa) > 4096:
                    raise InvalidValueError(
                        None, 'Vlan', interface.vlan_nativa)
                if 3967 < int(interface.vlan_nativa) < 4048 or int(interface.vlan_nativa) == 4096:
                    raise InvalidValueError(
                        None, 'Vlan Nativa', 'Range reservado: 3968-4047;4094.')
            try:
                interface.channel = kwargs['channel']
            except:
                pass

            return interface.save(authenticated_user)

        except InterfaceForEquipmentDuplicatedError, e:
            raise e
        except InvalidValueError, e:
            raise e
        except Exception, e:
            cls.log.error(u'Falha ao alterar a interface')
            raise InterfaceError(e, u'Falha ao alterar a interface')

    @classmethod
    def remove(cls, authenticated_user, id_interface):
        """Removes an interface

        @param id_interface: Interface identifier

        @return: Nothing

        @raise InterfaceNotFoundError: Interface doesn't exist
        @raise InterfaceUsedByOtherInterfaceError: Interface is connected to other interface and cannot be removed
        @raise InterfaceError: Failed to remove interface
        """
        # Obtém a interface a ser removida
        interface = Interface.get_by_pk(id_interface)
        try:
            # Verifica se ela não é relacionada a alguma interface
            if Interface.objects.filter(ligacao_front=interface).count() > 0 or \
               Interface.objects.filter(ligacao_back=interface).count() > 0:
                raise InterfaceUsedByOtherInterfaceError(
                    None, u'Interface used by other interface.')

            return interface.delete()

        except InterfaceUsedByOtherInterfaceError, e:
            raise e
        except Exception, e:
            cls.log.error(u'Failed to remove interface')
            raise InterfaceError(e, u'Failed to remove interface')

    def delete(self):
        """Override Django method to remove interface.

        Before removing interface, removes all relationships between this interface and others.
        """
        for i in self.interfaces_front.all():
            i.ligacao_front = None
            i.save()

        for i in self.interfaces_back.all():
            i.ligacao_back = None
            i.save()

        super(Interface, self).delete()


class EnvironmentInterface(BaseModel):

    log = logging.getLogger('EnvironmentInterface')

    id = models.AutoField(primary_key=True, db_column='id_int_ambiente')
    ambiente = models.ForeignKey(Ambiente, db_column='id_ambiente')
    interface = models.ForeignKey(Interface, db_column='id_interface')
    vlans = models.CharField(max_length=200, blank=True, null=True)

    class Meta(BaseModel.Meta):
        db_table = u'interface_do_ambiente'
        managed = True

    def create(self, authenticated_user):
        """Add new interface_do_ambiente"""

        try:
            return self.save()
        except Exception, e:
            self.log.error(u'Failed to add interface_do_ambiente.')
            raise InterfaceError(
                e, u'Failed to add interface_do_ambiente.')

    @classmethod
    def get_by_interface(cls, id):
        try:
            return EnvironmentInterface.objects.all().filter(interface_id=id)
        except ObjectDoesNotExist, e:
            raise InterfaceNotFoundError(
                e, u'Can not find a EnvironmentInterface with interface id = %s.' % id)
        except Exception, e:
            cls.log.error(u'Falha ao pesquisar interfaces neste ambiente.')
            raise InterfaceError(
                e, u'Falha ao pesquisar interfaces neste ambiente.')
