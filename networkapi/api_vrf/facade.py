# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist

from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.api_vrf import exceptions
from networkapi.api_vrf.models import Vrf
from networkapi.infrastructure.datatable import build_query_to_datatable_v3


log = logging.getLogger(__name__)


def get_vrfs_by_search(search=dict()):
    """
    Return a list of vrfs by dict

    :param search: dict
    """

    try:
        vrfs = Vrf.objects.filter()
        vrf_map = build_query_to_datatable_v3(vrfs, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
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


def get_vrfs_by_ids(vrf_ids):
    """
    Return vrf list by ids

    :param vrf_ids: ids list

    """

    vrf_ids = [get_vrf_by_id(vrf_id).id for vrf_id in vrf_ids]

    return Vrf.objects.filter(id__in=vrf_ids)


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

    :param vrf: dict
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
    Delete vrf

    :param vrf_id: int
    """

    Vrf.remove(vrf_id)
