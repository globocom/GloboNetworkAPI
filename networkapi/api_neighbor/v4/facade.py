# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError

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
        neighbor_map = build_query_to_datatable_v3(neighbors,
                                                            search)
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
        neighbor_ = Neighbor.get_by_pk(id=neighbor_id)
    except NeighborNotFoundError, e:
        raise exceptions.NeighborDoesNotExistException(str(e))

    return neighbor_


def get_neighbor_by_ids(neighbor_ids):
    """Return Neighbor list by ids.

    Args:
        neighbor_ids: List of Ids of Neighbors.
    """

    vi_ids = list()
    for vi_id in neighbor_ids:
        try:
            neighbor_ = get_neighbor_by_id(vi_id).id
            vi_ids.append(neighbor_)
        except exceptions.NeighborDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

    neighbors = Neighbor.objects.filter(id__in=vi_ids)

    return neighbors


def update_neighbor(vi_):
    """Update Neighbor."""

    try:
        vi_obj = get_neighbor_by_id(vi_.get('id'))
        vi_obj.update_v4(vi_)
    except NeighborErrorV4, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.NeighborDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return vi_obj


def create_neighbor(vi_):
    """Create Neighbor."""

    try:
        vi_obj = Neighbor()
        vi_obj.create_v4(vi_)
    except NeighborErrorV4, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return vi_obj


def delete_neighbor(vi_ids):
    """Delete Neighbor."""

    for vi_id in vi_ids:
        try:
            vi_obj = get_neighbor_by_id(vi_id)
            vi_obj.delete_v4()
        except exceptions.NeighborDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        # except exceptions.AsAssociatedToEquipmentError, e:
        #     raise ValidationAPIException(str(e))
        except NeighborError, e:
            raise NetworkAPIException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

