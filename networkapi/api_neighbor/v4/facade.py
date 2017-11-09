# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.db.transaction import commit_on_success

from networkapi.api_neighbor.models import NeighborV4
from networkapi.api_neighbor.models import NeighborV6
from networkapi.api_neighbor.v4 import exceptions
from networkapi.api_neighbor.v4.exceptions import NeighborV4Error
from networkapi.api_neighbor.v4.exceptions import NeighborV4NotFoundError
from networkapi.api_neighbor.v4.exceptions import NeighborV6Error
from networkapi.api_neighbor.v4.exceptions import NeighborV6NotFoundError
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3

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


def update_neighbor_v4(obj):
    """Update NeighborV4."""

    try:
        obj_to_update = get_neighbor_v4_by_id(obj.get('id'))
        obj_to_update.update_v4(obj)
    except NeighborV4Error, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.NeighborV4DoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return obj_to_update


def create_neighbor_v4(obj):
    """Create NeighborV4."""

    try:
        obj_to_create = NeighborV4()
        obj_to_create.create_v4(obj)
    except NeighborV4Error, e:
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


def update_neighbor_v6(obj):
    """Update NeighborV6."""

    try:
        obj_to_update = get_neighbor_v6_by_id(obj.get('id'))
        obj_to_update.update_v4(obj)
    except NeighborV6Error, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.NeighborV6DoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return obj_to_update


def create_neighbor_v6(obj):
    """Create NeighborV6."""

    try:
        obj_to_create = NeighborV6()
        obj_to_create.create_v4(obj)
    except NeighborV6Error, e:
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

    pass


@commit_on_success
def undeploy_neighbors_v4(neighbors):

    pass


@commit_on_success
def deploy_neighbors_v6(neighbors):

    pass


@commit_on_success
def undeploy_neighbors_v6(neighbors):

    pass
