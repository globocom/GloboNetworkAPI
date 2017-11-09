# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.db.transaction import commit_on_success

from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.api_route_map.models import RouteMap
from networkapi.api_route_map.models import RouteMapEntry
from networkapi.api_route_map.v4 import exceptions
from networkapi.api_route_map.v4.exceptions import RouteMapEntryError
from networkapi.api_route_map.v4.exceptions import RouteMapEntryNotFoundError
from networkapi.api_route_map.v4.exceptions import RouteMapError
from networkapi.api_route_map.v4.exceptions import RouteMapNotFoundError
from networkapi.infrastructure.datatable import build_query_to_datatable_v3

log = logging.getLogger(__name__)


def get_route_map_by_search(search=dict()):
    """Return a list of RouteMap's by dict."""

    try:
        objects = RouteMap.objects.filter()
        object_map = build_query_to_datatable_v3(objects, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return object_map


def get_route_map_by_id(obj_id):
    """Return an RouteMap by id.

    Args:
        obj_id: Id of RouteMap
    """

    try:
        obj = RouteMap.get_by_pk(id=obj_id)
    except RouteMapNotFoundError, e:
        raise exceptions.RouteMapDoesNotExistException(str(e))

    return obj


def get_route_map_by_ids(obj_ids):
    """Return RouteMap list by ids.

    Args:
        obj_ids: List of Ids of RouteMap's.
    """

    ids = list()
    for obj_id in obj_ids:
        try:
            obj = get_route_map_by_id(obj_id).id
            ids.append(obj)
        except exceptions.RouteMapDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

    return RouteMap.objects.filter(id__in=ids)


def update_route_map(obj):
    """Update RouteMap."""

    try:
        obj_to_update = get_route_map_by_id(obj.get('id'))
        obj_to_update.update_v4(obj)
    except RouteMapError, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.RouteMapDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return obj_to_update


def create_route_map(obj):
    """Create RouteMap."""

    try:
        obj_to_create = RouteMap()
        obj_to_create.create_v4(obj)
    except RouteMapError, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return obj_to_create


def delete_route_map(obj_ids):
    """Delete RouteMap."""

    for obj_id in obj_ids:
        try:
            obj_to_delete = get_route_map_by_id(obj_id)
            obj_to_delete.delete_v4()
        except exceptions.RouteMapDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except RouteMapError, e:
            raise NetworkAPIException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))


def get_route_map_entry_by_search(search=dict()):
    """Return a list of RouteMapEntry's by dict."""

    try:
        objects = RouteMapEntry.objects.filter()
        object_map = build_query_to_datatable_v3(objects, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return object_map


def get_route_map_entry_by_id(obj_id):
    """Return an RouteMapEntry by id.

    Args:
        obj_id: Id of RouteMapEntry
    """

    try:
        obj = RouteMapEntry.get_by_pk(id=obj_id)
    except RouteMapEntryNotFoundError, e:
        raise exceptions.RouteMapEntryDoesNotExistException(str(e))

    return obj


def get_route_map_entry_by_ids(obj_ids):
    """Return RouteMapEntry list by ids.

    Args:
        obj_ids: List of Ids of RouteMapEntry's.
    """

    ids = list()
    for obj_id in obj_ids:
        try:
            obj = get_route_map_entry_by_id(obj_id).id
            ids.append(obj)
        except exceptions.RouteMapEntryDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

    return RouteMapEntry.objects.filter(id__in=ids)


def update_route_map_entry(obj):
    """Update RouteMapEntry."""

    try:
        obj_to_update = get_route_map_entry_by_id(obj.get('id'))
        obj_to_update.update_v4(obj)
    except RouteMapEntryError, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.RouteMapEntryDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return obj_to_update


def create_route_map_entry(obj):
    """Create RouteMapEntry."""

    try:
        obj_to_create = RouteMapEntry()
        obj_to_create.create_v4(obj)
    except RouteMapEntryError, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return obj_to_create


def delete_route_map_entry(obj_ids):
    """Delete RouteMapEntry."""

    for obj_id in obj_ids:
        try:
            obj_to_delete = get_route_map_entry_by_id(obj_id)
            obj_to_delete.delete_v4()
        except exceptions.RouteMapEntryDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except RouteMapEntryError, e:
            raise NetworkAPIException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))


@commit_on_success
def deploy_route_maps(route_maps):
    pass


@commit_on_success
def undeploy_route_maps(route_maps):
    pass
