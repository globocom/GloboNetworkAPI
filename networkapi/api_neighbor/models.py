# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.api_neighbor.v4 import exceptions
from networkapi.models.BaseModel import BaseModel


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

    def create_v4(self):
        """Create NeighborV4."""
        pass

    def update_v4(self):
        """Update NeighborV4."""
        pass

    def delete_v4(self):
        """Delete NeighborV4.
        """
        pass


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

    def create_v4(self):
        """Create NeighborV6."""
        pass

    def update_v4(self):
        """Update NeighborV6."""
        pass

    def delete_v4(self):
        """Delete NeighborV6.
        """
        pass
