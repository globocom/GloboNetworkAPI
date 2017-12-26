# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError

from networkapi.api_list_config_bgp.models import ListConfigBGP
from networkapi.api_list_config_bgp.v4.exceptions import ListConfigBGPAssociatedToRouteMapEntryException
from networkapi.api_list_config_bgp.v4.exceptions import ListConfigBGPDoesNotExistException
from networkapi.api_list_config_bgp.v4.exceptions import ListConfigBGPError
from networkapi.api_list_config_bgp.v4.exceptions import ListConfigBGPIsDeployedException
from networkapi.api_list_config_bgp.v4.exceptions import \
    ListConfigBGPNotFoundError
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3

log = logging.getLogger(__name__)


def get_list_config_bgp_by_search(search=dict()):
    """Return a list of ListConfigBGP's by dict."""

    try:
        objects = ListConfigBGP.objects.filter()
        object_map = build_query_to_datatable_v3(objects, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return object_map


def get_list_config_bgp_by_id(obj_id):
    """Return an ListConfigBGP by id.

    Args:
        obj_id: Id of ListConfigBGP
    """

    try:
        obj = ListConfigBGP.get_by_pk(id=obj_id)
    except ListConfigBGPNotFoundError as e:
        raise ListConfigBGPDoesNotExistException(str(e))

    return obj


def get_list_config_bgp_by_ids(obj_ids):
    """Return ListConfigBGP list by ids.

    Args:
        obj_ids: List of Ids of ListConfigBGP's.
    """

    ids = list()
    for obj_id in obj_ids:
        try:
            obj = get_list_config_bgp_by_id(obj_id).id
            ids.append(obj)
        except ListConfigBGPDoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except Exception as e:
            raise NetworkAPIException(str(e))

    return ListConfigBGP.objects.filter(id__in=ids)


def update_list_config_bgp(obj):
    """Update ListConfigBGP."""

    try:
        obj_to_update = get_list_config_bgp_by_id(obj.get('id'))
        obj_to_update.update_v4(obj)
    except ListConfigBGPError as e:
        raise ValidationAPIException(str(e))
    except ListConfigBGPIsDeployedException as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except ListConfigBGPDoesNotExistException as e:
        raise ObjectDoesNotExistException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return obj_to_update


def create_list_config_bgp(obj):
    """Create ListConfigBGP."""

    try:
        obj_to_create = ListConfigBGP()
        obj_to_create.create_v4(obj)
    except ListConfigBGPError as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return obj_to_create


def delete_list_config_bgp(obj_ids):
    """Delete ListConfigBGP."""

    for obj_id in obj_ids:
        try:
            obj_to_delete = get_list_config_bgp_by_id(obj_id)
            obj_to_delete.delete_v4()
        except ListConfigBGPDoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except ListConfigBGPAssociatedToRouteMapEntryException as e:
            raise ValidationAPIException(str(e))
        except ListConfigBGPIsDeployedException as e:
            raise ValidationAPIException(str(e))
        except ListConfigBGPError as e:
            raise NetworkAPIException(str(e))
        except Exception as e:
            raise NetworkAPIException(str(e))
