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

from networkapi.plugins import exceptions
from networkapi.plugins.base import BasePlugin
from networkapi.util.decorators import mock_return

log = logging.getLogger(__name__)


class SH2200(BasePlugin):
    log.info('Mellanox SH2200 plugin.')

    VALID_TFTP_GET_MESSAGE = '#'

    @mock_return('')
    def ensure_privilege_level(self, privilege_level=None):

        self.channel.send('en\n')
        self.waitString('>|#')

    @mock_return('')
    def copyScriptFileToConfig(self, filename, use_vrf=None, destination='overwrite'):
        """
        Copy file from TFTP server to destination
        By default, plugin should apply file in running configuration (active)
        """
        if use_vrf is None:
            use_vrf = self.management_vrf

        fetch_file = 'configuration text fetch tftp://%s/%s %s %s\n\n' % (
            self.tftpserver, filename, destination, use_vrf)

        try:
            log.info('try: %s - sending command: %s' % (0, fetch_file))
            self.channel.send('%s\n' % fetch_file)
            recv = self.waitString(self.VALID_TFTP_PUT_MESSAGE)
        except exceptions.CurrentlyBusyErrorException:
            log.info('Error while sending command to equipment: %s' % fetch_file)
            return recv

        apply_config = 'configuration text file %s apply\n\n' % filename.split('/')[-1]

        try:
            log.info('try: %s - sending command: %s' % (0, apply_config))
            self.channel.send('%s\n' % apply_config)
            recv = self.waitString(self.VALID_TFTP_PUT_MESSAGE)
        except exceptions.CurrentlyBusyErrorException:
            log.info('Error while sending command to equipment: %s' % apply_config)
            return recv

        delete_file = 'configuration text file %s delete\n\n' % filename.split('/')[-1]

        try:
            log.info('try: %s - sending command: %s' % (0, delete_file))
            self.channel.send('%s\n' % delete_file)
            recv = self.waitString(self.VALID_TFTP_PUT_MESSAGE)
        except exceptions.CurrentlyBusyErrorException:
            log.info('Error while sending command to equipment: %s' % delete_file)
            return recv

        write_mem = 'write memory'

        try:
            log.info('try: %s - sending command: %s' % (0, write_mem))
            self.channel.send('%s\n' % delete_file)
            recv = self.waitString(self.VALID_TFTP_PUT_MESSAGE)
        except exceptions.CurrentlyBusyErrorException:
            log.info('Error while sending command to equipment: %s' % write_mem)
            return recv

        return recv
