# -*- coding:utf-8 -*-

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

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.plugins import exceptions as base_exceptions
import logging
from ..base import BasePlugin
import json

import bigsuds

log = logging.getLogger(__name__)


class Generic(BasePlugin):

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

    def __init__(self, **kwargs):
        if 'equipment' in kwargs:
            self.equipment = kwargs.get('equipment')

    def getStatusName(self, status):
        return self.STATUS_POOL_MEMBER[status]


    def getMethodName(self, method):
        return self.LB_METHOD[method]

    def connect(self, **kwargs):

        try:
            b = bigsuds.BIGIP(
                hostname=kwargs.get('fqdn'),
                username=kwargs.get('user'),
                password=kwargs.get('password'))
            self.channel = b
        except bigsuds.Connecti, detail:
            logging.critical(
                "Unable to connect to BIG-IP. Details: %s" %
                pformat(detail))
            raise base_exceptions.CommandErrorException(e)

    def newSession(self):
        self.channel = self.channel.with_session_id()
        self.channel.System.Session.set_transaction_timeout(99)

    def setStateMember(self, pools):

        self.connect(
            fqdn=pools['fqdn'],
            user=pools['user'],
            password=pools['password'])

        self.newSession()

        try:
            with bigsuds.Transaction(self.channel):
                self.channel.LocalLB.Pool.set_member_monitor_state(
                    pools['pools_name'],
                    pools['pools_members'],
                    pools['pools_members_monitor_state'])

                self.channel.LocalLB.Pool.set_member_session_enabled_state(
                    pools['pools_name'],
                    pools['pools_members'],
                    pools['pools_members_session_state'])
        except bigsuds.OperationFailed, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)

        except Exception, e:
            log.error("Error  %s" % e)
            raise base_exceptions.CommandErrorException(e)

    def getStateMember(self, pools):

        self.connect(
            fqdn=pools['fqdn'],
            user=pools['user'],
            password=pools['password'])

        self.newSession()

        try:
            with bigsuds.Transaction(self.channel):
                monitors = self.channel.LocalLB.Pool.get_member_monitor_status(
                    pools['pools_name'],
                    pools['pools_members'])

                sessions = self.channel.LocalLB.Pool.get_member_session_status(
                    pools['pools_name'],
                    pools['pools_members'])

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

        except bigsuds.OperationFailed, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)

        except Exception, e:
            log.error("Error  %s" % e)
            raise base_exceptions.CommandErrorException(e)

    def createPool(self, pools):
        self.connect(
            fqdn=pools['fqdn'],
            user=pools['user'],
            password=pools['password'])

        self.newSession()

        log.info(pools)
        try:
            with bigsuds.Transaction(self.channel):

                self.channel.LocalLB.Pool.create_v2(
                    pools['pools_name'],
                    pools['pools_lbmethod'],
                    pools['pools_members'])

            return True
        
        except bigsuds.OperationFailed, e:
            log.error(e)
            raise base_exceptions.CommandErrorException(e)

        except Exception, e:
            log.error("Error  %s" % e)
            raise base_exceptions.CommandErrorException(e)
