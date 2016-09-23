# -*- coding:utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

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
        raise exceptions.EnvironmentDoesNotExistException()

    return environment


def get_environment_by_ids(environment_ids):
    """
    Return environment list by ids
    param environment_ids: ids list
    """

    environments = list()
    for environment_id in environment_ids:
        env = get_environment_by_id(environment_id)
        environments.append(env)

    return environments


def list_environment_environment_vip_related(env_ids=None):

    if env_ids is None:
        env_list_net_related = Ambiente.objects.filter(
            Q(vlan__networkipv4__ambient_vip__id__isnull=False) |
            Q(vlan__networkipv6__ambient_vip__id__isnull=False)
        )
    else:
        env_list_net_related = Ambiente.objects.filter(
            Q(vlan__networkipv4__ambient_vip__id__in=env_ids) |
            Q(vlan__networkipv6__ambient_vip__id__in=env_ids)
        )

    env_list_net_related = env_list_net_related.order_by(
        'divisao_dc__nome', 'ambiente_logico__nome', 'grupo_l3__nome'
    ).select_related(
        'grupo_l3', 'ambiente_logico', 'divisao_dc', 'filter'
    ).distinct()

    return env_list_net_related
