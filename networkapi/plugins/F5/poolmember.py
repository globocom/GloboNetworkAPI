from networkapi.plugins import F5
from networkapi.plugins.F5 import util, lb

from networkapi.plugins import exceptions as base_exceptions

import logging

log = logging.getLogger(__name__)

#STATUS POOL MEMBER
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
    'weighted': ''
}

class PoolMember(object):

    def __init__(self, _lb=None):
        if _lb is not None and not isinstance(_lb, lb.Lb):
            base_exceptions.PluginUninstanced('lb must be of type F5.Lb')

        self._lb = _lb

    @util.transation
    def setStates(self, pools):
        self._lb._channel.LocalLB.Pool.set_member_monitor_state(
            pools['pools_name'],
            pools['pools_members'],
            pools['pools_members_monitor_state'])

        self._lb._channel.LocalLB.Pool.set_member_session_enabled_state(
            pools['pools_name'],
            pools['pools_members'],
            pools['pools_members_session_state'])

    @util.transation
    def getStates(self, pools):
        try:
            monitors = self._lb._channel.LocalLB.Pool.get_member_monitor_status(
                pools['pools_name'],
                pools['pools_members'])


            sessions = self._lb._channel.LocalLB.Pool.get_member_session_status(
                pools['pools_name'],
                pools['pools_members'])
        except Exception, e:
            raise e
        else:
            status_pools = []
            for p, pool in enumerate(monitors):
                status = []
                for s, state in enumerate(pool):
                    if state == 'MONITOR_STATUS_UP':
                        healthcheck = '1'
                        monitor = '1'
                    elif state == 'MONITOR_STATUS_DOWN':
                        healthcheck = '0'
                        monitor = '1'
                    elif state == 'MONITOR_STATUS_FORCED_DOWN':
                        healthcheck = '0'
                        monitor = '0'
                    else:
                        healthcheck = '0'
                        monitor = '0'

                    if sessions[p][s]=='SESSION_STATUS_ENABLED':
                        session = '1'
                    elif sessions[p][s]=='SESSION_STATUS_DISABLED':
                        session = '0'
                    else:
                        session = '0'

                    status.append(int(healthcheck+session+monitor,2))

                status_pools.append(status)

            return status_pools

    def __repr__(self):
        log.info('%s'  %(self._lb))
        return self._lb
