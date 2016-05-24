from functools import wraps
import logging

import bigsuds

from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.F5 import lb
from networkapi.util import is_healthcheck_valid

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
                self._lb = lb.Lb(args[0].get('fqdn'), args[0].get('user'), args[0].get('password'))
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
            self._lb = lb.Lb(args[0].get('fqdn'), args[0].get('user'), args[0].get('password'))
            self._lb._channel.System.Session.set_transaction_timeout(60)
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

        if p.get('healthcheck'):
            is_healthcheck_valid(p['healthcheck'])
            pls['pools_healthcheck'].append(p['healthcheck'])

        if p.get('action'):
            pls['pools_actions'].append(get_service_down_action_name(p['action']))

        member_status_monitor = []
        member_status_session = []
        member_limit = []
        member_priority = []
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

            if pool_member.get('limit'):
                member_limit.append(pool_member['limit'])

            if pool_member.get('priority'):
                member_priority.append(pool_member['priority'])

            if pool_member.get('weight'):
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
        pls['pools_members']['weight'].append(member_weight)
        pls['pools_members']['members'].append(member)
        pls['pools_members']['members_new'].append(member_new)
        pls['pools_members']['members_remove'].append(member_remove)

    return pls


def trata_param_vip(vips):

    vips_filter = list()
    vips_cache_filter = list()
    pool_filter = list()
    pool_filter_created = list()

    ids_pool_filter = list()
    ids_pool_filter_created = list()

    for vip in vips['vips']:

        vip_request = vip.get('vip_request')
        ports = vip_request.get('ports')

        dscp = vip_request['options']['dscp'] * 4 if vip_request['options']['dscp'] else 65535

        for port in ports:
            vip_filter = dict()
            conf = vip_request['conf']['conf']

            address = vip_request['ipv4']['ip_formated'] if vip_request['ipv4'] else vip_request['ipv6']['ip_formated']

            vip_filter['pool'] = list()
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
            for pool in pools:
                if not pool.get('l7_rule') in ['(nenhum)', 'default']:
                    raise NotImplementedError()

                server_pool = pool.get('server_pool')
                if not server_pool.get('pool_created'):
                    if server_pool.get('id') not in ids_pool_filter:
                        ids_pool_filter.append(server_pool.get('id'))
                        pool_filter.append(server_pool)
                else:
                    if server_pool.get('id') not in ids_pool_filter_created:
                        ids_pool_filter_created.append(server_pool.get('id'))
                        pool_filter_created.append(server_pool)

                vip_filter['pool'].append(server_pool['nome'])

                vip_filter['optionsvip']['dscp'] = {
                    'value': dscp,
                    'pool_name': server_pool['nome']
                }
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

                    vip_cache_filter['pool'] = list()
                    vip_cache_filter['name'] = 'VIP%s_%s_%s' % (vip_request['id'], address, port['port'])
                    vip_cache_filter['address'] = address
                    vip_cache_filter['port'] = port['port']

                    vip_cache_filter['optionsvip'] = dict()
                    vip_cache_filter['optionsvip_extended'] = dict()

                    vip_cache_filter['optionsvip']['l4_protocol'] = port['options']['l4_protocol']
                    for definition in definitions.get(str(port['port'])):
                        if definition.get('type') == 'pool':
                            vip_cache_filter['pool'] = [definition.get('value')]
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

    res_fil = {
        'vips_filter': vips_filter,
        'vips_cache_filter': vips_cache_filter,
        'pool_filter': pool_filter,
        'pool_filter_created': pool_filter_created
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
