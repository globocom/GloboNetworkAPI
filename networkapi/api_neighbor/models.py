# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q

from networkapi.admin_permission import AdminPermission
from networkapi.api_neighbor.v4 import exceptions
from networkapi.api_neighbor.v4.exceptions import \
    DontHavePermissionForPeerGroupException
from networkapi.api_neighbor.v4.exceptions import \
    LocalIpAndLocalAsnAtDifferentEquipmentsException
from networkapi.api_neighbor.v4.exceptions import \
    LocalIpAndPeerGroupAtDifferentEnvironmentsException
from networkapi.api_neighbor.v4.exceptions import \
    LocalIpAndRemoteIpAreInDifferentVrfsException
from networkapi.api_neighbor.v4.exceptions import NeighborDuplicatedException
from networkapi.api_neighbor.v4.exceptions import NeighborV4IsDeployed
from networkapi.api_neighbor.v4.exceptions import NeighborV6IsDeployed
from networkapi.api_neighbor.v4.exceptions import \
    RemoteIpAndRemoteAsnAtDifferentEquipmentsException
from networkapi.models.BaseModel import BaseModel
from networkapi.util.geral import get_model


class BgpType:
    ibgp = ('I', 'IBGP')
    ebgp = ('E', 'EBGP')
    list_type = (ibgp, ebgp)


class NeighborV4(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    local_asn = models.ForeignKey(
        'api_asn.Asn',
        db_column='id_local_asn',
        related_name='neighborv4_local_asn'

    )

    remote_asn = models.ForeignKey(
        'api_asn.Asn',
        db_column='id_remote_asn',
        related_name='neighborv4_remote_asn'

    )

    local_ip = models.ForeignKey(
        'ip.Ip',
        db_column='id_local_ip',
        related_name='neighborv4_local_ip'

    )

    remote_ip = models.ForeignKey(
        'ip.Ip',
        db_column='id_remote_ip',
        related_name='neighborv4_remote_ip'

    )

    peer_group = models.ForeignKey(
        'api_peer_group.PeerGroup',
        db_column='id_peer_group'
    )

    virtual_interface = models.CharField(
        blank=False,
        max_length=45,
        db_column='virtual_interface'
    )

    created = models.BooleanField(
        default=False,
        db_column='created'
    )

    log = logging.getLogger('NeighborV4')

    class Meta(BaseModel.Meta):
        db_table = u'neighbor_v4'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get NeighborV4 by id.

        :return: NeighborV4.

        :raise NeighborV4NotFoundError: NeighborV4 not registered.
        :raise NeighborV4Error: Failed to search for the NeighborV4.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return NeighborV4.objects.get(id=id)
        except ObjectDoesNotExist:
            cls.log.error(u'NeighborV4 not found. pk {}'.format(id))
            raise exceptions.NeighborV4NotFoundError(id)
        except OperationalError:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError()
        except Exception:
            cls.log.error(u'Failure to search the NeighborV4.')
            raise exceptions.NeighborV4Error(
                u'Failure to search the NeighborV4.')

    def create_v4(self, neighbor, user):
        """Create NeighborV4."""

        asn_model = get_model('api_asn', 'Asn')
        ipv4_model = get_model('ip', 'Ip')
        peergroup_model = get_model('api_peer_group', 'PeerGroup')

        self.local_asn = asn_model.get_by_pk(neighbor.get('local_asn'))
        self.remote_asn = asn_model.get_by_pk(neighbor.get('remote_asn'))
        self.local_ip = ipv4_model.get_by_pk(neighbor.get('local_ip'))
        self.remote_ip = ipv4_model.get_by_pk(neighbor.get('remote_ip'))
        self.peer_group = peergroup_model.get_by_pk(neighbor.get('peer_group'))
        self.virtual_interface = neighbor.get('virtual_interface')

        self.validate_neighbor_v4(user)

        self.save()

    def update_v4(self, neighbor, user):
        """Update NeighborV4."""

        asn_model = get_model('api_asn', 'Asn')
        ipv4_model = get_model('ip', 'Ip')
        peergroup_model = get_model('api_peer_group', 'PeerGroup')

        self.local_asn = asn_model.get_by_pk(neighbor.get('local_asn'))
        self.remote_asn = asn_model.get_by_pk(neighbor.get('remote_asn'))
        self.local_ip = ipv4_model.get_by_pk(neighbor.get('local_ip'))
        self.remote_ip = ipv4_model.get_by_pk(neighbor.get('remote_ip'))
        self.peer_group = peergroup_model.get_by_pk(neighbor.get('peer_group'))
        self.virtual_interface = neighbor.get('virtual_interface')

        self.validate_neighbor_v4(user)

        self.save()

    def delete_v4(self):
        """Delete NeighborV4."""

        self.check_if_neighbor_already_deployed()

        super(NeighborV4, self).delete()

    def check_if_neighbor_already_deployed(self):

        if self.created:
            raise NeighborV4IsDeployed(self)

    def check_if_local_ip_vrf_is_the_same_as_remote_ip_vrf(self):

        if self.local_ip.networkipv4.vlan.ambiente.default_vrf != \
           self.remote_ip.networkipv4.vlan.ambiente.default_vrf:
            raise LocalIpAndRemoteIpAreInDifferentVrfsException(self)

    def check_if_local_ip_and_local_asn_shares_at_least_one_equipment(self):

        eqpts_of_local_ip = set(self.local_ip.ipequipamento_set.all().
                                values_list('equipamento', flat=True))
        eqpts_of_local_asn = set(self.local_asn.asnequipment_set.all().
                                 values_list('equipment', flat=True))

        if not set.intersection(eqpts_of_local_ip, eqpts_of_local_asn):
            raise LocalIpAndLocalAsnAtDifferentEquipmentsException(self)

    def check_if_remote_ip_and_remote_asn_shares_at_least_one_equipment(self):

        eqpts_of_remote_ip = set(self.remote_ip.ipequipamento_set.all().
                                 values_list('equipamento', flat=True))
        eqpts_of_remote_asn = set(self.remote_asn.asnequipment_set.all().
                                  values_list('equipment', flat=True))

        if not set.intersection(eqpts_of_remote_ip, eqpts_of_remote_asn):
            raise RemoteIpAndRemoteAsnAtDifferentEquipmentsException(self)

    def check_if_peer_group_environments_has_local_ip_environment(self):

        # Check if PeerGroup Environments have the LocalIp Environment
        environments_of_peer_group = self.peer_group. \
            environmentpeergroup_set.all(). \
            values_list('environment', flat=True)
        environment_of_local_ip = self.local_ip.networkipv4.vlan. \
            ambiente.id

        if environment_of_local_ip not in environments_of_peer_group:
            raise LocalIpAndPeerGroupAtDifferentEnvironmentsException(self)

    def check_if_neighbor_is_not_duplicated(self):

        obj = NeighborV4.objects.filter(local_asn=self.local_asn.id,
                                        remote_asn=self.remote_asn.id,
                                        local_ip=self.local_ip.id,
                                        remote_ip=self.remote_ip.id,
                                        peer_group=self.peer_group.id)
        if obj:
            raise NeighborDuplicatedException(self)

    def validate_neighbor_v4(self, user):

        self.check_if_neighbor_already_deployed()
        check_permissions_in_peer_group(self, user)
        self.check_if_local_ip_vrf_is_the_same_as_remote_ip_vrf()
        self.check_if_local_ip_and_local_asn_shares_at_least_one_equipment()
        self.check_if_remote_ip_and_remote_asn_shares_at_least_one_equipment()
        self.check_if_peer_group_environments_has_local_ip_environment()
        self.check_if_neighbor_is_not_duplicated()


class NeighborV6(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    local_asn = models.ForeignKey(
        'api_asn.Asn',
        db_column='id_local_asn',
        related_name='neighborv6_local_asn'
    )

    remote_asn = models.ForeignKey(
        'api_asn.Asn',
        db_column='id_remote_asn',
        related_name='neighborv6_remote_asn'
    )

    local_ip = models.ForeignKey(
        'ip.Ipv6',
        db_column='id_local_ip',
        related_name='neighborv6_local_ip'
    )

    remote_ip = models.ForeignKey(
        'ip.Ipv6',
        db_column='id_remote_ip',
        related_name='neighborv6_remote_ip'
    )

    peer_group = models.ForeignKey(
        'api_peer_group.PeerGroup',
        db_column='id_peer_group'
    )

    virtual_interface = models.CharField(
        blank=False,
        max_length=45,
        db_column='virtual_interface'
    )

    created = models.BooleanField(
        default=False,
        db_column='created'
    )

    log = logging.getLogger('NeighborV6')

    class Meta(BaseModel.Meta):
        db_table = u'neighbor_v6'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get NeighborV6 by id.

        :return: NeighborV6.

        :raise NeighborV6NotFoundError: NeighborV6 not registered.
        :raise NeighborV6Error: Failed to search for the NeighborV6.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return NeighborV6.objects.get(id=id)
        except ObjectDoesNotExist:
            cls.log.error(u'NeighborV6 not found. pk {}'.format(id))
            raise exceptions.NeighborV6NotFoundError(id)
        except OperationalError:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError()
        except Exception:
            cls.log.error(u'Failure to search the NeighborV6.')
            raise exceptions.NeighborV6Error(
                u'Failure to search the NeighborV6.')

    def create_v4(self, neighbor, user):
        """Create NeighborV6."""

        asn_model = get_model('api_asn', 'Asn')
        ipv6_model = get_model('ip', 'Ipv6')
        peergroup_model = get_model('api_peer_group', 'PeerGroup')

        self.local_asn = asn_model.get_by_pk(neighbor.get('local_asn'))
        self.remote_asn = asn_model.get_by_pk(neighbor.get('remote_asn'))
        self.local_ip = ipv6_model.get_by_pk(neighbor.get('local_ip'))
        self.remote_ip = ipv6_model.get_by_pk(neighbor.get('remote_ip'))
        self.peer_group = peergroup_model.get_by_pk(neighbor.get('peer_group'))
        self.virtual_interface = neighbor.get('virtual_interface')

        self.validate_neighbor_v6(user)

        self.save()

    def update_v4(self, neighbor, user):
        """Update NeighborV6."""

        asn_model = get_model('api_asn', 'Asn')
        ipv6_model = get_model('ip', 'Ipv6')
        peergroup_model = get_model('api_peer_group', 'PeerGroup')

        self.local_asn = asn_model.get_by_pk(neighbor.get('local_asn'))
        self.remote_asn = asn_model.get_by_pk(neighbor.get('remote_asn'))
        self.local_ip = ipv6_model.get_by_pk(neighbor.get('local_ip'))
        self.remote_ip = ipv6_model.get_by_pk(neighbor.get('remote_ip'))
        self.peer_group = peergroup_model.get_by_pk(neighbor.get('peer_group'))
        self.virtual_interface = neighbor.get('virtual_interface')

        self.validate_neighbor_v6(user)

        self.save()

    def delete_v4(self):
        """Delete NeighborV6."""

        self.check_if_neighbor_already_deployed()

        super(NeighborV6, self).delete()

    def check_if_neighbor_already_deployed(self):

        if self.created:
            raise NeighborV6IsDeployed(self)

    def check_if_local_ip_vrf_is_the_same_as_remote_ip_vrf(self):

        if self.local_ip.networkipv6.vlan.ambiente.default_vrf != \
           self.remote_ip.networkipv6.vlan.ambiente.default_vrf:
            raise LocalIpAndRemoteIpAreInDifferentVrfsException(self)

    def check_if_local_ip_and_local_asn_shares_at_least_one_equipment(self):

        eqpts_of_local_ip = set(self.local_ip.ipv6equipament_set.all().
                                values_list('equipamento', flat=True))
        eqpts_of_local_asn = set(self.local_asn.asnequipment_set.all().
                                 values_list('equipment', flat=True))

        if not set.intersection(eqpts_of_local_ip, eqpts_of_local_asn):
            raise LocalIpAndLocalAsnAtDifferentEquipmentsException(self)

    def check_if_remote_ip_and_remote_asn_shares_at_least_one_equipment(self):

        eqpts_of_remote_ip = set(self.remote_ip.ipv6equipament_set.all().
                                 values_list('equipamento', flat=True))
        eqpts_of_remote_asn = set(self.remote_asn.asnequipment_set.all().
                                  values_list('equipment', flat=True))

        if not set.intersection(eqpts_of_remote_ip, eqpts_of_remote_asn):
            raise RemoteIpAndRemoteAsnAtDifferentEquipmentsException(self)

    def check_if_peer_group_environments_has_local_ip_environment(self):

        # Check if PeerGroup Environments have the LocalIp Environment
        environments_of_peer_group = self.peer_group. \
            environmentpeergroup_set.all(). \
            values_list('environment', flat=True)
        environment_of_local_ip = self.local_ip.networkipv6.vlan. \
            ambiente.id

        if environment_of_local_ip not in environments_of_peer_group:
            raise LocalIpAndPeerGroupAtDifferentEnvironmentsException(self)

    def check_if_neighbor_is_not_duplicated(self):

        obj = NeighborV6.objects.filter(local_asn=self.local_asn.id,
                                        remote_asn=self.remote_asn.id,
                                        local_ip=self.local_ip.id,
                                        remote_ip=self.remote_ip.id,
                                        peer_group=self.peer_group.id)
        if obj:
            raise NeighborDuplicatedException(self)

    def validate_neighbor_v6(self, user):

        self.check_if_neighbor_already_deployed()
        check_permissions_in_peer_group(self, user)
        self.check_if_local_ip_vrf_is_the_same_as_remote_ip_vrf()
        self.check_if_local_ip_and_local_asn_shares_at_least_one_equipment()
        self.check_if_remote_ip_and_remote_asn_shares_at_least_one_equipment()
        self.check_if_peer_group_environments_has_local_ip_environment()
        self.check_if_neighbor_is_not_duplicated()


def check_permissions_in_peer_group(neighbor, user):

    obj_group_perm_general = get_model('api_ogp',
                                       'ObjectGroupPermissionGeneral')
    obj_group_perm = get_model('api_ogp',
                               'ObjectGroupPermission')

    # Peer Group General
    perms_general = obj_group_perm_general.objects.filter(
        Q(write=True),
        Q(user_group__id__in=user.grupos.all()),
        Q(object_type__name=AdminPermission.OBJ_TYPE_PEER_GROUP)
    )
    # Peer Group Specific
    perms_specific = obj_group_perm.objects.filter(
        Q(write=True),
        Q(object_value=neighbor.peer_group.id),
        Q(user_group__id__in=user.grupos.all()),
        Q(object_type__name=AdminPermission.OBJ_TYPE_PEER_GROUP)
    )

    if not perms_general and not perms_specific:
        raise DontHavePermissionForPeerGroupException(neighbor)
