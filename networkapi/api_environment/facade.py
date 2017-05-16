# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.db.models import Q

from networkapi.equipamento.models import Equipamento
from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.ambiente.models import AmbienteUsedByEquipmentVlanError
from networkapi.ambiente.models import EnvironmentErrorV3
from networkapi.api_environment_vip.facade import get_environmentvip_by_id
from networkapi.api_pools import exceptions
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.plugins.factory import PluginFactory


log = logging.getLogger(__name__)


def get_environment_by_search(search=dict()):
    """Return a list of environments by dict."""

    try:
        environments = Ambiente.objects.filter()
        env_map = build_query_to_datatable_v3(environments, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return env_map


def get_environment_by_id(environment_id):
    """Return a environment by id.

    Args:
        environment_id: Id of environment
    """

    try:
        environment = Ambiente.get_by_pk(id=environment_id)
    except AmbienteNotFoundError, e:
        raise exceptions.EnvironmentDoesNotExistException(str(e))

    return environment


def get_environment_by_ids(environment_ids):
    """Return environment list by ids.

    Args:
        environment_ids: List of Ids of environments.
    """

    env_ids = list()
    for environment_id in environment_ids:
        try:
            env = get_environment_by_id(environment_id).id
            env_ids.append(env)
        except exceptions.EnvironmentDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

    environments = Ambiente.objects.filter(id__in=env_ids)

    return environments


def list_environment_environment_vip_related(env_id=None):
    """List of environments related with environment vip.

    Args:
        env_id: Id of environment(optional).
    """

    try:
        if env_id is None:
            env_list_net_related = Ambiente.objects.filter(
                Q(vlan__networkipv4__ambient_vip__id__isnull=False) |
                Q(vlan__networkipv6__ambient_vip__id__isnull=False)
            )
        else:
            env_vip = get_environmentvip_by_id(env_id)
            env_list_net_related = Ambiente.objects.filter(
                Q(vlan__networkipv4__ambient_vip=env_vip) |
                Q(vlan__networkipv6__ambient_vip=env_vip)
            )

        env_list_net_related = env_list_net_related.order_by(
            'divisao_dc__nome', 'ambiente_logico__nome', 'grupo_l3__nome'
        ).select_related(
            'grupo_l3', 'ambiente_logico', 'divisao_dc', 'filter'
        ).distinct()

    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return env_list_net_related


def update_environment(env):
    """Update environment."""

    try:
        env_obj = get_environment_by_id(env.get('id'))
        env_obj.update_v3(env)
    except EnvironmentErrorV3, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.EnvironmentDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return env_obj


def create_environment(env):
    """Create environment."""

    try:
        env_obj = Ambiente()
        env_obj.create_v3(env)
    except EnvironmentErrorV3, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return env_obj


def delete_environment(env_ids):
    """Delete environment."""

    for env_id in env_ids:
        try:
            env_obj = get_environment_by_id(env_id)
            env_obj.delete_v3()
        except AmbienteUsedByEquipmentVlanError, e:
            raise ValidationAPIException(str(e))
        except exceptions.EnvironmentDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except AmbienteError, e:
            raise NetworkAPIException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

def get_controller_by_envid(env_id):
    q_filter_environment = {
        'equipamentoambiente__ambiente': env_id,
        'equipamentoambiente__is_controller': env_id
    }

    return Equipamento.objects.filter(Q(**q_filter_environment)).uniqueResult()

def list_flows_by_envid(env_id, flow_id=0):
    eqpt = get_controller_by_envid(env_id)
    plugin = PluginFactory.factory(eqpt)

    try:
        if flow_id > 0:
            return plugin.get_flow(flow_id=flow_id)
        else:
            return plugin.get_flows()

    except Exception as e:
        log.error(e)
        raise NetworkAPIException("Failed to communicate with Controller plugin. See log for details.")

def insert_flow(env_id, data):
    eqpt = get_controller_by_envid(env_id)
    plugin = PluginFactory.factory(eqpt)

    try:
        return plugin.add_flow(data=data)
    except:
        raise NetworkAPIException("Failed to communicate with Controller plugin. See log for details.")

def delete_flow(env_id, flow_id):
    eqpt = get_controller_by_envid(env_id)
    plugin = PluginFactory.factory(eqpt)

    try:
        return plugin.del_flow(flow_id=flow_id)
    except:
        raise NetworkAPIException("Failed to communicate with Controller plugin. See log for details.")









