# -*- coding:utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist

from networkapi.ambiente.models import Ambiente
from networkapi.api_pools import exceptions
from networkapi.infrastructure.datatable import build_query_to_datatable_v3


log = logging.getLogger(__name__)


def get_environment_by_search(search=dict()):
    """
    Return a list of environments by dict

    :param search: dict
    """

    environments = Ambiente.objects.filter()

    env_map = build_query_to_datatable_v3(environments, 'envs', search)

    return env_map


def get_environment_by_id(environment_id):
    """
    Return a environment by id
    :param environment_id: id of environment
    """

    try:
        environment = Ambiente.objects.get(id=environment_id)
    except ObjectDoesNotExist:
        raise exceptions.PoolNotExist()

    return environment


def get_environment_by_ids(environment_ids):
    """
    Return pool list by ids
    param pools_ids: ids list
    example: [<pools_id>,...]
    """

    environments = list()
    for environment_id in environment_ids:
        try:
            sp = Ambiente.objects.get(id=environment_id)
        except ObjectDoesNotExist:
            raise exceptions.PoolNotExist()

        environments.append(sp)

    return environments
