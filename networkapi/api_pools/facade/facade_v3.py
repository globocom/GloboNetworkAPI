# -*- coding:utf-8 -*-
import logging

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.transaction import commit_on_success

from networkapi.ambiente.models import EnvironmentVip
from networkapi.api_equipment.exceptions import AllEquipmentsAreInMaintenanceException
from networkapi.api_equipment.facade import all_equipments_are_in_maintenance
from networkapi.api_pools import exceptions, models
from networkapi.distributedlock import distributedlock, LOCK_POOL
from networkapi.equipamento.models import Equipamento, EquipamentoAcesso, EquipamentoAmbiente
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.infrastructure.datatable import build_query_to_datatable
from networkapi.ip.models import Ip, Ipv6
from networkapi.plugins.factory import PluginFactory
from networkapi.requisicaovips.models import ServerPool, ServerPoolMember

log = logging.getLogger(__name__)
protocolo_access = 'https'


################
# Apply in eqpt
################
@commit_on_success
def create_real_pool(pools):
    """
        Create real pool in eqpt
    """

    load_balance = dict()
    keys_cache = list()

    for pool in pools:

        equips = _validate_pool_members_to_apply(pool)

        for e in equips:
            eqpt_id = str(e.equipamento.id)
            equipment_access = EquipamentoAcesso.search(
                equipamento=e.equipamento.id,
                protocolo=protocolo_access
            ).uniqueResult()
            equipment = Equipamento.get_by_pk(e.equipamento.id)

            plugin = PluginFactory.factory(equipment)

            if not load_balance.get(eqpt_id):

                load_balance[eqpt_id] = {
                    'plugin': plugin,
                    'fqdn': equipment_access.fqdn,
                    'user': equipment_access.user,
                    'password': equipment_access.password,
                    'pools': [],
                }

            keys_cache.append('pool:monitor:%s' % pool['identifier'])

            load_balance[eqpt_id]['pools'].append({
                'id': pool['id'],
                'nome': pool['identifier'],
                'lb_method': pool['lb_method'],
                'healthcheck': pool['healthcheck'],
                'action': pool['servicedownaction']['name'],
                'pools_members': [{
                    'id': pool_member['id'],
                    'ip': pool_member['ip']['ip_formated'] if pool_member['ip'] else pool_member['ipv6']['ip_formated'],
                    'port': pool_member['port_real'],
                    'member_status': pool_member['member_status'],
                    'limit': pool_member['limit'],
                    'priority': pool_member['priority'],
                    'weight': pool_member['weight']
                } for pool_member in pool['server_pool_members']]
            })

    for lb in load_balance:
        load_balance[lb]['plugin'].create_pool(load_balance[lb])

    for key_cache in keys_cache:
        cache.delete(key_cache)

    ids = [pool['id'] for pool in pools]
    ServerPool.objects.filter(id__in=ids).update(pool_created=True)

    return {}


@commit_on_success
def delete_real_pool(pools):
    """
    delete real pool in eqpt
    """

    load_balance = {}

    for pool in pools:

        equips = _validate_pool_members_to_apply(pool)

        for e in equips:
            eqpt_id = str(e.equipamento.id)
            equipment_access = EquipamentoAcesso.search(
                equipamento=e.equipamento.id,
                protocolo=protocolo_access
            ).uniqueResult()
            equipment = Equipamento.get_by_pk(e.equipamento.id)

            plugin = PluginFactory.factory(equipment)

            if not load_balance.get(eqpt_id):

                load_balance[eqpt_id] = {
                    'plugin': plugin,
                    'fqdn': equipment_access.fqdn,
                    'user': equipment_access.user,
                    'password': equipment_access.password,
                    'pools': [],
                }

            load_balance[eqpt_id]['pools'].append({
                'id': pool['id'],
                'nome': pool['identifier'],
                'lb_method': pool['lb_method'],
                'healthcheck': pool['healthcheck'],
                'action': pool['servicedownaction']['name'],
                'pools_members': [{
                    'id': pool_member['id'],
                    'ip': pool_member['ip']['ip_formated'] if pool_member['ip'] else pool_member['ipv6']['ip_formated'],
                    'port': pool_member['port_real'],
                    'member_status': pool_member['member_status'],
                    'limit': pool_member['limit'],
                    'priority': pool_member['priority'],
                    'weight': pool_member['weight']
                } for pool_member in pool['server_pool_members']]

            })

    for lb in load_balance:
        load_balance[lb]['plugin'].delete_pool(load_balance[lb])

    ids = [pool['id'] for pool in pools]
    ServerPool.objects.filter(id__in=ids).update(pool_created=False)

    return {}


@commit_on_success
def update_real_pool(pools):
    """
    - update real pool in eqpt
    - update data pool in db
    """
    load_balance = dict()
    keys_cache = list()

    for pool in pools['server_pools']:
        validate_save(pool, permit_created=True)

        member_ids = [spm['id'] for spm in pool['server_pool_members'] if spm['id']]

        db_members = ServerPoolMember.objects.filter(id__in=member_ids)
        db_members_id = [str(s.id) for s in db_members]

        db_members_remove = ServerPoolMember.objects.filter(
            server_pool__id=pool['id']).exclude(id__in=member_ids)

        pools_members = list()
        for pool_member in pool['server_pool_members']:

            ip = pool_member['ip']['ip_formated'] if pool_member['ip'] else pool_member['ipv6']['ip_formated']

            if pool_member['id']:

                member = db_members[db_members_id.index(str(pool_member['id']))]
                ip_db = member.ip.ip_formated if member.ip else member.ipv6.ip_formated

                if member.port_real == pool_member['port_real'] and ip_db == ip:
                    # update info of member
                    pools_members.append({
                        'id': pool_member['id'],
                        'ip': ip,
                        'port': pool_member['port_real'],
                        'limit': pool_member['limit'],
                        'priority': pool_member['priority'],
                        'weight': pool_member['weight'],
                    })
                else:
                    # delete member with old port and old ip
                    pools_members.append({
                        'id': None,
                        'ip': ip_db,
                        'port': member.port_real,
                        'remove': 1
                    })
                    # create delete member with new port and new ip
                    pools_members.append({
                        'id': pool_member['id'],
                        'ip': ip,
                        'port': pool_member['port_real'],
                        'limit': pool_member['limit'],
                        'priority': pool_member['priority'],
                        'weight': pool_member['weight'],
                        'new': 1
                    })
            else:
                # create member
                pools_members.append({
                    'id': None,
                    'ip': ip,
                    'port': pool_member['port_real'],
                    'limit': pool_member['limit'],
                    'priority': pool_member['priority'],
                    'weight': pool_member['weight'],
                    'new': 1
                })

        # delete members
        for member in db_members_remove:
            pools_members.append({
                'id': member.id,
                'ip': member.ip.ip_formated if member.ip else member.ipv6.ip_formated,
                'port': member.port_real,
                'remove': 1
            })

        # get eqpts associate with pool
        equips = _validate_pool_to_apply(pool, update=True)

        for e in equips:
            eqpt_id = str(e.equipamento.id)
            equipment_access = EquipamentoAcesso.search(
                equipamento=e.equipamento.id,
                protocolo=protocolo_access
            ).uniqueResult()
            equipment = Equipamento.get_by_pk(e.equipamento.id)

            plugin = PluginFactory.factory(equipment)

            if not load_balance.get(eqpt_id):

                load_balance[eqpt_id] = {
                    'plugin': plugin,
                    'fqdn': equipment_access.fqdn,
                    'user': equipment_access.user,
                    'password': equipment_access.password,
                    'pools': [],
                }

            keys_cache.append('pool:monitor:%s' % pool['identifier'])

            load_balance[eqpt_id]['pools'].append({
                'id': pool['id'],
                'nome': pool['identifier'],
                'lb_method': pool['lb_method'],
                'healthcheck': pool['healthcheck'],
                'action': pool['servicedownaction']['name'],
                'pools_members': pools_members
            })

        update_pool(pool)

    for lb in load_balance:
        load_balance[lb]['plugin'].update_pool(load_balance[lb])

    for key_cache in keys_cache:
        cache.delete(key_cache)

    return {}


def set_poolmember_state(pools):
    """
    Set Pool Members state

    """
    load_balance = {}

    for pool in pools['server_pools']:
        if pool['server_pool_members']:
            equips = _validate_pool_members_to_apply(pool)

            for e in equips:
                eqpt_id = str(e.equipamento.id)
                equipment_access = EquipamentoAcesso.search(
                    equipamento=e.equipamento.id,
                    protocolo=protocolo_access
                ).uniqueResult()
                equipment = Equipamento.get_by_pk(e.equipamento.id)

                plugin = PluginFactory.factory(equipment)

                if not load_balance.get(eqpt_id):

                    load_balance[eqpt_id] = {
                        'plugin': plugin,
                        'fqdn': equipment_access.fqdn,
                        'user': equipment_access.user,
                        'password': equipment_access.password,
                        'pools': [],
                    }

                load_balance[eqpt_id]['pools'].append({
                    'id': pool['id'],
                    'nome': pool['identifier'],
                    'pools_members': [{
                        'id': pool_member['id'],
                        'ip': pool_member['ip']['ip_formated'] if pool_member['ip'] else pool_member['ipv6']['ip_formated'],
                        'port': pool_member['port_real'],
                        'member_status': pool_member['member_status']
                    } for pool_member in pool['server_pool_members']]
                })

    for lb in load_balance:
        load_balance[lb]['plugin'].set_state_member(load_balance[lb])

    for pool in pools['server_pools']:
        for pool_member in pool['server_pool_members']:
            ServerPoolMember.objects.filter(id=pool_member['id']).update(member_status=pool_member['member_status'])

    return {}


def get_poolmember_state(pools):
    """
    Return Pool Members State
    """

    load_balance = {}

    for pool in pools:

        if pool['server_pool_members']:

            equips = _validate_pool_members_to_apply(pool)

            for e in equips:
                eqpt_id = str(e.equipamento.id)
                equipment_access = EquipamentoAcesso.search(
                    equipamento=e.equipamento.id,
                    protocolo=protocolo_access
                ).uniqueResult()
                equipment = Equipamento.get_by_pk(e.equipamento.id)

                plugin = PluginFactory.factory(equipment)

                if not load_balance.get(eqpt_id):

                    load_balance[eqpt_id] = {
                        'plugin': plugin,
                        'fqdn': equipment_access.fqdn,
                        'user': equipment_access.user,
                        'password': equipment_access.password,
                        'pools': [],
                    }

                load_balance[eqpt_id]['pools'].append({
                    'id': pool['id'],
                    'nome': pool['identifier'],
                    'pools_members': [{
                        'id': pool_member['id'],
                        'ip': pool_member['ip']['ip_formated'] if pool_member['ip'] else pool_member['ipv6']['ip_formated'],
                        'port': pool_member['port_real'],
                        'member_status': pool_member['member_status']
                    } for pool_member in pool['server_pool_members']]
                })

    ps = dict()
    status = dict()
    for lb in load_balance:
        # call plugin to get state member
        states = load_balance[lb]['plugin'].get_state_member(load_balance[lb])

        for idx, state in enumerate(states):
            pool_id = load_balance[lb]['pools'][idx]['id']
            if not ps.get(pool_id):
                ps[pool_id] = {}
                status[pool_id] = {}

            # populate variable for to verify diff states
            for idx_m, st in enumerate(state):
                member_id = load_balance[lb]['pools'][idx]['pools_members'][idx_m]['id']
                if not ps[pool_id].get(member_id):
                    ps[pool_id][member_id] = []

                ps[pool_id][member_id].append(st)
                status[pool_id][member_id] = st

    # Verify diff state of pool member in eqpts
    for idx in ps:
        for idx_m in ps[idx]:
            if len(set(ps[idx][idx_m])) > 1:
                msg = 'There are states differents in equipments.'
                log.error(msg)
                raise exceptions.DiffStatesEquipament(msg)

    return status


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


def delete_pool(pools_id):
    """Updates pool"""

    sp = ServerPool.objects.filter(id__in=pools_id)
    created = sp.filter(pool_created=True)
    if created:
        raise exceptions.PoolConstraintCreatedException()

    sp.delete()


def get_pool_by_ids(pools_ids):
    """
    Return pool list by ids
    param pools_ids: ids list
    example: [<pools_id>,...]
    """

    server_pools = ServerPool.objects.filter(id__in=pools_ids)

    return server_pools


def get_pool_by_search(search=dict()):

    pools = ServerPool.objects.filter()

    if search.get('asorting_cols'):
        search['asorting_cols'] = search.get('asorting_cols').split(';')

    pools, total = build_query_to_datatable(
        pools,
        search.get('asorting_cols') or None,
        search.get('custom_search') or None,
        search.get('searchable_columns') or None,
        search.get('start_record') or 0,
        search.get('end_record') or 25
    )
    pool_map = dict()
    pool_map["pools"] = pools
    pool_map["total"] = total

    return pool_map

########################
# Members
########################


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
            vips = EnvironmentVip.objects.filter(
                environmentenvironmentvip__environment__vlan__networkipv4__ip=member['ip']['id']
            ).filter(environmentenvironmentvip__environment__id=pool['environment'])
            if not vips:
                raise exceptions.IpNotFoundByEnvironment()

        if member['ipv6']:
            vips = EnvironmentVip.objects.filter(
                environmentenvironmentvip__environment__vlan__networkipv6__ipv6=member['ipv6']['id']
            ).filter(environmentenvironmentvip__environment__id=pool['environment'])
            if not vips:
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


def _validate_pool_members_to_apply(pool):

    if pool['server_pool_members']:
        q_filters = [{
            'ipv6': pool_member['ipv6']['id'] if pool_member['ipv6'] else None,
            'ip': pool_member['ip']['id'] if pool_member['ip'] else None,
            'id': pool_member['id'],
            'port_real': pool_member['port_real']
        } for pool_member in pool['server_pool_members']]

        server_pool_members = ServerPoolMember.objects.filter(
            reduce(
                lambda x, y: x | y, [Q(**q_filter) for q_filter in q_filters]),
            server_pool=pool['id'])
        if len(server_pool_members) != len(q_filters):
            raise exceptions.PoolmemberNotExist()

    equips = _validate_pool_to_apply(pool)

    return equips


def _validate_pool_to_apply(pool, update=False):
    server_pool = ServerPool.objects.get(
        identifier=pool['identifier'],
        environment=pool['environment'],
        id=pool['id'])
    if not server_pool:
        raise exceptions.PoolNotExist()

    if update and not server_pool.pool_created:
        raise exceptions.PoolNotCreated(server_pool.id)

    equips = EquipamentoAmbiente.objects.filter(
        equipamento__maintenance=0,
        ambiente__id=pool['environment'],
        equipamento__tipo_equipamento__tipo_equipamento=u'Balanceador')

    if all_equipments_are_in_maintenance([e.equipamento for e in equips]):
        raise AllEquipmentsAreInMaintenanceException()

    return equips


def _get_option_pool(option_name, option_type):
    try:
        return models.OptionPool.objects.get(name=option_name, type=option_type).id
    except:
        raise exceptions.InvalidServiceDownActionException()
