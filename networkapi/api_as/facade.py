# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from networkapi.api_as.exceptions import AsNotFoundError, AsError
from networkapi.api_as.exceptions import AsErrorV3
from networkapi.api_as.models import As
from networkapi.api_as import exceptions
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3


log = logging.getLogger(__name__)


def get_as_by_search(search=dict()):
    """Return a list of AS's by dict."""

    try:
        as_s = As.objects.filter()
        as_map = build_query_to_datatable_v3(as_s, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return as_map


def get_as_by_id(as_id):
    """Return an AS by id.

    Args:
        as_id: Id of AS
    """

    try:
        as_ = As.get_by_pk(id=as_id)
    except AsNotFoundError, e:
        raise exceptions.AsDoesNotExistException(str(e))

    return as_


def get_as_by_ids(autonomous_systems_ids):
    """Return AS list by ids.

    Args:
        as_ids: List of Ids of AS's.
    """

    as_ids = list()
    for as_id in autonomous_systems_ids:
        try:
            as_ = get_as_by_id(as_id).id
            as_ids.append(as_)
        except exceptions.AsDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

    as_s = As.objects.filter(id__in=as_ids)

    return as_s


def update_as(as_):
    """Update AS."""

    try:
        as_obj = get_as_by_id(as_.get('id'))
        as_obj.update_v3(as_)
    except AsErrorV3, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.AsDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return as_obj


def create_as(as_):
    """Create AS."""

    try:
        as_obj = As()
        as_obj.create_v3(as_)
    except AsErrorV3, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return as_obj


def delete_as(as_ids):
    """Delete AS."""

    for as_id in as_ids:
        try:
            as_obj = get_as_by_id(as_id)
            as_obj.delete_v3()
        except exceptions.AsDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except exceptions.AsAssociatedToEquipmentError, e:
            raise ValidationAPIException(str(e))
        except AsError, e:
            raise NetworkAPIException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

