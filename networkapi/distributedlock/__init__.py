# encoding: utf-8

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import with_statement

LOCK_LOGICAL_ENVIRONMENT = "logical_environment:%s"
LOCK_ENVIRONMENT = "environment:%s"
LOCK_DC_DIVISION = "division:%s"
LOCK_DCHCPv4_NET = "DHCPrelayIPv4Network:%s"
LOCK_DCHCPv6_NET = "DHCPrelayIPv6Network:%s"
LOCK_ENVIRONMENT_VIP = "environment_vip:%s"
LOCK_EQUIPMENT_ACCESS = "equipment_access:%s"
LOCK_EQUIPMENT = "equipment:%s"
LOCK_EQUIPMENT_GROUP = "equipment_group:%s"
LOCK_EQUIPMENT_DEPLOY_CONFIG_USERSCRIPT = "equipment_deploy_config_userscript:%s"
LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT = "equipment_deploy_config_network_script:%s"
LOCK_EQUIPMENT_SCRIPT = "equipment_script:%s"
LOCK_EQUIPMENT_ENVIRONMENT = "equipment_environment:%s"
LOCK_GROUP_USER = "group_user:%s"
LOCK_GROUP_EQUIPMENT = "group_equipment:%s"
LOCK_GROUP_RIGHTS = "group_rights:%s"
LOCK_GROUP_VIRTUAL = "group_virtual"
LOCK_GROUP_L3 = "group_l3:%s"
LOCK_PERM = "perm:%s"
LOCK_INTERFACE = "interface:%s"
LOCK_INTERFACE_DEPLOY_CONFIG = "interface_equipment:%s"
LOCK_IP_EQUIPMENT = "ip_equipment:%s:%s"
LOCK_IPV4 = "ipv4:%s"
LOCK_NETWORK_IPV4 = "network_ipv4:%s"
LOCK_IPV6 = "ipv6:%s"
LOCK_NETWORK_IPV6 = "network_ipv6:%s"
LOCK_BRAND = "brand:%s"
LOCK_MODEL = "model:%s"
LOCK_VIP = "vip:%s"
LOCK_OPTIONS_VIP = "options_vip:%s"
LOCK_VIP_IP_EQUIP = "vip_ip_equip:%s:%s:%s"
LOCK_SCRIPT = "script:%s"
LOCK_SCRIPT_TYPE = "script_type:%s"
LOCK_TYPE_ACCESS = "type_access:%s"
LOCK_TYPE_NETWORK = "type_network:%s"
LOCK_USER_GROUP = "user_group:%s:%s"
LOCK_USER = "user:%s"
LOCK_VLAN = "vlan:%s"
LOCK_RACK = "rack:%s"


# Adjusts settings
from django.core.cache import cache
from networkapi.distributedlock.memcachedlock import MemcachedLock

DEBUG = False
DEFAULT_TIMEOUT = 600
DEFAULT_BLOCKING = True
DEFAULT_MEMCACHED_CLIENT = cache
DEFAULT_LOCK_FACTORY = lambda key: MemcachedLock(
    key, DEFAULT_MEMCACHED_CLIENT, DEFAULT_TIMEOUT)


def _debug(msg):
    if DEBUG:
        print "LOCK:", msg


class LockNotAcquiredError(Exception):
    pass


class distributedlock(object):

    def __init__(self, key=None, lock=None, blocking=None):
        self.key = key
        self.lock = lock
        if blocking == None:
            self.blocking = DEFAULT_BLOCKING
        else:
            self.blocking = blocking

        if not self.lock:
            self.lock = DEFAULT_LOCK_FACTORY(self.key)

    # for use with decorator
    def __call__(self, f):
        if not self.key:
            self.key = "%s:%s" % (f.__module__, f.__name__)

        def wrapped(*args, **kargs):
            with self:
                return f(*args, **kargs)
        return wrapped

    # for use with "with" block
    def __enter__(self):
        if not (type(self.key) == str or type(self.key) == unicode) and self.key == '':
            raise RuntimeError("Key not specified!")

        if self.lock.acquire(self.blocking):
            _debug("locking with key %s" % self.key)
        else:
            raise LockNotAcquiredError()

    def __exit__(self, type, value, traceback):
        _debug("releasing lock %s" % self.key)
        self.lock.release()
