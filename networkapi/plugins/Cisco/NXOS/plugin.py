# -*- coding: utf-8 -*-
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
import logging
import re

from ...base import BasePlugin
from networkapi.util.decorators import mock_return
# from time import sleep
# import string
# import unicodedata
# from networkapi.api_rest import exceptions as api_exceptions
# from networkapi.plugins import exceptions as base_exceptions

log = logging.getLogger(__name__)


class NXOS(BasePlugin):

    admin_privileges = -1
    management_vrf = 'management'
    VALID_TFTP_GET_MESSAGE = 'Copy complete.|Copy complete, now saving to disk'
    ERROR_REGEX = '[Ee][Rr][Rr][Oo][Rr]|[Ff]ail|utility is occupied'

    @mock_return
    def create_svi(self, svi_number, svi_description='no description'):
        """
        Create SVI in switch
        """
        self.ensure_privilege_level(self)
        self.channel.send('terminal length 0\nconfigure terminal\n \
            interface Vlan%s \n description %s \n end \n' % (svi_number, svi_description))
        recv = self.waitString('#')

        return recv

    @mock_return
    def copyScriptFileToConfig(self, filename, use_vrf=None, destination='running-config'):
        """
        Copy file from TFTP server to destination
        By default, plugin should apply file in running configuration (active)
        """
        if use_vrf is None:
            use_vrf = self.management_vrf

        command = 'copy tftp://%s/%s %s vrf %s\n\n' % (
            self.tftpserver, filename, destination, use_vrf)

        log.info('sending command: %s' % command)

        self.channel.send('%s\n' % command)
        recv = self.waitString(self.VALID_TFTP_GET_MESSAGE)

        return recv

    @mock_return
    def ensure_privilege_level(self, privilege_level=None):

        if privilege_level is None:
            privilege_level = self.admin_privileges

        recv = self.waitString('>|#')
        self.channel.send('show privilege\n')
        recv = self.waitString('Current privilege level:')
        level = re.search(
            'Current privilege level: (-?[0-9]+?).*', recv, re.DOTALL).group(1)

        level = (level.split(' '))[-1]
        if int(level) < privilege_level:
            self.channel.send('enable\n')
            recv = self.waitString('Password:')
            self.channel.send('%s\n' % self.equipment_access.enable_pass)
            recv = self.waitString('#')

    @mock_return
    def remove_svi(self, svi_number):
        """
        Delete SVI from switch
        """
        self.ensure_privilege_level()
        self.channel.send(
            'terminal length 0\nconfigure terminal\nno interface Vlan%s \n end \n' % (svi_number))
        recv = self.waitString('#')

        return recv
