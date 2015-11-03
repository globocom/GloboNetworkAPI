import bigsuds
from functools import wraps
import logging
from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.F5 import lb

log = logging.getLogger(__name__)

########################################
# Decorators
########################################


def transation(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        if not kwargs.__contains__('connection') or kwargs['connection']:
            try:
                self._lb = lb.Lb(
                    args[0].get('fqdn'), args[0].get('user'), args[0].get('password'))
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


def getStatusName(status):
    try:
        return STATUS_POOL_MEMBER[status]
    except Exception, e:
        msg = 'Member status invalid: %s' % (status)
        log.error(msg)
        raise base_exceptions.NamePropertyInvalid(msg)


def getMethodName(lb_method):
    try:
        return LB_METHOD[lb_method]
    except Exception, e:
        msg = 'Member lb_method invalid: %s' % (lb_method)
        log.error(msg)
        raise base_exceptions.NamePropertyInvalid(msg)

def getServiceDownActionName(action):
    try:
        return SERVICE_DOWN_ACTION[action]
    except Exception, e:
        msg = '"%s" is not a valid value for Service Down Action' % (action)
        log.error(msg)
        raise base_exceptions.NamePropertyInvalid(msg)


def _trataParam(pools):
    pls = {
        'pools_names': [],
        'pools_lbmethod': [],
        'pools_healthcheck': [],
        'pools_actions': [],
        'pools_members': {
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
                getMethodName(p['lb_method']))

        if p.get('healthcheck'):
            pls['pools_healthcheck'].append(p['healthcheck'])

        if p.get('action'):
            pls['pools_actions'].append(getServiceDownActionName(p['action']))

        member_status_monitor = []
        member_status_session = []
        member_limit = []
        member_priority = []
        member_weight = []
        member = []
        for pool_member in p['pools_members']:
            if pool_member.get('member_status'):
                status = getStatusName(
                    str(pool_member['member_status']))
                member_status_monitor.append(status['monitor'])
                member_status_session.append(status['session'])

            if pool_member.get('limit'):
                member_limit.append(pool_member['limit'])

            if pool_member.get('priority'):
                member_priority.append(pool_member['priority'])

            if pool_member.get('weight'):
                member_weight.append(pool_member['weight'])

            member.append({
                'address': pool_member['ip'],
                'port': pool_member['port']})

        pls['pools_members']['monitor'].append(member_status_monitor)
        pls['pools_members']['session'].append(member_status_session)
        pls['pools_members']['limit'].append(member_limit)
        pls['pools_members']['priority'].append(member_priority)
        pls['pools_members']['weight'].append(member_weight)
        pls['pools_members']['members'].append(member)

    return pls


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
