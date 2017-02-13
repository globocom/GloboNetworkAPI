# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist

from networkapi.api_ogp import exceptions
from networkapi.api_ogp.models import ObjectGroupPermissionGeneral
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable \
    import build_query_to_datatable_v3

log = logging.getLogger(__name__)


def get_ogpgs_by_search(search=dict()):
    """
    Return a list of Object Groups Permissions General by dict

    :param search: dict
    """

    try:
        ogpgs = ObjectGroupPermissionGeneral.objects.filter()
        ogpg_map = build_query_to_datatable_v3(ogpgs, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return ogpg_map


def get_ogpg_by_id(ogpg_id):
    """
    Return a Object Group Permission General by id

    :param ogpg_id: id of Object Group Permission
    """

    try:
        return ObjectGroupPermissionGeneral.objects.get(id=ogpg_id)
    except ObjectDoesNotExist:
        raise exceptions.ObjectGroupPermissionGeneralNotFoundError(ogpg_id)


def get_ogpgs_by_ids(ogpg_ids):
    """
    Return Object Group Permission General list by ids

    :param ogpg_ids: ids list of Object Group Permissions

    """

    ogpg_ids = [get_ogpg_by_id(ogpg_id).id for ogpg_id in ogpg_ids]

    return ObjectGroupPermissionGeneral.objects.filter(id__in=ogpg_ids)


def create_ogpg(ogpg):
    """
    Create Object Group Permission General

    :param ogpg: dict
    """

    ogpg_obj = ObjectGroupPermissionGeneral()

    ogpg_obj.create_v3(ogpg)

    return ogpg_obj


def update_ogpg(ogpg):
    """
    Update Object Group Permission General

    :param ogpg: dict
    """

    ogpg_obj = get_ogpg_by_id(ogpg.get('id'))

    ogpg_obj.update_v3(ogpg)

    return ogpg_obj


def delete_ogpg(ogpg_id):
    """
    Delete Object Group Permission General

    :param ogpg_id: int
    """

    ogpg_obj = get_ogpg_by_id(ogpg_id)
    ogpg_obj.delete_v3()
