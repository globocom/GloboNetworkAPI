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
from django.conf import settings

import bigsuds

log = logging.getLogger(__name__)

class Generic(BasePlugin):

    def __init__(self, **kwargs):
        if 'equipment' in kwargs:
            self.equipment = kwargs.get('equipment')

    def connect(self, **kwargs):

        try:
            b = bigsuds.BIGIP(
                hostname = kwargs.get('fqdn'),
                username = kwargs.get('user'),
                password = kwargs.get('password'))
            self.channel = b
        except bigsuds.Connecti , detail:
            logging.critical("Unable to connect to BIG-IP. Details: %s" % pformat(detail))
            raise base_exceptions.CommandErrorException(e)

    def newSession(self):
        self.channel = self.channel.with_session_id() 
        self.channel.System.Session.set_transaction_timeout(99) 

    def setState(self, pools):

        self.connect(fqdn=pools['fqdn'], user=pools['user'], password=pools['password'])

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



    def getState(self, pools):

        self.connect(fqdn=pools['fqdn'], user=pools['user'], password=pools['password'])

        self.newSession()

        try: 
            with bigsuds.Transaction(self.channel): 
                monitor = self.channel.LocalLB.Pool.get_member_monitor_status(
                    pools['pools_name'],
                    pools['pools_members'])

                session = self.channel.LocalLB.Pool.get_member_session_status(
                    pools['pools_name'],
                    pools['pools_members'])

            return {'monitor':monitor, 'session':session}
        except bigsuds.OperationFailed, e: 
            log.error(e) 
            raise base_exceptions.CommandErrorException(e)

        except Exception, e:
            log.error("Error  %s" % e)
            raise base_exceptions.CommandErrorException(e)