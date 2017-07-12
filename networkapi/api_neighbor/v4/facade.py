# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.db.transaction import commit_on_success

from networkapi.api_neighbor.models import Neighbor
from networkapi.api_neighbor.v4 import exceptions
from networkapi.api_neighbor.v4.exceptions import NeighborErrorV4
from networkapi.api_neighbor.v4.exceptions import NeighborNotFoundError
from networkapi.api_neighbor.v4.exceptions import  NeighborError
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3

log = logging.getLogger(__name__)

def get_neighbor_by_search(search=dict()):
    """Return a list of Neighbor's by dict."""

    try:
        neighbors = Neighbor.objects.filter()
        neighbor_map = build_query_to_datatable_v3(neighbors, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return neighbor_map


def get_neighbor_by_id(neighbor_id):
    """Return an Neighbor by id.

    Args:
        neighbor_id: Id of Neighbor
    """

    try:
        neighbor = Neighbor.get_by_pk(id=neighbor_id)
    except NeighborNotFoundError, e:
        raise exceptions.NeighborDoesNotExistException(str(e))

    return neighbor


def get_neighbor_by_ids(neighbor_ids):
    """Return Neighbor list by ids.

    Args:
        neighbor_ids: List of Ids of Neighbors.
    """

    ids = list()
    for neighbor_id in neighbor_ids:
        try:
            neighbor = get_neighbor_by_id(neighbor_id).id
            ids.append(neighbor)
        except exceptions.NeighborDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

    neighbors = Neighbor.objects.filter(id__in=ids)

    return neighbors


def update_neighbor(neighbor):
    """Update Neighbor."""

    try:
        neighbor_obj = get_neighbor_by_id(neighbor.get('id'))
        neighbor_obj.update_v4(neighbor)
    except NeighborErrorV4, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.NeighborDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return neighbor_obj


def create_neighbor(neighbor):
    """Create Neighbor."""

    try:
        neighbor_obj = Neighbor()
        neighbor_obj.create_v4(neighbor)
    except NeighborErrorV4, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return neighbor_obj


def delete_neighbor(neighbor_ids):
    """Delete Neighbor."""

    for neighbor_id in neighbor_ids:
        try:
            neighbor_obj = get_neighbor_by_id(neighbor_id)
            neighbor_obj.delete_v4()
        except exceptions.NeighborDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        # except exceptions.AsAssociatedToEquipmentError, e:
        #     raise ValidationAPIException(str(e))
        except NeighborError, e:
            raise NetworkAPIException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))


@commit_on_success
def delete_real_neighbor(neighbors, user):
    pass
    # load_balance = dict()
    #
    # keys = list()
    # for vip in vip_requests:
    #     load_balance = prepare_apply(
    #         load_balance, vip, created=True, user=user)
    #
    #     keys.append(sorted([str(key) for key in load_balance.keys()]))
    #
    # # vips are in differents load balancers
    # keys = [','.join(key) for key in keys]
    # if len(list(set(keys))) > 1:
    #     raise Exception('Vips Request are in differents load balancers')
    #
    # pools_ids = list()
    #
    # for lb in load_balance:
    #     inst = copy.deepcopy(load_balance.get(lb))
    #     log.info('started call:%s' % lb)
    #     pool_del = inst.get('plugin').delete_vip(inst)
    #     log.info('ended call')
    #     pools_ids += pool_del
    #
    # ids = [vip_id.get('id') for vip_id in vip_requests]
    #
    # vips = VipRequest.objects.filter(id__in=ids)
    # vips.update(created=False)
    #
    # for vip in vips:
    #     syncs.new_to_old(vip)
    #
    # if pools_ids:
    #     pools_ids = list(set(pools_ids))
    #     ServerPool.objects.filter(id__in=pools_ids).update(pool_created=False)
    #

@commit_on_success
def create_real_neighbor(neighbors, user):
    pass
    # load_balance = dict()
    # keys = list()
    #
    # for vip in vip_requests:
    #     load_balance = prepare_apply(
    #         load_balance, vip, created=False, user=user)
    #
    #     keys.append(sorted([str(key) for key in load_balance.keys()]))
    #
    # # vips are in differents load balancers
    # keys = [','.join(key) for key in keys]
    # if len(list(set(keys))) > 1:
    #     raise Exception('Vips Request are in differents load balancers')
    #
    # for lb in load_balance:
    #     inst = copy.deepcopy(load_balance.get(lb))
    #     log.info('started call:%s' % lb)
    #     inst.get('plugin').create_vip(inst)
    #     log.info('ended call')
    #
    # ids = [vip_id.get('id') for vip_id in vip_requests]
    #
    # vips = VipRequest.objects.filter(id__in=ids)
    # vips.update(created=True)
    #
    # for vip in vips:
    #     syncs.new_to_old(vip)
    #
    # ServerPool.objects.filter(
    #     viprequestportpool__vip_request_port__vip_request__id__in=ids).update(pool_created=True)