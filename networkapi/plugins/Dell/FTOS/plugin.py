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
from time import sleep

from ... import exceptions
from ...base import BasePlugin
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.util.decorators import mock_return


log = logging.getLogger(__name__)


class FTOS(BasePlugin):

    MAX_TRIES = 10
    RETRY_WAIT_TIME = 5
    WAIT_FOR_CLI_RETURN = 1
    CURRENTLY_BUSY_WAIT = 'Currently busy with copying a file'
    INVALID_REGEX = '([Ii]nvalid)|overlaps with'
    WARNING_REGEX = 'config ignored|Warning'
    ERROR_REGEX = '[Ee][Rr][Rr][Oo][Rr]|[Ff]ail|\%|utility is occupied'

    admin_privileges = 15
    VALID_TFTP_PUT_MESSAGE = 'bytes successfully copied'

    def exec_command(self, command, success_regex='', invalid_regex=None, error_regex=None):
        """
        Send single command to equipment and than closes connection channel
        """
        if self.channel is None:
            log.error(
                'No channel connection to the equipment %s. Was the connect() funcion ever called?' % self.equipment.nome)
            raise exceptions.PluginNotConnected()

        try:
            stdin, stdout, stderr = self.channel.exec_command('%s' % (command))
        except Exception, e:
            log.error('Error in connection. Cannot send command %s: %s' %
                      (command, e))
            raise api_exceptions.NetworkAPIException

        equip_output_lines = stdout.readlines()
        output_text = ''.join(equip_output_lines)

        for output_line in output_text.splitlines():
            if re.search(self.INVALID_REGEX, output_line):
                raise exceptions.InvalidCommandException(output_text)
            elif re.search(error_regex, output_line):
                if re.seatch(self.WARNING_REGEX, output_line):
                    log.warning('This is threated as a warning: %s' %
                                output_line)
                else:
                    raise exceptions.CommandErrorException

        if re.search(success_regex, output_text, re.DOTALL):
            return output_text
        else:
            raise exceptions.UnableToVerifyResponse()

    @mock_return('')
    def create_svi(self, svi_number, svi_description='no description'):
        """
        Create SVI in switch
        """
        self.ensure_privilege_level(self)
        self.channel.send('terminal length 0\nconfigure terminal\n \
            interface Vlan%s \n description %s \n end \n' % (svi_number, svi_description))
        recv = self.waitString('#')

        return recv

    @mock_return('')
    def copyScriptFileToConfig(self, filename, use_vrf=None, destination='running-config'):
        """
        Copy file from TFTP server to destination
        By default, plugin should apply file in running configuration (active)
        """
        if use_vrf is None:
            use_vrf = self.management_vrf

        command = 'copy tftp://%s/%s %s %s\n\n' % (
            self.tftpserver, filename, destination, use_vrf)

        file_copied = 0
        retries = 0
        while(not file_copied and retries < self.MAX_TRIES):
            if retries is not 0:
                sleep(self.RETRY_WAIT_TIME)

            try:
                log.info('try: %s - sending command: %s' % (retries, command))
                self.channel.send('%s\n' % command)
                recv = self.waitString(self.VALID_TFTP_PUT_MESSAGE)
                file_copied = 1
            except exceptions.CurrentlyBusyErrorException:
                retries += 1

        # not capable of configuring after max retries
        if retries is self.MAX_TRIES:
            raise exceptions.CurrentlyBusyErrorException()

        return recv

    @mock_return('')
    def ensure_privilege_level(self, privilege_level=None):

        if privilege_level is None:
            privilege_level = self.admin_privileges

        self.channel.send('\n')
        recv = self.waitString('>|#')
        self.channel.send('show privilege\n')
        recv = self.waitString('Current privilege level is')
        level = re.search(
            'Current privilege level is ([0-9]+).*', recv, re.DOTALL).group(1)

        level = (level.split(' '))[-1]
        if int(level) < privilege_level:
            self.channel.send('enable\n')
            recv = self.waitString('Password:')
            self.channel.send('%s\n' % self.equipment_access.enable_pass)
            recv = self.waitString('#')

    @mock_return('')
    def remove_svi(self, svi_number):
        """
        Delete SVI from switch
        """
        return ''
        self.ensure_privilege_level()
        self.channel.send('terminal length 0\n')

        self.channel.send('show run interface Vlan %s\n' % (svi_number))
        recv = self.waitString('#')

        conf = 'nconfigure terminal\n interface Vlan %s\n' % (svi_number)
        for output_line in recv.splitlines():
            if re.search('(un)?tagged', output_line):
                conf = conf + 'no ' + output_line + '\n'

        conf = conf + ' end\n'
        self.channel.send(conf)
        recv = self.waitString('#')

        self.channel.send('\nconfigure terminal\n \
            no interface Vlan%s \n end \n' % (svi_number))
        recv = self.waitString('#')

        return recv

    def waitString(self, wait_str_ok_regex='', wait_str_invalid_regex=None, wait_str_failed_regex=None):

        if wait_str_invalid_regex is None:
            wait_str_invalid_regex = self.INVALID_REGEX

        if wait_str_failed_regex is None:
            wait_str_failed_regex = self.ERROR_REGEX

        string_ok = 0
        recv_string = ''
        while not string_ok:
            while not self.channel.recv_ready():
                sleep(self.WAIT_FOR_CLI_RETURN)

            recv_string = self.channel.recv(9999)
            file_name_string = self.removeDisallowedChars(recv_string)

            for output_line in recv_string.splitlines():
                if re.search(self.CURRENTLY_BUSY_WAIT, output_line):
                    log.warning('Need to wait - Switch busy: %s' % output_line)
                    raise exceptions.CurrentlyBusyErrorException()
                elif re.search(self.WARNING_REGEX, output_line):
                    log.warning('Equipment warning: %s' % output_line)
                elif re.search(wait_str_invalid_regex, output_line):
                    log.error('Equipment raised INVALID error: %s' %
                              output_line)
                    raise exceptions.CommandErrorException(file_name_string)
                elif re.search(wait_str_failed_regex, output_line):
                    log.error('Equipment raised FAILED error: %s' %
                              output_line)
                    raise exceptions.InvalidCommandException(file_name_string)
                elif re.search(wait_str_ok_regex, output_line):
                    log.debug('Equipment output: %s' % output_line)
                    # test bug switch copying 0 bytes
                    if output_line == '0 bytes successfully copied':
                        log.debug('Switch copied 0 bytes, need to try again.')
                        raise exceptions.CurrentlyBusyErrorException()
                    string_ok = 1

        return recv_string
