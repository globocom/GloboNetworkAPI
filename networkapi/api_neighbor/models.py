# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.api_neighbor.v4 import exceptions
from networkapi.api_neighbor.v4.exceptions import \
    LocalIpAndLocalAsnBelongToDifferentEquipmentsException
from networkapi.api_neighbor.v4.exceptions import \
    LocalIpAndPeerGroupBelongToDifferentEnvironmentsException
from networkapi.api_neighbor.v4.exceptions import \
    LocalIpAndRemoteIpAreInDifferentVrfsException
from networkapi.api_neighbor.v4.exceptions import \
    RemoteIpAndRemoteAsnBelongToDifferentEquipmentsException
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

    def create_v4(self, neighbor):
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

        validate_if_neighbor_can_be_save(self, 'v4')

        self.save()

    def update_v4(self, neighbor):
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

        validate_if_neighbor_can_be_save(self, 'v4')

        self.save()

    def delete_v4(self):
        """Delete NeighborV4."""

        super(NeighborV4, self).delete()


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

    def create_v4(self, neighbor):
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

        validate_if_neighbor_can_be_save(self, 'v6')

        self.save()

    def update_v4(self, neighbor):
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

        validate_if_neighbor_can_be_save(self, 'v6')

        self.save()

    def delete_v4(self):
        """Delete NeighborV6."""

        super(NeighborV6, self).delete()


def validate_if_neighbor_can_be_save(neighbor, type):

    if type == 'v4':

        if neighbor.local_ip.networkipv4.vlan.ambiente.default_vrf != \
           neighbor.remote_ip.networkipv4.vlan.ambiente.default_vrf:
            raise LocalIpAndRemoteIpAreInDifferentVrfsException(neighbor)

        equipments_of_local_ip = neighbor.local_ip.ipequipamento_set.all().\
            values_list('equipamento', flat=True)

        equipment_of_local_asn = neighbor.local_asn.asnequipment_set.all().\
            values_list('equipment', flat=True)[0]

        if equipment_of_local_asn not in equipments_of_local_ip:
            raise LocalIpAndLocalAsnBelongToDifferentEquipmentsException(
                neighbor)

        equipments_of_remote_ip = neighbor.remote_ip.ipequipamento_set.all().\
            values_list('equipamento', flat=True)

        equipment_of_remote_asn = neighbor.remote_asn.asnequipment_set.all().\
            values_list('equipment', flat=True)[0]

        if equipment_of_remote_asn not in equipments_of_remote_ip:
            raise RemoteIpAndRemoteAsnBelongToDifferentEquipmentsException(
                neighbor)

        if neighbor.peer_group:
            environments_of_peer_group = neighbor.peer_group.\
                environmentpeergroup_set.all().\
                values_list('environment', flat=True)
            environment_of_local_ip = neighbor.local_ip.networkipv4.vlan.\
                ambiente.id

            if environment_of_local_ip not in environments_of_peer_group:
                raise \
                    LocalIpAndPeerGroupBelongToDifferentEnvironmentsException(
                        neighbor)

    elif type == 'v6':

        if neighbor.local_ip.networkipv6.vlan.ambiente.default_vrf != \
                neighbor.remote_ip.networkipv6.vlan.ambiente.default_vrf:
            raise LocalIpAndRemoteIpAreInDifferentVrfsException(neighbor)

        equipments_of_local_ip = neighbor.local_ip.ipv6equipament_set.all().\
            values_list('equipamento', flat=True)

        equipment_of_local_asn = neighbor.local_asn.asnequipment_set.all().\
            values_list('equipment', flat=True)[0]

        if equipment_of_local_asn not in equipments_of_local_ip:
            raise LocalIpAndLocalAsnBelongToDifferentEquipmentsException(
                neighbor)

        equipments_of_remote_ip = neighbor.remote_ip.ipv6equipament_set.all().\
            values_list('equipamento', flat=True)

        equipment_of_remote_asn = neighbor.remote_asn.asnequipment_set.all().\
            values_list('equipment', flat=True)[0]

        if equipment_of_remote_asn not in equipments_of_remote_ip:
            raise RemoteIpAndRemoteAsnBelongToDifferentEquipmentsException(
                neighbor)

        if neighbor.peer_group:
            environments_of_peer_group = neighbor.peer_group.\
                environmentpeergroup_set.all().\
                values_list('environment', flat=True)
            environment_of_local_ip = neighbor.local_ip.networkipv6.vlan.\
                ambiente.id

            if environment_of_local_ip not in environments_of_peer_group:
                raise \
                    LocalIpAndPeerGroupBelongToDifferentEnvironmentsException(
                        neighbor)
