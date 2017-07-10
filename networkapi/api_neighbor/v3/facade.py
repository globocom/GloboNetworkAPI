# -*- coding: utf-8 -*-
from _mysql_exceptions import OperationalError
from django.core.exceptions import FieldError

from networkapi.api_neighbor.models import Neighbor
from networkapi.api_neighbor.v3.exceptions import NeighborError
from networkapi.api_neighbor.v3.exceptions import NeighborNotFoundError
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3


def get_neighbor_by_search(search=dict()):
    """Get List of Ipv4 by Search."""

    try:
        neighbors = Neighbor.objects.all()
        neighbors = build_query_to_datatable_v3(neighbors, search)
    except FieldError as e:
        raise ValidationAPIException(e.message)
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return neighbors


def get_neighbor_by_id(ip_id):
    """Get Ipv4."""

    try:
        neighbor = Neighbor.get_by_pk(ip_id)
    except NeighborNotFoundError, e:
        raise ObjectDoesNotExistException(e.message)
    except (Exception, OperationalError, NeighborError), e:
        raise NetworkAPIException(str(e))
    else:
        return neighbor


def get_neighbor_by_ids(ip_ids):
    """Get Many Ipv4."""

    ipv4_ids = list()
    for ip_id in ip_ids:
        ipv4_ids.append(get_neighbor_by_id(ip_id).id)

    neighbors = Neighbor.objects.filter(id__in=ipv4_ids)

    return neighbors
