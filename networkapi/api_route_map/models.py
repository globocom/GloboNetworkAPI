# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from networkapi.util.geral import get_model

from networkapi.api_route_map.v4 import exceptions
from networkapi.models.BaseModel import BaseModel

class RouteMapEntryAction:
    p = ('P', 'P')
    d = ('D', 'D')
    list_type = (p, d)

class RouteMap(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    name = models.CharField(
        blank=False,
        max_length=45,
        db_column='name'
    )

    log = logging.getLogger('RouteMap')

    class Meta(BaseModel.Meta):
        db_table = u'route_map'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get RouteMap by id.

        :return: RouteMap.

        :raise RouteMapNotFoundError: RouteMap not registered.
        :raise RouteMapError: Failed to search for the RouteMap.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return RouteMap.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'RouteMap not found. pk {}'.format(id))
            raise exceptions.RouteMapNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the RouteMap.')
            raise exceptions.RouteMapError(
                e, u'Failure to search the RouteMap.')

    def create_v4(self):
        """Create RouteMap."""
        pass

    def update_v4(self):
        """Update RouteMap."""
        pass

    def delete_v4(self):
        """Delete RouteMap.
        """
        pass


class RouteMapEntry(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    action = models.CharField(
        db_column='action',
        max_length=2,
        blank=False,
        choices=RouteMapEntryAction.list_type
    )

    action_reconfig = models.TextField(
        blank=False,
        db_column='action_reconfig'
    )

    order = models.IntegerField(
        db_column='order'
    )

    list_config_bgp = models.ForeignKey(
        'api_list_config_bgp.ListConfigBGP',
        db_column='id_list_config_bgp'
    )

    route_map = models.ForeignKey(
        'api_route_map.RouteMap',
        db_column='id_route_map'
    )

    log = logging.getLogger('RouteMapEntry')

    class Meta(BaseModel.Meta):
        db_table = u'route_map_entry'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get RouteMapEntry by id.

        :return: RouteMapEntry.

        :raise RouteMapEntryNotFoundError: RouteMapEntry not registered.
        :raise RouteMapEntryError: Failed to search for the RouteMapEntry.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return RouteMapEntry.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'RouteMapEntry not found. pk {}'.format(id))
            raise exceptions.RouteMapEntryNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the RouteMapEntry.')
            raise exceptions.RouteMapEntryError(
                e, u'Failure to search the RouteMapEntry.')

    def create_v4(self):
        """Create RouteMapEntry."""
        pass

    def update_v4(self):
        """Update RouteMapEntry."""
        pass

    def delete_v4(self):
        """Delete RouteMapEntry.
        """
        pass
