# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist

from networkapi.api_vrf import exceptions
from networkapi.api_vrf.models import Vrf
from networkapi.infrastructure.datatable import build_query_to_datatable_v3


log = logging.getLogger(__name__)


def get_vrfs_by_search(search=dict()):
    """
    Return a list of vrfs by dict

    :param search: dict
    """

    vrfs = Vrf.objects.filter()

    vrf_map = build_query_to_datatable_v3(vrfs, search)

    return vrf_map


def get_vrf_by_id(vrf_id):
    """
    Return a vrf by id

    :param vrf_id: id of vrf
    """

    try:
        vrf = Vrf.objects.get(id=vrf_id)
    except ObjectDoesNotExist:
        raise exceptions.VrfNotFoundError()

    return vrf


def get_vrfs_by_ids(vrfs_ids):
    """
    Return vrf list by ids

    :param vrfs_ids: ids list
    """

    vrfs = list()
    for vrf_id in vrfs_ids:
        vrf = get_vrf_by_id(vrf_id)
        vrfs.append(vrf)

    return vrfs


def create_vrf(vrf):
    """
    Create vrf

    :param env: dict
    """

    vrf_obj = Vrf()

    vrf_obj.vrf = vrf.get('vrf')
    vrf_obj.internal_name = vrf.get('internal_name')

    vrf_obj.create(None)

    return vrf_obj


def update_vrf(vrf):
    """
    Update vrf

    :param env: dict
    """

    vrf_obj = get_vrf_by_id(vrf.get('id'))

    Vrf.update(
        None,
        vrf_obj.id,
        vrf=vrf.get('vrf'),
        internal_name=vrf.get('internal_name'),
    )

    return vrf_obj


def delete_vrf(vrf_id):
    """
    Delete environment

    :param env: dict
    """

    Vrf.remove(None, vrf_id)
