# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.db.models import Q
from django.db.transaction import commit_on_success

from networkapi.api_neighbor.models import NeighborV4
from networkapi.api_neighbor.models import NeighborV6
from networkapi.api_neighbor.v4 import exceptions
from networkapi.api_neighbor.v4.exceptions import DontHavePermissionForPeerGroupException
from networkapi.api_neighbor.v4.exceptions import LocalIpAndLocalAsnAtDifferentEquipmentsException
from networkapi.api_neighbor.v4.exceptions import LocalIpAndPeerGroupAtDifferentEnvironmentsException
from networkapi.api_neighbor.v4.exceptions import LocalIpAndRemoteIpAreInDifferentVrfsException
from networkapi.api_neighbor.v4.exceptions import NeighborDuplicatedException
from networkapi.api_neighbor.v4.exceptions import NeighborV4Error
from networkapi.api_neighbor.v4.exceptions import NeighborV4NotFoundError
from networkapi.api_neighbor.v4.exceptions import NeighborV6Error
from networkapi.api_neighbor.v4.exceptions import NeighborV6NotFoundError
from networkapi.api_neighbor.v4.exceptions import RemoteIpAndRemoteAsnAtDifferentEquipmentsException
from networkapi.api_neighbor.v4.exceptions import \
    RouteMapsOfAssociatedPeerGroupAreNotDeployedException
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.api_route_map.models import RouteMap
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.plugins.factory import PluginFactory

log = logging.getLogger(__name__)


def get_neighbor_v4_by_search(search=dict()):
    """Return a list of NeighborV4's by dict."""

    try:
        objects = NeighborV4.objects.filter()
        object_map = build_query_to_datatable_v3(objects, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return object_map


def get_neighbor_v4_by_id(obj_id):
    """Return an NeighborV4 by id.

    Args:
        obj_id: Id of NeighborV4
    """

    try:
        obj = NeighborV4.get_by_pk(id=obj_id)
    except NeighborV4NotFoundError, e:
        raise exceptions.NeighborV4DoesNotExistException(str(e))

    return obj


def get_neighbor_v4_by_ids(obj_ids):
    """Return NeighborV4 list by ids.

    Args:
        obj_ids: List of Ids of NeighborV4's.
    """

    ids = list()
    for obj_id in obj_ids:
        try:
            obj = get_neighbor_v4_by_id(obj_id).id
            ids.append(obj)
        except exceptions.NeighborV4DoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

    return NeighborV4.objects.filter(id__in=ids)


def update_neighbor_v4(obj, user):
    """Update NeighborV4."""

    try:
        obj_to_update = get_neighbor_v4_by_id(obj.get('id'))
        obj_to_update.update_v4(obj, user)
    except NeighborV4Error, e:
        raise ValidationAPIException(str(e))
    except DontHavePermissionForPeerGroupException, e:
        raise ValidationAPIException(str(e))
    except LocalIpAndRemoteIpAreInDifferentVrfsException, e:
        raise ValidationAPIException(str(e))
    except LocalIpAndLocalAsnAtDifferentEquipmentsException, e:
        raise ValidationAPIException(str(e))
    except RemoteIpAndRemoteAsnAtDifferentEquipmentsException, e:
        raise ValidationAPIException(str(e))
    except LocalIpAndPeerGroupAtDifferentEnvironmentsException, e:
        raise ValidationAPIException(str(e))
    except NeighborDuplicatedException, e:
        raise ValidationAPIException(str(e))
    except exceptions.NeighborV4IsDeployed, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.NeighborV4DoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return obj_to_update


def create_neighbor_v4(obj, user):
    """Create NeighborV4."""

    try:
        obj_to_create = NeighborV4()
        obj_to_create.create_v4(obj, user)
    except NeighborV4Error, e:
        raise ValidationAPIException(str(e))
    except DontHavePermissionForPeerGroupException, e:
        raise ValidationAPIException(str(e))
    except LocalIpAndRemoteIpAreInDifferentVrfsException, e:
        raise ValidationAPIException(str(e))
    except LocalIpAndLocalAsnAtDifferentEquipmentsException, e:
        raise ValidationAPIException(str(e))
    except RemoteIpAndRemoteAsnAtDifferentEquipmentsException, e:
        raise ValidationAPIException(str(e))
    except LocalIpAndPeerGroupAtDifferentEnvironmentsException, e:
        raise ValidationAPIException(str(e))
    except NeighborDuplicatedException, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return obj_to_create


def delete_neighbor_v4(obj_ids):
    """Delete NeighborV4."""

    for obj_id in obj_ids:
        try:
            obj_to_delete = get_neighbor_v4_by_id(obj_id)
            obj_to_delete.delete_v4()
        except exceptions.NeighborV4DoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except exceptions.NeighborV4IsDeployed, e:
            raise ValidationAPIException(str(e))
        except NeighborV4Error, e:
            raise NetworkAPIException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))


def get_neighbor_v6_by_search(search=dict()):
    """Return a list of NeighborV6's by dict."""

    try:
        objects = NeighborV6.objects.filter()
        object_map = build_query_to_datatable_v3(objects, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return object_map


def get_neighbor_v6_by_id(obj_id):
    """Return an NeighborV6 by id.

    Args:
        obj_id: Id of NeighborV6
    """

    try:
        obj = NeighborV6.get_by_pk(id=obj_id)
    except NeighborV6NotFoundError, e:
        raise exceptions.NeighborV6DoesNotExistException(str(e))

    return obj


def get_neighbor_v6_by_ids(obj_ids):
    """Return NeighborV6 list by ids.

    Args:
        obj_ids: List of Ids of NeighborV6's.
    """

    ids = list()
    for obj_id in obj_ids:
        try:
            obj = get_neighbor_v6_by_id(obj_id).id
            ids.append(obj)
        except exceptions.NeighborV6DoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

    return NeighborV6.objects.filter(id__in=ids)


def update_neighbor_v6(obj, user):
    """Update NeighborV6."""

    try:
        obj_to_update = get_neighbor_v6_by_id(obj.get('id'))
        obj_to_update.update_v4(obj, user)
    except NeighborV6Error, e:
        raise ValidationAPIException(str(e))
    except DontHavePermissionForPeerGroupException, e:
        raise ValidationAPIException(str(e))
    except LocalIpAndRemoteIpAreInDifferentVrfsException, e:
        raise ValidationAPIException(str(e))
    except LocalIpAndLocalAsnAtDifferentEquipmentsException, e:
        raise ValidationAPIException(str(e))
    except RemoteIpAndRemoteAsnAtDifferentEquipmentsException, e:
        raise ValidationAPIException(str(e))
    except LocalIpAndPeerGroupAtDifferentEnvironmentsException, e:
        raise ValidationAPIException(str(e))
    except NeighborDuplicatedException, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.NeighborV6DoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return obj_to_update


def create_neighbor_v6(obj, user):
    """Create NeighborV6."""

    try:
        obj_to_create = NeighborV6()
        obj_to_create.create_v4(obj, user)
    except NeighborV6Error, e:
        raise ValidationAPIException(str(e))
    except DontHavePermissionForPeerGroupException, e:
        raise ValidationAPIException(str(e))
    except LocalIpAndRemoteIpAreInDifferentVrfsException, e:
        raise ValidationAPIException(str(e))
    except LocalIpAndLocalAsnAtDifferentEquipmentsException, e:
        raise ValidationAPIException(str(e))
    except RemoteIpAndRemoteAsnAtDifferentEquipmentsException, e:
        raise ValidationAPIException(str(e))
    except LocalIpAndPeerGroupAtDifferentEnvironmentsException, e:
        raise ValidationAPIException(str(e))
    except NeighborDuplicatedException, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return obj_to_create


def delete_neighbor_v6(obj_ids):
    """Delete NeighborV6."""

    for obj_id in obj_ids:
        try:
            obj_to_delete = get_neighbor_v6_by_id(obj_id)
            obj_to_delete.delete_v4()
        except exceptions.NeighborV6DoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except NeighborV6Error, e:
            raise NetworkAPIException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))


@commit_on_success
def deploy_neighbors_v4(neighbors):

    ids_peers = [neighbor.get('peer_group').get('id')
                 for neighbor in neighbors]
    check_route_maps_are_deployed(ids_peers)

    # TODO Get the correct equipment to manage
    for neighbor in neighbors:
        equipment = None
        plugin = PluginFactory.factory(equipment)
        plugin.bgp().deploy_neighbor()

    ids = [neighbor.get('id') for neighbor in neighbors]
    NeighborV4.objects.filter(id__in=ids).update(created=True)


@commit_on_success
def undeploy_neighbors_v4(neighbors):

    # TODO Get the correct equipment to manage
    for neighbor in neighbors:
        equipment = None
        plugin = PluginFactory.factory(equipment)
        plugin.bgp().undeploy_neighbor()

    ids = [neighbor.get('id') for neighbor in neighbors]
    NeighborV4.objects.filter(id__in=ids).update(created=False)


@commit_on_success
def deploy_neighbors_v6(neighbors):

    ids_peers = [neighbor.get('peer_group').get('id')
                 for neighbor in neighbors]
    check_route_maps_are_deployed(ids_peers)

    # TODO Get the correct equipment to manage
    for neighbor in neighbors:
        equipment = None
        plugin = PluginFactory.factory(equipment)
        plugin.bgp().deploy_neighbor()

    ids = [neighbor.get('id') for neighbor in neighbors]
    NeighborV6.objects.filter(id__in=ids).update(created=True)


@commit_on_success
def undeploy_neighbors_v6(neighbors):

    ids_peers = [neighbor.get('peer_group').get('id')
                 for neighbor in neighbors]

    # TODO Get the correct equipment to manage
    for neighbor in neighbors:
        equipment = None
        plugin = PluginFactory.factory(equipment)
        plugin.bgp().undeploy_neighbor()

    ids = [neighbor.get('id') for neighbor in neighbors]
    NeighborV6.objects.filter(id__in=ids).update(created=False)


def check_route_maps_are_deployed(ids_peers):

    route_maps = RouteMap.objects.filter(
        Q(created=False),
        Q(peergroup_route_map_in__id__in=ids_peers) |
        Q(peergroup_route_map_out__id__in=ids_peers)
    )

    if route_maps:
        raise RouteMapsOfAssociatedPeerGroupAreNotDeployedException(route_maps)
