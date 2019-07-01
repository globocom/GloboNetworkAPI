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
import httplib2
from json import dumps
from time import sleep
import re
import socket
from CumulusExceptions import *
from networkapi.equipamento.models import EquipamentoAcesso
from ..base import BasePlugin
from .. import exceptions
from networkapi.api_rest import exceptions as api_exceptions


log = logging.getLogger(__name__)


class Cumulus(BasePlugin):
    """Cumulus Plugin"""
    # httplib2 configurations
    HTTP = httplib2.Http('.cache', disable_ssl_certificate_validation=True)
    HEADERS = {'Content-Type': 'application/json; charset=UTF-8'}
    httplib2.RETRIES = 3
    # Cumulus commands to control the staging area
    COMMIT = {'cmd': 'commit'}
    ABORT_CHANGES = {'cmd': 'abort'}
    PENDING = {'cmd': 'pending'}
    # Expected strings when something bad occurs
    WARNINGS = 'WARNING: Committing these changes will cause problems'
    COMMIT_CONCURRENCY = 'Multiple users are currently'
    CONF_ALREADY_IN = 'net add'
    ALREADY_EXISTS = 'configuration already has'
    # Variables needed in the configuration files below
    MAX_WAIT = 5
    MAX_RETRIES = 3
    _command_list = []
    equipment_access = None
    equipment = None

    def ensure_privilege_level(self, privilege_level=None):
        """Cumulus don't use the concept of privilege level"""
        pass

    def close(self):
        """This configuration file won't use ssh connections"""
        pass

    def exec_command(
            self,
            command,
            success_regex='',
            invalid_regex=None,
            error_regex=None):
        """The exec command will not be needed here"""
        pass

    def connect(self):
        """Get info from database to access the device"""
        if self.equipment_access is None:
            try:
                self.equipment_access = EquipamentoAcesso.search(
                    None, self.equipment, 'https').uniqueResult()
            except Exception:
                log.error('Access type %s not found for equipment %s.' %
                          ('https', self.equipment.nome))
                raise exceptions.InvalidEquipmentAccessException()

        device = self.equipment_access.fqdn
        username = self.equipment_access.user
        password = self.equipment_access.password

        return device, username, password

    def _getConfFromFile(self, filename):
        """Get the configurations needed to be applyed
            and insert into a list"""
        try:
            with open(filename, 'r+') as lines:
                for line in lines:
                    self._command_list.append(line)
        except IOError as e:
            log.error('Error opening the file: %s' % filename)
            raise e
        except Exception as e:
            log.error('Error %s when trying to read the file %s' % e, filename)
            raise e
        return True

    def _send_request(self, data):
        """Send requests for the equipment"""
        device, username, password = self._getInfo()
        self.HTTP.add_credentials(username, password)
        try:
            count = 0
            # repeat this while loop if the response status isn't equal to 200
            # and while the count variable is below the max.retries
            while count < self.MAX_RETRIES:
                resp, content = self.HTTP.request(
                    device, method="POST",
                    headers=self.HEADERS, body=dumps(data))
                if resp.status != 200:
                    count += 1
                    if count >= self.MAX_RETRIES:
                        log.error('Wasn\'t possible to reach the equipment %s\
                                  Validate if the server has the\
                                  correct access\
                                  and if nginx and restserver\
                                  are running' % self.equipment.nome)
                        raise MaxRetryAchieved(
                            'The amount of time trying\
                            to connect to the server was exceeded.\
                            Verify if the server is up and running.')
                else:
                    break
        except socket.error as error:
            log.error('Error in socket connection: %s' % error)
            raise error
        except httplib2.ServerNotFoundError as error:
            log.error(
                'Error: %s. Check if the restserver is enabled in %s' %
                error, self.equipment.nome)
            raise error
        except Exception as error:
            log.error('Error: %s' % error)
            raise error
        return content

    def _search_pending_warnings(self):
        """Validate if exists any warnings in the staging configuration"""
        try:
            content = self._send_request(self.PENDING)
            check_warning = re.search(
                self.WARNINGS, content, flags=re.IGNORECASE)
            if check_warning:
                print(self.WARNINGS)
                self._send_request(self.ABORT_CHANGES)
                raise ConfigurationWarning(
                    'The abort was needed to be done\
                    because of errors in the configuration')
        except Exception as error:
            log.error('Error: %s' % error)
            raise error
        return True

    def _check_pending(self):
        """Verify if exists any configuration in the staging area
           made by another user"""
        try:
            count = 0
            # repeat this while loop if the equipment
            # is been configured by another user
            # and while the count variable is below the max.wait
            while count < self.MAX_WAIT:
                content = self._send_request(self.PENDING)
                check_users = re.search(
                    self.COMMIT_CONCURRENCY, content, flags=re.IGNORECASE)
                check_commands_in = re.search(
                    self.CONF_ALREADY_IN, content, flags=re.IGNORECASE)
                if check_users or check_commands_in:
                    log.warning(
                        'The configuration staging for %s is been used' %
                        self.equipment.nome)
                    sleep(5)
                    count += 1
                    if count >= self.MAX_WAIT:
                        log.error(
                            'The equipment %s has configuration\
                             pendings for too long.\
                             The process needed to be abort.' %
                            self.equipment.nome)
                        raise MaxTimeWaitExceeded(
                            'Time waiting the configuration\
                             be available exceeded')
                else:
                    break
        except Exception as error:
            log.error('Error: %s' % error)
            raise error
        return True

    def configurations(self):
        """Apply the configurations in equipment"""
        self._check_pending()
        for cmd in self._command_list:
            content = self._send_request({'cmd': cmd})
            check_error = re.search('ERROR:', content, flags=re.IGNORECASE)
            check_existence = re.search(
                self.ALREADY_EXISTS, content, flags=re.IGNORECASE)
            if check_error:
                log.error(
                    'Command "%s" not found!\
                    Verify the Syntax. Aborting configurations.' %
                    cmd)
                self._send_request(self.ABORT_CHANGES)
                raise ConfigurationError(
                    'Applying Rollback of the configuration')
            elif check_existence:
                log.info(
                    'The command "%s" already exists in %s' %
                    cmd, self.equipment.nome)
        check_warnings = self._search_pending_warnings()
        if check_warnings:
            content = self._send_request(self.COMMIT)
        return content

    def copyScriptFileToConfig(self, filename, use_vrf=None, destination=None):
        """Get the configurations needed for configure the equipment
              from the file generated

              The use_vrf and destination variables won't be used
              """
        success = self._getConfFromFile(filename)
        if success:
            output = self.configurations()
        return output