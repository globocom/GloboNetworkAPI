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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db import transaction

from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import ConfigEnvironment
from networkapi.ambiente.models import ConfigEnvironmentInvalidError
from networkapi.ambiente.models import EnvironmentVip
from networkapi.ambiente.models import IP_VERSION
from networkapi.api_vip_request.syncs import delete_new
from networkapi.api_vip_request.syncs import old_to_new
from networkapi.config.models import Configuration
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_ENVIRONMENT
from networkapi.distributedlock import LOCK_VIP
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAmbiente
from networkapi.equipamento.models import EquipamentoAmbienteDuplicatedError
from networkapi.equipamento.models import EquipamentoAmbienteNotFoundError
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import TipoEquipamento
from networkapi.exception import InvalidValueError
from networkapi.filterequiptype.models import FilterEquipType
from networkapi.infrastructure.ipaddr import AddressValueError
from networkapi.infrastructure.ipaddr import IPv4Address
from networkapi.infrastructure.ipaddr import IPv4Network
from networkapi.infrastructure.ipaddr import IPv6Address
from networkapi.infrastructure.ipaddr import IPv6Network
from networkapi.models.BaseModel import BaseModel
from networkapi.queue_tools import queue_keys
from networkapi.queue_tools.queue_manager import QueueManager
from networkapi.util import mount_ipv4_string
from networkapi.util import mount_ipv6_string
from networkapi.util.decorators import cached_property
from networkapi.vlan.models import TipoRede
from networkapi.vlan.models import Vlan


class NetworkIPv4Error(Exception):

    """Generic exception for everything related to NetworkIPv4."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Caused by: %s, Message: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class NetworkIPv6Error(Exception):

    """Generic exception for everything related to NetworkIPv6."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Caused by: %s, Message: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class NetworkIPvXError(Exception):

    """Generic exception for everything related to both NetworkIPv4 and NetworkIPv6."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Caused by: %s, Message: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class NetworkIPRangeEnvError(NetworkIPvXError):

    """Exception for two environments with same ip range when trying to add new network."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Caused by: %s, Message: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class IpError(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com IP."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Causa: %s, Mensagem: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class NetworkIPv4NotFoundError(NetworkIPv4Error):

    """Exception to search by primary key."""

    def __init__(self, cause, message=None):
        NetworkIPv4Error.__init__(self, cause, message)


class NetworkIPv6NotFoundError(NetworkIPv6Error):

    """Exception to search by primary key."""

    def __init__(self, cause, message=None):
        NetworkIPv6Error.__init__(self, cause, message)


class NetworkIPvXNotFoundError(NetworkIPvXError):

    """Exception to search by primary key."""

    def __init__(self, cause, message=None):
        NetworkIPvXError.__init__(self, cause, message)


class NetworkIPv4AddressNotAvailableError(NetworkIPv4Error):

    """Exception to unavailable address to create a new NetworkIPv4."""

    def __init__(self, cause, message=None):
        NetworkIPv4Error.__init__(self, cause, message)


class NetworkIPv6AddressNotAvailableError(NetworkIPv6Error):

    """Exception to unavailable address to create a new NetworkIPv6."""

    def __init__(self, cause, message=None):
        NetworkIPv6Error.__init__(self, cause, message)


class NetworkIpAddressNotAvailableError(NetworkIPvXError):

    """Exception to unavailable address."""

    def __init__(self, cause, message=None):
        NetworkIPvXError.__init__(self, cause, message)


class IpNotFoundError(IpError):

    """Retorna exceção para pesquisa de IP por chave primária."""

    def __init__(self, cause, message=None):
        IpError.__init__(self, cause, message)


class IpEquipmentNotFoundError(IpError):

    """Retorna exceção para pesquisa de IP-Equipamento por chave primária/ip e equipamento."""

    def __init__(self, cause, message=None):
        IpError.__init__(self, cause, message)


class IpEquipamentoDuplicatedError(IpError):

    """Retorna exceção para pesquisa de IP-Equipamento duplicado."""

    def __init__(self, cause, message=None):
        IpError.__init__(self, cause, message)


class IpNotAvailableError(IpError):

    """Retorna exceção porque não existe um IP disponível para a VLAN."""

    def __init__(self, cause, message=None):
        IpError.__init__(self, cause, message)


class IpEquipmentAlreadyAssociation(IpError):

    """Retorna exceção caso um Ip já esteja associado a um determinado equipamento."""

    def __init__(self, cause, message=None):
        IpError.__init__(self, cause, message)


class IpNotFoundByEquipAndVipError(IpError):

    """Retorna exceção caso um Ip já esteja associado a um determinado equipamento."""

    def __init__(self, cause, message=None):
        IpError.__init__(self, cause, message)


class IpCantBeRemovedFromVip(IpError):

    """Retorna exceção caso um Ip não possa ser excluído por estar em uso por uma requisição VIP."""

    def __init__(self, cause, message=None):
        IpError.__init__(self, cause, message)


class NetworkNotInEvip(IpError):

    """Retorna exceção caso não haja uma rede Ipv4 ou Ipv6 para o Ambiente Vip."""

    def __init__(self, cause, message=None):
        IpError.__init__(self, cause, message)


class IpRangeAlreadyAssociation(IpError):

    """Returns exception for equipment already having ip with same ip range in another network."""

    def __init__(self, cause, message=None):
        IpError.__init__(self, cause, message)


class IpEquipCantDissociateFromVip(IpError):

    """Returns exception when trying to dissociate ip and equipment, but equipment is the last balancer for Vip Request"""

    def __init__(self, cause, message=None):
        IpError.__init__(self, cause, message)


class IpCantRemoveFromServerPool(IpError):

    """Returns exception when trying to dissociate ip and equipment, but equipment is the last balancer for Vip Request"""

    def __init__(self, cause, message=None):
        IpError.__init__(self, cause, message)


class NetworkIPv4(BaseModel):

    id = models.AutoField(primary_key=True)
    oct1 = models.IntegerField(db_column='rede_oct1')
    oct2 = models.IntegerField(db_column='rede_oct2')
    oct3 = models.IntegerField(db_column='rede_oct3')
    oct4 = models.IntegerField(db_column='rede_oct4')
    block = models.IntegerField(db_column='bloco')
    mask_oct1 = models.IntegerField(db_column='masc_oct1')
    mask_oct2 = models.IntegerField(db_column='masc_oct2')
    mask_oct3 = models.IntegerField(db_column='masc_oct3')
    mask_oct4 = models.IntegerField(db_column='masc_oct4')
    broadcast = models.CharField(max_length=15, blank=False)
    vlan = models.ForeignKey(Vlan, db_column='id_vlan')
    network_type = models.ForeignKey(
        TipoRede, null=True, db_column='id_tipo_rede')
    ambient_vip = models.ForeignKey(
        EnvironmentVip, null=True, db_column='id_ambientevip')
    cluster_unit = models.CharField(max_length=45, db_column='cluster_unit')
    active = models.BooleanField()

    log = logging.getLogger('NetworkIPv4')

    class Meta(BaseModel.Meta):
        db_table = u'redeipv4'
        managed = True

    def _get_formated_ip(self):
        "Returns formated ip."
        return '%s.%s.%s.%s/%s' % (self.oct1, self.oct2, self.oct3, self.oct4, self.block)

    networkv4 = property(_get_formated_ip)

    @cached_property
    def dhcprelay(self):
        from networkapi.api_network.models import DHCPRelayIPv4

        return DHCPRelayIPv4.objects.filter(networkipv4=self)

    @classmethod
    def get_by_pk(cls, id):
        """Get NetworkIPv4 by id.
            @return: NetworkIPv4.
            @raise NetworkIPv4NotFoundError: NetworkIPv4 is not registered.
            @raise NetworkIPv4Error: Failed to search for the NetworkIPv4.
            @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return NetworkIPv4.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise NetworkIPv4NotFoundError(
                e, u'There is no NetworkIPv4 with pk = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the NetworkIPv4.')
            raise NetworkIPv4Error(e, u'Failure to search the NetworkIPv4.')

    def activate(self, authenticated_user):

        from networkapi.api_network.serializers import NetworkIPv4Serializer

        try:
            self.active = 1
            # Send to Queue
            queue_manager = QueueManager()
            serializer = NetworkIPv4Serializer(self)
            data_to_queue = serializer.data
            data_to_queue.update({'description': queue_keys.NETWORKv4_ACTIVATE})
            queue_manager.append({'action': queue_keys.NETWORKv4_ACTIVATE, 'kind': queue_keys.NETWORKv4_KEY, 'data': data_to_queue})
            queue_manager.send()
            self.save()

        except Exception, e:
            self.log.error(u'Error activating NetworkIPv4.')
            raise NetworkIPv4Error(e, u'Error activating NetworkIPv4.')

    def deactivate(self, authenticated_user, commit=False):
        '''
            Update status column  to 'active = 0'
            @param authenticated_user: User authenticate
            @raise NetworkIPv4Error: Error disabling a NetworkIPv4.
        '''

        from networkapi.api_network.serializers import NetworkIPv4Serializer

        try:

            self.active = 0
            # Send to Queue
            queue_manager = QueueManager()
            serializer = NetworkIPv4Serializer(self)
            data_to_queue = serializer.data
            data_to_queue.update({'description': queue_keys.NETWORKv4_DEACTIVATE})
            queue_manager.append({'action': queue_keys.NETWORKv4_DEACTIVATE, 'kind': queue_keys.NETWORKv4_KEY, 'data': data_to_queue})
            queue_manager.send()
            self.save(authenticated_user, commit=commit)

        except Exception, e:
            self.log.error(u'Error disabling NetworkIPv4.')
            raise NetworkIPv4Error(e, u'Error disabling NetworkIPv4.')

    def edit_network_ipv4(self, authenticated_user, id_net_type, id_env_vip, cluster_unit):
        try:
            self.network_type = id_net_type
            self.ambient_vip = id_env_vip
            self.cluster_unit = cluster_unit
            self.save()
        except Exception, e:
            self.log.error(u'Error on update NetworkIPv4.')
            raise NetworkIPv4Error(e, u'Error on update NetworkIPv4.')

    def add_network_ipv4(self, user, id_vlan, network_type, evip, prefix=None):
        """Allocate and Insert new NetworkIPv4 in database
            @return: Vlan map
            @raise VlanNotFoundError: Vlan is not registered.
            @raise VlanError: Failed to search for the Vlan
            @raise ConfigEnvironmentInvalidError: Invalid Environment Configuration or not registered
            @raise NetworkIPv4Error: Error persisting a NetworkIPv4.
            @raise NetworkIPv4AddressNotAvailableError: Unavailable address to create a NetworkIPv4.
            @raise Invalid: Unavailable address to create a NetworkIPv4.
            @raise InvalidValueError: Network type does not exist.
        """

        self.vlan = Vlan().get_by_pk(id_vlan)

        network_found = None
        stop = False
        internal_network_type = None
        type_ipv4 = IP_VERSION.IPv4[0]

        try:

            # Find all configs type v4 in environment
            configs = ConfigEnvironment.get_by_environment(
                self.vlan.ambiente.id).filter(ip_config__type=IP_VERSION.IPv4[0])

            # If not found, an exception is thrown
            if len(configs) == 0:
                raise ConfigEnvironmentInvalidError(
                    None, u'Invalid Configuration')

            # Needs to lock IPv4 listing when there are any allocation in progress
            # If not, it will allocate two networks with same range
            with distributedlock(LOCK_ENVIRONMENT % self.vlan.ambiente.id):
                # Find all networks ralated to environment
                nets = NetworkIPv4.objects.filter(vlan__ambiente__id=self.vlan.ambiente.id)

                # Cast to API class
                networksv4 = set([(IPv4Network(
                    '%d.%d.%d.%d/%d' % (net_ip.oct1, net_ip.oct2, net_ip.oct3, net_ip.oct4, net_ip.block))) for net_ip in nets])

                # For each configuration founded in environment
                for config in configs:

                    # If already get a network stop this
                    if stop:
                        break

                    # Need to be IPv4
                    if config.ip_config.type == IP_VERSION.IPv4[0]:

                        net4 = IPv4Network(config.ip_config.subnet)

                        if prefix is not None:
                            new_prefix = int(prefix)
                        else:
                            new_prefix = int(config.ip_config.new_prefix)

                        self.log.info(u"Prefix that will be used: %s" % new_prefix)
                        # For each subnet generated with configs
                        for subnet in net4.iter_subnets(new_prefix=new_prefix):

                            net_found = True
                            for network in networksv4:
                                if subnet in network:
                                    net_found = False

                            # Checks if the network generated is UNUSED
                            if net_found:

                                # Checks if it is subnet/supernet of any existing network
                                in_range = network_in_range(self.vlan, subnet, type_ipv4)
                                if not in_range:
                                    continue

                                # If not this will be USED
                                network_found = subnet

                                if network_type:
                                    internal_network_type = network_type
                                elif config.ip_config.network_type is not None:
                                    internal_network_type = config.ip_config.network_type
                                else:
                                    self.log.error(
                                        u'Parameter tipo_rede is invalid. Value: %s', network_type)
                                    raise InvalidValueError(
                                        None, 'network_type', network_type)

                                # Stop generation logic
                                stop = True
                                break

                    # If not IPv4
                    else:
                        # Throw an exception
                        raise ConfigEnvironmentInvalidError(
                            None, u'Invalid Configuration')

                # Checks if found any available network
                if network_found is None:
                    # If not found, an exception is thrown
                    raise NetworkIPv4AddressNotAvailableError(
                        None, u'Unavailable address to create a NetworkIPv4.')

                # Set octs by network generated
                self.oct1, self.oct2, self.oct3, self.oct4 = str(network_found.network).split('.')
                # Set block by network generated
                self.block = network_found.prefixlen
                # Set mask by network generated
                self.mask_oct1, self.mask_oct2, self.mask_oct3, self.mask_oct4 = str(network_found.netmask).split('.')
                # Set broadcast by network generated
                self.broadcast = network_found.broadcast

                try:
                    self.network_type = internal_network_type
                    self.ambient_vip = evip
                    self.save()
                    transaction.commit()
                except Exception, e:
                    self.log.error(u'Error persisting a NetworkIPv4.')
                    raise NetworkIPv4Error(e, u'Error persisting a NetworkIPv4.')

        except (ValueError, TypeError, AddressValueError), e:
            raise ConfigEnvironmentInvalidError(e, u'Invalid Configuration')

        # Return vlan map
        vlan_map = dict()
        vlan_map['id'] = self.vlan.id
        vlan_map['nome'] = self.vlan.nome
        vlan_map['num_vlan'] = self.vlan.num_vlan
        vlan_map['id_tipo_rede'] = self.network_type.id
        vlan_map['id_ambiente'] = self.vlan.ambiente.id
        vlan_map['rede_oct1'] = self.oct1
        vlan_map['rede_oct2'] = self.oct2
        vlan_map['rede_oct3'] = self.oct3
        vlan_map['rede_oct4'] = self.oct4
        vlan_map['bloco'] = self.block
        vlan_map['mascara_oct1'] = self.mask_oct1
        vlan_map['mascara_oct2'] = self.mask_oct2
        vlan_map['mascara_oct3'] = self.mask_oct3
        vlan_map['mascara_oct4'] = self.mask_oct4
        vlan_map['broadcast'] = self.broadcast
        vlan_map['descricao'] = self.vlan.descricao
        vlan_map['acl_file_name'] = self.vlan.acl_file_name
        vlan_map['acl_valida'] = self.vlan.acl_valida
        vlan_map['acl_file_name_v6'] = self.vlan.acl_file_name_v6
        vlan_map['acl_valida_v6'] = self.vlan.acl_valida_v6
        vlan_map['ativada'] = self.vlan.ativada
        vlan_map['id_network'] = self.id

        map = dict()
        map['vlan'] = vlan_map

        return map

    def delete(self):

        try:

            for ip in self.ip_set.all():
                ip.delete()

            super(NetworkIPv4, self).delete()

        except IpCantBeRemovedFromVip, e:
            # Network id and ReqVip id
            net_name = str(self.oct1) + '.' + str(self.oct2) + '.' + \
                str(self.oct3) + '.' + str(self.oct4) + '/' + str(self.block)
            cause = {'Net': net_name, 'ReqVip': e.cause}
            raise IpCantBeRemovedFromVip(
                cause, "Esta Rede possui um Vip apontando para ela, e não pode ser excluída")


class Ip(BaseModel):

    id = models.AutoField(primary_key=True, db_column='id_ip')
    oct4 = models.IntegerField()
    oct3 = models.IntegerField()
    oct2 = models.IntegerField()
    oct1 = models.IntegerField()
    descricao = models.CharField(max_length=100, blank=True)
    networkipv4 = models.ForeignKey(NetworkIPv4, db_column='id_redeipv4')

    log = logging.getLogger('Ip')

    class Meta(BaseModel.Meta):
        db_table = u'ips'
        managed = True
        unique_together = ('oct1', 'oct2', 'oct3', 'oct4', 'networkipv4')

    def _get_formated_ip(self):
        "Returns formated ip."
        return '%s.%s.%s.%s' % (self.oct1, self.oct2, self.oct3, self.oct4)

    ip_formated = property(_get_formated_ip)

    @classmethod
    def list_by_network(cls, id_network):
        """Get IP LIST by id_network.
            @return: IP List.
            @raise IpNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
            @raise OperationalError: Lock wait timeout exceeded.
        """

        try:
            return Ip.objects.filter(networkipv4=id_network)
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(
                e, u'There is no IP with network_id = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the IP.')
            raise IpError(e, u'Failure to search the IP')

    @classmethod
    def list_by_environment_and_equipment(cls, id_ambiente, id_equipment):
        """Get IP LIST by id_network.
            @return: IP List.
            @raise IpNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
            @raise OperationalError: Lock wait timeout exceeded.
        """

        try:
            return Ip.objects.select_related().filter(networkipv4__vlan__ambiente__id=id_ambiente, ipequipamento__equipamento__id=id_equipment)
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(
                e, u'There is no IP with network_id = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the IP.')
            raise IpError(e, u'Failure to search the IP')

    @classmethod
    def get_by_pk(cls, id):
        """Get IP by id.
            @return:  IP.
            @raise IpNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
            @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return Ip.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(e, u'There is no IP with pk = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the IP.')
            raise IpError(e, u'Failure to search the IP')

    def delete_ip4(self, user, id_ip):
        try:

            ip = self.get_by_pk(id_ip)
            ip.delete()

        except IpNotFoundError, e:
            raise IpNotFoundError(None, e)
        except Exception, e:
            self.log.error(u'Failure to delete the IP.')
            raise IpError(e, u'Failure to delete the IP')

    @classmethod
    def get_available_ip(cls, id_network):
        """Get a available Ipv4 for networkIPv4
            @return: Available Ipv4
            @raise IpNotAvailableError: NetworkIPv4 does not has available Ipv4
        """

        networkipv4 = NetworkIPv4().get_by_pk(id_network)

        # Cast to API
        net4 = IPv4Network('%d.%d.%d.%d/%d' % (networkipv4.oct1, networkipv4.oct2,
                                               networkipv4.oct3, networkipv4.oct4, networkipv4.block))

        # Find all ips ralated to network
        ips = Ip.objects.filter(networkipv4__id=networkipv4.id)

        # Cast all to API class
        ipsv4 = set(
            [(IPv4Address('%d.%d.%d.%d' % (ip.oct1, ip.oct2, ip.oct3, ip.oct4))) for ip in ips])

        # Get configuration
        conf = Configuration.get()

        selected_ip = None

        # For each ip generated
        i = 0
        for ip in net4.iterhosts():

            # Do not use some range of IPs (config)
            i = i + 1
            if i >= conf.IPv4_MIN and i < (net4.numhosts - conf.IPv4_MAX):

                # If IP generated was not used
                if ip not in ipsv4:

                    # Use it
                    selected_ip = ip

                    # Stop generation
                    return selected_ip

        if selected_ip is None:
            raise IpNotAvailableError(
                None, u'No IP available to NETWORK %s.' % networkipv4.id)

    @classmethod
    def get_first_available_ip(cls, id_network, topdown=False):
        """Get a first available Ipv4 for networkIPv4
            @return: Available Ipv4
            @raise IpNotAvailableError: NetworkIPv4 does not has available Ipv4
        """

        networkipv4 = NetworkIPv4().get_by_pk(id_network)

        # Cast to API
        net4 = IPv4Network('%d.%d.%d.%d/%d' % (networkipv4.oct1, networkipv4.oct2,
                                               networkipv4.oct3, networkipv4.oct4, networkipv4.block))

        # Find all ips ralated to network
        ips = Ip.objects.filter(networkipv4__id=networkipv4.id)

        # Cast all to API class
        ipsv4 = set(
            [(IPv4Address('%d.%d.%d.%d' % (ip.oct1, ip.oct2, ip.oct3, ip.oct4))) for ip in ips])

        selected_ip = None

        if topdown:
            method = net4.iterhostsTopDown
        else:
            method = net4.iterhosts

        # For each ip generated
        for ip in method():

            # If IP generated was not used
            if ip not in ipsv4:

                # Use it
                selected_ip = ip

                # Stop generation
                return selected_ip

        if selected_ip is None:
            raise IpNotAvailableError(
                None, u'No IP available to NETWORK %s.' % networkipv4.id)

    @classmethod
    def get_last_available_ip(cls, id_network):
        """Get an available Ipv4 for networkIPv4 from end of range
            @return: Available Ipv4
            @raise IpNotAvailableError: NetworkIPv4 does not has available Ipv4
        """

        networkipv4 = NetworkIPv4().get_by_pk(id_network)

        # Cast to API
        net4 = IPv4Network('%d.%d.%d.%d/%d' % (networkipv4.oct1, networkipv4.oct2,
                                               networkipv4.oct3, networkipv4.oct4, networkipv4.block))

        # Find all ips ralated to network
        ips = Ip.objects.filter(networkipv4__id=networkipv4.id)

        # Cast all to API class
        ipsv4 = set(
            [(IPv4Address('%d.%d.%d.%d' % (ip.oct1, ip.oct2, ip.oct3, ip.oct4))) for ip in ips])

        selected_ip = None

        # For each ip generated
        for ip in net4.iterhosts():

            # If IP generated was not used
            if ip not in ipsv4:

                # Use it
                selected_ip = ip

                # Stop generation
                return selected_ip

        if selected_ip is None:
            raise IpNotAvailableError(
                None, u'No IP available to NETWORK %s.' % networkipv4.id)

    def edit_ipv4(self, user):
        try:

            # Cast to API
            net4 = IPv4Network('%d.%d.%d.%d/%d' % (self.networkipv4.oct1, self.networkipv4.oct2,
                                                   self.networkipv4.oct3, self.networkipv4.oct4, self.networkipv4.block))

            # Find all ips ralated to network
            ips = Ip.objects.filter(networkipv4__id=self.networkipv4.id)

            ip4_object = IPv4Address(
                '%s.%s.%s.%s' % (self.oct1, self.oct2, self.oct3, self.oct4))

            # Cast all to API class
            ipsv4 = set(
                [IPv4Address('%d.%d.%d.%d' % (ip.oct1, ip.oct2, ip.oct3, ip.oct4)) for ip in ips])

            flag = True

            if ip4_object not in ipsv4:

                flag = False

                if ip4_object in net4:

                    # Get configuration
                    # conf = Configuration.get()

                    first_ip_network = int(net4.network)
                    bcast_ip_network = int(net4.broadcast)

                    ipv4_network = int(ip4_object)

                    if ipv4_network >= (first_ip_network) and ipv4_network < (bcast_ip_network):
                        flag = True

            else:
                ip4_aux = self.get_by_octs_and_net(
                    self.oct1, self.oct2, self.oct3, self.oct4, self.networkipv4.id)
                if self.id != ip4_aux.id:
                    raise IpNotAvailableError(None, u'Ip %s.%s.%s.%s already on use by network %s.' % (
                        self.oct1, self.oct2, self.oct3, self.oct4, self.networkipv4.id))

            if flag:
                self.save()
            else:
                raise IpNotAvailableError(None, u'Ip %s.%s.%s.%s not available for network %s.' % (
                    self.oct1, self.oct2, self.oct3, self.oct4, self.networkipv4.id))

        except IpEquipmentAlreadyAssociation, e:
            self.log.error(e)
            raise IpEquipmentAlreadyAssociation(None, e)
        except AddressValueError:
            raise InvalidValueError(
                None, 'ip', u'%s.%s.%s.%s' % (self.oct1, self.oct2, self.oct3, self.oct4))
        except IpNotAvailableError, e:
            raise IpNotAvailableError(None, u'Ip %s.%s.%s.%s not available for network %s.' % (
                self.oct1, self.oct2, self.oct3, self.oct4, self.networkipv4.id))
        except IpError, e:
            self.log.error(
                u'Error adding new IP or relationship ip-equipment.')
            raise IpError(
                e, u'Error adding new IP or relationship ip-equipment.')

    def save_ipv4(self, equipment_id, user, net):

        try:

            already_ip = False

            # Cast to API
            net4 = IPv4Network(
                '%d.%d.%d.%d/%d' % (net.oct1, net.oct2, net.oct3, net.oct4, net.block))

            # Find all ips ralated to network
            ips = Ip.objects.filter(networkipv4__id=net.id)

            ip4_object = IPv4Address(
                '%s.%s.%s.%s' % (self.oct1, self.oct2, self.oct3, self.oct4))

            # Cast all to API class
            ipsv4 = set(
                [IPv4Address('%d.%d.%d.%d' % (ip.oct1, ip.oct2, ip.oct3, ip.oct4)) for ip in ips])

            flag = False

            if ip4_object not in ipsv4:

                if ip4_object in net4:

                    # Get configuration
                    # conf = Configuration.get()

                    first_ip_network = int(net4.network)
                    bcast_ip_network = int(net4.broadcast)

                    ipv4_network = int(ip4_object)

                    if ipv4_network >= (first_ip_network) and ipv4_network < (bcast_ip_network):
                        flag = True

            else:

                ip_aux = self.get_by_octs_and_net(
                    self.oct1, self.oct2, self.oct3, self.oct4, net.id)
                try:
                    IpEquipamento.get_by_ip(ip_aux.id)
                    raise IpEquipmentAlreadyAssociation(None, u'Ip %s.%s.%s.%s already has association with an Equipament. Try using the association screen for this Ip.' % (
                        self.oct1, self.oct2, self.oct3, self.oct4))
                except IpEquipmentNotFoundError, e:
                    flag = True
                    already_ip = True

            if flag:
                equipment = Equipamento().get_by_pk(equipment_id)
                ip_equipment = IpEquipamento()
                if not already_ip:
                    self.networkipv4_id = net.id
                    self.save()
                    ip_equipment.ip = self

                else:
                    ip_equipment.ip = ip_aux
                    if self.descricao is not None and len(self.descricao) > 0:
                        ip_aux.descricao = self.descricao
                        ip_aux.save()

                ip_equipment.equipamento = equipment

                # # Filter case 2 - Adding new IpEquip for a equip that already have ip in other network with the same range ##

                # Get all IpEquipamento related to this equipment
                ip_equips = IpEquipamento.objects.filter(
                    equipamento=equipment_id)

                for ip_test in [ip_equip.ip for ip_equip in ip_equips]:
                    if ip_test.networkipv4.oct1 == self.networkipv4.oct1 and \
                            ip_test.networkipv4.oct2 == self.networkipv4.oct2 and \
                            ip_test.networkipv4.oct3 == self.networkipv4.oct3 and \
                            ip_test.networkipv4.oct4 == self.networkipv4.oct4 and \
                            ip_test.networkipv4.block == self.networkipv4.block and \
                            ip_test.networkipv4 != self.networkipv4:

                        # Filter testing
                        if ip_test.networkipv4.vlan.ambiente.filter is None or self.networkipv4.vlan.ambiente.filter is None:
                            raise IpRangeAlreadyAssociation(
                                None, u'Equipment is already associated with another ip with the same ip range.')
                        else:
                            # Test both environment's filters
                            tp_equip_list_one = list()
                            for fet in FilterEquipType.objects.filter(filter=self.networkipv4.vlan.ambiente.filter.id):
                                tp_equip_list_one.append(fet.equiptype)

                            tp_equip_list_two = list()
                            for fet in FilterEquipType.objects.filter(filter=ip_test.networkipv4.vlan.ambiente.filter.id):
                                tp_equip_list_two.append(fet.equiptype)

                            if equipment.tipo_equipamento not in tp_equip_list_one or equipment.tipo_equipamento not in tp_equip_list_two:
                                raise IpRangeAlreadyAssociation(
                                    None, u'Equipment is already associated with another ip with the same ip range.')

                # # Filter case 2 - end ##

                ip_equipment.save()

                # Makes Environment Equipment association
                try:
                    equipment_environment = EquipamentoAmbiente()
                    equipment_environment.equipamento = equipment
                    equipment_environment.ambiente = net.vlan.ambiente
                    equipment_environment.create(user)
                except EquipamentoAmbienteDuplicatedError, e:
                    # If already exists, OK !
                    pass

            else:
                raise IpNotAvailableError(None, u'Ip %s.%s.%s.%s not available for network %s.' % (
                    self.oct1, self.oct2, self.oct3, self.oct4, net.id))

        except IpRangeAlreadyAssociation, e:
            raise IpRangeAlreadyAssociation(None, e.message)
        except IpEquipmentAlreadyAssociation, e:
            raise IpEquipmentAlreadyAssociation(None, e.message)
        except AddressValueError:
            raise InvalidValueError(
                None, 'ip', u'%s.%s.%s.%s' % (self.oct1, self.oct2, self.oct3, self.oct4))
        except IpNotAvailableError, e:
            raise IpNotAvailableError(None, u'Ip %s.%s.%s.%s not available for network %s.' % (
                self.oct1, self.oct2, self.oct3, self.oct4, net.id))
        except (IpError, EquipamentoError), e:
            self.log.error(
                u'Error adding new IP or relationship ip-equipment.')
            raise IpError(
                e, u'Error adding new IP or relationship ip-equipment.')

    def create(self, authenticated_user, equipment_id, id, new):
        """Persist an IPv4 and associate it to an equipment.
            If equipment was not related with VLAN environment, this makes the relationship
            @return: Nothing
            @raise NetworkIPv6NotFoundError: NetworkIPv6 does not exist.
            @raise NetworkIPv6Error: Error finding NetworkIPv6.
            @raise EquipamentoNotFoundError: Equipment does not exist.
            @raise EquipamentoError: Error finding Equipment.
            @raise IpNotAvailableError: No IP available to VLAN.
            @raise IpError: Error persisting in database.
        """

        if new is False:
            # Search vlan by id
            vlan = Vlan().get_by_pk(id)

            # Get first networkipv4 related to vlan
            try:
                self.networkipv4 = vlan.networkipv4_set.order_by('id')[0]
            except IndexError, e:
                self.log.error(
                    u'Error finding the first networkipv4 from vlan.')
                raise NetworkIPv4NotFoundError(
                    e, u'Error finding the first networkipv4 from vlan.')
        else:
            self.networkipv4 = NetworkIPv4().get_by_pk(id)

        # Cast to API
        net4 = IPv4Network('%d.%d.%d.%d/%d' % (self.networkipv4.oct1, self.networkipv4.oct2,
                                               self.networkipv4.oct3, self.networkipv4.oct4, self.networkipv4.block))

        # Find all ips ralated to network
        ips = Ip.objects.filter(networkipv4__id=self.networkipv4.id)

        # Cast all to API class
        ipsv4 = set(
            [(IPv4Address('%d.%d.%d.%d' % (ip.oct1, ip.oct2, ip.oct3, ip.oct4))) for ip in ips])

        # Get configuration
        conf = Configuration.get()

        selected_ip = None

        # For each ip generated
        i = 0
        for ip in net4.iterhosts():

            # Do not use some range of IPs (config)
            i = i + 1
            if i >= conf.IPv4_MIN and i < (net4.numhosts - conf.IPv4_MAX):

                # If IP generated was not used
                if ip not in ipsv4:

                    # Use it
                    selected_ip = ip

                    # Stop generation
                    break

        if selected_ip is None:
            raise IpNotAvailableError(
                None, u'No IP available to VLAN %s.' % self.networkipv4.vlan.num_vlan)

        self.oct1, self.oct2, self.oct3, self.oct4 = str(
            selected_ip).split('.')

        equipment = Equipamento().get_by_pk(equipment_id)

        try:
            self.save()

            ip_equipment = IpEquipamento()
            ip_equipment.ip = self
            ip_equipment.equipamento = equipment

            ip_equipment.save(authenticated_user)

            try:
                equipment_environment = EquipamentoAmbiente().get_by_equipment_environment(equipment_id,
                                                                                           self.networkipv4.vlan.ambiente_id)
            except EquipamentoAmbienteNotFoundError:
                equipment_environment = EquipamentoAmbiente()
                equipment_environment.equipamento = equipment
                equipment_environment.ambiente = self.networkipv4.vlan.ambiente
                equipment_environment.save(authenticated_user)

        except Exception, e:
            self.log.error(
                u'Error adding new IP or relationship ip-equipment.')
            raise IpError(
                e, u'Error adding new IP or relationship ip-equipment.')

    def get_by_octs_equipment(self, oct1, oct2, oct3, oct4, equip_id):
        """Get IP by octs and equip_id.
            @return: IP.
            @raise IpNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
        """
        try:
            return Ip.objects.get(oct1=oct1, oct2=oct2, oct3=oct3, oct4=oct4, ipequipamento__equipamento__id=equip_id)
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(e, u'There is no IP %s.%s.%s.%s of the equipament %s.' % (
                oct1, oct2, oct3, oct4, equip_id))
        except Exception, e:
            self.log.error(u'Failure to search the IP.')
            raise IpError(e, u'Failure to search the IP.')

    @classmethod
    def get_by_octs_and_net(cls, oct1, oct2, oct3, oct4, id_network):
        """Get IP by octs and net.
            @return: IP.
            @raise IpNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
        """
        try:
            return Ip.objects.get(oct1=oct1, oct2=oct2, oct3=oct3, oct4=oct4, networkipv4=id_network)
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(
                e, u'There is no IP = %s.%s.%s.%s.' % (oct1, oct2, oct3, oct4))
        except Exception, e:
            cls.log.error(u'Failure to search the IP.')
            raise IpError(e, u'Failure to search the IP.')

    @classmethod
    def get_by_octs_and_environment_vip(cls, oct1, oct2, oct3, oct4, id_evip, valid=True):
        """Get IP by octs and environment vip.
            @return: IP.
            @raise IpNotFoundByEquipAndVipError: IP is not related with equipament.
            @raise IpNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
        """
        try:
            ips = Ip.objects.filter(oct1=oct1, oct2=oct2, oct3=oct3, oct4=oct4)
            if ips.count() == 0:
                raise IpNotFoundError(None)

            if valid is True:
                return Ip.objects.get(oct1=oct1, oct2=oct2, oct3=oct3, oct4=oct4,
                                      networkipv4__ambient_vip__id=id_evip)
            else:
                for ip in ips:
                    if ip.networkipv4.ambient_vip:
                        if ip.networkipv4.ambient_vip.id == id_evip:
                            return ip
                    else:
                        environments = Ambiente.objects.filter(vlan__networkipv4__ambient_vip__id=id_evip)
                        for env in environments:
                            if ip.networkipv4.vlan.ambiente.divisao_dc.id == env.divisao_dc.id \
                                    and ip.networkipv4.vlan.ambiente.ambiente_logico.id == env.ambiente_logico.id:
                                return ip
                raise ObjectDoesNotExist()
        except ObjectDoesNotExist, e:
            evip = EnvironmentVip.get_by_pk(id_evip)
            msg = u'Ipv4 não está relacionado ao Ambiente Vip: %s.' % evip.show_environment_vip()
            cls.log.error(msg)
            raise IpNotFoundByEquipAndVipError(e, msg)
        except IpNotFoundError, e:
            msg = u'Ipv4 "%s.%s.%s.%s" não exite.' % (oct1, oct2, oct3, oct4)
            cls.log.error(msg)
            raise IpNotFoundError(e, msg)
        except Exception, e:
            cls.log.error(u'Failure to search the IP.')
            raise IpError(e, u'Failure to search the IP.')

    @classmethod
    def get_by_octs_and_environment(cls, oct1, oct2, oct3, oct4, id_environment):
        """Get IP by octs and environment.
            @return: IP.
            @raise IpNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
        """
        try:
            return Ip.objects.get(oct1=oct1, oct2=oct2, oct3=oct3, oct4=oct4, networkipv4__vlan__ambiente__id=id_environment)
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(e, u'There is no IP %s.%s.%s.%s of the environment %s.' % (
                oct1, oct2, oct3, oct4, id_environment))
        except Exception, e:
            cls.log.error(u'Failure to search the IP.')
            raise IpError(e, u'Failure to search the IP.')

    @classmethod
    def valid_real_server(cls, oct1, oct2, oct3, oct4, id_evip, real_name):
        '''Validation
        @param name_equip:
        @param ip_real:
        @param id_evip:
        @return: On success: vip_map, vip, None
                 In case of error: vip_map, vip, code  (code error message).
        @todo:  arrruma tudo
        '''
        try:
            return Ip.objects.get(oct1=oct1, oct2=oct2, oct3=oct3, oct4=oct4, networkipv4__ambient_vip__id=id_evip, ipequipamento__equipamento__nome=real_name)
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(e, u'')
        except Exception, e:
            cls.log.error(u'')
            raise IpError(e, u'')

    @classmethod
    def get_by_octs(cls, oct1, oct2, oct3, oct4):
        """Get IP by octs.
            @return: IP.
            @raise IpNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
        """
        try:
            ips = Ip.objects.filter(oct1=oct1, oct2=oct2, oct3=oct3, oct4=oct4)

            if len(ips) == 0:
                raise ObjectDoesNotExist()

            return ips
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(
                e, u'There is no IP = %s.%s.%s.%s.' % (oct1, oct2, oct3, oct4))
        except Exception, e:
            cls.log.error(u'Failure to search the IP.')
            raise IpError(e, u'Failure to search the IP.')

    def delete(self):
        '''Sobrescreve o método do Django para remover um IP.
        Antes de remover o IP remove todas as suas requisições de VIP e os relacionamentos com equipamentos.
        '''
        try:
            for r in self.requisicaovips_set.all():
                r_alter = False
                # Assures VIP request is not being changed - issue #48
                with distributedlock(LOCK_VIP % r.id):
                    # updates query after lock for object
                    r = self.requisicaovips_set.get(id=r.id)
                    id_vip = r.id
                    if r.vip_criado:
                        raise IpCantBeRemovedFromVip(
                            r.id, "Ipv4 não pode ser removido, porque está em uso por Requisição Vip %s" % (r.id))
                    else:
                        if r.ipv6 is not None:
                            r.ip = None
                            r.validado = 0
                            r.save(authenticated_user)
                            r_alter = True

                            # SYNC_VIP
                            old_to_new(r)
                    if not r_alter:
                        r.delete()

                        # SYNC_VIP
                        delete_new(id_vip)

            for ie in self.ipequipamento_set.all():
                # Codigo removido, pois não devemos remover o ambiente do equipamento mesmo que não tenha IP
                # para o ambiente solicidado pelo Henrique

                # ambienteequip = EquipamentoAmbiente()
                # ambienteequip = ambienteequip.get_by_equipment_environment(
                #     ie.equipamento.id, self.networkipv4.vlan.ambiente_id)
                #
                # ips = Ip.list_by_environment_and_equipment(
                #     ambienteequip.ambiente_id, ie.equipamento.id)
                # ips6 = Ipv6.list_by_environment_and_equipment(
                #     ambienteequip.ambiente_id, ie.equipamento.id)
                #
                # if len(ips) <= 1 and len(ips6) <= 0:
                #
                #     ambienteequip.delete()

                ie.delete()

            from networkapi.api_pools.serializers import Ipv4Serializer
            serializer = Ipv4Serializer(self)
            data_to_queue = serializer.data

            super(Ip, self).delete()

            # Send to Queue
            queue_manager = QueueManager()
            data_to_queue.update({'description': queue_keys.IPv4_REMOVE})
            queue_manager.append(
                {'action': queue_keys.IPv4_REMOVE, 'kind': queue_keys.IPv4_KEY, 'data': data_to_queue})
            queue_manager.send()

        except EquipamentoAmbienteNotFoundError, e:
            raise EquipamentoAmbienteNotFoundError(None, e.message)
        except IpCantBeRemovedFromVip, e:
            raise IpCantBeRemovedFromVip(e.cause, e.message)
        except IpEquipmentNotFoundError, e:
            raise IpEquipmentNotFoundError(None, e.message)


class IpEquipamento(BaseModel):
    id = models.AutoField(
        primary_key=True, db_column='id_ips_dos_equipamentos')
    ip = models.ForeignKey(Ip, db_column='id_ip')
    equipamento = models.ForeignKey(Equipamento, db_column='id_equip')

    log = logging.getLogger('IpEquipamento')

    class Meta(BaseModel.Meta):
        db_table = u'ips_dos_equipamentos'
        managed = True
        unique_together = ('ip', 'equipamento')

    @classmethod
    def get_by_ip(cls, ip_id):
        """Get IP by id_ip
            @return: IP.
            @raise IpEquipmentNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
        """
        try:
            return IpEquipamento.objects.filter(ip__id=ip_id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise IpEquipmentNotFoundError(
                e, u'There is no IP-Equipament by IP = %s.')
        except Exception, e:
            cls.log.error(u'Failure to search the Ip-Equipament.')
            raise IpError(e, u'Failure to search the Ip-Equipament.')

    @classmethod
    def list_by_ip(cls, ip_id):
        """Get IP by id_ip
            @return: IP.
            @raise IpEquipmentNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
        """
        try:
            return IpEquipamento.objects.filter(ip__id=ip_id)
        except ObjectDoesNotExist, e:
            raise IpEquipmentNotFoundError(
                e, u'There is no IP-Equipament by IP = %s.')
        except Exception, e:
            cls.log.error(u'Failure to search the Ip-Equipament.')
            raise IpError(e, u'Failure to search the Ip-Equipament.')

    @classmethod
    def list_by_equip(cls, equip_id):
        """Get IP by id_ip
            @return: IPEquipment.
            @raise IpEquipmentNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
        """
        try:
            return IpEquipamento.objects.filter(equipamento__id=equip_id)
        except ObjectDoesNotExist, e:
            raise IpEquipmentNotFoundError(
                e, u'There is no IP-Equipament by Equip = %s.')
        except Exception, e:
            cls.log.error(u'Failure to search the Ip-Equipament.')
            raise IpError(e, u'Failure to search the Ip-Equipament.')

    @classmethod
    def get_by_ip_equipment(cls, ip_id, equip_id):
        """Get IP by id and equip_id.
            @return: IP.
            @raise IpEquipmentNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
        """
        try:
            return IpEquipamento.objects.get(ip__id=ip_id, equipamento__id=equip_id)
        except ObjectDoesNotExist, e:
            raise IpEquipmentNotFoundError(
                e, u'There is no IP-Equipament by IP = %s. and Equipament = %s.' % (ip_id, equip_id))
        except Exception, e:
            cls.log.error(u'Failure to search the Ip-Equipament.')
            raise IpError(e, u'Failure to search the Ip-Equipament.')

    def __validate_ip(self):
        try:
            IpEquipamento.objects.get(ip=self.ip, equipamento=self.equipamento)
            raise IpEquipamentoDuplicatedError(
                None, u'IP já cadastrado para o equipamento.')
        except ObjectDoesNotExist:
            pass

    def create(self, authenticated_user, ip_id, equipment_id):
        '''Insere um relacionamento entre IP e Equipamento.
        @return: Nothing.
        @raise IpError: Falha ao inserir.
        @raise EquipamentoNotFoundError: Equipamento não cadastrado.
        @raise IpNotFoundError: Ip não cadastrado.
        @raise IpEquipamentoDuplicatedError: IP já cadastrado para o equipamento.
        @raise EquipamentoError: Falha ao pesquisar o equipamento.
        '''
        self.equipamento = Equipamento().get_by_pk(equipment_id)
        self.ip = Ip().get_by_pk(ip_id)

        # Valida o ip
        self.__validate_ip()

        try:
            if self.equipamento not in [ea.equipamento for ea in self.ip.networkipv4.vlan.ambiente.equipamentoambiente_set.all().select_related('equipamento')]:
                ea = EquipamentoAmbiente(
                    ambiente=self.ip.networkipv4.vlan.ambiente, equipamento=self.equipamento)
                ea.save(authenticated_user)

            self.save()
        except Exception, e:
            self.log.error(u'Falha ao inserir um ip_equipamento.')
            raise IpError(e, u'Falha ao inserir um ip_equipamento.')

    def delete(self):
        '''Override Django's method to remove Ip and Equipment relationship.
        If Ip from this Ip-Equipment is associated with created Vip Request, and the Equipment
        is the last balancer associated, the IpEquipment association cannot be removed.
        If Ip has no relationship with other Equipments, then Ip is also removed.
        '''

        for r in self.ip.requisicaovips_set.all():
            if self.equipamento.tipo_equipamento == TipoEquipamento.get_tipo_balanceador():
                # Get all equipments (except the one being removed) related to ip
                # to find another balancer
                other_equips = self.ip.ipequipamento_set.exclude(
                    equipamento=self.equipamento.id)
                another_balancer = False
                for ipequip in other_equips:
                    if ipequip.equipamento.tipo_equipamento == TipoEquipamento.get_tipo_balanceador():
                        another_balancer = True
                        break

                if not another_balancer:
                    if r.vip_criado:
                        raise IpEquipCantDissociateFromVip({'vip_id': r.id, 'ip': mount_ipv4_string(
                            self.ip), 'equip_name': self.equipamento.nome}, "Ipv4 não pode ser disassociado do equipamento %s porque é o último balanceador da Requisição Vip %s." % (self.equipamento.nome, r.id))
                    else:
                        # Remove ip from vip or remove vip
                        id_vip = r.id
                        if r.ipv6 is not None:
                            r.ip = None
                            r.validado = 0
                            r.save(authenticated_user)

                            # SYNC_VIP
                            old_to_new(r)
                        else:
                            r.delete()

                            # SYNC_VIP
                            delete_new(id_vip)

        if self.ip.serverpoolmember_set.count() > 0:

            server_pool_identifiers = set()

            for svm in self.ip.serverpoolmember_set.all():
                item = '{}:{}'.format(svm.server_pool.id, svm.server_pool.identifier)
                server_pool_identifiers.add(item)

            server_pool_identifiers = list(server_pool_identifiers)
            server_pool_identifiers = ', '.join(str(server_pool) for server_pool in server_pool_identifiers)

            raise IpCantRemoveFromServerPool({'ip': mount_ipv4_string(self.ip), 'equip_name': self.equipamento.nome, 'server_pool_identifiers': server_pool_identifiers},
                                             "Ipv4 não pode ser disassociado do equipamento %s porque ele está sendo utilizando nos Server Pools (id:identifier) %s" % (self.equipamento.nome, server_pool_identifiers))

        super(IpEquipamento, self).delete()

        # If IP is not related to any other equipments, its removed
        if self.ip.ipequipamento_set.count() == 0:
            self.ip.delete()

    def remove(self, authenticated_user, ip_id, equip_id):
        '''Search and remove relationship between IP and equipment.
        @return: Nothing
        @raise IpEquipmentNotFoundError: There's no relationship between Ip and Equipment.
        @raise IpCantBeRemovedFromVip: Ip is associated with created Vip Request.
        @raise IpEquipCantDissociateFromVip: Equipment is the last balanced in a created Vip Request pointing to ip.
        @raise IpError: Failed to remove the relationship.
        '''
        ip_equipamento = self.get_by_ip_equipment(ip_id, equip_id)

        try:
            ip_equipamento.delete()

        except (IpCantBeRemovedFromVip, IpEquipCantDissociateFromVip), e:
            raise e
        except Exception, e:
            self.log.error(u'Falha ao remover um ip_equipamento.')
            raise IpError(e, u'Falha ao remover um ip_equipamento.')


class NetworkIPv6(BaseModel):

    id = models.AutoField(primary_key=True)
    vlan = models.ForeignKey(Vlan, db_column='id_vlan')
    network_type = models.ForeignKey(
        TipoRede, null=True, db_column='id_tipo_rede')
    ambient_vip = models.ForeignKey(
        EnvironmentVip, null=True, db_column='id_ambientevip')
    block = models.IntegerField(db_column='bloco')
    block1 = models.CharField(max_length=4, db_column='bloco1')
    block2 = models.CharField(max_length=4, db_column='bloco2')
    block3 = models.CharField(max_length=4, db_column='bloco3')
    block4 = models.CharField(max_length=4, db_column='bloco4')
    block5 = models.CharField(max_length=4, db_column='bloco5')
    block6 = models.CharField(max_length=4, db_column='bloco6')
    block7 = models.CharField(max_length=4, db_column='bloco7')
    block8 = models.CharField(max_length=4, db_column='bloco8')
    mask1 = models.CharField(max_length=4, db_column='mask_bloco1')
    mask2 = models.CharField(max_length=4, db_column='mask_bloco2')
    mask3 = models.CharField(max_length=4, db_column='mask_bloco3')
    mask4 = models.CharField(max_length=4, db_column='mask_bloco4')
    mask5 = models.CharField(max_length=4, db_column='mask_bloco5')
    mask6 = models.CharField(max_length=4, db_column='mask_bloco6')
    mask7 = models.CharField(max_length=4, db_column='mask_bloco7')
    mask8 = models.CharField(max_length=4, db_column='mask_bloco8')
    cluster_unit = models.CharField(max_length=45, db_column='cluster_unit')
    active = models.BooleanField()

    log = logging.getLogger('NetworkIPv6')

    class Meta(BaseModel.Meta):
        db_table = u'redeipv6'
        managed = True

    def _get_formated_ip(self):
        "Returns formated ip."
        return '%s:%s:%s:%s:%s:%s:%s:%s/%s' % (self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8, self.block)

    networkv6 = property(_get_formated_ip)

    @cached_property
    def dhcprelay(self):
        from networkapi.api_network.models import DHCPRelayIPv6

        return DHCPRelayIPv6.objects.filter(networkipv6=self)

    @classmethod
    def get_by_pk(cls, id):
        """Get NetworkIPv6 by id.
            @return: NetworkIPv6.
            @raise NetworkIPv6NotFoundError: NetworkIPv6 is not registered.
            @raise NetworkIPv6Error: Failed to search for the NetworkIPv6.
            @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return NetworkIPv6.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise NetworkIPv6NotFoundError(
                e, u'Can not find a NetworkIPv6 with id = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Error finding NetworkIPv6.')
            raise NetworkIPv6Error(e, u'Error finding NetworkIPv6.')

    def activate(self, authenticated_user):

        from networkapi.api_network.serializers import NetworkIPv6Serializer

        try:
            self.active = 1
            self.save()
            # Send to Queue
            queue_manager = QueueManager()
            serializer = NetworkIPv6Serializer(self)
            data_to_queue = serializer.data
            data_to_queue.update({'description': queue_keys.NETWORKv6_ACTIVATE})
            queue_manager.append({'action': queue_keys.NETWORKv6_ACTIVATE, 'kind': queue_keys.NETWORKv6_KEY, 'data': data_to_queue})
            queue_manager.send()
        except Exception, e:
            self.log.error(u'Error activating NetworkIPv6.')
            raise NetworkIPv4Error(e, u'Error activating NetworkIPv6.')

    def deactivate(self, authenticated_user, commit=False):
        '''
            Update status column  to 'active = 0'
            @param authenticated_user: User authenticate
            @raise NetworkIPv6Error: Error disabling NetworkIPv6.
        '''

        from networkapi.api_network.serializers import NetworkIPv6Serializer

        try:

            self.active = 0
            self.save(authenticated_user, commit=commit)
            # Send to Queue
            queue_manager = QueueManager()
            serializer = NetworkIPv6Serializer(self)
            data_to_queue = serializer.data
            data_to_queue.update({'description': queue_keys.NETWORKv6_DEACTIVATE})
            queue_manager.append({'action': queue_keys.NETWORKv6_DEACTIVATE, 'kind': queue_keys.NETWORKv6_KEY, 'data': data_to_queue})
            queue_manager.send()
        except Exception, e:
            self.log.error(u'Error disabling NetworkIPv6.')
            raise NetworkIPv6Error(e, u'Error disabling NetworkIPv6.')

    def edit_network_ipv6(self, authenticated_user, id_net_type, id_env_vip, cluster_unit):
        try:
            self.network_type = id_net_type
            self.ambient_vip = id_env_vip
            self.cluster_unit = cluster_unit
            self.save()
        except Exception, e:
            self.log.error(u'Error on update NetworkIPv6.')
            raise NetworkIPv4Error(e, u'Error on update NetworkIPv6.')

    def add_network_ipv6(self, user, id_vlan, network_type, evip, prefix=None):
        """
        Insert new NetworkIPv6 in database
        @return: Vlan map
        @raise VlanNotFoundError: Vlan is not registered.
        @raise VlanError: Failed to search for the Vlan
        @raise ConfigEnvironmentInvalidError: Invalid Environment Configuration or not registered
        @raise NetworkIPv6Error: Error persisting a NetworkIPv6.
        @raise NetworkIPv6AddressNotAvailableError: Unavailable address to create a NetworkIPv6.
        @raise InvalidValueError: Network type does not exist.
        """

        self.vlan = Vlan().get_by_pk(id_vlan)

        network_found = None
        stop = False
        internal_network_type = None
        type_ipv6 = IP_VERSION.IPv6[0]

        try:

            # Find all configs type v6 in environment
            configs = ConfigEnvironment.get_by_environment(
                self.vlan.ambiente.id).filter(ip_config__type=IP_VERSION.IPv6[0])

            # If not found, an exception is thrown
            if len(configs) == 0:
                raise ConfigEnvironmentInvalidError(
                    None, u'Invalid Configuration')

            # Find all networks ralated to environment
            nets = NetworkIPv6.objects.filter(
                vlan__ambiente__id=self.vlan.ambiente.id)

            # Cast to API class
            networksv6 = set([(IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%s' % (net_ip.block1, net_ip.block2, net_ip.block3,
                                                                           net_ip.block4, net_ip.block5, net_ip.block6, net_ip.block7, net_ip.block8, net_ip.block))) for net_ip in nets])

            # For each configuration founded in environment
            for config in configs:

                # If already get a network stop this
                if stop:
                    break

                # Need to be IPv6
                if config.ip_config.type == IP_VERSION.IPv6[0]:

                    net6 = IPv6Network(config.ip_config.subnet)

                    if prefix is not None:
                        new_prefix = int(prefix)
                    else:
                        new_prefix = int(config.ip_config.new_prefix)

                    self.log.info(u"Prefix that will be used: %s" % new_prefix)

                    # For each subnet generated with configs
                    for subnet in net6.iter_subnets(new_prefix=new_prefix):

                        # Checks if the network generated is UNUSED
                        if subnet not in networksv6:

                            in_range = network_in_range(self.vlan, subnet, type_ipv6)
                            if not in_range:
                                continue

                            # If not this will be USED
                            network_found = subnet

                            if network_type:
                                internal_network_type = network_type
                            elif config.ip_config.network_type is not None:
                                internal_network_type = config.ip_config.network_type
                            else:
                                self.log.error(
                                    u'Parameter tipo_rede is invalid. Value: %s', network_type)
                                raise InvalidValueError(
                                    None, 'network_type', network_type)

                            # Stop generation logic
                            stop = True
                            break

                # If not be IPv6
                else:
                    # Throw an exception
                    raise ConfigEnvironmentInvalidError(
                        None, u'Invalid Configuration')

        except (ValueError, TypeError, AddressValueError), e:
            raise ConfigEnvironmentInvalidError(e, u'Invalid Configuration')

        # Checks if found any available network
        if network_found is None:
            # If not found, an exception is thrown
            raise NetworkIPv6AddressNotAvailableError(
                None, u'Unavailable address to create a NetworkIPv6.')

        # Set block by network generated
        self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8 = str(
            network_found.network.exploded).split(':')

        # Set block by network generated
        self.block = network_found.prefixlen

        # Set mask by network generated
        self.mask1, self.mask2, self.mask3, self.mask4, self.mask5, self.mask6, self.mask7, self.mask8 = str(
            network_found.netmask.exploded).split(':')

        try:
            # Set Network Type
            self.network_type = internal_network_type
            # Set Environment VIP
            self.ambient_vip = evip
            self.save()

        except Exception, e:
            self.log.error(u'Error persisting a NetworkIPv6.')
            raise NetworkIPv6Error(e, u'Error persisting a NetworkIPv6.')

        # Return vlan map
        vlan_map = dict()
        vlan_map['id'] = self.vlan.id
        vlan_map['nome'] = self.vlan.nome
        vlan_map['num_vlan'] = self.vlan.num_vlan
        vlan_map['id_tipo_rede'] = self.network_type.id
        vlan_map['id_ambiente'] = self.vlan.ambiente.id
        vlan_map['bloco1'] = self.block1
        vlan_map['bloco2'] = self.block2
        vlan_map['bloco3'] = self.block3
        vlan_map['bloco4'] = self.block4
        vlan_map['bloco5'] = self.block5
        vlan_map['bloco6'] = self.block6
        vlan_map['bloco7'] = self.block7
        vlan_map['bloco8'] = self.block8
        vlan_map['bloco'] = self.block
        vlan_map['mask_bloco1'] = self.mask1
        vlan_map['mask_bloco2'] = self.mask2
        vlan_map['mask_bloco3'] = self.mask3
        vlan_map['mask_bloco4'] = self.mask4
        vlan_map['mask_bloco5'] = self.mask5
        vlan_map['mask_bloco6'] = self.mask6
        vlan_map['mask_bloco7'] = self.mask7
        vlan_map['mask_bloco8'] = self.mask8
        vlan_map['descricao'] = self.vlan.descricao
        vlan_map['acl_file_name'] = self.vlan.acl_file_name
        vlan_map['acl_valida'] = self.vlan.acl_valida
        vlan_map['acl_file_name_v6'] = self.vlan.acl_file_name_v6
        vlan_map['acl_valida_v6'] = self.vlan.acl_valida_v6
        vlan_map['ativada'] = self.vlan.ativada
        vlan_map['id_network'] = self.id

        map = dict()
        map['vlan'] = vlan_map

        return map

    def delete(self):

        try:

            for ip in self.ipv6_set.all():
                ip.delete()

            super(NetworkIPv6, self).delete()

        except IpCantBeRemovedFromVip, e:
            # Network id and ReqVip id
            net_name = str(self.block1) + ':' + str(self.block2) + \
                ':' + str(self.block3) + ':' + str(self.block4) + ':'
            net_name = net_name + str(self.block5) + ':' + str(self.block6) + ':' + str(
                self.block7) + ':' + str(self.block8) + '/' + str(self.block)
            cause = {'Net': net_name, 'ReqVip': e.cause}
            raise IpCantBeRemovedFromVip(
                cause, "Esta Rede possui um Vip apontando para ela, e não pode ser excluída")


class Ipv6(BaseModel):

    id = models.AutoField(primary_key=True, db_column='id_ipv6')
    description = models.CharField(
        max_length=100, blank=True, db_column='descricao')
    networkipv6 = models.ForeignKey(NetworkIPv6, db_column='id_redeipv6')
    block1 = models.CharField(max_length=4, db_column='bloco1')
    block2 = models.CharField(max_length=4, db_column='bloco2')
    block3 = models.CharField(max_length=4, db_column='bloco3')
    block4 = models.CharField(max_length=4, db_column='bloco4')
    block5 = models.CharField(max_length=4, db_column='bloco5')
    block6 = models.CharField(max_length=4, db_column='bloco6')
    block7 = models.CharField(max_length=4, db_column='bloco7')
    block8 = models.CharField(max_length=4, db_column='bloco8')

    log = logging.getLogger('Ipv6')

    class Meta(BaseModel.Meta):
        db_table = u'ipsv6'
        managed = True
        unique_together = ('block1', 'block2', 'block3', 'block4',
                           'block5', 'block6', 'block7', 'block8', 'networkipv6')

    def _get_formated_ip(self):
        "Returns formated ip."
        return '%s:%s:%s:%s:%s:%s:%s:%s' % (self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8)

    ip_formated = property(_get_formated_ip)

    @classmethod
    def get_by_pk(cls, id):
        '''Get IPv6 by id.
        @return: IPv6.
        @raise IpNotFoundError: IPv6 is not registered.
        @raise IpError: Failed to search for the IPv6.
        @raise OperationalError: Lock wait timeout exceeded.
        '''
        try:
            return Ipv6.objects.filter(id=id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(e, u'Dont there is a IP by pk = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the IP.')
            raise IpError(e, u'Failure to search the IP.')

    def get_by_blocks_equipment(self, block1, block2, block3, block4, block5, block6, block7, block8, equip_id):
        """Get IPv6 by blocks and equip_id.
            @return: IPv6.
            @raise IpNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
        """
        try:
            return Ipv6.objects.get(block1=block1, block2=block2, block3=block3, block4=block4, block5=block5, block6=block6, block7=block7, block8=block8, ipv6equipament__equipamento__id=equip_id)
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(e, u'There is no IP %s:%s:%s:%s:%s:%s:%s:%s of the equipament %s.' % (
                block1, block2, block3, block4, block5, block6, block7, block8, equip_id))
        except Exception, e:
            self.log.error(u'Failure to search the IP.')
            raise IpError(e, u'Failure to search the IP.')

    @classmethod
    def list_by_network(cls, id_network):
        """Get IP6 LIST by id_network.
            @return: IP6 List.
            @raise IpNotFoundError: IP6 is not registered.
            @raise IpError: Failed to search for the IP6.
            @raise OperationalError: Lock wait timeout exceeded.
        """

        try:
            return Ipv6.objects.filter(networkipv6=id_network)
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(
                e, u'Dont there is a IP by network_id = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the IP.')
            raise IpError(e, u'Failure to search the IP')

    @classmethod
    def list_by_environment_and_equipment(cls, id_ambiente, id_equipment):
        """Get IP LIST by id_network.
            @return: IP List.
            @raise IpNotFoundError: IP is not registered.
            @raise IpError: Failed to search for the IP.
            @raise OperationalError: Lock wait timeout exceeded.
        """

        try:
            return Ipv6.objects.select_related().filter(networkipv6__vlan__ambiente__id=id_ambiente, ipv6equipament__equipamento__id=id_equipment)
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(
                e, u'Dont there is a IP by network_id = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the IP.')
            raise IpError(e, u'Failure to search the IP')

    @classmethod
    def get_available_ip6(cls, id_network):
        """Get a available ip6 for network6
            @return: Available IP6
            @raise IpNotAvailableError: NetworkIPv6 does not has available Ip6
        """

        cls.networkipv6 = NetworkIPv6.get_by_pk(id_network)

        # Cast to API
        net6 = IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%s' % (
            cls.networkipv6.block1, cls.networkipv6.block2, cls.networkipv6.block3,
            cls.networkipv6.block4, cls.networkipv6.block5, cls.networkipv6.block6,
            cls.networkipv6.block7, cls.networkipv6.block8, cls.networkipv6.block))
        # Find all ipv6s ralated to network
        ips = Ipv6.objects.filter(networkipv6__id=cls.networkipv6.id)

        # Cast all to API class
        ipsv6 = set([(IPv6Address('%s:%s:%s:%s:%s:%s:%s:%s' % (
            ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8))) for ip in ips])

        # Get configuration
        conf = Configuration.get()

        selected_ip = None

        # For each ip generated
        # For each ip generated
        i = 0
        for ip in net6.iterhosts():

            # Do not use some range of IPs (config)
            i = i + 1
            if i >= conf.IPv6_MIN and i < (net6.numhosts - conf.IPv6_MAX):

                # If IP generated was not used
                if ip not in ipsv6:

                    # Use it
                    selected_ip = ip

                    return selected_ip.exploded

                    # Stop generation
                    break

        if selected_ip is None:
            raise IpNotAvailableError(
                None, u'No IP6 available to NETWORK %s.' % cls.networkipv6.id)

    @classmethod
    def get_first_available_ip6(cls, id_network, topdown=False):
        """Get a first available ip6 for network6
            @return: Available IP6
            @raise IpNotAvailableError: NetworkIPv6 does not has available Ip6
        """

        cls.networkipv6 = NetworkIPv6.get_by_pk(id_network)
        # Cast to API
        net6 = IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%s' % (
            cls.networkipv6.block1, cls.networkipv6.block2, cls.networkipv6.block3,
            cls.networkipv6.block4, cls.networkipv6.block5, cls.networkipv6.block6,
            cls.networkipv6.block7, cls.networkipv6.block8, cls.networkipv6.block))
        # Find all ipv6s ralated to network
        ips = Ipv6.objects.filter(networkipv6__id=cls.networkipv6.id)
        for ip in ips:
            cls.log.info("ip %s" % ip.block8)

        # Cast all to API class
        ipsv6 = set([(IPv6Address('%s:%s:%s:%s:%s:%s:%s:%s' % (
            ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8))) for ip in ips])

        selected_ip = None

        if topdown:
            method = net6.iterhostsTopDown
        else:
            method = net6.iterhosts

        # For each ip generated
        for ip in method():

            # If IP generated was not used
            if ip not in ipsv6:

                # Use it
                selected_ip = ip

                return selected_ip.exploded

                # Stop generation
                break

        if selected_ip is None:
            raise IpNotAvailableError(
                None, u'No IP6 available to NETWORK %s.' % cls.networkipv6.id)

    def delete_ip6(self, user, id_ip):
        try:

            ip = self.get_by_pk(id_ip)
            ip.delete()

        except IpNotFoundError, e:
            raise IpNotFoundError(None, e)
        except Exception, e:
            self.log.error(u'Failure to delete the IP.')
            raise IpError(e, u'Failure to delete the IP')

    def edit_ipv6(self, user):
        try:
            # Cast to API
            net6 = IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%s' % (self.networkipv6.block1, self.networkipv6.block2, self.networkipv6.block3, self.networkipv6.block4,
                                                               self.networkipv6.block5, self.networkipv6.block6, self.networkipv6.block7, self.networkipv6.block8, self.networkipv6.block))
            # Find all ipv6s ralated to network
            ips = Ipv6.objects.filter(networkipv6__id=self.networkipv6.id)

            ip6_object = IPv6Address('%s:%s:%s:%s:%s:%s:%s:%s' % (
                self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8))

            # Cast all to API class
            ipsv6 = set([IPv6Address('%s:%s:%s:%s:%s:%s:%s:%s' % (
                ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8)) for ip in ips])

            # Get configuration
            conf = Configuration.get()

            flag = True

            aux_ip6 = ip6_object.exploded
            aux_ip6 = aux_ip6.split(":")
            self.block1 = aux_ip6[0]
            self.block2 = aux_ip6[1]
            self.block3 = aux_ip6[2]
            self.block4 = aux_ip6[3]
            self.block5 = aux_ip6[4]
            self.block6 = aux_ip6[5]
            self.block7 = aux_ip6[6]
            self.block8 = aux_ip6[7]

            if ip6_object not in ipsv6:

                flag = False

                if ip6_object in net6:

                    # Get configuration
                    conf = Configuration.get()

                    first_ip_network = int(net6.network)
                    bcast_ip_network = int(net6.broadcast)

                    ipv6_network = int(ip6_object)

                    if ipv6_network >= (first_ip_network + conf.IPv6_MIN) and ipv6_network < (bcast_ip_network - conf.IPv6_MAX):
                        flag = True

            else:
                ip6_aux = self.get_by_blocks_and_net(
                    self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8, self.networkipv6.id)
                if self.id != ip6_aux.id:
                    raise IpNotAvailableError(None, u'Ipv6 %s:%s:%s:%s:%s:%s:%s:%s already on use by network %s.' % (
                        self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8, self.networkipv6.id))

            if flag:
                self.save()

            else:
                raise IpNotAvailableError(None, u'Ipv6 %s:%s:%s:%s:%s:%s:%s:%s not available for network %s.' % (
                    self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8, self.networkipv6.id))

        except IpEquipmentAlreadyAssociation, e:
            self.log.error(e)
            raise IpEquipmentAlreadyAssociation(None, e)
        except AddressValueError:
            raise InvalidValueError(None, 'ip6', u'%s:%s:%s:%s:%s:%s:%s:%s' % (
                self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8))
        except IpNotAvailableError, e:
            raise IpNotAvailableError(None, e.message)
        except IpError, e:
            self.log.error(
                u'Error adding new IPv6 or relationship ip-equipment.')
            raise IpError(
                e, u'Error adding new IPv6 or relationship ip-equipment.')

    def save_ipv6(self, equipment_id, user, net):

        try:

            already_ip = False

            # Cast to API
            net6 = IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%s' % (net.block1, net.block2, net.block3, net.block4,
                                                               net.block5, net.block6, net.block7, net.block8, net.block))
            # Find all ipv6s ralated to network
            ips = Ipv6.objects.filter(networkipv6__id=net.id)

            ip6_object = IPv6Address('%s:%s:%s:%s:%s:%s:%s:%s' % (
                self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8))

            # Cast all to API class
            ipsv6 = set([IPv6Address('%s:%s:%s:%s:%s:%s:%s:%s' % (
                ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8)) for ip in ips])

            # Get configuration
            # conf = Configuration.get()

            flag = False

            aux_ip6 = ip6_object.exploded
            aux_ip6 = aux_ip6.split(":")
            self.block1 = aux_ip6[0]
            self.block2 = aux_ip6[1]
            self.block3 = aux_ip6[2]
            self.block4 = aux_ip6[3]
            self.block5 = aux_ip6[4]
            self.block6 = aux_ip6[5]
            self.block7 = aux_ip6[6]
            self.block8 = aux_ip6[7]
            # ip6_object = ip6_object.exploded

            if ip6_object not in ipsv6:

                if ip6_object in net6:

                    # Get configuration
                    # conf = Configuration.get()

                    first_ip_network = int(net6.network)
                    bcast_ip_network = int(net6.broadcast)

                    ipv6_network = int(ip6_object)

                    if ipv6_network >= (first_ip_network) and ipv6_network < (bcast_ip_network):
                        flag = True

            else:
                ip_aux = self.get_by_blocks_and_net(
                    self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8, net.id)
                try:
                    Ipv6Equipament.get_by_ip6(ip_aux.id)
                    raise IpEquipmentAlreadyAssociation(None, u'Ipv6 %s:%s:%s:%s:%s:%s:%s:%s already has association with an Equipament. Try using the association screen for this Ip.' % (
                        self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8))
                except IpEquipmentNotFoundError, e:
                    flag = True
                    already_ip = True

            if flag:
                equipment = Equipamento().get_by_pk(equipment_id)
                ip6_equipment = Ipv6Equipament()
                if not already_ip:
                    self.networkipv6_id = net.id
                    self.save()
                    ip6_equipment.ip = self

                else:
                    ip6_equipment.ip = ip_aux
                    if self.description is not None and len(self.description) > 0:
                        ip_aux.description = self.description
                        ip_aux.save()

                ip6_equipment.equipamento = equipment

                # # Filter case 2 - Adding new IpEquip for a equip that already have ip in other network with the same range ##

                # Get all IpEquipamento related to this equipment
                ip_equips = Ipv6Equipament.objects.filter(
                    equipamento=equipment_id)

                for ip_test in [ip_equip.ip for ip_equip in ip_equips]:
                    if ip_test.networkipv6.block1 == self.networkipv6.block1 and \
                            ip_test.networkipv6.block2 == self.networkipv6.block2 and \
                            ip_test.networkipv6.block3 == self.networkipv6.block3 and \
                            ip_test.networkipv6.block4 == self.networkipv6.block4 and \
                            ip_test.networkipv6.block5 == self.networkipv6.block5 and \
                            ip_test.networkipv6.block6 == self.networkipv6.block6 and \
                            ip_test.networkipv6.block7 == self.networkipv6.block7 and \
                            ip_test.networkipv6.block8 == self.networkipv6.block8 and \
                            ip_test.networkipv6.block == self.networkipv6.block and \
                            ip_test.networkipv6 != self.networkipv6:

                        # Filter testing
                        if ip_test.networkipv6.vlan.ambiente.filter is None or self.networkipv6.vlan.ambiente.filter is None:
                            raise IpRangeAlreadyAssociation(
                                None, u'Equipment is already associated with another ip with the same ip range.')
                        else:
                            # Test both environment's filters
                            tp_equip_list_one = list()
                            for fet in FilterEquipType.objects.filter(filter=self.networkipv6.vlan.ambiente.filter.id):
                                tp_equip_list_one.append(fet.equiptype)

                            tp_equip_list_two = list()
                            for fet in FilterEquipType.objects.filter(filter=ip_test.networkipv6.vlan.ambiente.filter.id):
                                tp_equip_list_two.append(fet.equiptype)

                            if equipment.tipo_equipamento not in tp_equip_list_one or equipment.tipo_equipamento not in tp_equip_list_two:
                                raise IpRangeAlreadyAssociation(
                                    None, u'Equipment is already associated with another ip with the same ip range.')

                # # Filter case 2 - end ##

                ip6_equipment.save()

                # Makes Environment Equipment association
                try:
                    equipment_environment = EquipamentoAmbiente()
                    equipment_environment.equipamento = equipment
                    equipment_environment.ambiente = net.vlan.ambiente
                    equipment_environment.create(user)
                except EquipamentoAmbienteDuplicatedError, e:
                    # If already exists, OK !
                    pass

            else:
                raise IpNotAvailableError(None, u'Ipv6 %s:%s:%s:%s:%s:%s:%s:%s not available for network %s.' % (
                    self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8, net.id))

        except IpRangeAlreadyAssociation, e:
            raise IpRangeAlreadyAssociation(None, e.message)
        except IpEquipmentAlreadyAssociation, e:
            raise IpEquipmentAlreadyAssociation(None, e.message)
        except AddressValueError:
            raise InvalidValueError(None, 'ip6', u'%s:%s:%s:%s:%s:%s:%s:%s' % (
                self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8))
        except IpNotAvailableError, e:
            raise IpNotAvailableError(None, u'Ipv6 %s:%s:%s:%s:%s:%s:%s:%s not available for network %s.' % (
                self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8, net.id))
        except IpError, e:
            self.log.error(
                u'Error adding new IPv6 or relationship ip-equipment.')
            raise IpError(
                e, u'Error adding new IPv6 or relationship ip-equipment.')

    def create(self, authenticated_user, equipment_id, id):
        '''Persist an IPv6 and associate it to an equipment.
        If equipment was not related with VLAN environment, this makes the relationship
        @return: Nothing
        @raise NetworkIPv6NotFoundError: NetworkIPv6 does not exist.
        @raise NetworkIPv6Error: Error finding NetworkIPv6.
        @raise EquipamentoNotFoundError: Equipment does not exist.
        @raise EquipamentoError: Error finding Equipment.
        @raise IpNotAvailableError: No IP available to VLAN.
        @raise IpError: Error persisting in database.
        '''

        self.networkipv6 = NetworkIPv6().get_by_pk(id)

        # Cast to API
        net6 = IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%s' % (self.networkipv6.block1, self.networkipv6.block2, self.networkipv6.block3, self.networkipv6.block4,
                                                           self.networkipv6.block5, self.networkipv6.block6, self.networkipv6.block7, self.networkipv6.block8, self.networkipv6.block))
        # Find all ipv6s ralated to network
        ips = Ipv6.objects.filter(networkipv6__id=self.networkipv6.id)

        # Cast all to API class
        ipsv6 = set([(IPv6Address('%s:%s:%s:%s:%s:%s:%s:%s' % (
            ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8))) for ip in ips])

        # Get configuration
        conf = Configuration.get()

        selected_ip = None

        # For each ip generated
        i = 0
        for ip in net6.iterhosts():

            # Do not use some range of IPs (config)
            i = i + 1
            if i >= conf.IPv6_MIN and i < (net6.numhosts - conf.IPv6_MAX):

                # If IP generated was not used
                if ip not in ipsv6:

                    # Use it
                    selected_ip = ip

                    # Stop generation
                    break

        if selected_ip is None:
            raise IpNotAvailableError(
                None, u'No IPv6 available to VLAN %s.' % self.networkipv6.vlan.num_vlan)

        self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8 = str(
            selected_ip.exploded).split(':')

        equipment = Equipamento().get_by_pk(equipment_id)

        try:
            self.save()

            ipv6_equipment = Ipv6Equipament()
            ipv6_equipment.ip = self
            ipv6_equipment.equipamento = equipment
            ipv6_equipment.save(authenticated_user)

            try:
                equipment_environment = EquipamentoAmbiente().get_by_equipment_environment(
                    equipment_id, self.networkipv6.vlan.ambiente_id)

            except EquipamentoAmbienteNotFoundError:
                equipment_environment = EquipamentoAmbiente()
                equipment_environment.equipamento = equipment
                equipment_environment.ambiente = self.networkipv6.vlan.ambiente
                equipment_environment.save(authenticated_user)

        except Exception, e:
            self.log.error(
                u'Error adding new IPv6 or relationship ip-equipment.')
            raise IpError(
                e, u'Error adding new IPv6 or relationship ip-equipment.')

    @classmethod
    def get_by_blocks_and_net(cls, block1, block2, block3, block4, block5, block6, block7, block8, id_network):
        '''Get Ipv6 by blocks and network.
        @return: Ipv6.
        @raise IpNotFoundError: Ipv6 is not registered.
        @raise IpError: Failed to search for the Ipv6.
        '''
        try:
            return Ipv6.objects.get(block1=block1, block2=block2, block3=block3, block4=block4, block5=block5, block6=block6, block7=block7, block8=block8, networkipv6=id_network)
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(e, u'Dont there is a Ipv6 %s:%s:%s:%s:%s:%s:%s:%s  ' % (
                block1, block2, block3, block4, block5, block6, block7, block8))
        except Exception, e:
            cls.log.error(u'Failure to search the Ipv6.')
            raise IpError(e, u'Failure to search the Ipv6.')

    @classmethod
    def get_by_blocks(cls, block1, block2, block3, block4, block5, block6, block7, block8):
        '''Get Ipv6's  by blocks.
        @return: Ipv6's.
        @raise IpNotFoundError: Ipv6 is not registered.
        @raise IpError: Failed to search for the Ipv6.
        '''
        try:
            ips = Ipv6.objects.filter(block1=block1, block2=block2, block3=block3,
                                      block4=block4, block5=block5, block6=block6, block7=block7, block8=block8)

            if len(ips) == 0:
                raise ObjectDoesNotExist()

            return ips
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(e, u'Dont there is a Ipv6 %s:%s:%s:%s:%s:%s:%s:%s  ' % (
                block1, block2, block3, block4, block5, block6, block7, block8))
        except Exception, e:
            cls.log.error(u'Failure to search the Ipv6.')
            raise IpError(e, u'Failure to search the Ipv6.')

    @classmethod
    def get_by_octs_and_environment_vip(cls, block1, block2, block3, block4, block5, block6, block7, block8, id_evip, valid=True):
        '''Get Ipv6 by blocks and environment vip.
        @return: Ipv6.
        @raise IpNotFoundError: Ipv6 is not registered.
        @raise IpError: Failed to search for the Ipv6.
        '''
        try:
            ips = Ipv6.objects.filter(block1=block1, block2=block2, block3=block3,
                                      block4=block4, block5=block5, block6=block6, block7=block7, block8=block8)
            if ips.count() == 0:
                raise IpNotFoundError(None)

            if valid is True:
                return Ipv6.objects.get(block1=block1, block2=block2, block3=block3, block4=block4, block5=block5,
                                        block6=block6, block7=block7, block8=block8, networkipv6__ambient_vip__id=id_evip)
            else:
                for ip in ips:
                    if ip.networkipv6.ambient_vip:
                        if ip.networkipv6.ambient_vip.id == id_evip:
                            return ip
                    else:
                        environments = Ambiente.objects.filter(
                            vlan__networkipv6__ambient_vip__id=id_evip)
                        for env in environments:
                            if ip.networkipv6.vlan.ambiente.divisao_dc.id == env.divisao_dc.id \
                                    and ip.networkipv6.vlan.ambiente.ambiente_logico.id == env.ambiente_logico.id:
                                return ip
                raise ObjectDoesNotExist()

        except ObjectDoesNotExist, e:
            evip = EnvironmentVip.get_by_pk(id_evip)
            msg = u'Ipv6 não está relacionado ao Ambiente Vip: %s.' % evip.show_environment_vip()
            cls.log.error(msg)
            raise IpNotFoundByEquipAndVipError(e, msg)

        except IpNotFoundError, e:
            msg = u'Ipv6 "%s.%s.%s.%s.%s.%s.%s.%s" não existe.' % (
                block1, block2, block3, block4, block5, block6, block7, block8)
            cls.log.error(msg)
            raise IpNotFoundError(e, msg)

        except Exception, e:
            cls.log.error(u'Failure to search the Ipv6.')
            raise IpError(e, u'Failure to search the Ipv6.')

    @classmethod
    def get_by_octs_and_environment(cls, block1, block2, block3, block4, block5,
                                    block6, block7, block8, id_environment):
        '''Get Ipv6 by blocks and environment.
        @return: Ipv6.
        @raise IpNotFoundError: Ipv6 is not registered.
        @raise IpError: Failed to search for the Ipv6.
        '''
        try:
            return Ipv6.objects.get(
                block1=block1, block2=block2, block3=block3, block4=block4, block5=block5,
                block6=block6, block7=block7, block8=block8, networkipv6__vlan__ambiente__id=id_environment)
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(e, u'Dont there is a IPv6 %s:%s:%s:%s:%s:%s:%s:%s of the environment %s.' % (
                block1, block2, block3, block4, block5, block6, block7, block8, id_environment))
        except Exception, e:
            cls.log.error(u'Failure to search the Ipv6.')
            raise IpError(e, u'Failure to search the Ipv6.')

    def delete(self):
        '''Sobrescreve o método do Django para remover um IP.
        Antes de remover o IP remove todas as suas requisições de VIP e os relacionamentos com equipamentos.
        '''
        try:
            # Delete all Request Vip associeted
            for r in self.requisicaovips_set.all():
                r_alter = False
                id_vip = r.id
                if r.vip_criado:
                    raise IpCantBeRemovedFromVip(
                        r.id, "Ipv6 não pode ser removido, porque está em uso por Requisição Vip %s" % (r.id))
                else:
                    if r.ip is not None:
                        r.ipv6 = None
                        r.validado = 0
                        r.save(authenticated_user)
                        r_alter = True

                        # SYNC_VIP
                        old_to_new(r)

                if not r_alter:
                    r.delete()

                    # SYNC_VIP
                    delete_new(id_vip)

            # Delete all EquipmentIp and EnviromentEquip associated
            for ie in self.ipv6equipament_set.all():
                # Codigo removido, pois não devemos remover o ambiente do equipamento mesmo que não tenha IP
                # para o ambiente solicidado pelo Henrique

                # ambienteequip = EquipamentoAmbiente()
                # ambienteequip = ambienteequip.get_by_equipment_environment(
                #     ie.equipamento.id, self.networkipv6.vlan.ambiente_id)
                #
                # ips = Ip.list_by_environment_and_equipment(
                #     ambienteequip.ambiente_id, ie.equipamento.id)
                # ips6 = Ipv6.list_by_environment_and_equipment(
                #     ambienteequip.ambiente_id, ie.equipamento.id)
                #
                # if len(ips) <= 0 and len(ips6) <= 1:
                #
                #     ambienteequip.delete()

                ie.delete()

            from networkapi.api_pools.serializers import Ipv6Serializer
            serializer = Ipv6Serializer(self)
            data_to_queue = serializer.data

            super(Ipv6, self).delete()

            # Send to Queue
            queue_manager = QueueManager()
            data_to_queue.update({'description': queue_keys.IPv6_REMOVE})
            queue_manager.append(
                {'action': queue_keys.IPv6_REMOVE, 'kind': queue_keys.IPv6_KEY, 'data': data_to_queue})
            queue_manager.send()

        except EquipamentoAmbienteNotFoundError, e:
            raise EquipamentoAmbienteNotFoundError(None, e.message)
        except IpCantBeRemovedFromVip, e:
            raise IpCantBeRemovedFromVip(e.cause, e.message)
        except IpEquipmentNotFoundError, e:
            raise IpEquipmentNotFoundError(None, e.message)


class Ipv6Equipament(BaseModel):
    id = models.AutoField(
        primary_key=True, db_column='id_ipsv6_dos_equipamentos')
    ip = models.ForeignKey(Ipv6, db_column='id_ipv6')
    equipamento = models.ForeignKey(Equipamento, db_column='id_equip')

    log = logging.getLogger('Ipv6Equipament')

    class Meta(BaseModel.Meta):
        db_table = u'ipsv6_dos_equipamentos'
        managed = True
        unique_together = ('ip', 'equipamento')

    @classmethod
    def list_by_equip(cls, equip_id):
        """Get IP6 by id_ip
            @return: IPEquipment.
            @raise IpEquipmentNotFoundError: IP6 is not registered.
            @raise IpError: Failed to search for the IP.
        """
        try:
            return Ipv6Equipament.objects.filter(equipamento__id=equip_id)
        except ObjectDoesNotExist, e:
            raise IpEquipmentNotFoundError(
                e, u'Dont there is a IP-Equipament by Equip = %s.')
        except Exception, e:
            cls.log.error(u'Failure to search the Ip-Equipament.')
            raise IpError(e, u'Failure to search the Ip-Equipament.')

    @classmethod
    def get_by_ip6(cls, ip6_id):
        """Get IP6 by id_ip6
            @return: IP6.
            @raise IpEquipmentNotFoundError: IP6 is not registered.
            @raise IpError: Failed to search for the I6P.
        """
        try:
            return Ipv6Equipament.objects.filter(ip__id=ip6_id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise IpEquipmentNotFoundError(
                e, u'Dont there is a IP-Equipament by IP = %s.')
        except Exception, e:
            cls.log.error(u'Failure to search the Ip-Equipament.')
            raise IpError(e, u'Failure to search the Ip-Equipament.')

    @classmethod
    def list_by_ip6(cls, ip6_id):
        """Get IP6 by id_ip6
            @return: IP6.
            @raise IpEquipmentNotFoundError: IP6 is not registered.
            @raise IpError: Failed to search for the I6P.
        """
        try:
            return Ipv6Equipament.objects.filter(ip__id=ip6_id)
        except ObjectDoesNotExist, e:
            raise IpEquipmentNotFoundError(
                e, u'Dont there is a IP-Equipament by IP = %s.')
        except Exception, e:
            cls.log.error(u'Failure to search the Ip-Equipament.')
            raise IpError(e, u'Failure to search the Ip-Equipament.')

    @classmethod
    def get_by_ip_equipment(cls, ip_id, equip_id):
        """Get Ipv6Equipament by ip_id and equip_id.
        @return: Ipv6Equipament.
        @raise IpEquipmentNotFoundError: Ipv6Equipament is not registered.
        @raise IpError: Failed to search for the Ipv6Equipament.
        @raise OperationalError: Lock wait timeout exceeded.
        """
        try:
            return Ipv6Equipament.objects.filter(ip__id=ip_id, equipamento__id=equip_id).uniqueResult()
        except ObjectDoesNotExist, e:
            raise IpEquipmentNotFoundError(
                e, u'Dont there is a Ipv6Equipament by ip_id = %s and equip_id = %s' % (ip_id, equip_id))
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the Ipv6Equipament.')
            raise IpError(e, u'Failure to search the Ipv6Equipament.')

    def validate_ip(self):
        ''' Validates whether IPv6 is already associated with equipment
            @raise IpEquipamentoDuplicatedError: if IPv6 is already associated with equipment
        '''
        try:
            Ipv6Equipament.objects.get(
                ip=self.ip, equipamento=self.equipamento)
            raise IpEquipamentoDuplicatedError(
                None, u'IP already registered for the equipment.')
        except ObjectDoesNotExist:
            pass

    def create(self, authenticated_user, ip_id, equipment_id):
        '''Insere um relacionamento entre IP e Equipamento.
        @return: Nothing.
        @raise IpError: Falha ao inserir.
        @raise EquipamentoNotFoundError: Equipamento não cadastrado.
        @raise IpNotFoundError: Ip não cadastrado.
        @raise IpEquipamentoDuplicatedError: IP já cadastrado para o equipamento.
        @raise EquipamentoError: Falha ao pesquisar o equipamento.
        '''
        self.equipamento = Equipamento().get_by_pk(equipment_id)
        self.ip = Ipv6().get_by_pk(ip_id)

        # Valida o ip
        self.validate_ip()

        try:
            if self.equipamento not in [ea.equipamento for ea in self.ip.networkipv6.vlan.ambiente.equipamentoambiente_set.all()]:
                ea = EquipamentoAmbiente(
                    ambiente=self.ip.networkipv6.vlan.ambiente, equipamento=self.equipamento)
                ea.save(authenticated_user)

            self.save()
        except Exception, e:
            self.log.error(u'Falha ao inserir um ip_equipamento.')
            raise IpError(e, u'Falha ao inserir um ip_equipamento.')

    def remove(self, authenticated_user, ip_id, equip_id):
        '''Research and removes the relationship between IP and equipment.
        @return: Nothing
        @raise IpEquipmentNotFoundError: Dont is no relationship between the IP and Equipment.
        @raise IpError: Failure to remove the relationship.
        '''
        ip_equipamento = self.get_by_ip_equipment(ip_id, equip_id)

        try:
            ip_equipamento.delete()

        except (IpCantBeRemovedFromVip, IpEquipCantDissociateFromVip), e:
            raise e
        except Exception, e:
            self.log.error(u'Failure to remove the Ipv6Equipament.')
            raise IpError(e, u'Failure to remove the Ipv6Equipament.')

    def delete(self):
        '''Override Django's method to remove Ipv6 and Equipment relationship.
        If Ip from this Ip-Equipment is associated with created Vip Request, and the Equipment
        is the last balancer associated, the IpEquipment association cannot be removed.
        If Ip has no relationship with other Equipments, then Ip is also removed.
        '''

        for r in self.ip.requisicaovips_set.all():
            if self.equipamento.tipo_equipamento == TipoEquipamento.get_tipo_balanceador():
                # Get all equipments (except the one being removed) related to ip
                # to find another balancer
                other_equips = self.ip.ipv6equipament_set.exclude(
                    equipamento=self.equipamento.id)
                another_balancer = False
                for ipequip in other_equips:
                    if ipequip.equipamento.tipo_equipamento == TipoEquipamento.get_tipo_balanceador():
                        another_balancer = True
                        break

                if not another_balancer:
                    if r.vip_criado:
                        raise IpEquipCantDissociateFromVip({'vip_id': r.id, 'ip': mount_ipv6_string(
                            self.ip), 'equip_name': self.equipamento.nome}, "Ipv6 não pode ser disassociado do equipamento %s porque é o último balanceador da Requisição Vip %s." % (self.equipamento.nome, r.id))
                    else:
                        # Remove ip from vip or remove vip
                        id_vip = r.id
                        if r.ip is not None:
                            r.ipv6 = None
                            r.validado = 0
                            r.save(authenticated_user)

                            # SYNC_VIP
                            old_to_new(r)
                        else:
                            r.delete()

                            # SYNC_VIP
                            delete_new(id_vip)

        if self.ip.serverpoolmember_set.count() > 0:

            server_pool_identifiers = set()

            for svm in self.ip.serverpoolmember_set.all():
                item = '{}:{}'.format(svm.server_pool.id, svm.server_pool.identifier)
                server_pool_identifiers.add(item)

            server_pool_identifiers = list(server_pool_identifiers)
            server_pool_identifiers = ', '.join(str(server_pool) for server_pool in server_pool_identifiers)

            raise IpCantRemoveFromServerPool({'ip': mount_ipv6_string(self.ip), 'equip_name': self.equipamento.nome, 'server_pool_identifiers': server_pool_identifiers},
                                             "Ipv6 não pode ser disassociado do equipamento %s porque ele está sendo utilizando nos Server Pools (id:identifier) %s" % (self.equipamento.nome, server_pool_identifiers))

        super(Ipv6Equipament, self).delete()

        # If ip has no other equipment, than he will be removed to
        if self.ip.ipv6equipament_set.count() == 0:
            self.ip.delete()


def network_in_range(vlan, network, version):
    # Get all vlans environments from equipments of the current
    # environment

    equips = list()
    envs = list()
    envs_aux = list()
    ids_all = list()

    ambiente = vlan.ambiente
    filter = ambiente.filter
    equipment_types = TipoEquipamento.objects.filter(filterequiptype__filter=filter)

    # Get all equipments from the environment being tested
    # that are not supposed to be filtered
    # (not the same type of the equipment type of a filter of the environment)
    for env in ambiente.equipamentoambiente_set.all().exclude(equipamento__tipo_equipamento__in=equipment_types).select_related('equipamento'):
        equips.append(env.equipamento)

    # Get all environment that the equipments above are included
    for equip in equips:
        for env in equip.equipamentoambiente_set.all().select_related('ambiente'):
            if env.ambiente_id not in envs_aux:
                envs.append(env.ambiente)
                envs_aux.append(env.ambiente_id)

    # Check in all vlans from all environments above
    # if there is a network that is sub or super network of the current
    # network being tested
    for env in envs:
        for vlan in env.vlan_set.all().prefetch_related('networkipv4_set').prefetch_related('networkipv6_set'):
            ids_all.append(vlan.id)
            is_subnet = verify_subnet(vlan, network, version)
            if is_subnet:
                return False

    return True


def verify_subnet(vlan, network, version):

    from networkapi.infrastructure.ipaddr import IPNetwork

    if version == IP_VERSION.IPv4[0]:
        vlan_net = vlan.networkipv4_set.all()
    else:
        vlan_net = vlan.networkipv6_set.all()

    # One vlan may have many networks, iterate over it
    for net in vlan_net:
        if version == IP_VERSION.IPv4[0]:
            ip = "%s.%s.%s.%s/%s" % (net.oct1,
                                     net.oct2, net.oct3, net.oct4, net.block)
        else:
            ip = "%s:%s:%s:%s:%s:%s:%s:%s/%d" % (net.block1, net.block2, net.block3,
                                                 net.block4, net.block5, net.block6, net.block7, net.block8, net.block)

        ip_net = IPNetwork(ip)
        # If some network, inside this vlan, is subnet of network search param
        if ip_net in network or network in ip_net:
            # This vlan must be in vlans founded, don't need to continue
            # checking
            return True

    # If don't found any subnet return False
    return False
