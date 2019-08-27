# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.db.models import Q

from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import AmbienteError
from networkapi.ambiente.models import AmbienteNotFoundError
from networkapi.ambiente.models import AmbienteUsedByEquipmentVlanError
from networkapi.ambiente.models import AmbienteLogico
from networkapi.ambiente.models import DivisaoDc
from networkapi.ambiente.models import GrupoL3
from networkapi.ambiente.models import EnvironmentErrorV3
from networkapi.api_environment.tasks.flows import async_add_flow
from networkapi.api_environment.tasks.flows import async_delete_flow
from networkapi.api_environment.tasks.flows import async_flush_environment
from networkapi.api_environment_vip.facade import get_environmentvip_by_id
from networkapi.api_pools import exceptions
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.equipamento.models import Equipamento
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.plugins.factory import PluginFactory
from networkapi.api_equipment import exceptions as exceptions_eqpt
from networkapi.api_equipment import facade as facade_eqpt

log = logging.getLogger(__name__)


def get_l3_environment_by_search(search=dict()):
    """Return a list of dc environments by dict."""

    try:
        environments = GrupoL3.objects.filter()
        env_map = build_query_to_datatable_v3(environments, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return env_map


def create_l3_environment(env):
    """Create environment."""

    try:
        env_obj = GrupoL3()
        env_obj.create_v3(env)
    except EnvironmentErrorV3, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return env_obj


def get_logic_environment_by_search(search=dict()):
    """Return a list of dc environments by dict."""

    try:
        environments = AmbienteLogico.objects.filter()
        env_map = build_query_to_datatable_v3(environments, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return env_map


def create_logic_environment(env):
    """Create environment."""

    try:
        env_obj = AmbienteLogico()
        env_obj.create_v3(env)
    except EnvironmentErrorV3, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return env_obj


def get_dc_environment_by_search(search=dict()):
    """Return a list of dc environments by dict."""

    try:
        environments = DivisaoDc.objects.filter()
        env_map = build_query_to_datatable_v3(environments, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return env_map


def create_dc_environment(env):
    """Create environment."""

    try:
        env_obj = DivisaoDc()
        env_obj.create_v3(env)
    except EnvironmentErrorV3, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return env_obj


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
    """ Get all controllers from a given environment """

    q_filter_environment = {
        'equipmentcontrollerenvironment__environment': env_id,
        'maintenance': 0
    }

    equips = Equipamento.objects.filter(Q(**q_filter_environment))

    if facade_eqpt.all_equipments_are_in_maintenance(equips):
        raise exceptions_eqpt.AllEquipmentsAreInMaintenanceException()

    return equips


def list_flows_by_envid(env_id, flow_id=0):
    eqpts = get_controller_by_envid(env_id)
    flows_list = {}

    for eqpt in eqpts:
        plugin = PluginFactory.factory(eqpt, env_id=env_id)
        try:
            if flow_id > 0:
                flows_list.update(plugin.get_flow(flow_id=flow_id))
            else:
                flows_list.update(plugin.get_flows())

        except Exception as e:
            log.error(e)
            raise NetworkAPIException('Failed to list flow(s)'
                                      'plugin. %s' % e)

    return flows_list


def insert_flow(env_id, data, user_id):
    eqpts = get_controller_by_envid(env_id)
    plugins = []
    for eqpt in eqpts:
        plugins.append(PluginFactory.factory(eqpt, env_id=env_id))
    try:
        return async_add_flow.apply_async(
            args=[plugins, user_id, data], queue='napi.odl_flow'
        )
    except Exception as e:
        log.error(e)
        raise NetworkAPIException('Failed to insert flow(s) '
                                  'plugin. %s' % e)


def delete_flow(env_id, flow_id, user_id):
    """ Deletes one flow by id using the async task """

    eqpts = get_controller_by_envid(env_id)

    plugins = []
    for eqpt in eqpts:
        plugins.append(PluginFactory.factory(eqpt, env_id=env_id))

    try:
        return async_delete_flow.apply_async(
            args=[plugins, user_id, flow_id], queue='napi.odl_flow'
        )
    except Exception as err:
        log.error(err)
        raise NetworkAPIException('Failed to delete flow with error: %s' % err)


def flush_flows(env_id):
    """ Flushes flow from a environment without restore it """
    eqpts = get_controller_by_envid(env_id)
    for eqpt in eqpts:
        plugin = PluginFactory.factory(eqpt, env_id=env_id)
        try:
            plugin.flush_flows()
        except Exception as e:
            log.error(e)
            raise NetworkAPIException('Failed to flush Controller '
                                      'plugin. %s' % e)


def update_flows(env_id, data, user_id):
    """ Call equipment plugin to asynchronously flush the environment """
    eqpts = get_controller_by_envid(env_id)
    plugins = []
    for eqpt in eqpts:
        plugins.append(PluginFactory.factory(eqpt, env_id=env_id))

    try:
        return async_flush_environment.apply_async(
            args=[plugins, user_id, data], queue='napi.odl_flow'
        )
    except Exception as e:
        log.error(e)
        raise NetworkAPIException('Failed to flush flow(s) '
                                  'from environment: %s \n%s' % (env_id, e))
