# -*- coding: utf-8 -*-
import logging
from functools import wraps

from networkapi.plugins import exceptions as base_exceptions
from networkapi.plugins.Brocade import lb
from networkapi.plugins.Brocade.adx_device_driver_impl import BrocadeAdxDeviceDriverImpl
from networkapi.util import is_healthcheck_valid

log = logging.getLogger(__name__)


########################################
# Decorators
########################################
def logger(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        log.info('%s.%s: %s,%s' %
                 (self.__class__.__name__, func.__name__, args, kwargs))
        return func(self, *args, **kwargs)

    return inner


def connection(func):
    @wraps(func)
    def inner(self, *args, **kwargs):
        log.debug('decorator')
        try:
            access = args[0].get('access').filter(
                tipo_acesso__protocolo='ssh').uniqueResult()
            self._lb = lb.Lb(access.fqdn, access.user, access.password)
            self.baddi = BrocadeAdxDeviceDriverImpl(
                service_clients=self._lb.service_clients)
            return func(self, *args, **kwargs)
        except Exception, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)
        else:
            log.info('writing in mem')
            self.baddi.write_mem()
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


def trata_nome(name):
    name_spt = name.split('_')
    del name_spt[-1]
    return '_'.join(name_spt)


def trata_param_pool(pools):
    pls = {
        'pools_names': [],
        'pools_lbmethod': [],
        'pools_healthcheck': [],
        'pools_actions': [],
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
            pls['pools_actions'].append(
                get_service_down_action_name(p['action']))

        member_status_monitor = []
        member_status_session = []
        member_limit = []
        member_priority = []
        member_weight = []
        member = []
        member_new = []
        member_remove = []
        for pool_member in p['pools_members']:

            if pool_member.get('member_status'):
                status = get_status_name(
                    str(pool_member['member_status']))
                member_status_monitor.append(status['monitor'])

            if pool_member.get('limit'):
                member_limit.append(pool_member['limit'])

            if pool_member.get('priority'):
                member_priority.append(pool_member['priority'])

            if pool_member.get('weight'):
                member_weight.append(pool_member['weight'])

            if not pool_member.get('remove'):
                member.append({
                    'address': pool_member['ip'],
                    'protocol_port': pool_member['port']})

            if pool_member.get('new'):
                member_new.append({
                    'address': pool_member['ip'],
                    'protocol_port': pool_member['port']})

            if pool_member.get('remove'):
                member_remove.append({
                    'address': pool_member['ip'],
                    'protocol_port': pool_member['port']})

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
    pool_filter = list()
    pool_filter_created = list()

    for vip in vips['vips']:
        vip_request = vip.get('vip_request')
        vip_filter = dict()
        ports = vip_request.get('ports')
        for port in ports:
            address = vip_request['ipv4']['ip_formated'] if vip_request[
                'ipv4'] else vip_request['ipv6']['ip_formated']

            vip_filter['pool'] = list()
            vip_filter['name'] = '%s_%s' % (vip_request['name'], port['port'])
            vip_filter['address'] = address
            vip_filter['port'] = port['port']
            vip_filter['optionsvip'] = vip_request['options']
            vip_filter['optionsvip']['l7_protocol'] = port[
                'options']['l7_protocol']
            vip_filter['optionsvip']['l4_protocol'] = port[
                'options']['l4_protocol']

            conf = vip_request['conf']['conf']
            vip_filter['optionsvip_extended'] = conf['optionsvip_extended']
            pools = port.get('pools')
            for pool in pools:
                if not pool.get('l7_rule') in ['', 'default']:
                    raise NotImplementedError('l7_rule missing')

                server_pool = pool.get('server_pool')
                if not server_pool.get('pool_created'):
                    pool_filter.append(server_pool)
                else:
                    pool_filter_created.append(server_pool)

                vip_filter['pool'].append(server_pool['nome'])

        vips_filter.append(vip_filter)

    res_fil = {
        'vips_filter': vips_filter,
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
        'monitor': 'DISABLED',
        'session': '',
        'healthcheck': ''
    },
    '1': {
        'monitor': 'ENABLED',
        'session': '',
        'healthcheck': ''
    },
    '2': {
        'monitor': 'DISABLED',
        'session': '',
        'healthcheck': ''
    },
    '3': {
        'monitor': 'ENABLED',
        'session': '',
        'healthcheck': ''
    },
    '4': {
        'monitor': 'DISABLED',
        'session': '',
        'healthcheck': ''
    },
    '5': {
        'monitor': 'ENABLED',
        'session': '',
        'healthcheck': ''
    },
    '6': {
        'monitor': 'DISABLED',
        'session': '',
        'healthcheck': ''
    },
    '7': {
        'monitor': 'ENABLED',
        'session': '',
        'healthcheck': ''
    }
}

LB_METHOD = {
    'least-conn': 'LEAST_CONN',
    'round-robin': 'ROUND_ROBIN',
    'weighted': 'WEIGHTED',
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
