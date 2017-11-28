# -*- coding: utf-8 -*-
from __future__ import with_statement

LOCK_LOGICAL_ENVIRONMENT = 'logical_environment:%s'
LOCK_ENVIRONMENT = 'environment:%s'
LOCK_ENVIRONMENT_ALLOCATES = 'environment_allocates:%s'
LOCK_VLAN_ALLOCATES = 'vlan_allocates:%s'
LOCK_DC_DIVISION = 'division:%s'
LOCK_DCHCPv4_NET = 'DHCPrelayIPv4Network:%s'
LOCK_DCHCPv6_NET = 'DHCPrelayIPv6Network:%s'
LOCK_ENVIRONMENT_VIP = 'environment_vip:%s'
LOCK_EQUIPMENT_ACCESS = 'equipment_access:%s'
LOCK_EQUIPMENT = 'equipment:%s'
LOCK_EQUIPMENT_GROUP = 'equipment_group:%s'
LOCK_EQUIPMENT_DEPLOY_CONFIG_USERSCRIPT = 'equipment_deploy_config_userscript:%s'
LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT = 'equipment_deploy_config_network_script:%s'
LOCK_EQUIPMENT_SCRIPT = 'equipment_script:%s'
LOCK_EQUIPMENT_ENVIRONMENT = 'equipment_environment:%s'
LOCK_GROUP_USER = 'group_user:%s'
LOCK_GROUP_EQUIPMENT = 'group_equipment:%s'
LOCK_GROUP_RIGHTS = 'group_rights:%s'
LOCK_GROUP_VIRTUAL = 'group_virtual'
LOCK_GROUP_L3 = 'group_l3:%s'
LOCK_PERM = 'perm:%s'
LOCK_INTERFACE = 'interface:%s'
LOCK_INTERFACE_DEPLOY_CONFIG = 'interface_equipment:%s'
LOCK_IP_EQUIPMENT_ONE = 'ip_equipment:%s'
LOCK_IP_EQUIPMENT = 'ip_equipment:%s:%s'
LOCK_VINTERFACE = 'vinterface:%s'
LOCK_IPV6_EQUIPMENT_ONE = 'ipv6_equipment:%s'
LOCK_IPV6_EQUIPMENT = 'ipv6_equipment:%s:%s'
LOCK_IPV4 = 'ipv4:%s'
LOCK_NETWORK_IPV4 = 'network_ipv4:%s'
LOCK_IPV6 = 'ipv6:%s'
LOCK_NETWORK_IPV6 = 'network_ipv6:%s'
LOCK_BRAND = 'brand:%s'
LOCK_MODEL = 'model:%s'
LOCK_VIP = 'vip:%s'
LOCK_NEIGHBOR_V4 = 'neighbor_v4:%s'
LOCK_NEIGHBOR_V6 = 'neighbor_v6:%s'
LOCK_PEER_GROUP = 'peer_group:%s'
LOCK_ROUTE_MAP = 'route_map:%s'
LOCK_ROUTE_MAP_ENTRY = 'route_map_entry:%s'
LOCK_LIST_CONFIG_BGP = 'list_config_bgp:%s'
LOCK_OPTIONS_VIP = 'options_vip:%s'
LOCK_VIP_IP_EQUIP = 'vip_ip_equip:%s:%s:%s'
LOCK_POOL = 'pool:%s'
LOCK_SCRIPT = 'script:%s'
LOCK_SCRIPT_TYPE = 'script_type:%s'
LOCK_TYPE_ACCESS = 'type_access:%s'
LOCK_TYPE_NETWORK = 'type_network:%s'
LOCK_USER_GROUP = 'user_group:%s:%s'
LOCK_USER = 'user:%s'
LOCK_VLAN = 'vlan:%s'
LOCK_RACK = 'rack:%s'
LOCK_NEIGHBOR = 'neighbor:%s'
LOCK_GET_IPV4_AVAILABLE = 'Ipv4_get_available_for_vip:%s'
LOCK_GET_IPV6_AVAILABLE = 'Ipv6_get_available_for_vip:%s'


# Adjusts settings
from django.core.cache import cache
from networkapi.distributedlock.memcachedlock import MemcachedLock

DEBUG = False
DEFAULT_TIMEOUT = 1200
DEFAULT_BLOCKING = True
DEFAULT_MEMCACHED_CLIENT = cache


def default_lock_factory(key):
    return MemcachedLock(
        key, DEFAULT_MEMCACHED_CLIENT, DEFAULT_TIMEOUT)


def _debug(msg):
    if DEBUG:
        print 'LOCK:', msg


class LockNotAcquiredError(Exception):
    pass


class distributedlock(object):

    def __init__(self, key=None, lock=None, blocking=None):
        self.key = key
        self.lock = lock
        if blocking is None:
            self.blocking = DEFAULT_BLOCKING
        else:
            self.blocking = blocking

        if not self.lock:
            self.lock = default_lock_factory(self.key)

    # for use with decorator
    def __call__(self, f):
        if not self.key:
            self.key = '%s:%s' % (f.__module__, f.__name__)

        def wrapped(*args, **kargs):
            with self:
                return f(*args, **kargs)
        return wrapped

    # for use with "with" block
    def __enter__(self):
        if not (type(self.key) == str or type(self.key) == unicode) and self.key == '':
            raise RuntimeError('Key not specified!')

        if self.lock.acquire(self.blocking):
            _debug('locking with key %s' % self.key)
        else:
            raise LockNotAcquiredError()

    def __exit__(self, type, value, traceback):
        _debug('releasing lock %s' % self.key)
        self.lock.release()
