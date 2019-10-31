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

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db import transaction
from django.db.models import get_model
from rest_framework import status

from networkapi.ambiente.models import ConfigEnvironmentInvalidError
from networkapi.ambiente.models import IP_VERSION
from networkapi.api_network.exceptions import InvalidInputException
from networkapi.api_network.exceptions import NetworkConflictException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_vip_request import syncs
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_ENVIRONMENT
from networkapi.distributedlock import LOCK_ENVIRONMENT_ALLOCATES
from networkapi.distributedlock import LOCK_IP_EQUIPMENT
from networkapi.distributedlock import LOCK_IP_EQUIPMENT_ONE
from networkapi.distributedlock import LOCK_VINTERFACE
from networkapi.distributedlock import LOCK_IPV4
from networkapi.distributedlock import LOCK_IPV6
from networkapi.distributedlock import LOCK_IPV6_EQUIPMENT
from networkapi.distributedlock import LOCK_IPV6_EQUIPMENT_ONE
from networkapi.distributedlock import LOCK_NETWORK_IPV4
from networkapi.distributedlock import LOCK_NETWORK_IPV6
from networkapi.distributedlock import LOCK_VIP
from networkapi.equipamento.models import EquipamentoAmbienteDuplicatedError
from networkapi.equipamento.models import EquipamentoAmbienteNotFoundError
from networkapi.equipamento.models import EquipamentoError
from networkapi.exception import InvalidValueError
from networkapi.exception import NetworkActiveError
from networkapi.infrastructure.ipaddr import AddressValueError
from networkapi.infrastructure.ipaddr import IPNetwork
from networkapi.infrastructure.ipaddr import IPv4Address
from networkapi.infrastructure.ipaddr import IPv4Network
from networkapi.infrastructure.ipaddr import IPv6Address
from networkapi.infrastructure.ipaddr import IPv6Network
from networkapi.models.BaseModel import BaseModel
from networkapi.queue_tools import queue_keys
from networkapi.queue_tools.rabbitmq import QueueManager
from networkapi.util import mount_ipv4_string
from networkapi.util import mount_ipv6_string
from networkapi.util import network
from networkapi.util.decorators import cached_property
from networkapi.util.geral import create_lock_with_blocking
from networkapi.util.geral import destroy_lock
from networkapi.util.geral import get_app
from networkapi.api_rest.exceptions import NetworkAPIException


log = logging.getLogger(__name__)


class NetworkIPv4Error(Exception):

    """Generic exception for everything related to NetworkIPv4."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Caused by: %s, Message: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class NetworkIPv4ErrorV3(Exception):

    """Generic exception for everything related to NetworkIPv4."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


class NetworkIPv6ErrorV3(Exception):

    """Generic exception for everything related to NetworkIPv6."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


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


class NetworkSubnetRange(NetworkIPvXError):

    """Exception for a network that does not be a subnet of de environment network."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Caused by: %s, Message: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class NetworkEnvironmentError(NetworkIPvXError):

    """Exception for a environment that does not have a network."""

    def __init__(self, cause, message=None):
        self.cause = cause
        self.message = message

    def __str__(self):
        msg = u'Caused by: %s, Message: %s' % (self.cause, self.message)
        return msg.encode('utf-8', 'replace')


class IpErrorV3(Exception):

    """Representa um erro ocorrido durante acesso à tabelas relacionadas com IP."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


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

    status_code = status.HTTP_404_NOT_FOUND

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

    id = models.AutoField(
        primary_key=True
    )
    oct1 = models.IntegerField(
        db_column='rede_oct1'
    )
    oct2 = models.IntegerField(
        db_column='rede_oct2'
    )
    oct3 = models.IntegerField(
        db_column='rede_oct3'
    )
    oct4 = models.IntegerField(
        db_column='rede_oct4'
    )
    block = models.IntegerField(
        db_column='bloco'
    )
    mask_oct1 = models.IntegerField(
        db_column='masc_oct1'
    )
    mask_oct2 = models.IntegerField(
        db_column='masc_oct2'
    )
    mask_oct3 = models.IntegerField(
        db_column='masc_oct3'
    )
    mask_oct4 = models.IntegerField(
        db_column='masc_oct4'
    )
    broadcast = models.CharField(
        max_length=15,
        blank=False
    )
    vlan = models.ForeignKey(
        'vlan.Vlan',
        db_column='id_vlan'
    )
    network_type = models.ForeignKey(
        'vlan.TipoRede',
        null=True,
        db_column='id_tipo_rede'
    )
    ambient_vip = models.ForeignKey(
        'ambiente.EnvironmentVip',
        null=True,
        db_column='id_ambientevip'
    )
    cluster_unit = models.CharField(
        max_length=45,
        null=True,
        db_column='cluster_unit'
    )
    active = models.BooleanField()

    log = logging.getLogger('NetworkIPv4')

    class Meta(BaseModel.Meta):
        db_table = u'redeipv4'
        managed = True

    def __str__(self):
        return self.networkv4

    def _get_networkv4(self):
        """Returns formated ip."""
        return '{}/{}'.format(self.formated_octs, self.block)

    networkv4 = property(_get_networkv4)

    def _get_formated_octs(self):
        """Returns formated octs."""
        return '{}.{}.{}.{}'.format(self.oct1, self.oct2, self.oct3, self.oct4)

    formated_octs = property(_get_formated_octs)

    def _get_mask_formated(self):
        """Returns formated mask."""
        return '{}.{}.{}.{}'.format(self.mask_oct1, self.mask_oct2,
                                    self.mask_oct3, self.mask_oct4)

    mask_formated = property(_get_mask_formated)

    def _get_wildcard(self):
        return '%d.%d.%d.%d' % (255 - self.mask_oct1, 255 - self.mask_oct2,
                                255 - self.mask_oct3, 255 - self.mask_oct4)

    wildcard = property(_get_wildcard)

    def _get_dhcprelay(self):
        dhcprelay = self.dhcprelayipv4_set.all()
        return dhcprelay

    dhcprelay = property(_get_dhcprelay)

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
            raise ObjectDoesNotExistException(
                u'There is no NetworkIPv4 with pk = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the NetworkIPv4.')
            raise NetworkIPv4Error(e, u'Failure to search the NetworkIPv4.')

    def activate(self, authenticated_user):

        try:
            self.active = 1
            self.save()

            net_slz = get_app('api_network', 'serializers.v3')
            serializer = net_slz.NetworkIPv4V3Serializer(
                self,
                include=('vlan__details__environment__basic',))

            data_to_queue = serializer.data
            data_to_queue.update({
                'description': queue_keys.NETWORKv4_ACTIVATE
            })

            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            queue_manager.append({
                'action': queue_keys.NETWORKv4_ACTIVATE,
                'kind': queue_keys.NETWORKv4_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

        except Exception, e:
            self.log.error(u'Error activating NetworkIPv4.')
            raise NetworkIPv4Error(e, u'Error activating NetworkIPv4.')

    def deactivate(self, authenticated_user, commit=False):
        """
            Update status column  to 'active = 0'
            @param authenticated_user: User authenticate
            @raise NetworkIPv4Error: Error disabling a NetworkIPv4.
        """

        from networkapi.api_network.serializers.v1 import NetworkIPv4Serializer

        try:

            self.active = 0
            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            serializer = NetworkIPv4Serializer(self)
            data_to_queue = serializer.data
            data_to_queue.update({
                'description': queue_keys.NETWORKv4_DEACTIVATE})
            queue_manager.append({
                'action': queue_keys.NETWORKv4_DEACTIVATE,
                'kind': queue_keys.NETWORKv4_KEY,
                'data': data_to_queue})
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
        configenvironment = get_model('ambiente', 'ConfigEnvironment')
        vlan_model = get_model('vlan', 'Vlan')
        self.vlan = vlan_model().get_by_pk(id_vlan)

        network_found = None
        stop = False
        internal_network_type = None
        type_ipv4 = IP_VERSION.IPv4[0]

        try:

            # Find all configs type v4 in environment
            configs = configenvironment.get_by_environment(
                self.vlan.ambiente.id).filter(ip_config__type=IP_VERSION.IPv4[0])

            # If not found, an exception is thrown
            if len(configs) == 0:
                raise ConfigEnvironmentInvalidError(
                    None, u'Invalid Configuration')

            # Needs to lock IPv4 listing when there are any allocation in progress
            # If not, it will allocate two networks with same range
            with distributedlock(LOCK_ENVIRONMENT % self.vlan.ambiente.id):
                # Find all networks ralated to environment
                nets = NetworkIPv4.objects.filter(
                    vlan__ambiente__id=self.vlan.ambiente.id)

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

                        self.log.info(
                            u'Prefix that will be used: %s' % new_prefix)
                        # For each subnet generated with configs
                        for subnet in net4.iter_subnets(new_prefix=new_prefix):

                            net_found = True
                            for netv4 in networksv4:
                                if subnet in netv4:
                                    net_found = False

                            # Checks if the network generated is UNUSED
                            if net_found:

                                # Checks if it is subnet/supernet of any
                                # existing network
                                in_range = network_in_range(
                                    self.vlan, subnet, type_ipv4)
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
                self.oct1, self.oct2, self.oct3, self.oct4 = str(
                    network_found.network).split('.')
                # Set block by network generated
                self.block = network_found.prefixlen
                # Set mask by network generated
                self.mask_oct1, self.mask_oct2, self.mask_oct3, self.mask_oct4 = str(
                    network_found.netmask).split('.')
                # Set broadcast by network generated
                self.broadcast = network_found.broadcast

                try:
                    self.network_type = internal_network_type
                    self.ambient_vip = evip
                    self.save()
                    transaction.commit()
                except Exception, e:
                    self.log.error(u'Error persisting a NetworkIPv4.')
                    raise NetworkIPv4Error(
                        e, u'Error persisting a NetworkIPv4.')

        except (ValueError, TypeError, AddressValueError), e:
            raise ConfigEnvironmentInvalidError(e, u'Invalid Configuration')
        except NetworkAPIException as e:
            return self.response_error(150, e)

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
        vlan_map['vxlan'] = self.vlan.ambiente.vxlan

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
                cause, 'Esta Rede possui um Vip apontando para ela, e não pode ser excluída')

    ##################
    # Methods for V3 #
    ##################
    def create_v3(self, networkv4, locks_used=[], force=False):
        """Create new networkIPv4."""

        vlan_model = get_app('vlan')
        envvip_model = get_app('ambiente')

        try:
            self.oct1 = networkv4.get('oct1')
            self.oct2 = networkv4.get('oct2')
            self.oct3 = networkv4.get('oct3')
            self.oct4 = networkv4.get('oct4')
            self.block = networkv4.get('prefix')
            self.mask_oct1 = networkv4.get('mask_oct1')
            self.mask_oct2 = networkv4.get('mask_oct2')
            self.mask_oct3 = networkv4.get('mask_oct3')
            self.mask_oct4 = networkv4.get('mask_oct4')
            self.cluster_unit = networkv4.get('cluster_unit')

            if force:
                self.active = networkv4.get('active', False)

            # Vlan
            self.vlan = vlan_model.Vlan().get_by_pk(networkv4.get('vlan'))

            # Network Type
            if networkv4.get('network_type'):
                self.network_type = vlan_model.TipoRede()\
                    .get_by_pk(networkv4.get('network_type'))

            # Environment vip
            if networkv4.get('environmentvip'):
                self.ambient_vip = envvip_model.EnvironmentVip().get_by_pk(
                    networkv4.get('environmentvip'))

            # Get environments related
            envs = self.vlan.get_environment_related(use_vrf=True)\
                .values_list('id', flat=True)

        except vlan_model.VlanNotFoundError, e:
            self.log.error(e.message)
            raise InvalidInputException(e.message)

        except vlan_model.NetworkTypeNotFoundError, e:
            self.log.error(e.message)
            raise InvalidInputException(e.message)

        except envvip_model.EnvironmentVipNotFoundError, e:
            self.log.error(e.message)
            raise InvalidInputException(e.message)

        except NetworkIPv4ErrorV3, e:
            self.log.error(e.message)
            raise NetworkIPv4ErrorV3(e.message)

        except Exception, e:
            self.log.error(e)
            raise NetworkIPv4ErrorV3(e)

        else:
            # Create locks for environment
            locks_name = list()
            for env in envs:
                lock_name = LOCK_ENVIRONMENT_ALLOCATES % env
                if lock_name not in locks_used:
                    locks_name.append(lock_name)

            locks_list = create_lock_with_blocking(locks_name)

        try:
            if self.oct1 is None and self.oct2 is None and \
                    self.oct3 is None and self.oct4 is None:
                # Allocate network for vlan with prefix(optional)
                try:
                    self.allocate_network_v3(networkv4.get('vlan'),
                                             networkv4.get('prefix'))
                except NetworkIPv4AddressNotAvailableError, e:
                    self.log.error(e.message)
                    raise NetworkIPv4ErrorV3(e.message)

            elif self.block is not None and self.oct1 is not None and \
                self.oct2 is not None and self.oct3 is not None and \
                    self.oct4 is not None:

                # Was send prefix and octs
                # IP address manually configured
                ip = IPNetwork('%s/%s' % (self.formated_octs, self.block))
                self.broadcast = ip.broadcast.compressed
                mask = ip.netmask.exploded.split('.')
                self.mask_oct1 = mask[0]
                self.mask_oct2 = mask[1]
                self.mask_oct3 = mask[2]
                self.mask_oct4 = mask[3]

                envs = self.vlan.get_environment_related(use_vrf=True)
                net_ip = [IPNetwork(self.networkv4)]
                try:
                    network.validate_network(envs, net_ip, IP_VERSION.IPv4[0])
                except NetworkConflictException, e:
                    self.log.error(e.detail)
                    raise NetworkIPv4ErrorV3(e.detail)

            else:
                # Was not send correctly
                raise NetworkIPv4ErrorV3(
                    'There is need to send block ou mask.')

            try:
                self.validate_v3()
            except vlan_model.VlanErrorV3, e:
                self.log.error(e.message)
                raise NetworkIPv4ErrorV3(e.message)

            self.save()

            if self.block < 31:

                # Creates Ips for routers of environment
                eqpt_model = get_model('equipamento', 'EquipamentoAmbiente')
                eqpts = eqpt_model.get_routers_by_environment(self.vlan.ambiente)\
                    .values_list('equipamento', flat=True)

                if eqpts:
                    ip = Ip.get_first_available_ip(self.id)
                    gateway_ip = str(ip).split('.')

                    ip_map = {
                        'oct1': gateway_ip[0],
                        'oct2': gateway_ip[1],
                        'oct3': gateway_ip[2],
                        'oct4': gateway_ip[3],
                        'networkipv4': self.id,
                        'equipments': [{
                            'id': eqpt
                        } for eqpt in eqpts]
                    }
                    locks = locks_name + locks_used
                    ip_inst = Ip()
                    ip_inst.create_v3(ip_map, locks_used=locks)

                    if len(eqpts) > 1 and self.block < 30:

                        for eqpt in eqpts:

                            ip = Ip.get_first_available_ip(
                                self.id, topdown=True)
                            router_ip = str(ip).split('.')

                            ip_map = {
                                'oct1': router_ip[0],
                                'oct2': router_ip[1],
                                'oct3': router_ip[2],
                                'oct4': router_ip[3],
                                'networkipv4': self.id,
                                'equipments': [{
                                    'id': eqpt
                                }]
                            }
                            locks = locks_name + locks_used
                            ip_inst = Ip()
                            ip_inst.create_v3(ip_map, locks_used=locks)

        except NetworkIPv4ErrorV3, e:
            self.log.error(e.message)
            raise NetworkIPv4ErrorV3(e.message)

        except Exception, e:
            self.log.exception(e)
            raise NetworkIPv4ErrorV3(e)

        finally:
            destroy_lock(locks_list)

    def update_v3(self, networkv4, locks_used=[], force=False):
        """Update networkIPv4."""

        vlan_model = get_app('vlan')
        envvip_model = get_app('ambiente')

        try:
            self.cluster_unit = networkv4.get('cluster_unit')

            self.network_type = vlan_model.TipoRede()\
                .get_by_pk(networkv4.get('network_type'))

            if force:
                self.active = networkv4.get('active', False)

            # has environmentvip
            if networkv4.get('environmentvip'):
                self.ambient_vip = envvip_model.EnvironmentVip()\
                    .get_by_pk(networkv4.get('environmentvip'))
            else:
                self.ambient_vip = None

        except vlan_model.NetworkTypeNotFoundError, e:
            self.log.error(e.message)
            raise InvalidInputException(e.message)

        except envvip_model.EnvironmentVipNotFoundError, e:
            self.log.error(e.message)
            raise InvalidInputException(e.message)

        except NetworkIPv4ErrorV3, e:
            self.log.error(e.message)
            raise NetworkIPv4ErrorV3(e.message)

        except Exception, e:
            self.log.error(e)
            raise NetworkIPv4ErrorV3(e)

        else:

            # Create locks for environment
            locks_name = list()
            lock_name = LOCK_NETWORK_IPV4 % self.id
            if lock_name not in locks_used:
                locks_name.append(lock_name)

            locks_list = create_lock_with_blocking(locks_name)

        try:
            self.validate_v3()
            self.save()

        except vlan_model.VlanErrorV3, e:
            self.log.error(e.message)
            raise NetworkIPv4ErrorV3(e.message)

        except NetworkIPv4ErrorV3, e:
            self.log.error(e.message)
            raise NetworkIPv4ErrorV3(e.message)

        except Exception, e:
            self.log.error(e)
            raise NetworkIPv4ErrorV3(e)

        finally:
            destroy_lock(locks_list)

    def delete_v3(self, locks_used=[], force=False):
        """Method V3 to remove NetworkIPv4.

        Before removing the NetworkIPv4 removes all your Ipv4
        """

        # Get environments related
        envs = self.vlan.get_environment_related(use_vrf=True)\
            .values_list('id', flat=True)

        locks_name = list()

        # Prepares lock for object current network
        lock_name = LOCK_NETWORK_IPV4 % self.id
        if lock_name not in locks_used:
            locks_name.append(lock_name)

        # Prepares lock for environment related
        for env in envs:
            lock_name = LOCK_ENVIRONMENT_ALLOCATES % env
            if lock_name not in locks_used:
                locks_name.append(lock_name)

        # Create locks for environment and vlan
        locks_list = create_lock_with_blocking(locks_name)

        try:

            if self.active and not force:
                msg = 'Can\'t remove network {} because it is active. ' \
                    'Try to set it inactive before removing it.'.format(
                        str(self))
                raise NetworkActiveError(None, msg)

            for ip in self.ip_set.all():
                ip.delete_v3()

            super(NetworkIPv4, self).delete()

        except IpCantBeRemovedFromVip, e:
            msg = 'This network has a VIP pointing to it, and can not '\
                'be deleted. Network: {}, Vip Request: {}'.format(
                    str(self), e.cause)

            self.log.error(msg)
            raise NetworkIPv4ErrorV3(msg)

        except NetworkActiveError, e:
            self.log.error(e.message)
            raise NetworkIPv4ErrorV3(e.message)

        except NetworkIPv4ErrorV3, e:
            self.log.error(e.message)
            raise NetworkIPv4ErrorV3(e.message)

        except Exception, e:
            self.log.error(e)
            raise NetworkIPv4ErrorV3(e)

        finally:
            destroy_lock(locks_list)

    def validate_v3(self):
        """Validate networkIPv4."""

        if not self.network_type:
            raise NetworkIPv4ErrorV3('Network type can not null')

        # validate if network if allow in environment
        configs = self.vlan.ambiente.configs.all()
        self.vlan.allow_networks_environment(configs, [self], [])

    def activate_v3(self):
        """
            Send activate notication of network v4 for queue of ACL
                configuration system.
            Update status column  to 'active = 1'.

            @raise NetworkIPv4Error: Error activating a NetworkIPv4.
        """

        try:
            self.active = 1
            self.save()

            net_slz = get_app('api_network', 'serializers.v3')
            serializer = net_slz.NetworkIPv4V3Serializer(
                self,
                include=('vlan__details__environment__basic',))

            data_to_queue = serializer.data
            data_to_queue.update({
                'description': queue_keys.NETWORKv4_ACTIVATE
            })

            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            queue_manager.append({
                'action': queue_keys.NETWORKv4_ACTIVATE,
                'kind': queue_keys.NETWORKv4_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

        except Exception, e:
            self.log.error(u'Error activating NetworkIPv4.')
            raise NetworkIPv4Error(e, u'Error activating NetworkIPv4.')

    def deactivate_v3(self):
        """
            Send deactivate notication of network v4 for queue of ACL
                configuration system.
            Update status column  to 'active = 0'.

            @raise NetworkIPv4Error: Error disabling a NetworkIPv4.
        """

        try:

            net_slz = get_app('api_network', 'serializers.v3')
            self.active = 0

            serializer = net_slz.NetworkIPv4V3Serializer(
                self,
                include=('vlan__details__environment__basic',))

            data_to_queue = serializer.data
            data_to_queue.update({
                'description': queue_keys.NETWORKv4_DEACTIVATE
            })

            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            queue_manager.append({
                'action': queue_keys.NETWORKv4_DEACTIVATE,
                'kind': queue_keys.NETWORKv4_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

            self.save()

        except Exception, e:
            self.log.error(u'Error disabling NetworkIPv4.')
            raise NetworkIPv4Error(e, u'Error disabling NetworkIPv4.')

    def allocate_network_v3(self, id_vlan, prefix=None):
        """
            Allocate new NetworkIPv4.
            @raise VlanNotFoundError: Vlan is not registered.
            @raise VlanError: Failed to search for the Vlan
            @raise ConfigEnvironmentInvalidError: Invalid Environment
                                                  Configuration or not
                                                  registered
            @raise NetworkIPv4Error: Error persisting a NetworkIPv4.
            @raise NetworkIPv4AddressNotAvailableError: Unavailable address to
                                                        create a NetworkIPv4.
            @raise Invalid: Unavailable address to create a NetworkIPv4.
            @raise InvalidValueError: Network type does not exist.
        """

        vlan_model = get_model('vlan', 'Vlan')
        self.vlan = vlan_model().get_by_pk(id_vlan)

        nets_envs, netv6 = network.get_networks_related(
            vrfs=self.vlan.get_vrf(),
            eqpts=self.vlan.get_eqpt(),
            has_netv6=False
        )
        nets_envs = [IPNetwork(net.networkv4) for net in nets_envs]
        network_found = None

        try:

            configs = self.vlan.ambiente.configs.filter(
                ip_config__type=IP_VERSION.IPv4[0])

            # For each configuration founded in environment
            for config in configs:

                net4 = IPNetwork(config.ip_config.subnet)

                if prefix is not None:
                    new_prefix = int(prefix)
                else:
                    new_prefix = int(config.ip_config.new_prefix)

                self.log.info(
                    u'Prefix that will be used: %s' % new_prefix)

                free_nets = network.get_free_space_network([net4], nets_envs)

                for free_net in free_nets:
                    try:
                        subnets = free_net.iter_subnets(new_prefix=new_prefix)
                        subnet = subnets.next()
                    except Exception:
                        pass
                    else:
                        # Set octs by network generated
                        self.oct1, self.oct2, self.oct3, self.oct4 = str(
                            subnet.network).split('.')
                        # Set block by network generated
                        self.block = subnet.prefixlen

                        self.broadcast = subnet.broadcast.compressed
                        mask = subnet.netmask.exploded.split('.')
                        self.mask_oct1 = mask[0]
                        self.mask_oct2 = mask[1]
                        self.mask_oct3 = mask[2]
                        self.mask_oct4 = mask[3]

                        if not self.network_type:
                            self.network_type = config.ip_config.network_type

                        return

            # Checks if found any available network
            if network_found is None:
                self.log.error(u'Unavailable address to create a NetworkIPv4.')
                # If not found, an exception is thrown
                raise NetworkIPv4AddressNotAvailableError(
                    None, u'Unavailable address to create a NetworkIPv4.')

        except (ValueError, TypeError, AddressValueError), e:
            self.log.error(u'Invalid Configuration')
            raise ConfigEnvironmentInvalidError(e, u'Invalid Configuration')


class Ip(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id_ip'
    )
    oct4 = models.IntegerField()
    oct3 = models.IntegerField()
    oct2 = models.IntegerField()
    oct1 = models.IntegerField()
    descricao = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    networkipv4 = models.ForeignKey(
        'ip.NetworkIPv4',
        db_column='id_redeipv4'
    )

    log = logging.getLogger('Ip')

    class Meta(BaseModel.Meta):
        db_table = u'ips'
        managed = True
        unique_together = ('oct1', 'oct2', 'oct3', 'oct4', 'networkipv4')

    def __str__(self):
        return self.ip_formated

    def _get_formated_ip(self):
        """Returns formated ip."""
        return '%s.%s.%s.%s' % (self.oct1, self.oct2, self.oct3, self.oct4)

    ip_formated = property(_get_formated_ip)

    def _get_equipments(self):
        """Returns equipments list."""
        ipeqs = self.ipequipamento_set.all().select_related('equipamento')
        eqpts = [ipeq.equipamento for ipeq in ipeqs]
        return eqpts

    equipments = property(_get_equipments)

    def _get_ipv4_equipment(self):

        return self.ipequipamento_set.all()

    ipv4_equipment = \
        property(_get_ipv4_equipment)

    def _get_vips(self):
        """Returns vips list."""
        vips = self.viprequest_set.all()
        return vips

    vips = property(_get_vips)

    def _get_server_pool_members(self):
        """Returns pool members list."""
        server_pool_members = self.serverpoolmember_set.all()
        return server_pool_members

    server_pool_members = property(_get_server_pool_members)

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
            return Ip.objects.filter(
                networkipv4__vlan__ambiente__id=id_ambiente,
                ipequipamento__equipamento__id=id_equipment)
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

        configuration = get_model('config', 'Configuration')
        networkipv4 = NetworkIPv4().get_by_pk(id_network)

        # Cast to API
        net4 = IPv4Network(networkipv4.networkv4)

        # Find all ips ralated to network
        ips = Ip.objects.filter(networkipv4__id=networkipv4.id)

        # Cast all to API class
        ipsv4 = set([IPv4Address(ip.ip_formated) for ip in ips])

        # Get configuration
        conf = configuration.get()

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
        net4 = IPv4Network(networkipv4.networkv4)

        # Find all ips ralated to network
        ips = Ip.objects.filter(networkipv4__id=networkipv4.id)

        # Cast all to API class
        ipsv4 = set([IPv4Address(ip.ip_formated) for ip in ips])

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

        equipamentoambiente = get_model('equipamento', 'EquipamentoAmbiente')
        equipamento = get_model('equipamento', 'Equipamento')
        filterequiptype = get_model('filterequiptype', 'FilterEquipType')
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
                equipment = equipamento().get_by_pk(equipment_id)
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
                            for fet in filterequiptype.objects.filter(filter=self.networkipv4.vlan.ambiente.filter.id):
                                tp_equip_list_one.append(fet.equiptype)

                            tp_equip_list_two = list()
                            for fet in filterequiptype.objects.filter(filter=ip_test.networkipv4.vlan.ambiente.filter.id):
                                tp_equip_list_two.append(fet.equiptype)

                            if equipment.tipo_equipamento not in tp_equip_list_one or equipment.tipo_equipamento not in tp_equip_list_two:
                                raise IpRangeAlreadyAssociation(
                                    None, u'Equipment is already associated with another ip with the same ip range.')

                # # Filter case 2 - end ##

                ip_equipment.save()

                # Makes Environment Equipment association
                try:
                    equipment_environment = equipamentoambiente()
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
        equipamentoambiente = get_model('equipamento', 'EquipamentoAmbiente')
        equipamento = get_model('equipamento', 'Equipamento')
        configuration = get_model('config', 'Configuration')
        vlan_model = get_model('vlan', 'Vlan')
        if new is False:
            # Search vlan by id
            vlan = vlan_model().get_by_pk(id)

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
                                               self.networkipv4.oct3, self.networkipv4.oct4,
                                               self.networkipv4.block))

        # Find all ips ralated to network
        ips = Ip.objects.filter(networkipv4__id=self.networkipv4.id)

        # Cast all to API class
        ipsv4 = set(
            [(IPv4Address('%d.%d.%d.%d' % (ip.oct1, ip.oct2, ip.oct3, ip.oct4))) for ip in ips])

        # Get configuration
        conf = configuration.get()

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

        equipment = equipamento().get_by_pk(equipment_id)

        try:
            self.save()

            ip_equipment = IpEquipamento()
            ip_equipment.ip = self
            ip_equipment.equipamento = equipment

            ip_equipment.save(authenticated_user)

            try:
                equipment_environment = equipamentoambiente()\
                    .get_by_equipment_environment(
                    equipment_id,
                    self.networkipv4.vlan.ambiente_id
                )
            except EquipamentoAmbienteNotFoundError:
                equipment_environment = equipamentoambiente()
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
        environmentvip = get_model('ambiente', 'EnvironmentVip')
        ambiente_model = get_model('ambiente', 'Ambiente')
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
                        environments = ambiente_model.objects.filter(
                            vlan__networkipv4__ambient_vip__id=id_evip)
                        for env in environments:
                            if ip.networkipv4.vlan.ambiente.divisao_dc.id == env.divisao_dc.id \
                                    and ip.networkipv4.vlan.ambiente.ambiente_logico.id == env.ambiente_logico.id:
                                return ip
                raise ObjectDoesNotExist()
        except ObjectDoesNotExist, e:
            evip = environmentvip.get_by_pk(id_evip)
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
        """Sobrescreve o método do Django para remover um IP.
        Antes de remover o IP remove todas as suas requisições de VIP e os relacionamentos com equipamentos.
        """
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
                            r.id, 'Ipv4 não pode ser removido, porque está em uso por Requisição Vip %s' % (r.id))
                    else:
                        if r.ipv6 is not None:
                            r.ip = None
                            r.validado = 0
                            r.save()
                            r_alter = True

                            # SYNC_VIP
                            syncs.old_to_new(r)
                    if not r_alter:
                        r.delete()

                        # SYNC_VIP
                        syncs.delete_new(id_vip)

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

            ip_slz = get_app('api_ip', module_label='serializers')
            serializer = ip_slz.Ipv4V3Serializer(self)
            data_to_queue = serializer.data

            # Deletes Obj IP
            super(Ip, self).delete()

            # Sends to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            data_to_queue.update({'description': queue_keys.IPv4_REMOVE})
            queue_manager.append({
                'action': queue_keys.IPv4_REMOVE,
                'kind': queue_keys.IPv4_KEY,
                'data': data_to_queue
            })

        except EquipamentoAmbienteNotFoundError, e:
            raise EquipamentoAmbienteNotFoundError(None, e.message)
        except IpCantBeRemovedFromVip, e:
            raise IpCantBeRemovedFromVip(e.cause, e.message)
        except IpEquipmentNotFoundError, e:
            raise IpEquipmentNotFoundError(None, e.message)

    ##################
    # Methods for V3 #
    ##################
    def create_v3(self, ip_map, locks_used=[]):
        """Method V3 to create Ip."""

        models = get_app('equipamento', 'models')

        try:

            self.networkipv4 = NetworkIPv4()\
                .get_by_pk(ip_map.get('networkipv4'))
            self.oct1 = ip_map.get('oct1')
            self.oct2 = ip_map.get('oct2')
            self.oct3 = ip_map.get('oct3')
            self.oct4 = ip_map.get('oct4')
            self.descricao = ip_map.get('description')

            # Get environments related
            envs = self.networkipv4.vlan\
                .get_environment_related(use_vrf=True)\
                .values_list('id', flat=True)

            # Get objects of equipments
            eqpts = models.Equipamento.objects.filter(
                id__in=[eqpt.get('id')
                        for eqpt in ip_map.get('equipments', [])])
        except Exception, e:
            raise IpErrorV3(e)

        else:

            locks_name = list()

            # Prepare locks for environment
            for env in envs:
                lock_name = LOCK_ENVIRONMENT_ALLOCATES % env
                if lock_name not in locks_used:
                    locks_name.append(lock_name)

            for eqpt_obj in eqpts:
                # Prepare locks for ips-equipments
                lock_name = LOCK_IP_EQUIPMENT_ONE % eqpt_obj.id
                if lock_name not in locks_used:
                    locks_name.append(lock_name)

                # Prepare locks for environments related with equipaments
                for env in eqpt_obj.environments:
                    lock_name = LOCK_ENVIRONMENT_ALLOCATES % env.ambiente_id
                    if lock_name not in locks_used:
                        locks_name.append(lock_name)

            # Create Locks
            locks_name = list(set(locks_name))
            locks_list = create_lock_with_blocking(locks_name)

        try:

            if self.oct1 is None and self.oct2 is None and \
                    self.oct3 is None and self.oct4 is None:
                self.allocate_v3()
            else:
                net4 = IPv4Network(self.networkipv4.networkv4)

                # Find all ips ralated to network
                ips = Ip.objects.filter(networkipv4=self.networkipv4)

                ip4_object = IPv4Address(self.ip_formated)

                # Cast all to API class
                ipsv4 = set([IPv4Address(ip.ip_formated) for ip in ips])

                flag = False

                if ip4_object not in ipsv4:

                    if ip4_object in net4:

                        first_ip_network = int(net4.network)
                        bcast_ip_network = int(net4.broadcast)

                        ipv4_network = int(ip4_object)

                        # First and last ip are reserved in network
                        if first_ip_network <= ipv4_network < bcast_ip_network:
                            flag = True

                if flag is False:
                    raise IpNotAvailableError(
                        None,
                        u'Ip %s not available for network %s.' %
                        (self.ip_formated, self.networkipv4.id))

                self.validate_v3(eqpts)

            self.save()

            # Creates relationship between ip and equipment #
            for eqpt in ip_map.get('equipments', []):
                ip_equipment = IpEquipamento()
                ip_equipment.create_v3({
                    'ip': self.id,
                    'equipment': eqpt.get('id')
                })

        except IpErrorV3, e:
            self.log.error(e.message)
            raise IpErrorV3(e.message)

        except IpNotAvailableError, e:
            self.log.error(e.message)
            raise IpErrorV3(e.message)

        except Exception, e:
            msg = u'Error save new IP.: %s' % e
            self.log.exception(msg)
            raise IpErrorV3(msg)

        finally:
            # Destroy locks
            destroy_lock(locks_list)

    def update_v3(self, ip_map, locks_used=[]):
        """Method V3 to update Ip."""

        models = get_app('equipamento', 'models')

        try:
            self.descricao = ip_map.get('description')

            # Get environments related
            envs = self.networkipv4.vlan.get_environment_related(use_vrf=True)\
                .values_list('id', flat=True)

            # Get objects of equipments
            eqpts = models.Equipamento.objects.filter(id__in=[
                eqpt.get('id') for eqpt in ip_map.get('equipments', [])]
            )
        except Exception, e:
            raise IpErrorV3(e)

        else:

            locks_name = list()

            # Prepare lock for ip
            lock_name = LOCK_IPV4 % self.id
            if lock_name not in locks_used:
                locks_name.append(lock_name)

            # Prepare locks for environment
            for env in envs:
                lock_name = LOCK_ENVIRONMENT_ALLOCATES % env
                if lock_name not in locks_used:
                    locks_name.append(lock_name)

            for eqpt_obj in eqpts:
                # Prepare locks for ips-equipments
                lock_name = LOCK_IP_EQUIPMENT % (self.id, eqpt_obj.id)
                if lock_name not in locks_used:
                    locks_name.append(lock_name)

                # Prepare locks for environments related with equipaments
                for env in eqpt_obj.environments:
                    lock_name = LOCK_ENVIRONMENT_ALLOCATES % env.ambiente_id
                    if lock_name not in locks_used:
                        locks_name.append(lock_name)

            # Create Locks
            locks_name = list(set(locks_name))
            locks_list = create_lock_with_blocking(locks_name)
        try:

            self.validate_v3(eqpts)

            self.save()

            # Get current associates
            current = self.ipequipamento_set\
                .filter(equipamento__in=eqpts)\
                .values_list('equipamento', flat=True)

            # Creates new associate
            for eqpt in eqpts:
                if eqpt.id not in current:
                    ip_equipment = IpEquipamento()
                    ip_equipment.create_v3({
                        'ip': self.id,
                        'equipment': eqpt.id
                    })

            # Removes old associates
            for ip_eqpt in self.ipequipamento_set\
                    .exclude(equipamento__in=eqpts):
                ip_eqpt.delete_v3(bypass_ip=True)

        except IpErrorV3, e:
            self.log.error(e.message)
            raise IpErrorV3(e.message)

        except Exception, e:
            msg = u'Error edit IP.: %s' % e
            self.log.error(msg)
            raise IpErrorV3(msg)

        finally:
            # Destroy locks
            destroy_lock(locks_list)

    def delete_v3(self, locks_used=[]):
        """
        Method V3 to remove Ip.
        Before removing the IP removes all your requests
        VIP and relationships with equipment.

        @raise IpCantBeRemovedFromVip: Ip is associated with created
                                       Vip Request.
        """

        locks_name = list()

        # Prepare lock for ip
        lock_name = LOCK_IPV4 % self.id
        if lock_name not in locks_used:
            locks_name.append(lock_name)

        # Create Locks
        locks_name = list(set(locks_name))
        locks_list = create_lock_with_blocking(locks_name)

        try:
            for vip in self.viprequest_set.all():
                id_vip = vip.id
                with distributedlock(LOCK_VIP % id_vip):
                    if vip.created:
                        raise IpCantBeRemovedFromVip(
                            str(vip),
                            'IPv4 can not be removed because it is '
                            'in use by Vip Request: {}'.format(str(vip)))

                    # Deletes only VIP, Related Ipv6 with VIP is not removed
                    vip.delete_v3(bypass_ipv4=True, bypass_ipv6=True)

            # Deletes Related Equipment
            for ip_eqpt in self.ipequipamento_set.all():
                ip_eqpt.delete_v3(bypass_ip=True)

            # Serializes obj
            ip_slz = get_app('api_ip', module_label='serializers')
            serializer = ip_slz.Ipv4V3Serializer(self)
            data_to_queue = serializer.data

            # Deletes Obj IP
            super(Ip, self).delete()

            # Sends to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            data_to_queue.update({'description': queue_keys.IPv4_REMOVE})
            queue_manager.append({
                'action': queue_keys.IPv4_REMOVE,
                'kind': queue_keys.IPv4_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

        except IpCantBeRemovedFromVip, e:
            raise IpCantBeRemovedFromVip(e.cause, e.message)

        except Exception, e:
            msg = u'Error delete IP.: %s' % e
            self.log.error(msg)
            raise IpErrorV3(msg)

        finally:
            # Destroy locks
            destroy_lock(locks_list)

    def validate_v3(self, equipments):
        """Validate Ip."""

        env_ip = self.networkipv4.vlan.ambiente
        network.validate_conflict_join_envs(env_ip, equipments)

    def allocate_v3(self):
        """Persist an IPv4 and associate it to an equipment.
            If equipment was not related with VLAN environment, this makes the relationship
            @return: Nothing
            @raise NetworkIPv4NotFoundError: NetworkIPv4 does not exist.
            @raise NetworkIPv4Error: Error finding NetworkIPv4.
            @raise EquipamentoNotFoundError: Equipment does not exist.
            @raise EquipamentoError: Error finding Equipment.
            @raise IpNotAvailableError: No IP available to VLAN.
            @raise IpError: Error persisting in database.
        """
        configuration = get_model('config', 'Configuration')
        # Cast to API
        net4 = IPNetwork(self.networkipv4.networkv4)

        # Find all ips ralated to network
        ips = self.networkipv4.ip_set.all()

        # Cast all to API class
        ipsv4 = set([IPv4Address(ip.ip_formated) for ip in ips])

        # Get configuration
        conf = configuration.get()

        selected_ip = None

        # For each ip generated
        i = 0
        for ip in net4.iterhosts():

            # Do not use some range of IPs (config)
            # IPv4_MIN = Firsts
            # IPv4_MAX = Number minimum of Ip reserveds
            # First IP and 2 last I
            i = i + 1
            if i >= conf.IPv4_MIN and i < (net4.numhosts - conf.IPv4_MAX):

                # If IP generated was not used
                if ip not in ipsv4:

                    # Use it
                    selected_ip = ip

                    # Stop generation
                    break

        if selected_ip is None:
            raise IpNotAvailableError(None, u'No IP available to VLAN %s.' %
                                            self.networkipv4.vlan.num_vlan)

        self.oct1, self.oct2, self.oct3, self.oct4 = str(
            selected_ip).split('.')


class IpEquipamento(BaseModel):
    id = models.AutoField(
        primary_key=True,
        db_column='id_ips_dos_equipamentos'
    )
    ip = models.ForeignKey(
        'ip.Ip',
        db_column='id_ip'
    )
    equipamento = models.ForeignKey(
        'equipamento.Equipamento',
        db_column='id_equip'
    )

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
        """Insere um relacionamento entre IP e Equipamento.
        @return: Nothing.
        @raise IpError: Falha ao inserir.
        @raise EquipamentoNotFoundError: Equipamento não cadastrado.
        @raise IpNotFoundError: Ip não cadastrado.
        @raise IpEquipamentoDuplicatedError: IP já cadastrado para o equipamento.
        @raise EquipamentoError: Falha ao pesquisar o equipamento.
        """
        equipamentoambiente = get_model('equipamento', 'EquipamentoAmbiente')
        equipamento = get_model('equipamento', 'Equipamento')
        self.equipamento = equipamento().get_by_pk(equipment_id)
        self.ip = Ip().get_by_pk(ip_id)

        # Valida o ip
        self.__validate_ip()

        try:
            if self.equipamento not in [ea.equipamento for ea in self.ip.networkipv4.vlan.ambiente.equipamentoambiente_set.all().select_related('equipamento')]:
                ea = equipamentoambiente(
                    ambiente=self.ip.networkipv4.vlan.ambiente, equipamento=self.equipamento)
                ea.save(authenticated_user)

            self.save()
        except Exception, e:
            self.log.error(u'Falha ao inserir um ip_equipamento.')
            raise IpError(e, u'Falha ao inserir um ip_equipamento.')

    def delete(self):
        """Override Django's method to remove Ip and Equipment relationship.
        If Ip from this Ip-Equipment is associated with created Vip Request, and the Equipment
        is the last balancer associated, the IpEquipment association cannot be removed.
        If Ip has no relationship with other Equipments, then Ip is also removed.
        """
        tipoequipamento = get_model('equipamento', 'TipoEquipamento')

        for r in self.ip.requisicaovips_set.all():
            if self.equipamento.tipo_equipamento == tipoequipamento.get_tipo_balanceador():
                # Get all equipments (except the one being removed) related to ip
                # to find another balancer
                other_equips = self.ip.ipequipamento_set.exclude(
                    equipamento=self.equipamento.id)
                another_balancer = False
                for ipequip in other_equips:
                    if ipequip.equipamento.tipo_equipamento == tipoequipamento.get_tipo_balanceador():
                        another_balancer = True
                        break

                if not another_balancer:
                    if r.vip_criado:
                        raise IpEquipCantDissociateFromVip({'vip_id': r.id, 'ip': mount_ipv4_string(
                            self.ip), 'equip_name': self.equipamento.nome}, 'Ipv4 não pode ser disassociado do equipamento %s porque é o último balanceador da Requisição Vip %s.' % (self.equipamento.nome, r.id))
                    else:
                        # Remove ip from vip or remove vip
                        id_vip = r.id
                        if r.ipv6 is not None:
                            r.ip = None
                            r.validado = 0
                            r.save()

                            # SYNC_VIP
                            syncs.old_to_new(r)
                        else:
                            r.delete()

                            # SYNC_VIP
                            syncs.delete_new(id_vip)

        if self.ip.serverpoolmember_set.count() > 0:

            server_pool_identifiers = set()

            for svm in self.ip.serverpoolmember_set.all():
                item = '{}:{}'.format(svm.server_pool.id,
                                      svm.server_pool.identifier)
                server_pool_identifiers.add(item)

            server_pool_identifiers = list(server_pool_identifiers)
            server_pool_identifiers = ', '.join(
                str(server_pool) for server_pool in server_pool_identifiers)

            raise IpCantRemoveFromServerPool(
                {
                    'ip': mount_ipv4_string(self.ip),
                    'equip_name': self.equipamento.nome,
                    'server_pool_identifiers': server_pool_identifiers
                },
                'Ipv4 não pode ser disassociado do equipamento %s porque ele '
                'está sendo utilizando nos Server Pools (id:identifier) %s' %
                (self.equipamento.nome, server_pool_identifiers))

        super(IpEquipamento, self).delete()

        # If IP is not related to any other equipments, its removed
        if self.ip.ipequipamento_set.count() == 0:
            self.ip.delete()

    def remove(self, authenticated_user, ip_id, equip_id):
        """Search and remove relationship between IP and equipment.
        @return: Nothing
        @raise IpEquipmentNotFoundError: There's no relationship between Ip and Equipment.
        @raise IpCantBeRemovedFromVip: Ip is associated with created Vip Request.
        @raise IpEquipCantDissociateFromVip: Equipment is the last balanced in a created Vip Request pointing to ip.
        @raise IpError: Failed to remove the relationship.
        """
        ip_equipamento = self.get_by_ip_equipment(ip_id, equip_id)

        try:
            ip_equipamento.delete()

        except (IpCantBeRemovedFromVip, IpEquipCantDissociateFromVip), e:
            raise e
        except Exception, e:
            self.log.error(u'Falha ao remover um ip_equipamento.')
            raise IpError(e, u'Falha ao remover um ip_equipamento.')

    ##################
    # Methods for V3 #
    ##################
    def create_v3(self, ip_equipment):
        """Inserts a relationship between IP e Equipment.
        @return: Nothing.
        @raise IpError: Failure to insert.
        @raise EquipamentoNotFoundError: Equipment do not registered.
        @raise IpNotFoundError: Ip do not registered.
        @raise IpEquipamentoDuplicatedError: IP already registered for the equipment.
        @raise EquipamentoError: Failure to search equipment.
        """
        equipamentoambiente = get_model('equipamento', 'EquipamentoAmbiente')
        equipamento = get_model('equipamento', 'Equipamento')

        self.equipamento = equipamento().get_by_pk(ip_equipment.get('equipment'))
        self.ip = Ip().get_by_pk(ip_equipment.get('ip'))

        # Validate the ip
        self.__validate_ip()

        try:

            try:
                equipment_environment = equipamentoambiente()
                equipment_environment.create_v3({
                    'equipment': self.equipamento_id,
                    'environment': self.ip.networkipv4.vlan.ambiente_id
                })
            except EquipamentoAmbienteDuplicatedError, e:
                # If already exists, OK !
                pass

            self.save()
        except Exception, e:
            self.log.error(u'Failure to insert an ip_equipamento.')
            raise IpError(e, u'Failure to insert an ip_equipamento.')

    def delete_v3(self, bypass_ip=False):
        """
        Method V3 to remove Ip and Equipment relationship.
        If Ip from this Ip-Equipment is associated with created Vip Request,
            and the Equipment is the last balancer associated, the IpEquipment
            association cannot be removed.
        If Ip has no relationship with other Equipments, then Ip is also
            removed.

        @raise IpCantRemoveFromServerPool: Ip is associated with associated
                                           Pool Member.
        @raise IpEquipCantDissociateFromVip: Equipment is the last balanced
                                             in a created Vip Request
                                             pointing to ip.
        """
        tipoequipamento = get_model('equipamento', 'TipoEquipamento')

        type_eqpt = tipoequipamento.get_tipo_balanceador()

        if self.equipamento.tipo_equipamento == type_eqpt:

            for vip in self.ip.viprequest_set.all():

                # Filter equipments to find another balancer
                another_balancer = self.ip.ipequipamento_set.exclude(
                    equipamento=self.equipamento.id
                ).filter(equipamento__tipo_equipamento=type_eqpt)

                id_vip = vip.id

                if not another_balancer:
                    with distributedlock(LOCK_VIP % id_vip):
                        if vip.created:
                            raise IpEquipCantDissociateFromVip(
                                {
                                    'vip_id': id_vip,
                                    'ip': self.ip.ip_formated,
                                    'equip_name': self.equipamento.nome
                                },
                                'IPv4 can not be dissociated from the '
                                'equipment %s because it is the last '
                                'balancer of Vip Request %s.'
                                % (self.equipamento.nome, id_vip)
                            )
                        else:
                            # Remove ip from vip
                            if vip.ipv6 is not None:
                                vip.ipv4 = None
                                id_vip.save()

                                # SYNC_VIP
                                syncs.new_to_old(vip)
                            # Remove vip
                            else:
                                vip.delete_v3(bypass_ipv4=True,
                                              bypass_ipv6=True)

        if self.ip.serverpoolmember_set.count() > 0:

            items = ['{}:{}'.format(
                svm.server_pool.id,
                svm.server_pool.identifier
            ) for svm in self.ip.serverpoolmember_set.all()]

            items = ', '.join(items)

            raise IpCantRemoveFromServerPool(
                {
                    'ip': self.ip.ip_formated,
                    'equip_name': self.equipamento.nome,
                    'server_pool_identifiers': items
                },
                'IPv4 can not be dissociated from the equipment% s because it'
                'is being using in the Server Pools (id: identifier)%s' %
                (self.equipamento.nome, items)
            )

        super(IpEquipamento, self).delete()

        # If IP is not related to any other equipments, its removed
        if self.ip.ipequipamento_set.count() == 0 and not bypass_ip:
            self.ip.delete_v3()


class NetworkIPv6(BaseModel):

    id = models.AutoField(
        primary_key=True
    )
    vlan = models.ForeignKey(
        'vlan.Vlan',
        db_column='id_vlan'
    )
    network_type = models.ForeignKey(
        'vlan.TipoRede',
        null=True,
        db_column='id_tipo_rede'
    )
    ambient_vip = models.ForeignKey(
        'ambiente.EnvironmentVip',
        null=True,
        db_column='id_ambientevip'
    )
    block = models.IntegerField(
        db_column='bloco'
    )
    block1 = models.CharField(
        max_length=4,
        db_column='bloco1'
    )
    block2 = models.CharField(
        max_length=4,
        db_column='bloco2'
    )
    block3 = models.CharField(
        max_length=4,
        db_column='bloco3'
    )
    block4 = models.CharField(
        max_length=4,
        db_column='bloco4'
    )
    block5 = models.CharField(
        max_length=4,
        db_column='bloco5'
    )
    block6 = models.CharField(
        max_length=4,
        db_column='bloco6'
    )
    block7 = models.CharField(
        max_length=4,
        db_column='bloco7'
    )
    block8 = models.CharField(
        max_length=4,
        db_column='bloco8'
    )
    mask1 = models.CharField(
        max_length=4,
        db_column='mask_bloco1'
    )
    mask2 = models.CharField(
        max_length=4,
        db_column='mask_bloco2'
    )
    mask3 = models.CharField(
        max_length=4,
        db_column='mask_bloco3'
    )
    mask4 = models.CharField(
        max_length=4,
        db_column='mask_bloco4'
    )
    mask5 = models.CharField(
        max_length=4,
        db_column='mask_bloco5'
    )
    mask6 = models.CharField(
        max_length=4,
        db_column='mask_bloco6'
    )
    mask7 = models.CharField(
        max_length=4,
        db_column='mask_bloco7'
    )
    mask8 = models.CharField(
        max_length=4,
        db_column='mask_bloco8'
    )
    cluster_unit = models.CharField(
        max_length=45,
        null=True,
        db_column='cluster_unit'
    )
    active = models.BooleanField()

    log = logging.getLogger('NetworkIPv6')

    class Meta(BaseModel.Meta):
        db_table = u'redeipv6'
        managed = True

    def __str__(self):
        return self.networkv6

    def _get_formated_network(self):
        """Returns formated ip."""

        return '{}/{}'.format(self.formated_octs, self.block)

    networkv6 = property(_get_formated_network)

    def _get_formated_mask(self):
        """Returns formated mask."""

        return '{}:{}:{}:{}:{}:{}:{}:{}'.format(
            self.mask1, self.mask2, self.mask3, self.mask4,
            self.mask5, self.mask6, self.mask7, self.mask8)

    mask_formated = property(_get_formated_mask)

    def _get_formated_octs(self):
        """Returns formated octs."""

        return '{}:{}:{}:{}:{}:{}:{}:{}'.format(
            self.block1, self.block2, self.block3, self.block4,
            self.block5, self.block6, self.block7, self.block8)

    formated_octs = property(_get_formated_octs)

    @cached_property
    def dhcprelay(self):
        dhcprelay = self.dhcprelayipv6_set.all()
        return dhcprelay

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
            raise ObjectDoesNotExistException(
                u'There is no NetworkIPv6 with pk = %s.' % id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Error finding NetworkIPv6.')
            raise NetworkIPv6Error(e, u'Error finding NetworkIPv6.')

    def activate(self, authenticated_user):

        try:
            self.active = 1
            self.save()

            net_slz = get_app('api_network', 'serializers.v3')

            serializer = net_slz.NetworkIPv6V3Serializer(
                self,
                include=('vlan__details__environment__basic',))

            data_to_queue = serializer.data
            data_to_queue.update({
                'description': queue_keys.NETWORKv6_ACTIVATE
            })

            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            queue_manager.append({
                'action': queue_keys.NETWORKv6_ACTIVATE,
                'kind': queue_keys.NETWORKv6_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

        except Exception, e:
            self.log.error(u'Error activating NetworkIPv6.')
            raise NetworkIPv4Error(e, u'Error activating NetworkIPv6.')

    def deactivate(self, authenticated_user, commit=False):
        """
            Update status column  to 'active = 0'
            @param authenticated_user: User authenticate
            @raise NetworkIPv6Error: Error disabling NetworkIPv6.
        """

        try:

            self.active = 0
            self.save(authenticated_user, commit=commit)

            net_slz = get_app('api_network', 'serializers.v3')

            serializer = net_slz.NetworkIPv6V3Serializer(
                self,
                include=('vlan__details__environment__basic',))

            data_to_queue = serializer.data
            data_to_queue.update({
                'description': queue_keys.NETWORKv6_DEACTIVATE
            })

            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            queue_manager.append({
                'action': queue_keys.NETWORKv6_DEACTIVATE,
                'kind': queue_keys.NETWORKv6_KEY,
                'data': data_to_queue
            })
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
        configenvironment = get_model('ambiente', 'ConfigEnvironment')
        vlan_model = get_model('vlan', 'Vlan')
        self.vlan = vlan_model().get_by_pk(id_vlan)

        network_found = None
        stop = False
        internal_network_type = None
        type_ipv6 = IP_VERSION.IPv6[0]

        try:

            # Find all configs type v6 in environment
            configs = configenvironment.get_by_environment(
                self.vlan.ambiente.id).filter(ip_config__type=IP_VERSION.IPv6[0])

            # If not found, an exception is thrown
            if len(configs) == 0:
                raise ConfigEnvironmentInvalidError(
                    None, u'Invalid Configuration')

            # Find all networks ralated to environment
            nets = NetworkIPv6.objects.filter(
                vlan__ambiente__id=self.vlan.ambiente.id)

            # Cast to API class
            networksv6 = set([(IPv6Network(
                '%s:%s:%s:%s:%s:%s:%s:%s/%s' %
                (net_ip.block1, net_ip.block2, net_ip.block3,
                 net_ip.block4, net_ip.block5, net_ip.block6,
                 net_ip.block7, net_ip.block8, net_ip.block))) for net_ip in nets])

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

                    self.log.info(u'Prefix that will be used: %s' % new_prefix)

                    # For each subnet generated with configs
                    for subnet in net6.iter_subnets(new_prefix=new_prefix):

                        # Checks if the network generated is UNUSED
                        if subnet not in networksv6:

                            in_range = network_in_range(
                                self.vlan, subnet, type_ipv6)
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
        vlan_map['vxlan'] = self.vlan.ambiente.vxlan

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
                cause, 'Esta Rede possui um Vip apontando para ela, e não pode ser excluída')

    ##################
    # Methods for V3 #
    ##################
    def create_v3(self, networkv6, locks_used=[], force=False):
        """Create new networkIPv6."""

        vlan_model = get_app('vlan')
        envvip_model = get_app('ambiente')

        try:
            self.block1 = networkv6.get('block1')
            self.block2 = networkv6.get('block2')
            self.block3 = networkv6.get('block3')
            self.block4 = networkv6.get('block4')
            self.block5 = networkv6.get('block5')
            self.block6 = networkv6.get('block6')
            self.block7 = networkv6.get('block7')
            self.block8 = networkv6.get('block8')
            self.block = networkv6.get('prefix')
            self.mask1 = networkv6.get('mask1')
            self.mask2 = networkv6.get('mask2')
            self.mask3 = networkv6.get('mask3')
            self.mask4 = networkv6.get('mask4')
            self.mask5 = networkv6.get('mask5')
            self.mask6 = networkv6.get('mask6')
            self.mask7 = networkv6.get('mask7')
            self.mask8 = networkv6.get('mask8')

            self.cluster_unit = networkv6.get('cluster_unit')

            if force:
                self.active = networkv6.get('active', False)

            # Vlan
            self.vlan = vlan_model.Vlan().get_by_pk(networkv6.get('vlan'))

            # Type of Network
            if networkv6.get('network_type'):
                self.network_type = vlan_model.TipoRede()\
                    .get_by_pk(networkv6.get('network_type'))

            # has environmentvip
            if networkv6.get('environmentvip'):
                self.ambient_vip = envvip_model.EnvironmentVip()\
                    .get_by_pk(networkv6.get('environmentvip'))

            # Get environments related
            envs = self.vlan.get_environment_related(use_vrf=True)\
                .values_list('id', flat=True)

        except vlan_model.VlanNotFoundError, e:
            self.log.error(e.message)
            raise InvalidInputException(e.message)

        except vlan_model.NetworkTypeNotFoundError, e:
            self.log.error(e.message)
            raise InvalidInputException(e.message)

        except envvip_model.EnvironmentVipNotFoundError, e:
            self.log.error(e.message)
            raise InvalidInputException(e.message)

        except NetworkIPv6ErrorV3, e:
            self.log.error(e.message)
            raise NetworkIPv6ErrorV3(e.message)

        except Exception, e:
            self.log.error(e)
            raise NetworkIPv6ErrorV3(e)

        else:

            locks_name = list()
            for env in envs:
                lock_name = LOCK_ENVIRONMENT_ALLOCATES % env
                if lock_name not in locks_used:
                    locks_name.append(lock_name)

            locks_list = create_lock_with_blocking(locks_name)

        try:

            # Allocate network for vlan with prefix(optional)
            if not self.block1 and not self.block2 and not self.block3 and \
                not self.block4 and not self.block5 and \
                    not self.block6 and not self.block7 and not self.block8:

                try:
                    self.allocate_network_v3(networkv6.get('vlan'),
                                             networkv6.get('prefix'))
                except NetworkIPv6AddressNotAvailableError, e:
                    self.log.error(e.message)
                    raise NetworkIPv6ErrorV3(e.message)

            # Was send prefix and octs
            elif self.block and self.block1 and self.block2 and self.block3 \
                and self.block4 and self.block5 and self.block6 and \
                    self.block7 and self.block8:

                ip = IPNetwork('%s/%s' % (self.formated_octs, self.block))

                mask = ip.netmask.exploded.split(':')
                self.mask1 = mask[0]
                self.mask2 = mask[1]
                self.mask3 = mask[2]
                self.mask4 = mask[3]
                self.mask5 = mask[4]
                self.mask6 = mask[5]
                self.mask7 = mask[6]
                self.mask8 = mask[7]

                envs = self.vlan.get_environment_related()
                net_ip = [IPNetwork(self.networkv6)]
                try:
                    network.validate_network(envs, net_ip, IP_VERSION.IPv6[0])
                except NetworkConflictException, e:
                    self.log.error(e.detail)
                    raise NetworkIPv6ErrorV3(e.detail)

                try:
                    self.validate_v3()
                except vlan_model.VlanErrorV3, e:
                    self.log.error(e.message)
                    raise NetworkIPv6ErrorV3(e.message)

            else:
                # Was not send correctly
                self.log.error('There is need to send block ou mask.')
                raise NetworkIPv6ErrorV3(
                    'There is need to send block ou mask.')

            self.save()

            if self.block < 127:

                # Creates Ips for routers of environment
                eqpt_model = get_model('equipamento', 'EquipamentoAmbiente')
                eqpts = eqpt_model.get_routers_by_environment(self.vlan.ambiente)\
                    .values_list('equipamento', flat=True)

                if eqpts:
                    ip = Ipv6.get_first_available_ip6(self.id)
                    gateway_ip = str(ip).split(':')

                    ip_map = {
                        'block1': gateway_ip[0],
                        'block2': gateway_ip[1],
                        'block3': gateway_ip[2],
                        'block4': gateway_ip[3],
                        'block5': gateway_ip[4],
                        'block6': gateway_ip[5],
                        'block7': gateway_ip[6],
                        'block8': gateway_ip[7],
                        'networkipv6': self.id,
                        'equipments': [{
                            'id': eqpt
                        } for eqpt in eqpts]
                    }
                    locks = locks_name + locks_used
                    ip_inst = Ipv6()
                    ip_inst.create_v3(ip_map, locks_used=locks)

                    if len(eqpts) > 1 and self.block < 126:

                        for eqpt in eqpts:

                            ip = Ipv6.get_first_available_ip6(self.id, True)
                            router_ip = str(ip).split(':')

                            ip_map = {
                                'block1': router_ip[0],
                                'block2': router_ip[1],
                                'block3': router_ip[2],
                                'block4': router_ip[3],
                                'block5': router_ip[4],
                                'block6': router_ip[5],
                                'block7': router_ip[6],
                                'block8': router_ip[7],
                                'networkipv6': self.id,
                                'equipments': [{
                                    'id': eqpt
                                }]
                            }
                            locks = locks_name + locks_used
                            ip_inst = Ipv6()
                            ip_inst.create_v3(ip_map, locks_used=locks)

        except NetworkIPv6ErrorV3, e:
            self.log.error(e.message)
            raise NetworkIPv6ErrorV3(e.message)

        except Exception, e:
            self.log.error(e)
            raise NetworkIPv6ErrorV3(e)

        finally:
            destroy_lock(locks_list)

    def update_v3(self, networkv6, locks_used=[], force=False):
        """
        Update networkIPv6.
        """

        vlan_model = get_app('vlan')
        envvip_model = get_app('ambiente')

        try:
            self.cluster_unit = networkv6.get('cluster_unit')

            self.network_type = vlan_model.TipoRede() \
                .get_by_pk(networkv6.get('network_type'))

            if force:
                self.active = networkv6.get('active', False)

            # has environmentvip
            if networkv6.get('environmentvip'):
                self.ambient_vip = envvip_model.EnvironmentVip() \
                    .get_by_pk(networkv6.get('environmentvip'))
            else:
                self.ambient_vip = None

        except vlan_model.NetworkTypeNotFoundError, e:
            self.log.error(e.message)
            raise InvalidInputException(e.message)

        except envvip_model.EnvironmentVipNotFoundError, e:
            self.log.error(e.message)
            raise InvalidInputException(e.message)

        except NetworkIPv6ErrorV3, e:
            self.log.error(e.message)
            raise NetworkIPv6ErrorV3(e.message)

        except Exception, e:
            self.log.error(e)
            raise NetworkIPv6ErrorV3(e)

        else:

            # Create locks for environment
            locks_name = list()
            lock_name = LOCK_NETWORK_IPV6 % self.id
            if locks_name not in locks_used:
                locks_name.append(lock_name)

            locks_list = create_lock_with_blocking(locks_name)

        try:
            self.validate_v3()
            self.save()

        except vlan_model.VlanErrorV3, e:
            self.log.error(e.message)
            raise NetworkIPv6ErrorV3(e.message)

        except NetworkIPv6ErrorV3, e:
            self.log.error(e)
            raise NetworkIPv6ErrorV3(e)

        except Exception, e:
            self.log.error(e)
            raise NetworkIPv6ErrorV3(e)

        finally:
            destroy_lock(locks_list)

    def delete_v3(self, locks_used=[], force=False):
        """Method V3 to remove networkIPv6.

        Before removing the networkIPv6 removes all your Ipv4.
        """

        # Get environments related
        envs = self.vlan.get_environment_related(use_vrf=True)\
            .values_list('id', flat=True)

        locks_name = list()

        # Prepares lock for object current network
        lock_name = LOCK_NETWORK_IPV6 % self.id
        if lock_name not in locks_used:
            locks_name.append(lock_name)

        # Prepares lock for environment related
        for env in envs:
            lock_name = LOCK_ENVIRONMENT_ALLOCATES % env
            if lock_name not in locks_used:
                locks_name.append(lock_name)

        # Create locks for environment and vlan
        locks_list = create_lock_with_blocking(locks_name)

        try:
            if self.active and not force:
                msg = 'Can\'t remove network {} because it is active. ' \
                    'Try to set it inactive before removing it.'.format(
                        str(self))
                raise NetworkActiveError(None, msg)

            for ip in self.ipv6_set.all():
                ip.delete_v3()

            super(NetworkIPv6, self).delete()

        except IpCantBeRemovedFromVip, e:
            msg = 'This network has a VIP pointing to it, and can not '\
                'be deleted. Network: {}, Vip Request: {}'.format(
                    str(self), e.cause)

            self.log.error(msg)
            raise NetworkIPv6ErrorV3(msg)

        except NetworkActiveError, e:
            self.log.error(e.message)
            raise NetworkIPv6ErrorV3(e.message)

        except NetworkIPv6ErrorV3, e:
            self.log.error(e.message)
            raise NetworkIPv6ErrorV3(e.message)

        except Exception, e:
            self.log.error(e)
            raise NetworkIPv6ErrorV3(e)

        finally:
            destroy_lock(locks_list)

    def validate_v3(self):
        """
        Validate NetworkIPv6.
        """

        if not self.network_type:
            raise NetworkIPv6ErrorV3('Network type can not null')
        # validate if network if allow in environment
        configs = self.vlan.ambiente.configs.all()
        self.vlan.allow_networks_environment(configs, [], [self])

    def activate_v3(self):
        """
            Send activate info of network v6 for queue of ACL configuration
                system.
            Update status column  to 'active = 1'.

            @raise NetworkIPv6Error: Error activating a NetworkIPv6.
        """

        try:
            self.active = 1
            self.save()

            net_slz = get_app('api_network', 'serializers.v3')
            serializer = net_slz.NetworkIPv6V3Serializer(
                self,
                include=('vlan__details__environment__basic',))

            data_to_queue = serializer.data
            data_to_queue.update({
                'description': queue_keys.NETWORKv6_ACTIVATE
            })

            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            queue_manager.append({
                'action': queue_keys.NETWORKv6_ACTIVATE,
                'kind': queue_keys.NETWORKv6_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

        except Exception, e:
            self.log.error(u'Error activating NetworkIPv6.')
            raise NetworkIPv6ErrorV3(e, u'Error activating NetworkIPv6.')

    def deactivate_v3(self):
        """
            Send deactivate info of network v6 for queue of ACL configuration
                system.
            Update status column  to 'active = 0'.

            @raise NetworkIPv6Error: Error disabling a NetworkIPv6.
        """

        try:

            net_slz = get_app('api_network', 'serializers.v3')
            self.active = 0

            serializer = net_slz.NetworkIPv6V3Serializer(
                self,
                include=('vlan__details__environment__basic',))

            data_to_queue = serializer.data
            data_to_queue.update({
                'description': queue_keys.NETWORKv6_DEACTIVATE
            })

            # Send to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            queue_manager.append({
                'action': queue_keys.NETWORKv6_DEACTIVATE,
                'kind': queue_keys.NETWORKv6_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

            self.save()

        except Exception, e:
            self.log.error(u'Error disabling NetworkIPv6.')
            raise NetworkIPv6ErrorV3(e, u'Error disabling NetworkIPv6.')

    def allocate_network_v3(self, id_vlan, prefix=None):
        """Allocate new NetworkIPv6
            @raise VlanNotFoundError: Vlan is not registered.
            @raise VlanError: Failed to search for the Vlan
            @raise ConfigEnvironmentInvalidError: Invalid Environment
                                                  Configuration or not
                                                  registered
            @raise NetworkIPv6Error: Error persisting a NetworkIPv6.
            @raise NetworkIPv6AddressNotAvailableError: Unavailable address to
                                                        create a NetworkIPv6.
            @raise Invalid: Unavailable address to create a NetworkIPv6.
            @raise InvalidValueError: Network type does not exist.
        """

        vlan_model = get_model('vlan', 'Vlan')
        self.vlan = vlan_model().get_by_pk(id_vlan)

        netv4, nets_envs = network.get_networks_related(
            vrfs=self.vlan.get_vrf(),
            eqpts=self.vlan.get_eqpt(),
            has_netv4=False
        )
        nets_envs = [IPNetwork(net.networkv6) for net in nets_envs]
        network_found = None

        try:

            configs = self.vlan.ambiente.configs.filter(
                ip_config__type=IP_VERSION.IPv6[0])

            # For each configuration founded in environment
            for config in configs:

                net6 = IPNetwork(config.ip_config.subnet)

                if prefix is not None:
                    new_prefix = int(prefix)
                else:
                    new_prefix = int(config.ip_config.new_prefix)

                self.log.info(
                    u'Prefix that will be used: %s' % new_prefix)

                free_nets = network.get_free_space_network([net6], nets_envs)

                for free_net in free_nets:
                    try:
                        subnets = free_net.iter_subnets(new_prefix=new_prefix)
                        subnet = subnets.next()
                    except Exception:
                        pass
                    else:

                        # Set octs by network generated
                        self.block1, self.block2, self.block3, self.block4,\
                            self.block5, self.block6, self.block7, \
                            self.block8 = str(
                                subnet.network.exploded
                            ).split(':')

                        # Set block by network generated
                        self.block = subnet.prefixlen

                        mask = subnet.netmask.exploded.split(':')
                        self.mask1 = mask[0]
                        self.mask2 = mask[1]
                        self.mask3 = mask[2]
                        self.mask4 = mask[3]
                        self.mask5 = mask[4]
                        self.mask6 = mask[5]
                        self.mask7 = mask[6]
                        self.mask8 = mask[7]
                        if not self.network_type:
                            self.network_type = config.ip_config.network_type
                        return

            # Checks if found any available network
            if network_found is None:
                # If not found, an exception is thrown
                raise NetworkIPv6AddressNotAvailableError(
                    None, u'Unavailable address to create a NetworkIPv6.')

        except (ValueError, TypeError, AddressValueError), e:
            raise ConfigEnvironmentInvalidError(e, u'Invalid Configuration')


class Ipv6(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id_ipv6'
    )
    description = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_column='descricao'
    )
    networkipv6 = models.ForeignKey(
        'ip.NetworkIPv6',
        db_column='id_redeipv6'
    )
    block1 = models.CharField(
        max_length=4,
        db_column='bloco1'
    )
    block2 = models.CharField(
        max_length=4,
        db_column='bloco2'
    )
    block3 = models.CharField(
        max_length=4,
        db_column='bloco3'
    )
    block4 = models.CharField(
        max_length=4,
        db_column='bloco4'
    )
    block5 = models.CharField(
        max_length=4,
        db_column='bloco5'
    )
    block6 = models.CharField(
        max_length=4,
        db_column='bloco6'
    )
    block7 = models.CharField(
        max_length=4,
        db_column='bloco7'
    )
    block8 = models.CharField(
        max_length=4,
        db_column='bloco8'
    )

    log = logging.getLogger('Ipv6')

    class Meta(BaseModel.Meta):
        db_table = u'ipsv6'
        managed = True
        unique_together = ('block1', 'block2', 'block3', 'block4',
                           'block5', 'block6', 'block7', 'block8',
                           'networkipv6')

    def __str__(self):
        return self.ip_formated

    def _get_formated_ip(self):
        """Returns formated ip."""
        return '%s:%s:%s:%s:%s:%s:%s:%s' % (
            self.block1, self.block2, self.block3, self.block4,
            self.block5, self.block6, self.block7, self.block8)

    ip_formated = property(_get_formated_ip)

    def _get_equipments(self):
        """Returns equipments list."""
        ipeqs = self.ipv6equipament_set.all().select_related('equipamento')
        eqpts = [ipeq.equipamento for ipeq in ipeqs]
        return eqpts

    equipments = property(_get_equipments)

    def _get_ipv6_equipment(self):

        return self.ipv6equipament_set.all()

    ipv6_equipment = \
        property(_get_ipv6_equipment)

    def _get_vips(self):
        """Returns vips list."""
        vips = self.viprequest_set.all()
        return vips

    vips = property(_get_vips)

    def _get_server_pool_members(self):
        """Returns pool members list."""
        server_pool_members = self.serverpoolmember_set.all()
        return server_pool_members

    server_pool_members = property(_get_server_pool_members)

    @classmethod
    def get_by_pk(cls, id):
        """Get IPv6 by id.
        @return: IPv6.
        @raise IpNotFoundError: IPv6 is not registered.
        @raise IpError: Failed to search for the IPv6.
        @raise OperationalError: Lock wait timeout exceeded.
        """
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
            return Ipv6.objects.get(
                block1=block1, block2=block2, block3=block3, block4=block4,
                block5=block5, block6=block6, block7=block7, block8=block8,
                ipv6equipament__equipamento__id=equip_id)
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
            return Ipv6.objects.filter(
                networkipv6__vlan__ambiente__id=id_ambiente,
                ipv6equipament__equipamento__id=id_equipment)
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
        configuration = get_model('config', 'Configuration')

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
        conf = configuration.get()

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
            cls.log.info('ip %s' % ip.block8)

        # Cast all to API class
        ipsv6 = set([(IPv6Address('%s:%s:%s:%s:%s:%s:%s:%s' % (
            ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8)
        )) for ip in ips])

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
        configuration = get_model('config', 'Configuration')
        try:
            # Cast to API
            net6 = IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%s' %
                               (self.networkipv6.block1, self.networkipv6.block2, self.networkipv6.block3,
                                self.networkipv6.block4, self.networkipv6.block5, self.networkipv6.block6,
                                self.networkipv6.block7, self.networkipv6.block8, self.networkipv6.block))
            # Find all ipv6s ralated to network
            ips = Ipv6.objects.filter(networkipv6__id=self.networkipv6.id)

            ip6_object = IPv6Address('%s:%s:%s:%s:%s:%s:%s:%s' % (
                self.block1, self.block2, self.block3, self.block4, self.block5, self.block6, self.block7, self.block8))

            # Cast all to API class
            ipsv6 = set([IPv6Address('%s:%s:%s:%s:%s:%s:%s:%s' % (
                ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8)) for ip in ips])

            # Get configuration
            conf = configuration.get()

            flag = True

            aux_ip6 = ip6_object.exploded
            aux_ip6 = aux_ip6.split(':')
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
                    conf = configuration.get()

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
                        self.block1, self.block2, self.block3, self.block4, self.block5,
                        self.block6, self.block7, self.block8, self.networkipv6.id))

            if flag:
                self.save()

            else:
                raise IpNotAvailableError(None, u'Ipv6 %s:%s:%s:%s:%s:%s:%s:%s not available for network %s.' % (
                    self.block1, self.block2, self.block3, self.block4, self.block5,
                    self.block6, self.block7, self.block8, self.networkipv6.id))

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
        equipamentoambiente = get_model('equipamento', 'EquipamentoAmbiente')
        equipamento = get_model('equipamento', 'Equipamento')
        filterequiptype = get_model('filterequiptype', 'FilterEquipType')
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
            aux_ip6 = aux_ip6.split(':')
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
                equipment = equipamento().get_by_pk(equipment_id)
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
                            for fet in filterequiptype.objects.filter(filter=self.networkipv6.vlan.ambiente.filter.id):
                                tp_equip_list_one.append(fet.equiptype)

                            tp_equip_list_two = list()
                            for fet in filterequiptype.objects.filter(filter=ip_test.networkipv6.vlan.ambiente.filter.id):
                                tp_equip_list_two.append(fet.equiptype)

                            if equipment.tipo_equipamento not in tp_equip_list_one or equipment.tipo_equipamento not in tp_equip_list_two:
                                raise IpRangeAlreadyAssociation(
                                    None, u'Equipment is already associated with another ip with the same ip range.')

                # # Filter case 2 - end ##

                ip6_equipment.save()

                # Makes Environment Equipment association
                try:
                    equipment_environment = equipamentoambiente()
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
        """Persist an IPv6 and associate it to an equipment.
        If equipment was not related with VLAN environment, this makes the relationship
        @return: Nothing
        @raise NetworkIPv6NotFoundError: NetworkIPv6 does not exist.
        @raise NetworkIPv6Error: Error finding NetworkIPv6.
        @raise EquipamentoNotFoundError: Equipment does not exist.
        @raise EquipamentoError: Error finding Equipment.
        @raise IpNotAvailableError: No IP available to VLAN.
        @raise IpError: Error persisting in database.
        """
        configuration = get_model('config', 'Configuration')
        equipamento = get_model('equipamento', 'Equipamento')
        equipamentoambiente = get_model('equipamento', 'EquipamentoAmbiente')
        self.networkipv6 = NetworkIPv6().get_by_pk(id)

        # Cast to API
        net6 = IPv6Network('%s:%s:%s:%s:%s:%s:%s:%s/%s' % (
            self.networkipv6.block1, self.networkipv6.block2, self.networkipv6.block3, self.networkipv6.block4,
            self.networkipv6.block5, self.networkipv6.block6, self.networkipv6.block7, self.networkipv6.block8, self.networkipv6.block))
        # Find all ipv6s ralated to network
        ips = Ipv6.objects.filter(networkipv6__id=self.networkipv6.id)

        # Cast all to API class
        ipsv6 = set([(IPv6Address('%s:%s:%s:%s:%s:%s:%s:%s' % (
            ip.block1, ip.block2, ip.block3, ip.block4, ip.block5, ip.block6, ip.block7, ip.block8))) for ip in ips])

        # Get configuration
        conf = configuration.get()

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

        equipment = equipamento().get_by_pk(equipment_id)

        try:
            self.save()

            ipv6_equipment = Ipv6Equipament()
            ipv6_equipment.ip = self
            ipv6_equipment.equipamento = equipment
            ipv6_equipment.save(authenticated_user)

            try:
                equipment_environment = equipamentoambiente().get_by_equipment_environment(
                    equipment_id, self.networkipv6.vlan.ambiente_id)

            except EquipamentoAmbienteNotFoundError:
                equipment_environment = equipamentoambiente()
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
        """Get Ipv6 by blocks and network.
        @return: Ipv6.
        @raise IpNotFoundError: Ipv6 is not registered.
        @raise IpError: Failed to search for the Ipv6.
        """
        try:
            return Ipv6.objects.get(
                block1=block1, block2=block2, block3=block3, block4=block4, block5=block5,
                block6=block6, block7=block7, block8=block8, networkipv6=id_network)
        except ObjectDoesNotExist, e:
            raise IpNotFoundError(e, u'Dont there is a Ipv6 %s:%s:%s:%s:%s:%s:%s:%s  ' % (
                block1, block2, block3, block4, block5, block6, block7, block8))
        except Exception, e:
            cls.log.error(u'Failure to search the Ipv6.')
            raise IpError(e, u'Failure to search the Ipv6.')

    @classmethod
    def get_by_blocks(cls, block1, block2, block3, block4, block5, block6, block7, block8):
        """Get Ipv6's  by blocks.
        @return: Ipv6's.
        @raise IpNotFoundError: Ipv6 is not registered.
        @raise IpError: Failed to search for the Ipv6.
        """
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
    def get_by_octs_and_environment_vip(cls, block1, block2, block3, block4, block5,
                                        block6, block7, block8, id_evip, valid=True):
        """
        Get Ipv6 by blocks and environment vip.
        @return: Ipv6.
        @raise IpNotFoundError: Ipv6 is not registered.
        @raise IpError: Failed to search for the Ipv6.
        """
        environmentvip = get_model('ambiente', 'EnvironmentVip')
        ambiente_model = get_model('ambiente', 'Ambiente')
        try:
            ips = Ipv6.objects.filter(
                block1=block1, block2=block2, block3=block3,
                block4=block4, block5=block5, block6=block6, block7=block7, block8=block8)
            if ips.count() == 0:
                raise IpNotFoundError(None)

            if valid is True:
                return Ipv6.objects.get(
                    block1=block1, block2=block2, block3=block3, block4=block4, block5=block5,
                    block6=block6, block7=block7, block8=block8, networkipv6__ambient_vip__id=id_evip)
            else:
                for ip in ips:
                    if ip.networkipv6.ambient_vip:
                        if ip.networkipv6.ambient_vip.id == id_evip:
                            return ip
                    else:
                        environments = ambiente_model.objects.filter(
                            vlan__networkipv6__ambient_vip__id=id_evip)
                        for env in environments:
                            if ip.networkipv6.vlan.ambiente.divisao_dc.id == env.divisao_dc.id \
                                    and ip.networkipv6.vlan.ambiente.ambiente_logico.id == env.ambiente_logico.id:
                                return ip
                raise ObjectDoesNotExist()

        except ObjectDoesNotExist, e:
            evip = environmentvip.get_by_pk(id_evip)
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
        """Get Ipv6 by blocks and environment.
        @return: Ipv6.
        @raise IpNotFoundError: Ipv6 is not registered.
        @raise IpError: Failed to search for the Ipv6.
        """
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
        """Sobrescreve o método do Django para remover um IP.
        Antes de remover o IP remove todas as suas requisições de VIP e os relacionamentos com equipamentos.
        """
        try:
            # Delete all Request Vip associeted
            for r in self.requisicaovips_set.all():
                r_alter = False
                id_vip = r.id
                if r.vip_criado:
                    raise IpCantBeRemovedFromVip(
                        r.id, 'Ipv6 não pode ser removido, porque está em uso por Requisição Vip %s' % (r.id))
                else:
                    if r.ip is not None:
                        r.ipv6 = None
                        r.validado = 0
                        r.save()
                        r_alter = True

                        # SYNC_VIP
                        syncs.old_to_new(r)

                if not r_alter:
                    r.delete()

                    # SYNC_VIP
                    syncs.delete_new(id_vip)

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

            # Serializes obj
            ip_slz = get_app('api_ip', module_label='serializers')
            serializer = ip_slz.Ipv6V3Serializer(self)
            data_to_queue = serializer.data

            # Deletes Obj IP
            super(Ipv6, self).delete()

            # Sends to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            data_to_queue.update({'description': queue_keys.IPv6_REMOVE})
            queue_manager.append({
                'action': queue_keys.IPv6_REMOVE,
                'kind': queue_keys.IPv6_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

        except EquipamentoAmbienteNotFoundError, e:
            raise EquipamentoAmbienteNotFoundError(None, e.message)
        except IpCantBeRemovedFromVip, e:
            raise IpCantBeRemovedFromVip(e.cause, e.message)
        except IpEquipmentNotFoundError, e:
            raise IpEquipmentNotFoundError(None, e.message)

    ##################
    # Methods for V3 #
    ##################
    def create_v3(self, ip_map, locks_used=[]):
        """Method V3 to create Ipv6."""

        models = get_app('equipamento', 'models')

        try:

            self.networkipv6_id = NetworkIPv6()\
                .get_by_pk(ip_map.get('networkipv6')).id
            self.block1 = ip_map.get('block1')
            self.block2 = ip_map.get('block2')
            self.block3 = ip_map.get('block3')
            self.block4 = ip_map.get('block4')
            self.block5 = ip_map.get('block5')
            self.block6 = ip_map.get('block6')
            self.block7 = ip_map.get('block7')
            self.block8 = ip_map.get('block8')
            self.descricao = ip_map.get('description')

            # Get environments related
            envs = self.networkipv6.vlan\
                .get_environment_related(use_vrf=True)\
                .values_list('id', flat=True)

            # Get objects of equipments
            eqpts = models.Equipamento.objects.filter(
                id__in=[eqpt.get('id')
                        for eqpt in ip_map.get('equipments', [])])
        except Exception, e:
            raise IpErrorV3(e)

        else:

            locks_name = list()

            # Prepare locks for environment
            for env in envs:
                lock_name = LOCK_ENVIRONMENT_ALLOCATES % env
                if lock_name not in locks_used:
                    locks_name.append(lock_name)

            for eqpt_obj in eqpts:
                # Prepare locks for ips-equipments
                lock_name = LOCK_IPV6_EQUIPMENT_ONE % eqpt_obj.id
                if lock_name not in locks_used:
                    locks_name.append(lock_name)

                # Prepare locks for environments related with equipaments
                for env in eqpt_obj.environments:
                    lock_name = LOCK_ENVIRONMENT_ALLOCATES % env.ambiente_id
                    if lock_name not in locks_used:
                        locks_name.append(lock_name)

            # Create Locks
            locks_name = list(set(locks_name))
            locks_list = create_lock_with_blocking(locks_name)

        try:

            if self.block1 is None and self.block2 is None and \
                    self.block3 is None and self.block4 is None and \
                    self.block5 is None and self.block6 is None and \
                    self.block7 is None and self.block8 is None:

                self.allocate_v3()

            else:
                net6 = IPv6Network(self.networkipv6.networkv6)

                # Find all ips ralated to network
                ips = Ipv6.objects.filter(networkipv6=self.networkipv6)

                ip6_object = IPv6Address(self.ip_formated)

                # Cast all to API class
                ipsv6 = set([IPv6Address(ip.ip_formated) for ip in ips])

                flag = False

                if ip6_object not in ipsv6:

                    if ip6_object in net6:

                        first_ip_network = int(net6.network)
                        bcast_ip_network = int(net6.broadcast)

                        ipv6_network = int(ip6_object)

                        # First and last ip are reserved in network
                        if ipv6_network >= (first_ip_network) and \
                                ipv6_network < (bcast_ip_network):
                            flag = True

                if flag is False:
                    raise IpNotAvailableError(
                        None,
                        u'Ip %s not available for network %s.' %
                        (self.ip_formated, self.networkipv6.id))

                self.validate_v3(eqpts)

            self.save()

            # Creates relationship between ip and equipment
            for eqpt in ip_map.get('equipments', []):
                ip_equipment = Ipv6Equipament()
                ip_equipment.create_v3({
                    'ip': self.id,
                    'equipment': eqpt.get('id')
                })

        except IpErrorV3, e:
            self.log.error(e.message)
            raise IpErrorV3(e.message)

        except IpNotAvailableError, e:
            self.log.error(e.message)
            raise IpErrorV3(e.message)

        except Exception, e:
            msg = u'Error save new IPV6.: %s' % e
            self.log.exception(msg)
            raise IpErrorV3(msg)

        finally:
            # Destroy locks
            destroy_lock(locks_list)

    def update_v3(self, ip_map, locks_used=[]):
        """Method V3 to update Ipv6."""

        models = get_app('equipamento', 'models')

        try:
            self.descricao = ip_map.get('description')

            # Get environments related
            envs = self.networkipv6.vlan.get_environment_related(use_vrf=True)\
                .values_list('id', flat=True)

            # Get objects of equipments
            eqpts = models.Equipamento.objects.filter(id__in=[
                eqpt.get('id') for eqpt in ip_map.get('equipments', [])]
            )
        except Exception, e:
            raise IpErrorV3(e)

        else:

            locks_name = list()

            # Prepare lock for ipv6
            lock_name = LOCK_IPV6 % self.id
            if lock_name not in locks_used:
                locks_name.append(lock_name)

            # Prepare locks for environment
            for env in envs:
                lock_name = LOCK_ENVIRONMENT_ALLOCATES % env
                if lock_name not in locks_used:
                    locks_name.append(lock_name)

            for eqpt_obj in eqpts:
                # Prepare locks for ips-equipments
                lock_name = LOCK_IPV6_EQUIPMENT % (self.id, eqpt_obj.id)
                if lock_name not in locks_used:
                    locks_name.append(lock_name)

                # Prepare locks for environments related with equipaments
                for env in eqpt_obj.environments:
                    lock_name = LOCK_ENVIRONMENT_ALLOCATES % env.ambiente_id
                    if lock_name not in locks_used:
                        locks_name.append(lock_name)

            # Create Locks
            locks_name = list(set(locks_name))
            locks_list = create_lock_with_blocking(locks_name)
        try:

            self.validate_v3(eqpts)

            self.save()

            # Get current associates
            current = self.ipv6equipament_set\
                .filter(equipamento__in=eqpts)\
                .values_list('equipamento', flat=True)

            # Creates new associate
            for eqpt in eqpts:
                if eqpt.id not in current:
                    ip_equipment = Ipv6Equipament()
                    ip_equipment.create_v3({
                        'ip': self.id,
                        'equipment': eqpt.id
                    })

            # Removes old associates
            for ip_eqpt in self.ipv6equipament_set\
                    .exclude(equipamento__in=eqpts):
                ip_eqpt.delete_v3(bypass_ip=True)

        except IpErrorV3, e:
            self.log.error(e.message)
            raise IpErrorV3(e.message)

        except Exception, e:
            msg = u'Error edit IP.: %s' % e
            self.log.error(msg)
            raise IpErrorV3(msg)

        finally:
            # Destroy locks
            destroy_lock(locks_list)

    def delete_v3(self, locks_used=[]):
        """
        Method V3 to remove Ipv6.
        Before removing the IP removes all your requests
        VIP and relationships with equipment.

        @raise IpCantBeRemovedFromVip: Ipv6 is associated with created
                                       Vip Request.
        """

        locks_name = list()

        # Prepare lock for ipv6
        lock_name = LOCK_IPV6 % self.id
        if lock_name not in locks_used:
            locks_name.append(lock_name)

        # Create Locks
        locks_name = list(set(locks_name))
        locks_list = create_lock_with_blocking(locks_name)

        try:
            for vip in self.viprequest_set.all():
                id_vip = vip.id
                with distributedlock(LOCK_VIP % id_vip):
                    if vip.created:
                        raise IpCantBeRemovedFromVip(
                            id_vip,
                            'IPv6 can not be removed because it is '
                            'in use by Vip Request %s' % (id_vip))

                    # Deletes only VIP, Related Ipv6 with VIP is not removed
                    vip.delete_v3(bypass_ipv4=True, bypass_ipv6=True)

            # Deletes Related Equipment
            for ip_eqpt in self.ipv6equipament_set.all():
                ip_eqpt.delete_v3(bypass_ip=True)

            # Serializes obj
            ip_slz = get_app('api_ip', module_label='serializers')
            serializer = ip_slz.Ipv6V3Serializer(self)
            data_to_queue = serializer.data

            # Deletes Obj IP
            super(Ipv6, self).delete()

            # Sends to Queue
            queue_manager = QueueManager(broker_vhost='tasks',
                                         queue_name='tasks.aclapi',
                                         exchange_name='tasks.aclapi',
                                         routing_key='tasks.aclapi')
            data_to_queue.update({'description': queue_keys.IPv6_REMOVE})
            queue_manager.append({
                'action': queue_keys.IPv6_REMOVE,
                'kind': queue_keys.IPv6_KEY,
                'data': data_to_queue
            })
            queue_manager.send()

        except IpCantBeRemovedFromVip, e:
            raise IpCantBeRemovedFromVip(e.cause, e.message)

        except Exception, e:
            msg = u'Error edit IP.: %s' % e
            self.log.error(msg)
            raise IpErrorV3(msg)

        finally:
            # Destroy locks
            destroy_lock(locks_list)

    def validate_v3(self, equipments):
        """Validate Ip."""

        env_ip = self.networkipv6.vlan.ambiente
        network.validate_conflict_join_envs(env_ip, equipments)

    def allocate_v3(self):
        """Persist an IPv6 and associate it to an equipment.
            If equipment was not related with VLAN environment, this makes the relationship
            @return: Nothing
            @raise NetworkIPv6NotFoundError: NetworkIPv6 does not exist.
            @raise NetworkIPv6Error: Error finding NetworkIPv6.
            @raise EquipamentoNotFoundError: Equipment does not exist.
            @raise EquipamentoError: Error finding Equipment.
            @raise IpNotAvailableError: No IP available to VLAN.
            @raise IpError: Error persisting in database.
        """
        configuration = get_model('config', 'Configuration')
        # Cast to API
        net6 = IPNetwork(self.networkipv6.networkv6)

        # Find all ips ralated to network
        ips = self.networkipv6.ipv6_set.all()

        # Cast all to API class
        ipsv6 = set([IPv6Address(ip.ip_formated) for ip in ips])

        # Get configuration
        conf = configuration.get()

        selected_ip = None

        # For each ip generated
        i = 0
        for ip in net6.iterhosts():

            # Do not use some range of IPs (config)
            # IPv6_MIN = Firsts
            # IPv6_MAX = Number minimum of Ip reserveds
            # First IP and 2 last I
            i = i + 1
            if i >= conf.IPv6_MIN and i < (net6.numhosts - conf.IPv6_MAX):

                # If IP generated was not used
                if ip not in ipsv6:

                    # Use it
                    selected_ip = ip

                    # Stop generation
                    break

        if selected_ip is None:
            raise IpNotAvailableError(None, u'No IP available to VLAN %s.' %
                                            self.networkipv6.vlan.num_vlan)

        self.block1, self.block2, self.block3, self.block4, self.block5, \
            self.block6, self.block7, self.block8 = str(
                selected_ip.exploded).split(':')


class Ipv6Equipament(BaseModel):
    id = models.AutoField(
        primary_key=True,
        db_column='id_ipsv6_dos_equipamentos'
    )
    ip = models.ForeignKey(
        'ip.Ipv6',
        db_column='id_ipv6'
    )
    equipamento = models.ForeignKey(
        'equipamento.Equipamento',
        db_column='id_equip'
    )

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
        """Validates whether IPv6 is already associated with equipment
            @raise IpEquipamentoDuplicatedError: if IPv6 is already associated with equipment
        """
        try:
            Ipv6Equipament.objects.get(
                ip=self.ip, equipamento=self.equipamento)
            raise IpEquipamentoDuplicatedError(
                None, u'IP already registered for the equipment. '
                'Ip: %s, Equipment: %s' %
                (str(self.ip), str(self.equipamento)))
        except ObjectDoesNotExist:
            pass

    def create(self, authenticated_user, ip_id, equipment_id):
        """Insere um relacionamento entre IP e Equipamento.
        @return: Nothing.
        @raise IpError: Falha ao inserir.
        @raise EquipamentoNotFoundError: Equipamento não cadastrado.
        @raise IpNotFoundError: Ip não cadastrado.
        @raise IpEquipamentoDuplicatedError: IP já cadastrado para o equipamento.
        @raise EquipamentoError: Falha ao pesquisar o equipamento.
        """
        equipamento = get_model('equipamento', 'Equipamento')
        equipamentoambiente = get_model('equipamento', 'EquipamentoAmbiente')

        self.equipamento = equipamento().get_by_pk(equipment_id)
        self.ip = Ipv6().get_by_pk(ip_id)

        # Valida o ip
        self.validate_ip()

        try:
            if self.equipamento not in [ea.equipamento for ea in self.ip.networkipv6.vlan.ambiente.equipamentoambiente_set.all()]:
                ea = equipamentoambiente(
                    ambiente=self.ip.networkipv6.vlan.ambiente, equipamento=self.equipamento)
                ea.save(authenticated_user)

            self.save()
        except Exception, e:
            self.log.error(u'Falha ao inserir um ip_equipamento.')
            raise IpError(e, u'Falha ao inserir um ip_equipamento.')

    def remove(self, authenticated_user, ip_id, equip_id):
        """Research and removes the relationship between IP and equipment.
        @return: Nothing
        @raise IpEquipmentNotFoundError: Dont is no relationship between the IP and Equipment.
        @raise IpError: Failure to remove the relationship.
        """
        ip_equipamento = self.get_by_ip_equipment(ip_id, equip_id)

        try:
            ip_equipamento.delete()

        except (IpCantBeRemovedFromVip, IpEquipCantDissociateFromVip), e:
            raise e
        except Exception, e:
            self.log.error(u'Failure to remove the Ipv6Equipament.')
            raise IpError(e, u'Failure to remove the Ipv6Equipament.')

    def delete(self):
        """Override Django's method to remove Ipv6 and Equipment relationship.
        If Ip from this Ip-Equipment is associated with created Vip Request, and the Equipment
        is the last balancer associated, the IpEquipment association cannot be removed.
        If Ip has no relationship with other Equipments, then Ip is also removed.
        """
        tipoequipamento = get_model('equipamento', 'TipoEquipamento')

        for r in self.ip.requisicaovips_set.all():
            if self.equipamento.tipo_equipamento == tipoequipamento.get_tipo_balanceador():
                # Get all equipments (except the one being removed) related to ip
                # to find another balancer
                other_equips = self.ip.ipv6equipament_set.exclude(
                    equipamento=self.equipamento.id)
                another_balancer = False
                for ipequip in other_equips:
                    if ipequip.equipamento.tipo_equipamento == tipoequipamento.get_tipo_balanceador():
                        another_balancer = True
                        break

                if not another_balancer:
                    if r.vip_criado:
                        raise IpEquipCantDissociateFromVip(
                            {
                                'vip_id': r.id,
                                'ip': mount_ipv6_string(self.ip),
                                'equip_name': self.equipamento.nome
                            }, 'Ipv6 não pode ser disassociado do equipamento %s '
                            'porque é o último balanceador da Requisição Vip %s.' %
                            (self.equipamento.nome, r.id))
                    else:
                        # Remove ip from vip or remove vip
                        id_vip = r.id
                        if r.ip is not None:
                            r.ipv6 = None
                            r.validado = 0
                            r.save()

                            # SYNC_VIP
                            syncs.old_to_new(r)
                        else:
                            r.delete()

                            # SYNC_VIP
                            syncs.delete_new(id_vip)

        if self.ip.serverpoolmember_set.count() > 0:

            server_pool_identifiers = set()

            for svm in self.ip.serverpoolmember_set.all():
                item = '{}:{}'.format(svm.server_pool.id,
                                      svm.server_pool.identifier)
                server_pool_identifiers.add(item)

            server_pool_identifiers = list(server_pool_identifiers)
            server_pool_identifiers = ', '.join(
                str(server_pool) for server_pool in server_pool_identifiers)

            raise IpCantRemoveFromServerPool(
                {
                    'ip': mount_ipv6_string(self.ip),
                    'equip_name': self.equipamento.nome,
                    'server_pool_identifiers': server_pool_identifiers
                },
                'Ipv6 não pode ser disassociado do equipamento %s '
                'porque ele está sendo utilizando nos Server Pools '
                '(id:identifier) %s' % (
                    self.equipamento.nome, server_pool_identifiers)
            )

        super(Ipv6Equipament, self).delete()

        # If ip has no other equipment, than he will be removed to
        if self.ip.ipv6equipament_set.count() == 0:
            self.ip.delete()

    ##################
    # Methods for V3 #
    ##################
    def create_v3(self, ip_equipment):
        """Inserts a relationship between IP e Equipment.
        @return: Nothing.
        @raise IpError: Failure to insert.
        @raise EquipamentoNotFoundError: Equipment do not registered.
        @raise IpNotFoundError: Ip do not registered.
        @raise IpEquipamentoDuplicatedError: IP already registered for the equipment.
        @raise EquipamentoError: Failure to search equipment.
        """
        equipamento = get_model('equipamento', 'Equipamento')
        equipamentoambiente = get_model('equipamento', 'EquipamentoAmbiente')

        self.equipamento = equipamento().get_by_pk(ip_equipment.get('equipment'))
        self.ip = Ipv6().get_by_pk(ip_equipment.get('ip'))

        # Validate the ip
        self.validate_ip()

        try:

            # All equipments related with environment of IP
            eqpts = self.ip.networkipv6.vlan.ambiente\
                .equipamentoambiente_set.all()\
                .values_list('equipamento', flat=True)

            if ip_equipment.get('equipment') not in eqpts:
                ea = equipamentoambiente(
                    ambiente=self.ip.networkipv6.vlan.ambiente,
                    equipamento=self.equipamento
                )
                ea.save()

            self.save()
        except Exception, e:
            self.log.error(u'Failure to insert an ip_equipamento.')
            raise IpError(e, u'Failure to insert an ip_equipamento.')

    def delete_v3(self, bypass_ip=False):
        """
        Method V3 to remove Ipv6 and Equipment relationship.
        If Ipv6 from this Ipv6-Equipment is associated with created Vip
            Request and the Equipment is the last balancer associated,
            the IpEquipment association cannot be removed.
        If Ipv6 has no relationship with other Equipments, then Ipv6 is
            also removed.

        @raise IpCantRemoveFromServerPool: Ip is associated with associated
                                           Pool Member.
        @raise IpEquipCantDissociateFromVip: Equipment is the last balanced
                                             in a created Vip Request
                                             pointing to ip.
        """
        tipoequipamento = get_model('equipamento', 'TipoEquipamento')

        type_eqpt = tipoequipamento.get_tipo_balanceador()

        if self.equipamento.tipo_equipamento == type_eqpt:

            for vip in self.ip.viprequest_set.all():

                # Filter equipments to find another balancer
                another_balancer = self.ip.ipv6equipament_set.exclude(
                    equipamento=self.equipamento.id
                ).filter(equipamento__tipo_equipamento=type_eqpt)

                id_vip = vip.id

                if not another_balancer:
                    with distributedlock(LOCK_VIP % id_vip):
                        if vip.created:
                            raise IpEquipCantDissociateFromVip(
                                {
                                    'vip_id': id_vip,
                                    'ip': self.ip.ip_formated,
                                    'equip_name': self.equipamento.nome
                                },
                                'Ipv6 can not be dissociated from the '
                                'equipment %s because it is the last '
                                'balancer of Vip Request %s.'
                                % (self.equipamento.nome, id_vip)
                            )
                        else:
                            # Remove ipv6 from vip
                            if vip.ipv4 is not None:
                                vip.ipv6 = None
                                id_vip.save()

                                # SYNC_VIP
                                syncs.new_to_old(vip)
                            # Remove vip
                            else:
                                vip.delete_v3(bypass_ipv4=True,
                                              bypass_ipv6=True)

        if self.ip.serverpoolmember_set.count() > 0:

            items = ['{}:{}'.format(
                svm.server_pool.id,
                svm.server_pool.identifier
            ) for svm in self.ip.serverpoolmember_set.all()]

            items = ', '.join(items)

            raise IpCantRemoveFromServerPool(
                {
                    'ip': self.ip.ip_formated,
                    'equip_name': self.equipamento.nome,
                    'server_pool_identifiers': items
                },
                'IPv6 can not be dissociated from the equipment% s because it'
                'is being using in the Server Pools (id: identifier)%s' %
                (self.equipamento.nome, items)
            )

        super(Ipv6Equipament, self).delete()

        # If ip has no other equipment, than he will be removed to
        if self.ip.ipv6equipament_set.count() == 0 and not bypass_ip:
            self.ip.delete_v3()


def network_in_range(vlan, network, version):
    # Get all vlans environments from equipments of the current
    # environment
    tipoequipamento = get_model('equipamento', 'TipoEquipamento')
    equips = list()
    envs = list()
    envs_aux = list()
    ids_all = list()

    ambiente = vlan.ambiente
    filter = ambiente.filter
    equipment_types = tipoequipamento.objects.filter(
        filterequiptype__filter=filter)

    # Get all equipments from the environment being tested
    # that are not supposed to be filtered
    # (not the same type of the equipment type of a filter of the environment)
    for env in ambiente.equipamentoambiente_set.all().exclude(
        equipamento__tipo_equipamento__in=equipment_types
    ).select_related('equipamento'):
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
        for vlan in env.vlan_set.all().prefetch_related(
            'networkipv4_set'
        ).prefetch_related('networkipv6_set'):
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
            ip = '%s.%s.%s.%s/%s' % (net.oct1,
                                     net.oct2, net.oct3, net.oct4, net.block)
        else:
            ip = '%s:%s:%s:%s:%s:%s:%s:%s/%d' % (
                net.block1, net.block2, net.block3, net.block4,
                net.block5, net.block6, net.block7, net.block8, net.block)

        ip_net = IPNetwork(ip)
        # If some network, inside this vlan, is subnet of network search param
        if ip_net in network or network in ip_net:
            # This vlan must be in vlans founded, don't need to continue
            # checking
            return True

    # If don't found any subnet return False
    return False
