# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError

from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.api_route_map.models import RouteMap
from networkapi.api_route_map.models import RouteMapEntry
from networkapi.api_route_map.v4.exceptions import RouteMapAssociatedToPeerGroupException
from networkapi.api_route_map.v4.exceptions import RouteMapAssociatedToRouteMapEntryException
from networkapi.api_route_map.v4.exceptions import RouteMapDoesNotExistException
from networkapi.api_route_map.v4.exceptions import RouteMapEntryDoesNotExistException
from networkapi.api_route_map.v4.exceptions import \
    RouteMapEntryDuplicatedException
from networkapi.api_route_map.v4.exceptions import RouteMapEntryError
from networkapi.api_route_map.v4.exceptions import RouteMapEntryNotFoundError
from networkapi.api_route_map.v4.exceptions import RouteMapEntryWithDeployedRouteMapException
from networkapi.api_route_map.v4.exceptions import RouteMapError
from networkapi.api_route_map.v4.exceptions import RouteMapIsDeployedException
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
    except RouteMapNotFoundError as e:
        raise RouteMapDoesNotExistException(str(e))

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
        except RouteMapDoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except Exception as e:
            raise NetworkAPIException(str(e))

    return RouteMap.objects.filter(id__in=ids)


def update_route_map(obj):
    """Update RouteMap."""

    try:
        obj_to_update = get_route_map_by_id(obj.get('id'))
        obj_to_update.update_v4(obj)
    except RouteMapError as e:
        raise ValidationAPIException(str(e))
    except RouteMapIsDeployedException as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except RouteMapDoesNotExistException as e:
        raise ObjectDoesNotExistException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return obj_to_update


def create_route_map(obj):
    """Create RouteMap."""

    try:
        obj_to_create = RouteMap()
        obj_to_create.create_v4(obj)
    except RouteMapError as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return obj_to_create


def delete_route_map(obj_ids):
    """Delete RouteMap."""

    for obj_id in obj_ids:
        try:
            obj_to_delete = get_route_map_by_id(obj_id)
            obj_to_delete.delete_v4()
        except RouteMapDoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except RouteMapIsDeployedException as e:
            raise ValidationAPIException(str(e))
        except RouteMapAssociatedToRouteMapEntryException as e:
            raise ValidationAPIException(str(e))
        except RouteMapAssociatedToPeerGroupException as e:
            raise ValidationAPIException(str(e))
        except RouteMapError as e:
            raise NetworkAPIException(str(e))
        except Exception as e:
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
    except RouteMapEntryNotFoundError as e:
        raise RouteMapEntryDoesNotExistException(str(e))

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
        except RouteMapEntryDoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except Exception as e:
            raise NetworkAPIException(str(e))

    return RouteMapEntry.objects.filter(id__in=ids)


def update_route_map_entry(obj):
    """Update RouteMapEntry."""

    try:
        obj_to_update = get_route_map_entry_by_id(obj.get('id'))
        obj_to_update.update_v4(obj)
    except RouteMapEntryError as e:
        raise ValidationAPIException(str(e))
    except RouteMapEntryDuplicatedException as e:
        raise ValidationAPIException(str(e))
    except RouteMapEntryWithDeployedRouteMapException as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except RouteMapEntryDoesNotExistException as e:
        raise ObjectDoesNotExistException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return obj_to_update


def check_dict(obj):

    obj_to_create = dict(action=obj.get('action'),
                         action_reconfig=obj.get('action_reconfig'),
                         list_config_bgp=obj.get('list_config_bgp'),
                         order=obj.get('order'))

    if obj.get('route_map').get('id'):
        obj_to_create['route_map'] = RouteMap.get_by_pk(obj.get('route_map').get('id'))
    else:
        route_map_name = create_route_map(obj.get('route_map'))
        obj_to_create['route_map'] = route_map_name.id

    return obj_to_create


def create_route_map_entry(obj):
    """Create RouteMapEntry."""

    check_dict(obj)
    obj_to_create = RouteMapEntry()
    obj_to_create.create_v4(obj)



def delete_route_map_entry(obj_ids):
    """Delete RouteMapEntry."""

    for obj_id in obj_ids:
        try:
            obj_to_delete = get_route_map_entry_by_id(obj_id)
            obj_to_delete.delete_v4()
        except RouteMapEntryDoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except RouteMapEntryWithDeployedRouteMapException as e:
            raise ValidationAPIException(str(e))
        except RouteMapEntryError as e:
            raise NetworkAPIException(str(e))
        except Exception as e:
            raise NetworkAPIException(str(e))
