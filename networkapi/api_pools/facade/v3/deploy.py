# -*- coding: utf-8 -*-
import copy
import logging

import json_delta
from django.db.models import Q
from django.db.transaction import commit_on_success

from networkapi.api_equipment import exceptions as exceptions_eqpt
from networkapi.api_equipment import facade as facade_eqpt
from networkapi.api_pools import exceptions
from networkapi.api_pools.facade.v3 import base as facade_v3
from networkapi.api_pools.serializers import v3 as serializers
from networkapi.api_vip_request.serializers import v3 as serializers_vip
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.plugins.factory import PluginFactory
from networkapi.requisicaovips.models import ServerPool
from networkapi.requisicaovips.models import ServerPoolMember

log = logging.getLogger(__name__)


################
# Apply in eqpt
################
def _prepare_apply(pools, created=False, user=None):

    load_balance = dict()
    keys = list()

    for pool in pools:

        equips = _validate_pool_members_to_apply(pool, user)

        keys.append(sorted([str(eqpt.id) for eqpt in equips]))

        healthcheck = pool['healthcheck']
        healthcheck['identifier'] = facade_v3.\
            reserve_name_healthcheck(pool['identifier'])
        healthcheck['new'] = True

        for e in equips:

            eqpt_id = str(e.id)
            equipment_access = EquipamentoAcesso.search(
                equipamento=e.id
            )

            plugin = PluginFactory.factory(e)

            if not load_balance.get(eqpt_id):

                load_balance[eqpt_id] = {
                    'plugin': plugin,
                    'access': equipment_access,
                    'pools': [],
                }

            vips_requests = ServerPool().get_vips_related(pool['id'])

            serializer_vips = serializers_vip.VipRequestV3Serializer(
                vips_requests,
                many=True,
                include=(
                    'ipv4__details',
                    'ipv6__details',
                    'ports__identifier',
                    'ports__pools__server_pool__basic__lb_method',
                )
            )
            vips = serializer_vips.data

            load_balance[eqpt_id]['pools'].append({
                'id': pool['id'],
                'nome': pool['identifier'],
                'lb_method': pool['lb_method'],
                'healthcheck': healthcheck,
                'action': pool['servicedownaction']['name'],
                'vips': vips,
                'pools_members': [{
                    'id': pool_member['id'],
                    'identifier': pool_member['identifier'],
                    'ip': pool_member['ip']['ip_formated']
                    if pool_member['ip'] else
                    pool_member['ipv6']['ip_formated'],
                    'port': pool_member['port_real'],
                    'member_status': pool_member['member_status'],
                    'limit': pool_member['limit'],
                    'priority': pool_member['priority'],
                    'weight': pool_member['weight']
                } for pool_member in pool['server_pool_members']]
            })

    # pools are in differents load balancers
    keys = [','.join(key) for key in keys]
    if len(list(set(keys))) > 1:
        raise Exception('Pools are in differents load balancers')

    return load_balance


@commit_on_success
def create_real_pool(pools, user):
    """Create real pool in eqpt."""

    load_balance = _prepare_apply(pools=pools, created=False, user=user)

    for lb in load_balance:
        load_balance[lb]['plugin'].create_pool(load_balance[lb])

    ids = [pool['id'] for pool in pools]
    ServerPool.objects.filter(id__in=ids).update(pool_created=True)

    return {}


@commit_on_success
def delete_real_pool(pools, user):
    """Delete real pool in eqpt."""

    load_balance = _prepare_apply(pools=pools, created=True, user=user)

    for lb_id in load_balance:
        load_balance[lb_id]['plugin'].delete_pool(load_balance[lb_id])

    ids = [pool['id'] for pool in pools]
    ServerPool.objects.filter(id__in=ids).update(pool_created=False)

    return {}


@commit_on_success
def update_real_pool(pools, user):
    """Update real pool in Load Balancer and DB."""

    load_balance = dict()
    keys = list()

    for pool in pools:

        pool_obj = facade_v3.get_pool_by_id(pool['id'])

        healthcheck_old = serializers.HealthcheckV3Serializer(
            pool_obj.healthcheck).data

        db_members = pool_obj.serverpoolmember_set.all()
        member_ids = [spm['id'] for spm in pool['server_pool_members']
                      if spm['id']]
        db_members_remove = list(db_members.exclude(id__in=member_ids))
        db_members_id = [str(s.id) for s in db_members]

        pool_obj.update_v3(pool, user, permit_created=True)

        pools_members = list()
        for pool_member in pool['server_pool_members']:

            ip = pool_member['ip']['ip_formated'] if pool_member[
                'ip'] else pool_member['ipv6']['ip_formated']

            if pool_member.get('id', None) is not None:

                member = db_members[
                    db_members_id.index(str(pool_member['id']))]
                ip_db = member.ip.ip_formated \
                    if member.ip else member.ipv6.ip_formated

                if member.port_real == pool_member['port_real'] \
                        and ip_db == ip:
                    # update info of member
                    pools_members.append({
                        'id': pool_member['id'],
                        'identifier': member.identifier,
                        'ip': ip,
                        'port': pool_member['port_real'],
                        'limit': pool_member['limit'],
                        'priority': pool_member['priority'],
                        'member_status': pool_member['member_status'],
                        'weight': pool_member['weight'],
                    })
                else:
                    # delete member with old port and old ip
                    pools_members.append({
                        'id': None,
                        'identifier': member.identifier,
                        'ip': ip_db,
                        'port': member.port_real,
                        'remove': 1
                    })
                    # create member with new port and new ip
                    pools_members.append({
                        'id': pool_member['id'],
                        'identifier': ip,
                        'ip': ip,
                        'port': pool_member['port_real'],
                        'limit': pool_member['limit'],
                        'priority': pool_member['priority'],
                        'weight': pool_member['weight'],
                        'member_status': pool_member['member_status'],
                        'new': 1
                    })
            else:
                # create member
                pools_members.append({
                    'id': None,
                    'identifier': ip,
                    'ip': ip,
                    'port': pool_member['port_real'],
                    'limit': pool_member['limit'],
                    'priority': pool_member['priority'],
                    'weight': pool_member['weight'],
                    'member_status': pool_member['member_status'],
                    'new': 1
                })

        # delete members
        for member in db_members_remove:
            pools_members.append({
                'id': member.id,
                'identifier': member.identifier,
                'ip': member.ip.ip_formated
                if member.ip else member.ipv6.ip_formated,
                'port': member.port_real,
                'remove': 1
            })

        # get eqpts associate with pool
        equips = _validate_pool_to_apply(pool, update=True, user=user)

        keys.append(sorted([str(eqpt.id) for eqpt in equips]))

        healthcheck = copy.deepcopy(pool['healthcheck'])
        healthcheck['new'] = False
        if json_delta.diff(healthcheck_old, pool['healthcheck']):
            healthcheck['identifier'] = facade_v3.reserve_name_healthcheck(
                pool['identifier'])
            healthcheck['new'] = True

        for e in equips:
            eqpt_id = str(e.id)
            equipment_access = EquipamentoAcesso.search(
                equipamento=e.id
            )

            plugin = PluginFactory.factory(e)

            if not load_balance.get(eqpt_id):

                load_balance[eqpt_id] = {
                    'plugin': plugin,
                    'access': equipment_access,
                    'pools': [],
                }

            vips_requests = ServerPool().get_vips_related(pool['id'])

            serializer_vips = serializers_vip.VipRequestV3Serializer(
                vips_requests,
                many=True,
                include=(
                    'ipv4__details',
                    'ipv6__details',
                    'ports__identifier',
                    'ports__pools__server_pool__basic__lb_method',
                )
            )
            vips = serializer_vips.data

            load_balance[eqpt_id]['pools'].append({
                'id': pool['id'],
                'nome': pool['identifier'],
                'lb_method': pool['lb_method'],
                'healthcheck': healthcheck,
                'action': pool['servicedownaction']['name'],
                'vips': vips,
                'pools_members': pools_members
            })

    # pools are in differents load balancers
    keys = [','.join(key) for key in keys]
    if len(list(set(keys))) > 1:
        raise Exception('Pools are in differents load balancers')

    for lb in load_balance:
        load_balance[lb]['plugin'].update_pool(load_balance[lb])

    return {}


def _prepare_apply_state(pools, user=None):
    load_balance = dict()
    keys = list()

    for pool in pools:
        server_pool = ServerPool.objects.get(id=pool['id'])

        server_pool_members = server_pool.serverpoolmember_set.all()

        if pool['server_pool_members']:
            equips = _validate_pool_members_to_apply(pool, user)

            keys.append(sorted([str(eqpt.id) for eqpt in equips]))

            for e in equips:
                eqpt_id = str(e.id)
                equipment_access = EquipamentoAcesso.search(
                    equipamento=e.id
                )

                plugin = PluginFactory.factory(e)

                if not load_balance.get(eqpt_id):

                    load_balance[eqpt_id] = {
                        'plugin': plugin,
                        'access': equipment_access,
                        'pools': [],
                    }

                mbs = pool['server_pool_members']
                idx_mbs = [mb['id'] for mb in mbs]

                load_balance[eqpt_id]['pools'].append({
                    'id': server_pool.id,
                    'nome': server_pool.identifier,
                    'pools_members': [{
                        'id': pool_member.id,
                        'ip': pool_member.ip.ip_formated
                        if pool_member.ip else pool_member.ipv6.ip_formated,
                        'port': pool_member.port_real,
                        'member_status': mbs
                        [idx_mbs.index(pool_member.id)]['member_status']
                    } for pool_member in server_pool_members
                        if pool_member.id in idx_mbs]
                })
    # pools are in differents load balancers
    keys = [','.join(key) for key in keys]
    if len(list(set(keys))) > 1:
        raise Exception('Pools are in differents load balancers')

    return load_balance


def set_poolmember_state(pools, user):
    """Set Pool Members state."""

    load_balance = _prepare_apply_state(pools['server_pools'], user)

    for lb in load_balance:
        load_balance[lb]['plugin'].set_state_member(load_balance[lb])

    for pool in pools['server_pools']:
        for pool_member in pool['server_pool_members']:
            ServerPoolMember.objects.filter(
                id=pool_member['id']
            ).update(
                member_status=pool_member['member_status']
            )

    return {}


def get_poolmember_state(pools):
    """Return Pool Members State."""

    load_balance = _prepare_apply_state(pools)

    ps = dict()
    status = dict()
    for lb in load_balance:
        # call plugin to get state member
        states = load_balance[lb]['plugin'].\
            get_state_member(load_balance[lb])

        for idx, state in enumerate(states):
            pool_id = load_balance[lb]['pools'][idx]['id']
            if not ps.get(pool_id):
                ps[pool_id] = {}
                status[pool_id] = {}

            # populate variable for to verify diff states
            for idx_m, st in enumerate(state):
                member_id = load_balance[lb]['pools'][
                    idx]['pools_members'][idx_m]['id']
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


def _validate_pool_members_to_apply(pool, user=None):

    if pool['server_pool_members']:
        q_filters = [{
            'id': pool_member['id']
        } for pool_member in pool['server_pool_members']]

        server_pool_members = ServerPoolMember.objects.filter(
            reduce(lambda x, y: x | y, [
                Q(**q_filter) for q_filter in q_filters]),
            server_pool=pool['id'])
        if len(server_pool_members) != len(q_filters):
            raise exceptions.PoolmemberNotExist()

    equips = _validate_pool_to_apply(pool, user=user)

    return equips


def _validate_pool_to_apply(pool, update=False, user=None):

    server_pool = ServerPool.objects.get(id=pool['id'])
    if not server_pool:
        raise exceptions.PoolNotExist()

    if update and not server_pool.pool_created:
        raise exceptions.PoolNotCreated(server_pool.id)

    equips = Equipamento.objects.filter(
        maintenance=0,
        equipamentoambiente__ambiente__id=server_pool.environment.id,
        tipo_equipamento__tipo_equipamento=u'Balanceador').distinct()

    if facade_eqpt.all_equipments_are_in_maintenance(equips):
        raise exceptions_eqpt.AllEquipmentsAreInMaintenanceException()

    if user:
        if not facade_eqpt.all_equipments_can_update_config(equips, user):
            raise exceptions_eqpt.UserDoesNotHavePermInAllEqptException(
                'User does not have permission to update conf in eqpt. '
                'Verify the permissions of user group with equipment '
                'group. Pool:{}'.format(pool['id']))

    return equips
