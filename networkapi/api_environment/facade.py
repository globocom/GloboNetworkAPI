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

    :param environment_ids: ids list
    """

    environments = list()
    for environment_id in environment_ids:
        env = get_environment_by_id(environment_id)
        environments.append(env)

    return environments


def list_environment_environment_vip_related(env_ids=None):
    """
    List of environments related with environment vip

    :param env_id: environment id(optional)
    """

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


def update_environment(env):
    """
    Update environment

    :param env: dict
    """

    env_obj = get_environment_by_id(env.get('id'))

    env_obj.grupo_l3_id = env.get('grupo_l3')
    env_obj.ambiente_logico_id = env.get('ambiente_logico')
    env_obj.divisao_dc_id = env.get('divisao_dc')
    env_obj.filter_id = env.get('filter')
    env_obj.acl_path = env.get('acl_path')
    env_obj.ipv4_template = env.get('ipv4_template')
    env_obj.ipv6_template = env.get('ipv6_template')
    env_obj.link = env.get('link')
    env_obj.min_num_vlan_1 = env.get('min_num_vlan_1')
    env_obj.max_num_vlan_1 = env.get('max_num_vlan_1')
    env_obj.min_num_vlan_2 = env.get('min_num_vlan_2')
    env_obj.max_num_vlan_2 = env.get('max_num_vlan_2')
    env_obj.vrf = env.get('vrf')
    env_obj.father_environment_id = env.get('father_environment')

    env_obj.save()

    return env_obj


def create_environment(env):
    """
    Create environment

    :param env: dict
    """

    env_obj = Ambiente()

    env_obj.grupo_l3_id = env.get('grupo_l3')
    env_obj.ambiente_logico_id = env.get('ambiente_logico')
    env_obj.divisao_dc_id = env.get('divisao_dc')
    env_obj.filter_id = env.get('filter')
    env_obj.acl_path = env.get('acl_path')
    env_obj.ipv4_template = env.get('ipv4_template')
    env_obj.ipv6_template = env.get('ipv6_template')
    env_obj.link = env.get('link')
    env_obj.min_num_vlan_1 = env.get('min_num_vlan_1')
    env_obj.max_num_vlan_1 = env.get('max_num_vlan_1')
    env_obj.min_num_vlan_2 = env.get('min_num_vlan_2')
    env_obj.max_num_vlan_2 = env.get('max_num_vlan_2')
    env_obj.vrf = env.get('vrf')
    env_obj.father_environment_id = env.get('father_environment')

    env_obj.save()

    return env_obj


def delete_environment(env_ids):
    """
    Delete environment

    :param env: dict
    """

    for env_id in env_ids:
        env_obj = get_environment_by_id(env_id)
        env_obj.delete()
