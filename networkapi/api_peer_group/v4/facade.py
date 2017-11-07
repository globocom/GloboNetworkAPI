# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError

from networkapi.api_peer_group.models import PeerGroup
from networkapi.api_peer_group.v4 import exceptions
from networkapi.api_peer_group.v4.exceptions import PeerGroupError
from networkapi.api_peer_group.v4.exceptions import PeerGroupNotFoundError
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3

log = logging.getLogger(__name__)


def get_peer_group_by_search(search=dict()):
    """Return a list of PeerGroup's by dict."""

    try:
        objects = PeerGroup.objects.filter()
        object_map = build_query_to_datatable_v3(objects, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return object_map


def get_peer_group_by_id(obj_id):
    """Return an PeerGroup by id.

    Args:
        obj_id: Id of PeerGroup
    """

    try:
        obj = PeerGroup.get_by_pk(id=obj_id)
    except PeerGroupNotFoundError, e:
        raise exceptions.PeerGroupDoesNotExistException(str(e))

    return obj


def get_peer_group_by_ids(obj_ids):
    """Return PeerGroup list by ids.

    Args:
        obj_ids: List of Ids of PeerGroup's.
    """

    ids = list()
    for obj_id in obj_ids:
        try:
            obj = get_peer_group_by_id(obj_id).id
            ids.append(obj)
        except exceptions.PeerGroupDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

    return PeerGroup.objects.filter(id__in=ids)


def update_peer_group(obj, user):
    """Update PeerGroup."""

    try:
        obj_to_update = get_peer_group_by_id(obj.get('id'))
        obj_to_update.update_v4(obj, user)
    except PeerGroupError, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.PeerGroupDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return obj_to_update


def create_peer_group(obj, user):
    """Create PeerGroup."""

    try:
        obj_to_create = PeerGroup()
        obj_to_create.create_v4(obj, user)
    except PeerGroupError, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return obj_to_create


def delete_peer_group(obj_ids):
    """Delete PeerGroup."""

    for obj_id in obj_ids:
        try:
            obj_to_delete = get_peer_group_by_id(obj_id)
            obj_to_delete.delete_v4()
        except exceptions.PeerGroupDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except PeerGroupError, e:
            raise NetworkAPIException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))
