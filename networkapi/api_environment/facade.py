# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import IPConfig
from networkapi.api_pools import exceptions
from networkapi.infrastructure.datatable import build_query_to_datatable_v3


log = logging.getLogger(__name__)


def get_environment_by_search(search=dict()):
    """
    Return a list of environments by dict

    :param search: dict
    """

    environments = Ambiente.objects.filter()
    env_map = build_query_to_datatable_v3(environments, search)

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

    :param environment_ids: ids list
    """

    env_ids = list()
    for environment_id in environment_ids:
        env = get_environment_by_id(environment_id).id
        env_ids.append(env)

    environments = Ambiente.objects.filter(id__in=env_ids)

    return environments


def list_environment_environment_vip_related(env_id=None):
    """
    List of environments related with environment vip

    :param env_id: environment id(optional)
    """

    if env_id is None:
        env_list_net_related = Ambiente.objects.filter(
            Q(vlan__networkipv4__ambient_vip__id__isnull=False) |
            Q(vlan__networkipv6__ambient_vip__id__isnull=False)
        )
    else:
        env_list_net_related = Ambiente.objects.filter(
            Q(vlan__networkipv4__ambient_vip__id=env_id) |
            Q(vlan__networkipv6__ambient_vip__id=env_id)
        )

    env_list_net_related = env_list_net_related.order_by(
        'divisao_dc__nome', 'ambiente_logico__nome', 'grupo_l3__nome'
    ).select_related(
        'grupo_l3', 'ambiente_logico', 'divisao_dc', 'filter'
    ).distinct()

    return env_list_net_related


def update_environment(env):
    """
    Update environment

    :param env: dict
    """

    env_obj = get_environment_by_id(env.get('id'))
    env_obj.update_v3(env)

    return env_obj


def create_environment(env):
    """
    Create environment

    :param env: dict
    """

    env_obj = Ambiente()
    env_obj.create_v3(env)

    return env_obj


def delete_environment(env_ids):
    """
    Delete environment

    :param env: dict
    """

    for env_id in env_ids:
        Ambiente.remove(None, env_id)


def get_configs_by_id(config_id, env_id=None):
    """
    Get config by id

    :param config: Configs of environment
    """

    try:

        ip_config = IPConfig.objects
        if env_id:
            ip_config.get(
                id=config_id,
                configenvironment__environment=env_id
            )
        else:
            ip_config.get(
                id=config_id
            )
    except ObjectDoesNotExist:
        raise exceptions.ConfigIpDoesNotExistException()
