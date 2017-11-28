# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.db.transaction import commit_on_success

from networkapi.api_neighbor.models import NeighborV4
from networkapi.api_neighbor.models import NeighborV6
from networkapi.api_neighbor.v4.exceptions import DontHavePermissionForPeerGroupException
from networkapi.api_neighbor.v4.exceptions import \
    LocalIpAndLocalAsnAtDifferentEquipmentsException
from networkapi.api_neighbor.v4.exceptions import \
    LocalIpAndPeerGroupAtDifferentEnvironmentsException
from networkapi.api_neighbor.v4.exceptions import \
    LocalIpAndRemoteIpAreInDifferentVrfsException
from networkapi.api_neighbor.v4.exceptions import NeighborDuplicatedException
from networkapi.api_neighbor.v4.exceptions import NeighborV4DoesNotExistException
from networkapi.api_neighbor.v4.exceptions import NeighborV4Error
from networkapi.api_neighbor.v4.exceptions import NeighborV4IsDeployed
from networkapi.api_neighbor.v4.exceptions import NeighborV4IsUndeployed
from networkapi.api_neighbor.v4.exceptions import NeighborV4NotFoundError
from networkapi.api_neighbor.v4.exceptions import NeighborV6DoesNotExistException
from networkapi.api_neighbor.v4.exceptions import NeighborV6Error
from networkapi.api_neighbor.v4.exceptions import NeighborV6IsDeployed
from networkapi.api_neighbor.v4.exceptions import NeighborV6IsUndeployed
from networkapi.api_neighbor.v4.exceptions import NeighborV6NotFoundError
from networkapi.api_neighbor.v4.exceptions import \
    RemoteIpAndRemoteAsnAtDifferentEquipmentsException
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.distributedlock import LOCK_LIST_CONFIG_BGP
from networkapi.distributedlock import LOCK_NEIGHBOR
from networkapi.distributedlock import LOCK_NEIGHBOR_V4
from networkapi.distributedlock import LOCK_NEIGHBOR_V6
from networkapi.distributedlock import LOCK_PEER_GROUP
from networkapi.distributedlock import LOCK_ROUTE_MAP
from networkapi.distributedlock import LOCK_ROUTE_MAP_ENTRY
from networkapi.equipamento.models import Equipamento
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.plugins.factory import PluginFactory
from networkapi.util.geral import create_lock_with_blocking
from networkapi.util.geral import destroy_lock

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
    except NeighborV4NotFoundError as e:
        raise NeighborV4DoesNotExistException(str(e))

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
        except NeighborV4DoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except Exception as e:
            raise NetworkAPIException(str(e))

    return NeighborV4.objects.filter(id__in=ids)


def update_neighbor_v4(obj, user):
    """Update NeighborV4."""

    try:
        obj_to_update = get_neighbor_v4_by_id(obj.get('id'))
        obj_to_update.update_v4(obj, user)
    except NeighborV4Error as e:
        raise ValidationAPIException(str(e))
    except DontHavePermissionForPeerGroupException as e:
        raise ValidationAPIException(str(e))
    except LocalIpAndRemoteIpAreInDifferentVrfsException as e:
        raise ValidationAPIException(str(e))
    except LocalIpAndLocalAsnAtDifferentEquipmentsException as e:
        raise ValidationAPIException(str(e))
    except RemoteIpAndRemoteAsnAtDifferentEquipmentsException as e:
        raise ValidationAPIException(str(e))
    except LocalIpAndPeerGroupAtDifferentEnvironmentsException as e:
        raise ValidationAPIException(str(e))
    except NeighborDuplicatedException as e:
        raise ValidationAPIException(str(e))
    except NeighborV4IsDeployed as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except NeighborV4DoesNotExistException as e:
        raise ObjectDoesNotExistException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return obj_to_update


def create_neighbor_v4(obj, user):
    """Create NeighborV4."""

    try:
        obj_to_create = NeighborV4()
        obj_to_create.create_v4(obj, user)
    except NeighborV4Error as e:
        raise ValidationAPIException(str(e))
    except DontHavePermissionForPeerGroupException as e:
        raise ValidationAPIException(str(e))
    except LocalIpAndRemoteIpAreInDifferentVrfsException as e:
        raise ValidationAPIException(str(e))
    except LocalIpAndLocalAsnAtDifferentEquipmentsException as e:
        raise ValidationAPIException(str(e))
    except RemoteIpAndRemoteAsnAtDifferentEquipmentsException as e:
        raise ValidationAPIException(str(e))
    except LocalIpAndPeerGroupAtDifferentEnvironmentsException as e:
        raise ValidationAPIException(str(e))
    except NeighborDuplicatedException as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return obj_to_create


def delete_neighbor_v4(obj_ids):
    """Delete NeighborV4."""

    for obj_id in obj_ids:
        try:
            obj_to_delete = get_neighbor_v4_by_id(obj_id)
            obj_to_delete.delete_v4()
        except NeighborV4DoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except NeighborV4IsDeployed as e:
            raise ValidationAPIException(str(e))
        except NeighborV4Error as e:
            raise NetworkAPIException(str(e))
        except Exception as e:
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
    except NeighborV6NotFoundError as e:
        raise NeighborV6DoesNotExistException(str(e))

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
        except NeighborV6DoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except Exception as e:
            raise NetworkAPIException(str(e))

    return NeighborV6.objects.filter(id__in=ids)


def update_neighbor_v6(obj, user):
    """Update NeighborV6."""

    try:
        obj_to_update = get_neighbor_v6_by_id(obj.get('id'))
        obj_to_update.update_v4(obj, user)
    except NeighborV6Error as e:
        raise ValidationAPIException(str(e))
    except DontHavePermissionForPeerGroupException as e:
        raise ValidationAPIException(str(e))
    except LocalIpAndRemoteIpAreInDifferentVrfsException as e:
        raise ValidationAPIException(str(e))
    except LocalIpAndLocalAsnAtDifferentEquipmentsException as e:
        raise ValidationAPIException(str(e))
    except RemoteIpAndRemoteAsnAtDifferentEquipmentsException as e:
        raise ValidationAPIException(str(e))
    except LocalIpAndPeerGroupAtDifferentEnvironmentsException as e:
        raise ValidationAPIException(str(e))
    except NeighborDuplicatedException as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except NeighborV6DoesNotExistException as e:
        raise ObjectDoesNotExistException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return obj_to_update


def create_neighbor_v6(obj, user):
    """Create NeighborV6."""

    try:
        obj_to_create = NeighborV6()
        obj_to_create.create_v4(obj, user)
    except NeighborV6Error as e:
        raise ValidationAPIException(str(e))
    except DontHavePermissionForPeerGroupException as e:
        raise ValidationAPIException(str(e))
    except LocalIpAndRemoteIpAreInDifferentVrfsException as e:
        raise ValidationAPIException(str(e))
    except LocalIpAndLocalAsnAtDifferentEquipmentsException as e:
        raise ValidationAPIException(str(e))
    except RemoteIpAndRemoteAsnAtDifferentEquipmentsException as e:
        raise ValidationAPIException(str(e))
    except LocalIpAndPeerGroupAtDifferentEnvironmentsException as e:
        raise ValidationAPIException(str(e))
    except NeighborDuplicatedException as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return obj_to_create


def delete_neighbor_v6(obj_ids):
    """Delete NeighborV6."""

    for obj_id in obj_ids:
        try:
            obj_to_delete = get_neighbor_v6_by_id(obj_id)
            obj_to_delete.delete_v4()
        except NeighborV6DoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except NeighborV6Error as e:
            raise NetworkAPIException(str(e))
        except Exception as e:
            raise NetworkAPIException(str(e))


@commit_on_success
def deploy_neighbor_v4(neighbor_id):

    neighbor = NeighborV4.objects.get(id=neighbor_id)

    if neighbor.created:
        raise NeighborV4IsDeployed(neighbor)

    locks_list = lock_resources_used_by_neighbor_v4(neighbor)

    try:
        depl_v4 = get_created_neighbors_v4_shares_same_eqpt_and_peer(neighbor)
        depl_v6 = get_created_neighbors_v6_shares_same_eqpt_and_peer(neighbor)

        eqpt = get_v4_equipment(neighbor)

        plugin = PluginFactory.factory(eqpt)

        # Only if not exists other deployed neighbors sharing same
        # peer group and equipment with the neighbor that will be deployed,
        # deploy also RouteMaps and ListsConfigBGP.
        if not depl_v4 and not depl_v6:

            # Concatenate RouteMapEntries Lists
            rms = neighbor.peer_group.route_map_in.route_map_entries | \
                neighbor.peer_group.route_map_out.route_map_entries
            for rm_entry in rms:
                deploy_list_config_bgp(rm_entry.list_config_bgp, plugin)

            deploy_route_map(neighbor.peer_group.route_map_in, plugin)
            deploy_route_map(neighbor.peer_group.route_map_out, plugin)

        # TODO deploys neighbor
        # plugin.bgp()

        neighbor.update(created=True)

    except Exception as e:
        raise NetworkAPIException(str(e))

    finally:
        destroy_lock(locks_list)


@commit_on_success
def undeploy_neighbor_v4(neighbor_id):

    neighbor = NeighborV4.objects.get(id=neighbor_id)

    if not neighbor.created:
        raise NeighborV4IsUndeployed(neighbor)

    locks_list = lock_resources_used_by_neighbor_v4(neighbor)

    try:
        depl_v4 = get_created_neighbors_v4_shares_same_eqpt_and_peer(neighbor)
        depl_v6 = get_created_neighbors_v6_shares_same_eqpt_and_peer(neighbor)

        eqpt = get_v4_equipment(neighbor)

        plugin = PluginFactory.factory(eqpt)

        # TODO undeploys neighbor
        # plugin.bgp()

        # Only if not exists other deployed neighbors sharing same
        # peer group and the same equipment, undeploy also RouteMaps
        # and ListsConfigBGP.
        if depl_v4.count() + depl_v6.count() == 1:

            undeploy_route_map(neighbor.peer_group.route_map_in, plugin)
            undeploy_route_map(neighbor.peer_group.route_map_out, plugin)

            # Concatenate RouteMapEntries Lists
            rms = neighbor.peer_group.route_map_in.route_map_entries | \
                neighbor.peer_group.route_map_out.route_map_entries
            for rm_entry in rms:
                undeploy_list_config_bgp(rm_entry.list_config_bgp, plugin)

        neighbor.update(created=False)

    except Exception as e:
        raise NetworkAPIException(str(e))

    finally:
        destroy_lock(locks_list)


@commit_on_success
def deploy_neighbor_v6(neighbor_id):

    neighbor = NeighborV6.objects.get(id=neighbor_id)

    if neighbor.created:
        raise NeighborV6IsDeployed(neighbor)

    locks_list = lock_resources_used_by_neighbor_v6(neighbor)

    try:
        depl_v4 = get_created_neighbors_v4_shares_same_eqpt_and_peer(neighbor)
        depl_v6 = get_created_neighbors_v6_shares_same_eqpt_and_peer(neighbor)

        eqpt = get_v6_equipment(neighbor)

        plugin = PluginFactory.factory(eqpt)

        # Only if not exists other deployed neighbors sharing same
        # peer group and equipment with the neighbor that will be deployed,
        # deploy also RouteMaps and ListsConfigBGP.
        if not depl_v4 and not depl_v6:

            # Concatenate RouteMapEntries Lists
            rms = neighbor.peer_group.route_map_in.route_map_entries | \
                neighbor.peer_group.route_map_out.route_map_entries
            for rm_entry in rms:
                deploy_list_config_bgp(rm_entry.list_config_bgp, plugin)

            deploy_route_map(neighbor.peer_group.route_map_in, plugin)
            deploy_route_map(neighbor.peer_group.route_map_out, plugin)

        # TODO deploys neighbor
        # plugin.bgp()

        neighbor.update(created=True)

    except Exception as e:
        raise NetworkAPIException(str(e))

    finally:
        destroy_lock(locks_list)


@commit_on_success
def undeploy_neighbor_v6(neighbor_id):

    neighbor = NeighborV6.objects.get(id=neighbor_id)

    if not neighbor.created:
        raise NeighborV6IsUndeployed(neighbor)

    locks_list = lock_resources_used_by_neighbor_v6(neighbor)

    try:
        depl_v4 = get_created_neighbors_v4_shares_same_eqpt_and_peer(neighbor)
        depl_v6 = get_created_neighbors_v6_shares_same_eqpt_and_peer(neighbor)

        eqpt = get_v6_equipment(neighbor)

        plugin = PluginFactory.factory(eqpt)

        # TODO undeploys neighbor
        # plugin.bgp()

        # Only if not exists other deployed neighbors sharing same
        # peer group and the same equipment, undeploy also RouteMaps
        # and ListsConfigBGP.
        if depl_v4.count() + depl_v6.count() == 1:

            undeploy_route_map(neighbor.peer_group.route_map_in, plugin)
            undeploy_route_map(neighbor.peer_group.route_map_out, plugin)

            # Concatenate RouteMapEntries Lists
            rms = neighbor.peer_group.route_map_in.route_map_entries | \
                neighbor.peer_group.route_map_out.route_map_entries
            for rm_entry in rms:
                undeploy_list_config_bgp(rm_entry.list_config_bgp, plugin)

        neighbor.update(created=False)

    except Exception as e:
        raise NetworkAPIException(str(e))

    finally:
        destroy_lock(locks_list)


def deploy_list_config_bgp(list_config_bgp, plugin):
    pass
    # deploys neighbor
    # plugin.bgp()


def deploy_route_map(route_map, plugin):
    pass
    # deploys neighbor
    # plugin.bgp()


def undeploy_list_config_bgp(list_config_bgp, plugin):
    pass
    # deploys neighbor
    # plugin.bgp()


def undeploy_route_map(route_map, plugin):
    pass
    # deploys neighbor
    # plugin.bgp()


def lock_resources_used_by_neighbor_v4(neighbor):

    locks_name = list()
    locks_name.append(LOCK_NEIGHBOR_V4 % neighbor.id)
    locks_name.append(LOCK_PEER_GROUP % neighbor.peer_group_id)
    locks_name.append(LOCK_ROUTE_MAP % neighbor.peer_group.route_map_in_id)

    for route_map_entry in neighbor.peer_group.route_map_in:
        locks_name.append(LOCK_ROUTE_MAP_ENTRY %
                          route_map_entry.id)
        locks_name.append(LOCK_LIST_CONFIG_BGP %
                          route_map_entry.list_config_bgp_id)

    for route_map_entry in neighbor.peer_group.route_map_out:
        locks_name.append(LOCK_ROUTE_MAP_ENTRY %
                          route_map_entry.id)
        locks_name.append(LOCK_LIST_CONFIG_BGP %
                          route_map_entry.list_config_bgp_id)

    # Remove duplicates locks
    locks_name = list(set(locks_name))
    return create_lock_with_blocking(locks_name)


def lock_resources_used_by_neighbor_v6(neighbor):

    locks_name = list()
    locks_name.append(LOCK_NEIGHBOR_V6 % neighbor.id)
    locks_name.append(LOCK_PEER_GROUP % neighbor.peer_group_id)
    locks_name.append(LOCK_ROUTE_MAP % neighbor.peer_group.route_map_in_id)

    for route_map_entry in neighbor.peer_group.route_map_in:
        locks_name.append(LOCK_ROUTE_MAP_ENTRY %
                          route_map_entry.id)
        locks_name.append(LOCK_LIST_CONFIG_BGP %
                          route_map_entry.list_config_bgp_id)

    for route_map_entry in neighbor.peer_group.route_map_out:
        locks_name.append(LOCK_ROUTE_MAP_ENTRY %
                          route_map_entry.id)
        locks_name.append(LOCK_LIST_CONFIG_BGP %
                          route_map_entry.list_config_bgp_id)

    # Remove duplicates locks
    locks_name = list(set(locks_name))
    return create_lock_with_blocking(locks_name)


def get_created_neighbors_v4_shares_same_eqpt_and_peer(neighbor):

    return NeighborV4.objects.filter(created=True,
                                     peer_group=neighbor.peer_group_id,
                                     local_asn=neighbor.local_asn_id,
                                     local_ip=neighbor.local_ip_id)


def get_created_neighbors_v6_shares_same_eqpt_and_peer(neighbor):

    return NeighborV6.objects.filter(created=True,
                                     peer_group=neighbor.peer_group_id,
                                     local_asn=neighbor.local_asn_id,
                                     local_ip=neighbor.local_ip_id)


def get_v4_equipment(neighbor):

    eqpts_of_local_ip = set(neighbor.local_ip.ipequipamento_set.all().
                            values_list('equipamento', flat=True))
    eqpts_of_local_asn = set(neighbor.local_asn.asnequipment_set.all().
                             values_list('equipment', flat=True))

    ids_eqpts = set.intersection(eqpts_of_local_ip, eqpts_of_local_asn)

    return Equipamento.objects.get(id__in=ids_eqpts)


def get_v6_equipment(neighbor):

    eqpts_of_local_ip = set(neighbor.local_ip.ipv6equipament_set.all().
                            values_list('equipamento', flat=True))
    eqpts_of_local_asn = set(neighbor.local_asn.asnequipment_set.all().
                             values_list('equipment', flat=True))

    ids_eqpts = set.intersection(eqpts_of_local_ip, eqpts_of_local_asn)

    return Equipamento.objects.get(id__in=ids_eqpts)
