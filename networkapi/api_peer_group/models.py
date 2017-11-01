# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from networkapi.util.geral import get_model

from networkapi.api_peer_group.v4 import exceptions
from networkapi.models.BaseModel import BaseModel

class PeerGroup(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    name = models.CharField(
        blank=False,
        max_length=45,
        db_column='name'
    )

    route_map_in = models.ForeignKey(
        'api_route_map.RouteMap',
        db_column='id_route_map_in'
    )

    route_map_out = models.ForeignKey(
        'api_route_map.RouteMap',
        db_column='id_route_map_out'
    )

    log = logging.getLogger('PeerGroup')

    class Meta(BaseModel.Meta):
        db_table = u'peer_group'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get PeerGroup by id.

        :return: PeerGroup.

        :raise PeerGroupNotFoundError: PeerGroup not registered.
        :raise PeerGroupError: Failed to search for the PeerGroup.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return PeerGroup.objects.get(id=id)
        except ObjectDoesNotExist:
            cls.log.error(u'PeerGroup not found. pk {}'.format(id))
            raise exceptions.PeerGroupNotFoundError(id)
        except OperationalError:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError()
        except Exception:
            cls.log.error(u'Failure to search the PeerGroup.')
            raise exceptions.PeerGroupError(
                u'Failure to search the PeerGroup.')

    def create_v4(self):
        """Create PeerGroup."""
        pass

    def update_v4(self):
        """Update PeerGroup."""
        pass

    def delete_v4(self):
        """Delete PeerGroup.
        """
        pass


class EnvironmentPeerGroup(BaseModel):
    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    name = models.CharField(
        blank=False,
        max_length=45,
        db_column='name'
    )

    environment = models.ForeignKey(
        'ambiente.Ambiente',
        db_column='id_environment'
    )

    peer_group = models.ForeignKey(
        'api_peer_group.PeerGroup',
        db_column='id_peer_group'
    )

    log = logging.getLogger('EnvironmentPeerGroup')

    class Meta(BaseModel.Meta):
        db_table = u'environment_peer_group'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get EnvironmentPeerGroup by id.

        :return: EnvironmentPeerGroup.

        :raise EnvironmentPeerGroupNotFoundError: EnvironmentPeerGroup not registered.
        :raise EnvironmentPeerGroupError: Failed to search for the EnvironmentPeerGroup.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return EnvironmentPeerGroup.objects.get(id=id)
        except ObjectDoesNotExist:
            cls.log.error(u'EnvironmentPeerGroup not found. pk {}'.format(id))
            raise exceptions.EnvironmentPeerGroupNotFoundError(id)
        except OperationalError:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError()
        except Exception:
            cls.log.error(u'Failure to search the EnvironmentPeerGroup.')
            raise exceptions.EnvironmentPeerGroupError(
                u'Failure to search the EnvironmentPeerGroup.')

    def create_v4(self):
        """Create EnvironmentPeerGroup."""
        pass

    def update_v4(self):
        """Update EnvironmentPeerGroup."""
        pass

    def delete_v4(self):
        """Delete EnvironmentPeerGroup.
        """
        pass

