# -*- coding:utf-8 -*-
import copy
import logging
from functools import wraps

import bigsuds

from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.F5 import lb

log = logging.getLogger(__name__)


########################################
# Decorators
########################################
def logger(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        log.info('%s.%s: %s,%s' % (self.__class__.__name__, func.__name__, args, kwargs))
        return func(self, *args, **kwargs)

    return inner


def transation(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        if not kwargs.__contains__('connection') or kwargs['connection']:
            try:
                access = args[0].get('access').filter(tipo_acesso__protocolo='https').uniqueResult()
                self._lb = lb.Lb(access.fqdn, access.user, access.password)
                if not kwargs.__contains__('transation') or kwargs['transation']:
                    log.info('Transaction Started')
                    with bigsuds.Transaction(self._lb._channel):
                        return func(self, *args, **kwargs)
                else:
                    return func(self, *args, **kwargs)
            except bigsuds.OperationFailed, e:
                log.error(e)
                raise base_exceptions.CommandErrorException(e)
            except Exception, e:
                log.error("Error  %s" % e)
                raise base_exceptions.CommandErrorException(e)
        else:
            return func(self, *args, **kwargs)
    return inner


def connection(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        try:
            access = args[0].get('access').filter(tipo_acesso__protocolo='https').uniqueResult()
            self._lb = lb.Lb(access.fqdn, access.user, access.password)
            self._lb._channel.System.Session.set_transaction_timeout(60)
            return func(self, *args, **kwargs)
        except bigsuds.OperationFailed, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)
    return inner


def connection_simple(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        try:
            access = args[0].get('access').filter(tipo_acesso__protocolo='https').uniqueResult()
            self._lb = lb.Lb(access.fqdn, access.user, access.password, False)
            return func(self, *args, **kwargs)
        except bigsuds.OperationFailed, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)
    return inner


def get_status_name(status):
    try:
        return STATUS_POOL_MEMBER[status]
    except Exception:
        msg = 'Member status invalid: %s' % (status)
        log.error(msg)
        raise base_exceptions.NamePropertyInvalid(msg)


def get_method_name(lb_method):
    try:
        return LB_METHOD[lb_method]
    except Exception:
        msg = 'Member lb_method invalid: %s' % (lb_method)
        log.error(msg)
        raise base_exceptions.NamePropertyInvalid(msg)


def get_service_down_action_name(action):
    try:
        return SERVICE_DOWN_ACTION[action]
    except Exception:
        msg = '"%s" is not a valid value for Service Down Action' % (action)
        log.error(msg)
        raise base_exceptions.NamePropertyInvalid(msg)


def trata_param_pool(pools):
    pls = {
        'pools_names': [],
        'pools_lbmethod': [],
        'pools_healthcheck': [],
        'pools_actions': [],
        'pools_confirm': {
            'pools_names': [],
            'members': [],
            'monitor': []
        },
        'pools_members': {
            'members_new': [],
            'members_remove': [],
            'members': [],
            'monitor': [],
            'session': [],
            'description': [],
            'priority': [],
            'weight': [],
            'limit': []
        }

    }

    for p in pools['pools']:
        pls['pools_names'].append(p['nome'])

        if p.get('lb_method'):
            pls['pools_lbmethod'].append(
                get_method_name(p['lb_method']))

        if p.get('healthcheck') is not None:
            if p.get('healthcheck').get('new'):
                pls['pools_healthcheck'].append(p['healthcheck'])

        if p.get('action'):
            pls['pools_actions'].append(get_service_down_action_name(p['action']))

        member_status_monitor = []
        member_status_session = []
        member_limit = []
        member_priority = []
        member_description = []
        member_weight = []
        member = []
        member_new = []
        member_remove = []
        for pool_member in p['pools_members']:

            state = str(pool_member.get('member_status'))

            if pool_member.get('new'):
                node_port = {
                    'address': pool_member['ip'],
                    'port': pool_member['port']}
                member_new.append(node_port)
                if state == '7':
                    if p['nome'] not in pls['pools_confirm']['pools_names']:
                        pls['pools_confirm']['pools_names'].append(p['nome'])
                        pls['pools_confirm']['members'].append(list())
                        pls['pools_confirm']['monitor'].append(list())
                    status_confirm = get_status_name(state)
                    state = '2'

                    idx = pls['pools_confirm']['pools_names'].index(p['nome'])
                    pls['pools_confirm']['members'][idx].append(node_port)
                    pls['pools_confirm']['monitor'][idx].append(status_confirm['monitor'])

            if pool_member.get('member_status') is not None:
                status = get_status_name(state)
                member_status_monitor.append(status['monitor'])
                member_status_session.append(status['session'])

            if pool_member.get('limit') is not None:
                member_limit.append(pool_member['limit'])

            if pool_member.get('priority') is not None:
                member_priority.append(pool_member['priority'])

            if pool_member.get('identifier') is not None:
                member_description.append(pool_member['identifier'])

            if pool_member.get('weight') is not None:
                member_weight.append(pool_member['weight'])

            if not pool_member.get('remove'):
                member.append({
                    'address': pool_member['ip'],
                    'port': pool_member['port']})

            if pool_member.get('remove'):
                member_remove.append({
                    'address': pool_member['ip'],
                    'port': pool_member['port']})

        pls['pools_members']['monitor'].append(member_status_monitor)
        pls['pools_members']['session'].append(member_status_session)
        pls['pools_members']['limit'].append(member_limit)
        pls['pools_members']['priority'].append(member_priority)
        pls['pools_members']['description'].append(member_description)
        pls['pools_members']['weight'].append(member_weight)
        pls['pools_members']['members'].append(member)
        pls['pools_members']['members_new'].append(member_new)
        pls['pools_members']['members_remove'].append(member_remove)

    return pls


def trata_param_vip(vips):

    vips_filter = list()
    pool_filter = list()
    ids_pool_filter = list()
    vips_cache_filter = list()

    # when pool already created in eqpt
    pool_filter_created = list()
    ids_pool_filter_created = list()

    # to use in pool and port deleted(update vip)
    vips_filter_to_delete = list()
    pool_filter_to_delete = list()
    ids_pool_filter_to_delete = list()

    # to use in new pool or new port(update vip)
    vips_filter_to_insert = list()
    pool_filter_to_insert = list()
    ids_pool_filter_to_insert = list()

    for vip in vips['vips']:

        vp = copy.deepcopy(vip.get('vip_request'))

        ports = vp.get('ports')
        for pt in ports:

            vip_filter = dict()
            vip_request = copy.deepcopy(vp)
            port = copy.deepcopy(pt)

            dscp = vip_request['options']['dscp'] * 4 if vip_request['options']['dscp'] else 65535
            conf = vip_request['conf']['conf']
            address = vip_request['ipv4']['ip_formated'] if vip_request['ipv4'] else vip_request['ipv6']['ip_formated']

            vip_filter['name'] = 'VIP%s_%s_%s' % (vip_request['id'], address, port['port'])
            vip_filter['address'] = address
            vip_filter['port'] = port['port']
            vip_filter['optionsvip'] = vip_request['options']
            vip_filter['optionsvip']['l7_protocol'] = port['options']['l7_protocol']
            vip_filter['optionsvip']['l4_protocol'] = port['options']['l4_protocol']

            try:
                cluster_unit = None
                for keys in conf['keys']:
                    cluster_unit = keys.get(vip_request['options']['cluster_unit'])

                    # traffic-group-1 is default, so must be ignored
                    if cluster_unit == 'traffic-group-1':
                        cluster_unit = None
                        break

                    if cluster_unit:
                        break
                vip_filter['optionsvip']['traffic_group'] = cluster_unit
            except:
                vip_filter['optionsvip']['traffic_group'] = None
                pass
            vip_filter['optionsvip_extended'] = conf['optionsvip_extended']

            pools = port.get('pools')
            rules = dict()
            default_l7 = ''

            for pl in pools:
                pool = copy.deepcopy(pl)
                server_pool = pool.get('server_pool')
                name_pool = server_pool['nome']
                usage_l7 = True

                # pool to delete in put request of vip(when delete pool or port)
                if pl.get('delete') or pt.get('delete'):
                    usage_l7 = False
                    if server_pool.get('id') not in ids_pool_filter_to_delete:
                        ids_pool_filter_to_delete.append(server_pool.get('id'))
                        pool_filter_to_delete.append(server_pool)
                # pool to insert in put request of vip(update port or insert port)
                elif not pl.get('id'):
                    if server_pool.get('id') not in pool_filter_to_insert and \
                            not server_pool.get('pool_created'):
                        ids_pool_filter_to_insert.append(server_pool.get('id'))
                        pool_filter_to_insert.append(server_pool)
                # used in post and delete request of vip
                else:
                    if not server_pool.get('pool_created'):
                        if server_pool.get('id') not in ids_pool_filter:
                            ids_pool_filter.append(server_pool.get('id'))
                            pool_filter.append(server_pool)
                    else:
                        # pool already created
                        if server_pool.get('id') not in ids_pool_filter_created:
                            ids_pool_filter_created.append(server_pool.get('id'))
                            pool_filter_created.append(server_pool)

                # no l7 rule
                if pool.get('l7_rule') == 'default_vip':

                    vip_filter['pool'] = name_pool

                    vip_filter['optionsvip']['dscp'] = {
                        'value': dscp,
                        'pool_name': name_pool
                    }
                # default of l7 rule
                elif usage_l7:
                    if pool.get('l7_rule') == 'default_glob':
                        default_l7 = "            default {{ pool {0} }}\n".format(
                            name_pool)
                    # l7 rule
                    elif pool.get('l7_rule') == 'glob':

                        rule = '"{0}"'.format(pool.get('l7_value'))
                        order = pool.get('order', 'Z')
                        key_rule = '{}_{}'.format(order, name_pool)
                        if not rules.get(key_rule):
                            rules[key_rule] = dict()
                            rules[key_rule]['pool'] = name_pool
                            rules[key_rule]['rule'] = list()
                        rules[key_rule]['rule'].append(rule)

            # rules to create
            if rules:
                rule_l7_ln = "\n            ".join([
                    "{0} {{\n                pool {1}\n            }}".format(
                        " -\n            ".join(rules[idx]['rule']),
                        rules[idx]['pool']
                    ) for idx in sorted(rules)
                ])

                rule_l7 = \
                    "when HTTP_REQUEST {{\n" + \
                    "        switch -glob [HTTP::uri] {{\n" + \
                    "            {0}\n{1}" + \
                    "        }}\n" + \
                    "    }}"
                rule_l7 = rule_l7.format(rule_l7_ln, default_l7)

                vip_filter['pool_l7'] = rule_l7

            # port(vip_port) to delete in update of vip
            if pt.get('delete'):
                vips_filter_to_delete.append(vip_filter)
            # port(vip_port) to insert in update of vip
            elif not pt.get('id'):
                vips_filter_to_insert.append(vip_filter)
            # vips to create/delete/update
            else:
                vips_filter.append(vip_filter)

    if vips.get('layers'):
        for vip_id in vips.get('layers'):
            for id_layer in vips.get('layers').get(vip_id):
                definitions = vips.get('layers').get(vip_id).get(id_layer).get('definitions')
                vip_request = vips.get('layers').get(vip_id).get(id_layer).get('vip_request')
                ports = vip_request.get('ports')
                for port in ports:
                    vip_cache_filter = dict()

                    address = vip_request['ipv4']['ip_formated'] if vip_request['ipv4'] else vip_request['ipv6']['ip_formated']

                    vip_cache_filter['pool'] = None
                    vip_cache_filter['name'] = 'VIP%s_%s_%s' % (vip_request['id'], address, port['port'])
                    vip_cache_filter['address'] = address
                    vip_cache_filter['port'] = port['port']

                    vip_cache_filter['optionsvip'] = dict()
                    vip_cache_filter['optionsvip_extended'] = dict()

                    vip_cache_filter['optionsvip']['l4_protocol'] = port['options']['l4_protocol']
                    for definition in definitions.get(str(port['port'])):
                        if definition.get('type') == 'pool':
                            vip_cache_filter['pool'] = definition.get('value')
                        if definition.get('type') == 'rule':
                            if definition.get('value'):
                                vip_cache_filter['rules'] = [definition.get('value')]
                        if definition.get('type') == 'profile':
                            vip_cache_filter['optionsvip_extended'] = {
                                "requiments": [{
                                    "condicionals": [{
                                        "validations": [],
                                        "use":[
                                            definition
                                        ]
                                    }]
                                }]
                            }
                        if definition.get('type') == 'traffic_group':
                            if definition.get('value') == 'traffic-group-1':
                                vip_cache_filter['optionsvip']['traffic_group'] = None
                            else:
                                vip_cache_filter['optionsvip']['traffic_group'] = definition.get('value')

                    vips_cache_filter.append(vip_cache_filter)

    # remove pools in both lists(to delete and to insert)
    to_delete = list(set(ids_pool_filter_to_delete) - set(ids_pool_filter_to_insert))
    to_insert = list(set(ids_pool_filter_to_insert) - set(ids_pool_filter_to_delete))
    pool_filter_to_delete = [pool_del for pool_del in pool_filter_to_delete if pool_del.get('id') in to_delete]
    pool_filter_to_insert = [pool_ins for pool_ins in pool_filter_to_insert if pool_ins.get('id') in to_insert]

    res_fil = {
        'vips_filter': vips_filter,
        'pool_filter': pool_filter,
        'vips_cache_filter': vips_cache_filter,
        'pool_filter_created': pool_filter_created,
        # used in update of vips
        'pool_filter_to_delete': pool_filter_to_delete,
        'pool_filter_to_insert': pool_filter_to_insert,
        'vips_filter_to_delete': vips_filter_to_delete,
        'vips_filter_to_insert': vips_filter_to_insert,
    }
    return res_fil


def search_dict(mylist, lookup):
    for val in mylist:
        if lookup == val:
            return True
    return False


#######################
# PROPERTIES DICT
#######################

########
# POOL
########
SERVICE_DOWN_ACTION = {
    'reset': 'SERVICE_DOWN_ACTION_RESET',
    'drop': 'SERVICE_DOWN_ACTION_DROP',
    'reselect': 'SERVICE_DOWN_ACTION_RESELECT',
    'none': 'SERVICE_DOWN_ACTION_NONE'
}

###############
# POOL MEMBER
###############
# healthcheck+session enable/disable+user up/down(000 - 111 = 0 - 7)

# 0 0 0
# | | \-- user up/user down (forcado a nao receber nem sessoes de persistencia)
# | |     1/0 forcar disable do membro no pool (user up/down)
# | \---- habilitar/desabilitar membro (session enable/session disable -
# |       nao recebe novas sessoes mas honra persistencia)
# |       1/0 habilitar/desabilitar membro no pool para novas sessoes (session disable)
# \------ status do healthcheck no LB, somente GET, nao e alterado
#         por usuario flag ignorada no PUT.
#         1/0 status do healthcheck no LB member up/down
STATUS_POOL_MEMBER = {
    '0': {
        'monitor': 'STATE_DISABLED',
        'session': 'STATE_DISABLED',
        'healthcheck': 'STATE_DISABLED'
    },
    '1': {
        'monitor': 'STATE_ENABLED',
        'session': 'STATE_DISABLED',
        'healthcheck': 'STATE_DISABLED'
    },
    '2': {
        'monitor': 'STATE_DISABLED',
        'session': 'STATE_ENABLED',
        'healthcheck': 'STATE_DISABLED'
    },
    '3': {
        'monitor': 'STATE_ENABLED',
        'session': 'STATE_ENABLED',
        'healthcheck': 'STATE_DISABLED'
    },
    '4': {
        'monitor': 'STATE_DISABLED',
        'session': 'STATE_DISABLED',
        'healthcheck': 'STATE_ENABLED'
    },
    '5': {
        'monitor': 'STATE_ENABLED',
        'session': 'STATE_DISABLED',
        'healthcheck': 'STATE_ENABLED'
    },
    '6': {
        'monitor': 'STATE_DISABLED',
        'session': 'STATE_ENABLED',
        'healthcheck': 'STATE_ENABLED'
    },
    '7': {
        'monitor': 'STATE_ENABLED',
        'session': 'STATE_ENABLED',
        'healthcheck': 'STATE_ENABLED'
    }
}

LB_METHOD = {
    'least-conn': 'LB_METHOD_LEAST_CONNECTION_MEMBER',
    'round-robin': 'LB_METHOD_ROUND_ROBIN',
    'weighted': 'LB_METHOD_RATIO_MEMBER',
    # '': 'LB_METHOD_LEAST_CONNECTION_MEMBER',
    # '': 'LB_METHOD_OBSERVED_MEMBER',
    # '': 'LB_METHOD_PREDICTIVE_MEMBER',
    # '': 'LB_METHOD_RATIO_NODE_ADDRESS',
    # '': 'LB_METHOD_LEAST_CONNECTION_NODE_ADDRESS',
    # '': 'LB_METHOD_FASTEST_NODE_ADDRESS',
    # '': 'LB_METHOD_OBSERVED_NODE_ADDRESS',
    # '': 'LB_METHOD_PREDICTIVE_NODE_ADDRESS',
    # '': 'LB_METHOD_DYNAMIC_RATIO',
    # '': 'LB_METHOD_FASTEST_APP_RESPONSE',
    # '': 'LB_METHOD_LEAST_SESSIONS',
    # '': 'LB_METHOD_DYNAMIC_RATIO_MEMBER',
    # '': 'LB_METHOD_L3_ADDR',
    # '': 'LB_METHOD_UNKNOWN',
    # '': 'LB_METHOD_WEIGHTED_LEAST_CONNECTION_MEMBER',
    # '': 'LB_METHOD_WEIGHTED_LEAST_CONNECTION_NODE_ADDRESS',
    # '': 'LB_METHOD_RATIO_SESSION',
    # '': 'LB_METHOD_RATIO_LEAST_CONNECTION_MEMBER',
    # '': 'LB_METHOD_RATIO_LEAST_CONNECTION_NODE_ADDRESS'
}
