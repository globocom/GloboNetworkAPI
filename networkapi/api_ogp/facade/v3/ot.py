# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.core.exceptions import ObjectDoesNotExist

from networkapi.api_ogp import exceptions
from networkapi.api_ogp.models import ObjectType
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable \
    import build_query_to_datatable_v3


log = logging.getLogger(__name__)


def get_ots_by_search(search=dict()):
    """
    Return a list of Object Types by dict

    :param search: dict
    """

    try:
        ots = ObjectType.objects.filter()
        ot_map = build_query_to_datatable_v3(ots, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return ot_map


def get_ot_by_id(ot_id):
    """
    Return a Object Type by id

    :param ot_id: id of Object Type
    """

    try:
        return ObjectType.objects.get(id=ot_id)
    except ObjectDoesNotExist:
        raise exceptions.ObjectTypeNotFoundError(ot_id)


def get_ots_by_ids(ot_ids):
    """
    Return Object Type list by ids

    :param ot_ids: ids list of Object Type

    """

    ot_ids = [get_ot_by_id(ot_id).id for ot_id in ot_ids]

    return ObjectType.objects.filter(id__in=ot_ids)
