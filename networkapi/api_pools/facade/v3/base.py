# -*- coding:utf-8 -*-
import logging
import time

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from networkapi.ambiente.models import Ambiente
from networkapi.ambiente.models import EnvironmentVip
from networkapi.api_pools import exceptions
from networkapi.api_pools import models
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_POOL
from networkapi.grupo.models import UGrupo
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.infrastructure.datatable import build_query_to_datatable
from networkapi.ip.models import Ip
from networkapi.ip.models import Ipv6
from networkapi.requisicaovips.models import ServerPool
from networkapi.requisicaovips.models import ServerPoolMember

log = logging.getLogger(__name__)


########################
# Pools
########################
def create_pool(pool):
    """Creates pool"""

    sp = ServerPool()
    sp.identifier = pool.get('identifier')
    sp.default_port = pool.get('default_port')
    sp.environment_id = pool.get('environment')
    sp.servicedownaction_id = _get_option_pool(
        pool.get('servicedownaction').get('name'),
        'ServiceDownAction')
    sp.lb_method = pool.get('lb_method')
    sp.default_limit = pool.get('default_limit')
    healthcheck = _get_healthcheck(pool.get('healthcheck'))
    sp.healthcheck = healthcheck
    sp.pool_created = False

    sp.save()

    _create_pool_member(pool['server_pool_members'], sp.id)

    if pool.get('groups_permissions'):
        _create_groups_permissions(pool['groups_permissions'], sp.id)

    return sp


def update_pool(pool):
    """Updates pool"""

    sp = ServerPool.objects.get(id=pool.get('id'))
    sp.identifier = pool.get('identifier')
    sp.default_port = pool.get('default_port')
    sp.environment_id = pool.get('environment')
    sp.servicedownaction_id = _get_option_pool(
        pool.get('servicedownaction').get('name'),
        'ServiceDownAction')
    sp.lb_method = pool.get('lb_method')
    sp.default_limit = pool.get('default_limit')
    healthcheck = _get_healthcheck(pool.get('healthcheck'))
    sp.healthcheck = healthcheck

    members_create = [member for member in pool['server_pool_members'] if not member['id']]
    members_update = [member for member in pool['server_pool_members'] if member['id']]
    members_ids = [member['id'] for member in pool['server_pool_members'] if member['id']]
    members_remove = [member.id for member in sp.serverpoolmember_set.all() if member.id not in members_ids]

    sp.save()

    _create_pool_member(members_create, sp.id)
    _update_pool_member(members_update)
    _delete_pool_member(members_remove)

    return sp


def delete_pool(pools_ids):
    """Updates pool"""

    for pools_id in pools_ids:
        try:
            sp = ServerPool.objects.get(id=pools_id)
        except ObjectDoesNotExist:
            raise exceptions.PoolNotExist()

        if sp.pool_created:
            raise exceptions.PoolConstraintCreatedException()

        sp.delete()


def get_pool_by_ids(pools_ids):
    """
    Return pool list by ids
    param pools_ids: ids list
    example: [<pools_id>,...]
    """

    server_pools = list()
    for pools_id in pools_ids:
        try:
            sp = ServerPool.objects.get(id=pools_id)
        except ObjectDoesNotExist:
            raise exceptions.PoolNotExist()

        server_pools.append(sp)

    return server_pools


def get_pool_by_id(pool_id):
    """
    Return pool by id
    param pools_id: id
    """

    try:
        server_pool = ServerPool.objects.get(id=pool_id)
    except ObjectDoesNotExist:
        raise exceptions.PoolNotExist()

    return server_pool


def get_pool_list_by_environmentvip(environment_vip_id):
    """
    Return pool list by environment_vip_id
    param environment_vip_id: environment_vip_id
    """

    env_vip = EnvironmentVip.objects.get(id=environment_vip_id)

    server_pool = ServerPool.objects.filter(
        Q(environment__vlan__networkipv4__ambient_vip=env_vip) |
        Q(environment__vlan__networkipv6__ambient_vip=env_vip)
    ).distinct().order_by('identifier')

    return server_pool


def get_options_pool_list_by_environment(environment_id):
    """
    Return list of options pool by environment_id
    param environment_id: environment_id
    """

    options_pool = models.OptionPool.objects.filter(
        optionpoolenvironment__environment=environment_id)

    return options_pool


def get_pool_by_search(search=dict()):

    pools = ServerPool.objects.filter()
    if search.get('extends_search'):
        pools = pools.filter(reduce(
            lambda x, y: x | y, [Q(**item) for item in search.get('extends_search')]))

    search_query = dict()
    search_query['asorting_cols'] = search.get('asorting_cols') or ['-id']
    search_query['custom_search'] = search.get('custom_search') or None
    search_query['searchable_columns'] = search.get('searchable_columns') or None
    search_query['start_record'] = search.get('start_record') or 0
    search_query['end_record'] = search.get('end_record') or 25

    pools, total = build_query_to_datatable(
        pools,
        search_query['asorting_cols'],
        search_query['custom_search'],
        search_query['searchable_columns'],
        search_query['start_record'],
        search_query['end_record'])

    pool_map = dict()
    pool_map["pools"] = pools
    pool_map["total"] = total

    return pool_map


########################
# Members
########################
def _create_groups_permissions(groups_permissions, pool_id):
    """Creates permissions to access for pools"""

    for groups_permission in groups_permissions:
        pool_perm = models.ServerPoolGroupPermission()
        pool_perm.server_pool_id = pool_id
        pool_perm.group = UGrupo.get_by_pk(groups_permission['group'])
        pool_perm.read = groups_permission['read']
        pool_perm.write = groups_permission['write']
        pool_perm.delete = groups_permission['delete']
        pool_perm.change_config = groups_permission['change_config']
        pool_perm.save()


def _create_pool_member(members, pool_id):
    """Creates pool members"""

    for member in members:
        pool_member = ServerPoolMember()
        pool_member.server_pool_id = pool_id
        pool_member.ip = Ip.get_by_pk(member['ip']['id']) if member['ip'] else None
        pool_member.ipv6 = Ipv6.get_by_pk(member['ipv6']['id']) if member['ipv6'] else None
        pool_member.identifier = member['identifier']
        pool_member.weight = member['weight']
        pool_member.priority = member['priority']
        pool_member.port_real = member['port_real']
        pool_member.member_status = member['member_status']
        pool_member.limit = member['limit']
        pool_member.save()


def _update_pool_member(members):
    """Updates pool members"""

    for member in members:
        pool_member = ServerPoolMember.objects.get(id=member['id'])
        pool_member.ip = Ip.get_by_pk(member['ip']['id']) if member['ip'] else None
        pool_member.ipv6 = Ipv6.get_by_pk(member['ipv6']['id']) if member['ipv6'] else None
        pool_member.identifier = member['identifier']
        pool_member.weight = member['weight']
        pool_member.priority = member['priority']
        pool_member.port_real = member['port_real']
        pool_member.member_status = member['member_status']
        pool_member.limit = member['limit']
        pool_member.save()


def _delete_pool_member(members):
    """Deletes pool members"""
    ServerPoolMember.objects.filter(id__in=members).delete()


########################
# Helpers
########################
def validate_save(pool, permit_created=False):

    has_identifier = ServerPool.objects.filter(
        identifier=pool['identifier'],
        environment=pool['environment']
    )

    try:
        Ambiente.objects.get(id=pool['environment'])
    except ObjectDoesNotExist:
        raise exceptions.InvalidIdEnvironmentException('pool identifier: %s' % pool['identifier'])

    if pool.get('id'):
        server_pool = ServerPool.objects.get(id=pool['id'])
        if server_pool.pool_created:
            if not permit_created:
                raise exceptions.CreatedPoolValuesException('pool id: %s' % pool['id'])

            if server_pool.identifier != pool['identifier']:
                raise exceptions.PoolNameChange('pool id: %s' % pool['id'])

            if server_pool.environment_id != pool['environment']:
                raise exceptions.PoolEnvironmentChange('pool id: %s' % pool['id'])

        members_db = [spm.id for spm in server_pool.serverpoolmember_set.all()]
        has_identifier = has_identifier.exclude(id=pool['id'])

    if has_identifier.count() > 0:
        raise exceptions.InvalidIdentifierAlreadyPoolException()

    for member in pool['server_pool_members']:
        if member['ip']:
            amb = Ambiente.objects.filter(
                environmentenvironmentvip__environment_vip__in=EnvironmentVip.objects.filter(
                    networkipv4__vlan__ambiente=pool['environment'])
            ).filter(
                environmentenvironmentvip__environment__vlan__networkipv4__ip=member['ip']['id']
            )
            if not amb:
                raise exceptions.IpNotFoundByEnvironment()

        if member['ipv6']:
            amb = Ambiente.objects.filter(
                environmentenvironmentvip__environment_vip__in=EnvironmentVip.objects.filter(
                    networkipv6__vlan__ambiente=pool['environment'])
            ).filter(
                environmentenvironmentvip__environment__vlan__networkipv6__ipv6=member['ipv6']['id']
            )
            if not amb:
                raise exceptions.IpNotFoundByEnvironment()

        if member['id']:
            if member['id'] not in members_db:
                raise exceptions.InvalidRealPoolException()


def _get_healthcheck(healthcheck_obj):
    """Get or creates a healthcheck"""

    healthcheck = {
        'identifier': healthcheck_obj['identifier'],
        'healthcheck_expect': healthcheck_obj['healthcheck_expect'],
        'healthcheck_type': healthcheck_obj['healthcheck_type'],
        'healthcheck_request': healthcheck_obj['healthcheck_request'],
        'destination': healthcheck_obj['destination']
    }

    try:
        hc = Healthcheck.objects.get(**healthcheck)
    except ObjectDoesNotExist:
        hc = Healthcheck(**healthcheck)
        hc.save()

    return hc


def create_lock(pools):
    """
    Create locks to pools list
    """
    locks_list = list()
    for pool in pools:
        lock = distributedlock(LOCK_POOL % pool['id'])
        lock.__enter__()
        locks_list.append(lock)

    return locks_list


def destroy_lock(locks_list):
    """
    Destroy locks by pools list
    """
    for lock in locks_list:
        lock.__exit__('', '', '')


def reserve_name_healthcheck(pool_name):
    name = '/Common/MONITOR_POOL_%s_%s' % (pool_name, str(time.time()))

    return name


def _get_option_pool(option_name, option_type):
    try:
        return models.OptionPool.objects.get(name=option_name, type=option_type).id
    except:
        raise exceptions.InvalidServiceDownActionException()
