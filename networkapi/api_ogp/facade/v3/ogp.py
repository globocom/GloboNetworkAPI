# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist

from networkapi.api_ogp import exceptions
from networkapi.api_ogp.models import ObjectGroupPermission
from networkapi.infrastructure.datatable \
    import build_query_to_datatable_v3


log = logging.getLogger(__name__)


def get_ogps_by_search(search=dict()):
    """
    Return a list of Object Groups Permissions by dict

    :param search: dict
    """

    ogps = ObjectGroupPermission.objects.filter()

    ogp_map = build_query_to_datatable_v3(ogps, search)

    return ogp_map


def get_ogp_by_id(ogp_id):
    """
    Return a Object Group Permission by id

    :param ogp_id: id of Object Group Permission
    """

    try:
        return ObjectGroupPermission.objects.get(id=ogp_id)
    except ObjectDoesNotExist:
        raise exceptions.ObjectGroupPermissionNotFoundError()


def get_ogps_by_ids(ogp_ids):
    """
    Return Object Group Permission list by ids

    :param ogp_ids: ids list of Object Group Permissions

    """

    ogp_ids = [get_ogp_by_id(ogp_id).id for ogp_id in ogp_ids]

    return ObjectGroupPermission.objects.filter(id__in=ogp_ids)


def create_ogp(ogp):
    """
    Create Object Group Permission

    :param ogp: dict
    """

    ogp_obj = ObjectGroupPermission()

    ogp_obj.create_v3(ogp)

    return ogp_obj


def update_ogp(ogp):
    """
    Update Object Group Permission

    :param ogp: dict
    """

    ogp_obj = get_ogp_by_id(ogp.get('id'))

    ogp_obj.update_v3(ogp)

    return ogp_obj


def delete_ogp(ogp_id):
    """
    Delete Object Group Permission

    :param ogp_id: int
    """

    ogp_obj = get_ogp_by_id(ogp_id)
    ogp_obj.delete_v3()
