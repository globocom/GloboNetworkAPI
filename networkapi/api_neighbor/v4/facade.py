# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.db.transaction import commit_on_success

from networkapi.api_neighbor.models import NeighborV4
from networkapi.api_neighbor.models import NeighborV6
from networkapi.api_neighbor.v4 import exceptions
from networkapi.api_rest import exceptions as api_rest_exceptions
from networkapi.distributedlock import LOCK_LIST_CONFIG_BGP
from networkapi.distributedlock import LOCK_NEIGHBOR_V4
from networkapi.distributedlock import LOCK_NEIGHBOR_V6
from networkapi.distributedlock import LOCK_PEER_GROUP
from networkapi.distributedlock import LOCK_ROUTE_MAP
from networkapi.distributedlock import LOCK_ROUTE_MAP_ENTRY
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.plugins.factory import PluginFactory
from networkapi.util.geral import create_lock_with_blocking
from networkapi.util.geral import destroy_lock

log = logging.getLogger(__name__)


def get_neighbor_v4_by_search(search=None):
    """Return a list of NeighborV4's by dict."""

    try:
        objects = NeighborV4.objects.filter()
        search_dict = search if search else search
        object_map = build_query_to_datatable_v3(objects, search_dict)
    except FieldError as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except Exception as e:
        raise api_rest_exceptions.NetworkAPIException(str(e))
    else:
        return object_map


def get_neighbor_v4_by_id(obj_id):
    """Return an NeighborV4 by id.

    Args:
        obj_id: Id of NeighborV4
    """

    try:
        obj = NeighborV4.get_by_pk(id=obj_id)
    except exceptions.NeighborV4NotFoundError as e:
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
        except exceptions.NeighborV4DoesNotExistException as e:
            raise api_rest_exceptions.ObjectDoesNotExistException(str(e))
        except Exception as e:
            raise api_rest_exceptions.NetworkAPIException(str(e))

    return NeighborV4.objects.filter(id__in=ids)


def update_neighbor_v4(obj, user):
    """Update NeighborV4."""

    try:
        obj_to_update = get_neighbor_v4_by_id(obj.get('id'))
        obj_to_update.update_v4(obj, user)
    except exceptions.NeighborV4Error as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.DontHavePermissionForPeerGroupException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndRemoteIpAreInDifferentVrfsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndLocalAsnAtDifferentEquipmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.RemoteIpAndRemoteAsnAtDifferentEquipmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndPeerGroupAtDifferentEnvironmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.NeighborDuplicatedException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.NeighborV4IsDeployed as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except api_rest_exceptions.ValidationAPIException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.NeighborV4DoesNotExistException as e:
        raise api_rest_exceptions.ObjectDoesNotExistException(str(e))
    except Exception as e:
        raise api_rest_exceptions.NetworkAPIException(str(e))

    return obj_to_update


def save_new_asn(name=None):
    log.info("save_new_asn")

    from networkapi.api_asn.v4 import facade

    idt = facade.create_as(dict(name=name))
    return idt.id


def link_asn_equipment(asn_id, equip_id):
    log.info("link_asn_equipment")

    from networkapi.api_asn.models import AsnEquipment

    asn_equipment = AsnEquipment()
    asn_equipment.create_v4(dict(equipment=equip_id, asn=asn_id))


def allocate_ipv4(equipment=None, ipv4=None):
    log.info('allocate_ipv4')

    from networkapi.api_ip import facade

    dic = dict(networkipv4=ipv4.get('networkv4'),
               equipments=[{'id': equipment}])

    if ipv4.get('ipv4'):
        dic['oct1'], dic['oct2'], dic['oct3'], dic['oct4'] = \
            ipv4.get('ipv4').split('.')

    idt = facade.create_ipv4(dic)
    return idt.id


def save_new_peer_group(user, peer_group=None):
    log.info('save_new_peer_group')

    from networkapi.api_route_map.v4 import facade as facade_route_map
    from networkapi.api_peer_group.v4 import facade as facade_peer_group

    if peer_group.get('route-map').get('route-map-in').get('id'):
        route_map_in = peer_group.get('route-map').get('route-map-in').get('id')
    else:
        route_map_in = facade_route_map.create_route_map(dict(
            name=peer_group.get('route-map').get('route-map-in').get('name')))

    if peer_group.get('route-map').get('route-map-out').get('id'):
        route_map_out = peer_group.get('route-map').get('route-map-out').get('id')
    else:
        route_map_out = facade_route_map.create_route_map(dict(
            name=peer_group.get('route-map').get('route-map-out').get('name')))

    idt = facade_peer_group.create_peer_group(dict(route_map_in=route_map_in.id,
                                                   route_map_out=route_map_out.id,
                                                   name=peer_group.get('name'),
                                                   environments=peer_group.get('environment')),
                                              user)
    return idt.id


def check_obj(obj, user):
    log.info('check_obj')

    neighbor = dict(community=obj.get('community'),
                    soft_reconfiguration=obj.get('soft_reconfiguration'),
                    remove_private_as=obj.get('remove_private_as'),
                    next_hop_self=obj.get('next_hop_self'),
                    kind=obj.get('kind'),
                    remote_ip=obj.get('neighbor_remote').get('ip').get('id'),
                    local_ip=obj.get('neighbor_local').get('ip').get('id'))

    local_equipment = obj.get('neighbor_local').get('equipment').get('id')
    remote_equipment = obj.get('neighbor_remote').get('equipment').get('id')

    if obj.get('neighbor_local').get('asn').get('id'):
        neighbor['local_asn'] = obj.get('neighbor_local').get('asn').get('id')
    else:
        neighbor['local_asn'] = save_new_asn(obj.get('neighbor_local').get('asn').get('name'))
        link_asn_equipment(neighbor['local_asn'], local_equipment)

    log.debug('local asn %s' % neighbor['local_asn'])

    if obj.get('neighbor_remote').get('asn').get('id'):
        neighbor['remote_asn'] = obj.get('neighbor_remote').get('asn').get('id')
    else:
        neighbor['remote_asn'] = save_new_asn(obj.get('neighbor_remote').get('asn').get('name'))
        link_asn_equipment(neighbor['remote_asn'], remote_equipment)

    log.debug('remote_asn %s' % neighbor['remote_asn'])

    if obj.get('peer_group').get('id'):
        neighbor['peer_group'] = obj.get('peer_group').get('id')
    else:
        neighbor['peer_group'] = save_new_peer_group(user, obj.get('peer_group'))

    log.debug('peer_group %s' % neighbor['peer_group'])

    return neighbor


def create_neighbor(obj, user):
    """Create NeighborV4."""

    try:
        neighbor = check_obj(obj, user)
        obj_to_create = NeighborV4()
        obj_to_create.create_v4(neighbor, user)

    except exceptions.NeighborV4Error as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.DontHavePermissionForPeerGroupException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndRemoteIpAreInDifferentVrfsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndLocalAsnAtDifferentEquipmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.RemoteIpAndRemoteAsnAtDifferentEquipmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndPeerGroupAtDifferentEnvironmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.NeighborDuplicatedException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except api_rest_exceptions.ValidationAPIException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except Exception as e:
        raise api_rest_exceptions.NetworkAPIException(str(e))

    return obj_to_create


def create_neighbor_v4(obj, user):
    """Create NeighborV4."""

    try:
        obj_to_create = NeighborV4()
        obj_to_create.create_v4(obj, user)
    except exceptions.NeighborV4Error as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.DontHavePermissionForPeerGroupException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndRemoteIpAreInDifferentVrfsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndLocalAsnAtDifferentEquipmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.RemoteIpAndRemoteAsnAtDifferentEquipmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndPeerGroupAtDifferentEnvironmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.NeighborDuplicatedException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except api_rest_exceptions.ValidationAPIException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except Exception as e:
        raise api_rest_exceptions.NetworkAPIException(str(e))

    return obj_to_create


def delete_neighbor_v4(obj_ids):
    """Delete NeighborV4."""

    for obj_id in obj_ids:
        try:
            obj_to_delete = get_neighbor_v4_by_id(obj_id)
            obj_to_delete.delete_v4()
        except exceptions.NeighborV4DoesNotExistException as e:
            raise api_rest_exceptions.ObjectDoesNotExistException(str(e))
        except exceptions.NeighborV4IsDeployed as e:
            raise api_rest_exceptions.ValidationAPIException(str(e))
        except exceptions.NeighborV4Error as e:
            raise api_rest_exceptions.NetworkAPIException(str(e))
        except Exception as e:
            raise api_rest_exceptions.NetworkAPIException(str(e))


def get_neighbor_v6_by_search(search=None):
    """Return a list of NeighborV6's by dict."""

    try:
        objects = NeighborV6.objects.filter()
        search_dict = search if search else dict()
        object_map = build_query_to_datatable_v3(objects, search_dict)
    except FieldError as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except Exception as e:
        raise api_rest_exceptions.NetworkAPIException(str(e))
    else:
        return object_map


def get_neighbor_v6_by_id(obj_id):
    """Return an NeighborV6 by id.

    Args:
        obj_id: Id of NeighborV6
    """

    try:
        obj = NeighborV6.get_by_pk(id=obj_id)
    except exceptions.NeighborV6NotFoundError as e:
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
        except exceptions.NeighborV6DoesNotExistException as e:
            raise api_rest_exceptions.ObjectDoesNotExistException(str(e))
        except Exception as e:
            raise api_rest_exceptions.NetworkAPIException(str(e))

    return NeighborV6.objects.filter(id__in=ids)


def update_neighbor_v6(obj, user):
    """Update NeighborV6."""

    try:
        obj_to_update = get_neighbor_v6_by_id(obj.get('id'))
        obj_to_update.update_v4(obj, user)
    except exceptions.NeighborV6Error as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.DontHavePermissionForPeerGroupException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndRemoteIpAreInDifferentVrfsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndLocalAsnAtDifferentEquipmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.RemoteIpAndRemoteAsnAtDifferentEquipmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndPeerGroupAtDifferentEnvironmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.NeighborDuplicatedException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except api_rest_exceptions.ValidationAPIException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.NeighborV6DoesNotExistException as e:
        raise api_rest_exceptions.ObjectDoesNotExistException(str(e))
    except Exception as e:
        raise api_rest_exceptions.NetworkAPIException(str(e))

    return obj_to_update


def create_neighbor_v6(obj, user):
    """Create NeighborV6."""

    try:
        obj_to_create = NeighborV6()
        obj_to_create.create_v4(obj, user)
    except exceptions.NeighborV6Error as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.DontHavePermissionForPeerGroupException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndRemoteIpAreInDifferentVrfsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndLocalAsnAtDifferentEquipmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.RemoteIpAndRemoteAsnAtDifferentEquipmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.LocalIpAndPeerGroupAtDifferentEnvironmentsException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except exceptions.NeighborDuplicatedException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except api_rest_exceptions.ValidationAPIException as e:
        raise api_rest_exceptions.ValidationAPIException(str(e))
    except Exception as e:
        raise api_rest_exceptions.NetworkAPIException(str(e))

    return obj_to_create


def delete_neighbor_v6(obj_ids):
    """Delete NeighborV6."""

    for obj_id in obj_ids:
        try:
            obj_to_delete = get_neighbor_v6_by_id(obj_id)
            obj_to_delete.delete_v4()
        except exceptions.NeighborV6DoesNotExistException as e:
            raise api_rest_exceptions.ObjectDoesNotExistException(str(e))
        except exceptions.NeighborV6IsDeployed as e:
            raise api_rest_exceptions.ValidationAPIException(str(e))
        except exceptions.NeighborV6Error as e:
            raise api_rest_exceptions.NetworkAPIException(str(e))
        except Exception as e:
            raise api_rest_exceptions.NetworkAPIException(str(e))


@commit_on_success
def deploy_neighbor_v4(neighbor_id):

    neighbor = NeighborV4.objects.get(id=neighbor_id)

    if neighbor.created:
        raise exceptions.NeighborV4IsDeployed(neighbor)

    locks_list = lock_resources_used_by_neighbor_v4(neighbor)

    try:
        get_created_neighbors_v4_shares_same_eqpt_and_peer(neighbor)
        get_created_neighbors_v6_shares_same_eqpt_and_peer(neighbor)

        eqpt = get_v4_equipment(neighbor)

        plugin = PluginFactory.factory(eqpt)
        plugin.bgp().deploy_neighbor(neighbor)

        neighbor.deploy()

    except Exception as e:
        raise api_rest_exceptions.NetworkAPIException(str(e))

    finally:
        destroy_lock(locks_list)


@commit_on_success
def undeploy_neighbor_v4(neighbor_id):

    neighbor = NeighborV4.objects.get(id=neighbor_id)

    if not neighbor.created:
        raise exceptions.NeighborV4IsUndeployed(neighbor)

    locks_list = lock_resources_used_by_neighbor_v4(neighbor)

    try:
        get_created_neighbors_v4_shares_same_eqpt_and_peer(neighbor)
        get_created_neighbors_v6_shares_same_eqpt_and_peer(neighbor)

        eqpt = get_v4_equipment(neighbor)

        plugin = PluginFactory.factory(eqpt)
        plugin.bgp().undeploy_neighbor(neighbor)
        neighbor.undeploy()

    except Exception as e:
        raise api_rest_exceptions.NetworkAPIException(str(e))

    finally:
        destroy_lock(locks_list)


@commit_on_success
def deploy_neighbor_v6(neighbor_id):

    neighbor = NeighborV6.objects.get(id=neighbor_id)

    if neighbor.created:
        raise exceptions.NeighborV6IsDeployed(neighbor)

    locks_list = lock_resources_used_by_neighbor_v6(neighbor)

    try:
        get_created_neighbors_v4_shares_same_eqpt_and_peer(neighbor)
        get_created_neighbors_v6_shares_same_eqpt_and_peer(neighbor)

        eqpt = get_v6_equipment(neighbor)

        plugin = PluginFactory.factory(eqpt)
        plugin.bgp().deploy_neighbor(neighbor)

        neighbor.deploy()

    except Exception as e:
        raise api_rest_exceptions.NetworkAPIException(str(e))

    finally:
        destroy_lock(locks_list)


@commit_on_success
def undeploy_neighbor_v6(neighbor_id):

    neighbor = NeighborV6.objects.get(id=neighbor_id)

    if not neighbor.created:
        raise exceptions.NeighborV6IsUndeployed(neighbor)

    locks_list = lock_resources_used_by_neighbor_v6(neighbor)

    try:
        get_created_neighbors_v4_shares_same_eqpt_and_peer(neighbor)
        get_created_neighbors_v6_shares_same_eqpt_and_peer(neighbor)

        eqpt = get_v6_equipment(neighbor)

        plugin = PluginFactory.factory(eqpt)
        plugin.bgp().undeploy_neighbor(neighbor)

        neighbor.deploy()

    except Exception as e:
        raise api_rest_exceptions.NetworkAPIException(str(e))

    finally:
        destroy_lock(locks_list)


def deploy_list_config_bgp(list_config_bgp, plugin):
    # deploys neighbor
    # pass
    plugin.bgp().deploy_list_config_bgp(list_config_bgp)


def deploy_route_map(route_map, plugin):
    # deploys neighbor
    # pass
    plugin.bgp().deploy_route_map(route_map)


def undeploy_list_config_bgp(list_config_bgp, plugin):
    # deploys neighbor
    pass
    # plugin.undeploy_list_config_bgp()


def undeploy_route_map(route_map, plugin):
    # deploys neighbor
    pass
    # plugin.undeploy_route_map()


def lock_resources_used_by_neighbor_v4(neighbor):

    locks_name = list()
    locks_name.append(LOCK_NEIGHBOR_V4 % neighbor.id)
    locks_name.append(LOCK_PEER_GROUP % neighbor.peer_group_id)
    locks_name.append(LOCK_ROUTE_MAP % neighbor.peer_group.route_map_in_id)
    locks_name.append(LOCK_ROUTE_MAP % neighbor.peer_group.route_map_out_id)

    for route_map_entry in neighbor.peer_group.route_map_in.route_map_entries:
        locks_name.append(LOCK_ROUTE_MAP_ENTRY %
                          route_map_entry.id)
        locks_name.append(LOCK_LIST_CONFIG_BGP %
                          route_map_entry.list_config_bgp_id)

    for route_map_entry in neighbor.peer_group.route_map_out.route_map_entries:
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
    locks_name.append(LOCK_ROUTE_MAP % neighbor.peer_group.route_map_out_id)

    for route_map_entry in neighbor.peer_group.route_map_in.route_map_entries:
        locks_name.append(LOCK_ROUTE_MAP_ENTRY %
                          route_map_entry.id)
        locks_name.append(LOCK_LIST_CONFIG_BGP %
                          route_map_entry.list_config_bgp_id)

    for route_map_entry in neighbor.peer_group.route_map_out.route_map_entries:
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
    from networkapi.equipamento.models import Equipamento

    eqpts_of_local_ip = set(neighbor.local_ip.ipequipamento_set.all().
                            values_list('equipamento', flat=True))
    eqpts_of_local_asn = set(neighbor.local_asn.asnequipment_set.all().
                             values_list('equipment', flat=True))

    ids_eqpts = set.intersection(eqpts_of_local_ip, eqpts_of_local_asn)

    return Equipamento.objects.get(id__in=ids_eqpts)


def get_v6_equipment(neighbor):
    from networkapi.equipamento.models import Equipamento

    eqpts_of_local_ip = set(neighbor.local_ip.ipv6equipament_set.all().
                            values_list('equipamento', flat=True))
    eqpts_of_local_asn = set(neighbor.local_asn.asnequipment_set.all().
                             values_list('equipment', flat=True))

    ids_eqpts = set.intersection(eqpts_of_local_ip, eqpts_of_local_asn)

    return Equipamento.objects.get(id__in=ids_eqpts)
