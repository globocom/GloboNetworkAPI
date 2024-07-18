# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q

from networkapi.api_list_config_bgp.v4 import exceptions
from networkapi.api_list_config_bgp.v4.exceptions import \
    ListConfigBGPAssociatedToRouteMapEntryException
from networkapi.api_list_config_bgp.v4.exceptions import \
    ListConfigBGPIsDeployedException
from networkapi.api_neighbor.models import NeighborV4
from networkapi.api_neighbor.models import NeighborV6
from networkapi.models.BaseModel import BaseModel
from networkapi.util.geral import get_model


class ListConfigBGPType:
    p = ('P', 'P')
    a = ('A', 'A')
    c = ('C', 'C')
    list_type = (p, a, c)


class ListConfigBGP(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    name = models.CharField(
        blank=False,
        max_length=100,
        db_column='name'
    )

    type = models.CharField(
        db_column='type',
        max_length=2,
        blank=False,
        choices=ListConfigBGPType.list_type
    )

    config = models.TextField(
        blank=False,
        db_column='config'
    )

    equipments = models.ManyToManyField(
        'equipamento.Equipamento',
        through='EquipmentListConfig'
    )

    log = logging.getLogger('ListConfigBGP')

    class Meta(BaseModel.Meta):
        db_table = u'list_config_bgp'
        managed = True

    def _get_route_map_entries(self):
        return self.routemapentry_set.all()

    route_map_entries = property(_get_route_map_entries)

    def _get_route_map_entries_id(self):
        return map(int,
                   self.routemapentry_set.all().values_list('id', flat=True))

    route_map_entries_id = property(_get_route_map_entries_id)

    @classmethod
    def get_by_pk(cls, id):
        """Get ListConfigBGP by id.

        :return: ListConfigBGP.

        :raise ListConfigBGPNotFoundError: ListConfigBGP not registered.
        :raise ListConfigBGPError: Failed to search for the ListConfigBGP.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return ListConfigBGP.objects.get(id=id)
        except ObjectDoesNotExist:
            cls.log.error(u'ListConfigBGP not found. pk {}'.format(id))
            raise exceptions.ListConfigBGPNotFoundError(id)
        except OperationalError:
            cls.log.error(u'Lock wait timeout exceeded')
            raise OperationalError()
        except Exception:
            cls.log.error(u'Failure to search the ListConfigBGP')
            raise exceptions.ListConfigBGPError(
                u'Failure to search the ListConfigBGP')

    def create_v4(self, list_config_bgp):
        """Create ListConfigBGP."""

        self.name = list_config_bgp.get('name')
        self.type = list_config_bgp.get('type')
        self.config = list_config_bgp.get('config')

        self.save()

    def update_v4(self, list_config_bgp):
        """Update ListConfigBGP."""

        self.name = list_config_bgp.get('name')
        self.type = list_config_bgp.get('type')
        self.config = list_config_bgp.get('config')

        # Validate
        self.validate_list_config_bgp()

        self.save()

    def delete_v4(self):
        """Delete ListConfigBGP."""

        if self.routemapentry_set.count() > 0:
            raise ListConfigBGPAssociatedToRouteMapEntryException(self)

        super(ListConfigBGP, self).delete()

    def validate_list_config_bgp(self):

        routemapentry_set = self.routemapentry_set.all()
        neighbors_v4 = NeighborV4.objects.filter(
            Q(created=True),
            Q(peer_group__route_map_in__routemapentry__in=routemapentry_set) |
            Q(peer_group__route_map_out__routemapentry__in=routemapentry_set)
        )

        neighbors_v6 = NeighborV6.objects.filter(
            Q(created=True),
            Q(peer_group__route_map_in__routemapentry__in=routemapentry_set) |
            Q(peer_group__route_map_out__routemapentry__in=routemapentry_set)
        )

        if neighbors_v4 or neighbors_v6:
            raise ListConfigBGPIsDeployedException(self,
                                                   neighbors_v4, neighbors_v6)


class EquipmentListConfig(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    equipment = models.ForeignKey(
        'equipamento.Equipamento',
        db_column='id_equipment'
    )
    list_config_bgp = models.ForeignKey(
        'api_list_config_bgp.ListConfigBGP',
        db_column='id'
    )

    class Meta(BaseModel.Meta):
        db_table = u'equipment_list_config_bgp'
        managed = True

    def create_v4(self, list_config_bgp):

        eqpt_model = get_model('equipamento', 'Equipamento')

        self.equipment = eqpt_model.get_by_pk(
            list_config_bgp.get('equipment'))
        self.list_config_bgp = ListConfigBGP.get_by_pk(
            list_config_bgp.get('list_config_bgp'))
        self.save()
