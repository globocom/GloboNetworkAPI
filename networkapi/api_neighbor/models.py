# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from networkapi.util.geral import get_model

from networkapi.api_neighbor.v4 import exceptions
from networkapi.models.BaseModel import BaseModel


class BgpType:
    ibgp = ('I', 'IBGP')
    ebgp = ('E', 'EBGP')
    list_type = (ibgp, ebgp)


class Neighbor(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    remote_as = models.CharField(
        blank=False,
        max_length=45,
        db_column='remote_as'
    )

    remote_ip = models.CharField(
        blank=False,
        max_length=45,
        db_column='remote_ip'
    )

    password = models.CharField(
        blank=True,
        max_length=45,
        db_column='password'
    )

    maximum_hops = models.CharField(
        blank=False,
        max_length=45,
        db_column='maximum_hops'
    )

    timer_keepalive = models.CharField(
        blank=False,
        max_length=45,
        db_column='timer_keepalive'
    )

    timer_timeout = models.CharField(
        blank=False,
        max_length=45,
        db_column='timer_timeout'
    )

    description = models.CharField(
        blank=False,
        max_length=45,
        db_column='description'
    )

    soft_reconfiguration = models.BooleanField(
        db_column='soft_reconfiguration')

    community = models.BooleanField(
        db_column='community')

    remove_private_as = models.BooleanField(
        db_column='remove_private_as')

    next_hop_self = models.BooleanField(
        db_column='next_hop_self')

    kind = models.CharField(
        db_column='kind',
        max_length=2,
        blank=False,
        choices=BgpType.list_type
    )

    created = models.BooleanField(db_column='created')

    virtual_interface = models.ForeignKey(
        'api_virtual_interface.VirtualInterface',
        db_column='id_virtual_interface'
    )

    log = logging.getLogger('Neighbor')

    class Meta(BaseModel.Meta):
        db_table = u'neighbor'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get Neighbor by id.

        :return: Neighbor.

        :raise NeighborNotFoundError: Neighbor not registered.
        :raise NeighborError: Failed to search for the As.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return Neighbor.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'Neighbor not found. pk {}'.format(id))
            raise exceptions.NeighborNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the Neighbor.')
            raise exceptions.NeighborError(
                e, u'Failure to search the Neighbor.')

    def create_v4(self, neighbor_map):
        """Create Neighbor."""

        vi_model = get_model('api_virtual_interface', 'VirtualInterface')

        self.remote_as = neighbor_map.get('remote_as')
        self.remote_ip = neighbor_map.get('remote_ip')
        self.password =  neighbor_map.get('password')
        self.maximum_hops =  neighbor_map.get('maximum_hops')
        self.timer_keepalive = neighbor_map.get('timer_keepalive')
        self.timer_timeout = neighbor_map.get('timer_timeout')
        self.description = neighbor_map.get('description')
        self.soft_reconfiguration = neighbor_map.get('soft_reconfiguration')
        self.community = neighbor_map.get('community')
        self.remove_private_as = neighbor_map.get('remove_private_as')
        self.next_hop_self = neighbor_map.get('next_hop_self')
        self.kind = neighbor_map.get('kind')
        # self.created =  neighbor_map.get('created')
        self.virtual_interface = vi_model.get_by_pk(
            neighbor_map.get('virtual_interface')
        )

        self.save()

    def update_v4(self, neighbor_map):
        """Update Neighbor."""

        vi_model = get_model('api_virtual_interface', 'VirtualInterface')

        self.remote_as = neighbor_map.get('remote_as')
        self.remote_ip = neighbor_map.get('remote_ip')
        self.password = neighbor_map.get('password')
        self.maximum_hops = neighbor_map.get('maximum_hops')
        self.timer_keepalive = neighbor_map.get('timer_keepalive')
        self.timer_timeout = neighbor_map.get('timer_timeout')
        self.description = neighbor_map.get('description')
        self.soft_reconfiguration = neighbor_map.get('soft_reconfiguration')
        self.community = neighbor_map.get('community')
        self.remove_private_as = neighbor_map.get('remove_private_as')
        self.next_hop_self = neighbor_map.get('next_hop_self')
        self.kind = neighbor_map.get('kind')
        # self.created =  neighbor_map.get('created')
        self.virtual_interface = vi_model.get_by_pk(
            neighbor_map.get('virtual_interface')
        )

        self.save()

    def delete_v4(self):
        """Delete Neighbor.
        """
        try:

            super(Neighbor, self).delete()

        except Exception, e:
            self.log.error(e)
            raise exceptions.NeighborErrorV4(e)
