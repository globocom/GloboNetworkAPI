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

import re
import logging
import string
from time import sleep

from networkapi.plugins import exceptions
from networkapi.plugins.base import BasePlugin
from networkapi.util.decorators import mock_return

log = logging.getLogger(__name__)


class HPE(BasePlugin):

    ERROR_REGEX = 'Wrong parameter found at|File not found|Timeout was reached|The file or directory doesn\'t exist'
    INVALID_REGEX = '([Ii]nvalid)|% Incomplete command found at|already exists'
    VALID_OUTPUT_CHARS = '-_.():/#<>\\\r\n %s%s' % (string.ascii_letters, string.digits)
    VALID_TFTP_GET_MESSAGE = '>'
    RETRY_WAIT_TIME = 5
    MAX_TRIES = 5

    @mock_return('')
    def copyScriptFileToConfig(self, filepath, use_vrf=None, destination=''):
        """
        Copy file from TFTP server to destination
        By default, plugin should apply file in running configuration (active)
        """

        tftp_command = 'tftp %s get %s \n\n' % (self.tftpserver, filepath)

        recv = ''
        retries = 0
        file_copied = 0

        while not file_copied and retries < self.MAX_TRIES:
            if retries is not 0:
                sleep(self.RETRY_WAIT_TIME)

            try:
                log.info('try: %s - sending command: %s' % (retries, tftp_command))
                self.channel.send('%s\n' % tftp_command)
                recv = self.waitString(self.VALID_TFTP_GET_MESSAGE)
                log.debug(str(recv))
                file_copied = 1
            except exceptions.CurrentlyBusyErrorException:
                retries += 1

        filename = filepath.split('/')
        python_command = 'python %s' % (filename[-1])
        try:
            self.channel.send('%s\n' % python_command)
            self.waitString(wait_str_ok_regex=">", wait_str_failed_regex="SystemError")
        except Exception, e:
            raise Exception("Error sending command %s to equipment %s: %s" % (python_command, filepath, e))

        clean_command = 'delete %s' % (filename[-1])
        confirm_command = 'Y'
        try:
            self.channel.send('%s\n' % clean_command)
            self.waitString(wait_str_ok_regex="[Y/N]")
            self.channel.send('%s\n' % confirm_command)
            self.waitString(wait_str_ok_regex="Done")
        except Exception, e:
            raise Exception("Error sending command %s to equipment %s: %s" % (python_command, filepath, e))

        # not capable of configuring after max retries
        if retries is self.MAX_TRIES:
            raise exceptions.CurrentlyBusyErrorException()

        return recv

    @mock_return('')
    def ensure_privilege_level(self, privilege_level=None):

        self.channel.send('\n')
        self.waitString('>|#')

    def waitString(self, wait_str_ok_regex='>', wait_str_invalid_regex=None, wait_str_failed_regex=None):

        if wait_str_invalid_regex is None:
            wait_str_invalid_regex = self.INVALID_REGEX

        if wait_str_failed_regex is None:
            wait_str_failed_regex = self.ERROR_REGEX

        string_ok = 0
        recv_string = ''
        while not string_ok:
            while not self.channel.recv_ready():
                sleep(1)
            recv_string = self.channel.recv(9999)
            file_name_string = self.removeDisallowedChars(recv_string)
            if re.search(wait_str_failed_regex, recv_string):
                log.error('Equipment raised INVALID error: %s' % recv_string)
                raise exceptions.InvalidCommandException(file_name_string)
            elif re.search(wait_str_invalid_regex, recv_string):
                log.error('Equipment raised Failed error: %s' % recv_string)
                raise exceptions.CommandErrorException(file_name_string)
            elif re.search(wait_str_ok_regex, recv_string):
                log.debug('Equipment output: %s' % recv_string)
                string_ok = 1

        return recv_string