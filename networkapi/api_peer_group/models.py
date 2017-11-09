# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.admin_permission import AdminPermission
from networkapi.api_peer_group.v4 import exceptions
from networkapi.api_peer_group.v4.exceptions import \
    EnvironmentPeerGroupDuplicatedException
from networkapi.api_peer_group.v4.exceptions import \
    PeerGroupDuplicatedException
from networkapi.models.BaseModel import BaseModel
from networkapi.util.geral import get_model


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
        db_column='id_route_map_in',
        related_name='peergroup_route_map_in'
    )

    route_map_out = models.ForeignKey(
        'api_route_map.RouteMap',
        db_column='id_route_map_out',
        related_name='peergroup_route_map_out'
    )

    def _get_environments(self):
        return self.environmentpeergroup_set.all()

    environments = property(_get_environments)

    def _get_environments_id(self):
        return self.environmentpeergroup_set.all().values_list('id',
                                                               flat=True)

    environments_id = property(_get_environments_id)

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

    def create_v4(self, peer_group, user):
        """Create PeerGroup."""

        self.name = peer_group.get('name')

        routemap_model = get_model('api_route_map', 'RouteMap')

        route_map_in_id = peer_group.get('route_map_in')
        route_map_out_id = peer_group.get('route_map_out')

        self.route_map_in = routemap_model.get_by_pk(route_map_in_id)
        self.route_map_out = routemap_model.get_by_pk(route_map_out_id)

        # check if peer group already exists
        obj = PeerGroup.objects.filter(route_map_in=route_map_in_id,
                                       route_map_out=route_map_out_id)
        if obj:
            raise PeerGroupDuplicatedException(self)

        self.save()

        # Save relationships with environments
        environment_peergroup_model = get_model('api_peer_group',
                                                'EnvironmentPeerGroup')
        for id_environment in peer_group.get('environments'):
            environment_peergroup_model().create_v4({
                'peer_group': self.id,
                'environment': id_environment
            })

        # Permissions
        object_group_perm_model = get_model('api_ogp', 'ObjectGroupPermission')
        object_group_perm_model().create_perms(
            peer_group, self.id, AdminPermission.OBJ_TYPE_PEER_GROUP, user)

    def update_v4(self, peer_group, user):
        """Update PeerGroup."""

        self.name = peer_group.get('name')

        routemap_model = get_model('api_route_map', 'RouteMap')

        route_map_in_id = peer_group.get('route_map_in')
        route_map_out_id = peer_group.get('route_map_out')

        self.route_map_in = routemap_model.get_by_pk(route_map_in_id)
        self.route_map_out = routemap_model.get_by_pk(route_map_out_id)

        # check if peer group already exists
        obj = PeerGroup.objects.filter(route_map_in=route_map_in_id,
                                       route_map_out=route_map_out_id)
        if obj:
            raise PeerGroupDuplicatedException(self)

        self.save()

        self.save()

        environment_ids = peer_group.get('environments')

        # Get current associates
        current = self.environmentpeergroup_set \
            .filter(environment__in=environment_ids) \
            .values_list('environment', flat=True)

        # Creates new associate
        for id_environment in environment_ids:
            if id_environment not in current:
                EnvironmentPeerGroup().create_v4({
                    'peer_group': self.id,
                    'environment': id_environment
                })

        # Removes old associates
        for environment_peer_group in self.environmentpeergroup_set\
                .exclude(environment__in=environment_ids):
            environment_peer_group.delete_v4()

        # Permissions
        object_group_perm_model = get_model('api_ogp',
                                            'ObjectGroupPermission')
        object_group_perm_model().update_perms(
            peer_group, self.id, AdminPermission.OBJ_TYPE_PEER_GROUP, user)

    def delete_v4(self):
        """Delete PeerGroup."""

        # Deletes Permissions
        object_group_perm_model = get_model('api_ogp',
                                            'ObjectGroupPermission')
        object_group_perm_model.objects.filter(
            object_type__name=AdminPermission.OBJ_TYPE_PEER_GROUP,
            object_value=self.id
        ).delete()

        for environment_peergroup in self.environmentpeergroup_set.all():
            environment_peergroup.delete_v4()

        super(PeerGroup, self).delete()


class EnvironmentPeerGroup(BaseModel):
    id = models.AutoField(
        primary_key=True,
        db_column='id'
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

    def create_v4(self, environment_peergroup):
        """Create EnvironmentPeerGroup."""

        environment_model = get_model('ambiente', 'Ambiente')

        environment_id = environment_peergroup.get('environment')
        peer_group_id = environment_peergroup.get('peer_group')

        # check if already exists relationship
        obj = EnvironmentPeerGroup.objects.filter(environment=environment_id,
                                                  peer_group=peer_group_id)
        if obj:
            raise EnvironmentPeerGroupDuplicatedException(self)

        self.environment = environment_model.get_by_pk(environment_id)
        self.peer_group = PeerGroup.get_by_pk(peer_group_id)

        self.save()

    def delete_v4(self):
        """Delete EnvironmentPeerGroup."""

        super(EnvironmentPeerGroup, self).delete()
