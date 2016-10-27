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

    environments = list()
    for environment_id in environment_ids:
        env = get_environment_by_id(environment_id)
        environments.append(env)

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

    Ambiente.update(
        None,
        env_obj.id,
        grupo_l3_id=env.get('grupo_l3'),
        ambiente_logico_id=env.get('ambiente_logico'),
        divisao_dc_id=env.get('divisao_dc'),
        filter_id=env.get('filter'),
        acl_path=env.get('acl_path'),
        ipv4_template=env.get('ipv4_template'),
        ipv6_template=env.get('ipv6_template'),
        link=env.get('link'),
        min_num_vlan_1=env.get('min_num_vlan_1'),
        max_num_vlan_1=env.get('max_num_vlan_1'),
        min_num_vlan_2=env.get('min_num_vlan_2'),
        max_num_vlan_2=env.get('max_num_vlan_2'),
        vrf=env.get('vrf'),
        default_vrf=env.get('default_vrf'),
        father_environment_id=env.get('father_environment'),
    )

    # configs of environment
    # env_id = env.get('id')
    # configs = env.get('configs', [])
    # ips_by_env = IPConfig.get_by_environment(None, env_id)
    # ids_conf_current = [ip_by_env.id for ip_by_env in ips_by_env]

    # if configs:
    #     # configs with ids
    #     ids_conf_receive = [cfg.get('id') for cfg in configs
    #                         if cfg.get('id')]

    #     # configs to update: configs with id
    #     cfg_upt = [cfg for cfg in configs if cfg.get('id') and
    #                cfg.get('id') in ids_conf_current]

    #     # configs to create: configs without id
    #     cfg_ins = [cfg for cfg in configs if not cfg.get('id')]

    #     # configs to delete: configs not received
    #     cfg_del = [id_conf for id_conf in ids_conf_current
    #                if id_conf not in ids_conf_receive]

    #     update_configs(cfg_upt, env_id)
    #     create_configs(cfg_ins, env_id)
    #     delete_configs(cfg_del, env_id)

    # else:
    #     delete_configs(ids_conf_current, env_id)

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
    env_obj.default_vrf_id = env.get('default_vrf')
    env_obj.father_environment_id = env.get('father_environment')

    env_obj.create(None)

    # create_configs(env.get('configs', []), env_obj.id)

    return env_obj


def delete_environment(env_ids):
    """
    Delete environment

    :param env: dict
    """

    for env_id in env_ids:
        Ambiente.remove(None, env_id)


def update_configs(configs, env_id):
    """
    Update configs of environment

    :param configs: Configs of environment
    :param env: Id of environment
    """
    for config in configs:
        try:
            ip_config = IPConfig.objects.get(
                id=config.get('id'),
                configenvironment__environment=env_id
            )
        except ObjectDoesNotExist:
            raise exceptions.ConfigIpDoesNotExistException()

        ip_config.subnet = config.get('subnet')
        ip_config.new_prefix = config.get('new_prefix')
        ip_config.type = config.get('type')
        ip_config.network_type_id = config.get('network_type')

        ip_config.save()


def create_configs(configs, env_id):
    """
    Create configs of environment

    :param configs: Configs of environment
    :param env: Id of environment
    """

    for config in configs:
        IPConfig.create(env_id, config)


def delete_configs(configs_ids, env_id):
    """
    Delete configs of environment

    :param configs_ids: Id of Configs of environment
    :param env: Id of environment
    """

    for config_id in configs_ids:
        IPConfig.remove(None, env_id, config_id)


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
