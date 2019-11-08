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
import httplib2
import socket
from json import dumps
from time import sleep

from rest_framework import status
from CumulusExceptions import *
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.settings import TFTPBOOT_FILES_PATH
from ..base import BasePlugin
from .. import exceptions


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
    # Expected strings when something not expected occurs
    WARNINGS = 'WARNING: Committing these changes will cause problems'
    COMMIT_CONCURRENCY = 'Multiple users are currently'
    COMMON_USERS = 'cumulus|root'
    COMMIT_ERRORS = 'error:|returned non-zero exit status'
    ALREADY_EXISTS = 'configuration already has'
    CLI_ERROR = 'ERROR:'
    # Variables needed in the configuration below
    MAX_WAIT = 5
    MAX_RETRIES = 3
    SLEEP_WAIT_TIME = 5
    _command_list = list()
    device = None

    def _get_info(self):
        """Get info from database to access the device"""
        if self.equipment_access is None:
            try:
                self.equipment_access = EquipamentoAcesso.search(
                    None, self.equipment, 'https').uniqueResult()
            except Exception:
                log.error('Access type %s not found for equipment %s.' %
                          ('https', self.equipment.nome))
                raise exceptions.InvalidEquipmentAccessException()

        self.device = self.equipment_access.fqdn
        username = self.equipment_access.user
        password = self.equipment_access.password

        self.HTTP.add_credentials(username, password)

    def connect(self):
        """Use the connect function of the superclass to get
        the informations for access the device"""
        self._get_info()

    def _get_conf_from_file(self, filename):
        """Get the configurations needed to be applied
            and insert into a list

            TFTPBOOT_FILES_PATH is required so we can read
            the generated config file
            """
        try:
            with open(TFTPBOOT_FILES_PATH + filename, 'r+') as lines:
                for line in lines:
                    self._command_list.append(line)
        except IOError as e:
            log.error('Error opening the file: %s' % filename)
            raise e
        except Exception as e:
            log.error("Error %s when trying to "
                      "read the file %s" % (e, filename))
            raise e
        return True

    def _send_request(self, data, uri):
        """Send requests for the equipment"""
        try:
            count = 0
            while count < self.MAX_RETRIES:
                resp, content = self.HTTP.request(uri,
                                                  method="POST",
                                                  headers=self.HEADERS,
                                                  body=dumps(data))
                if resp.status == status.HTTP_200_OK:
                    return content
                count += 1
                if count >= self.MAX_RETRIES:
                    raise MaxRetryAchieved(self.equipment.nome)
        except MaxRetryAchieved as error:
            log.error(error)
            raise error
        except socket.error as error:
            log.error('Error in socket connection: %s' % error)
            raise error
        except httplib2.ServerNotFoundError as error:
            log.error(
                'Error: %s. Check if the restserver is enabled in %s' %
                (error, self.equipment.nome))
            raise error
        except Exception as error:
            log.error('Error: %s' % error)
            raise error

    def _send_nclu_request(self, data):
        """Send requests to equipment using nclu route"""
        schema = 'https://'
        path = ':8080/nclu/v1/rpc'
        uri = schema + self.device + path

        output = self._send_request(data, uri)

        return output

    def _search_pending_warnings(self):
        """Validate if exists any warnings in the staging configuration"""
        try:
            content = self._send_nclu_request(self.PENDING)
            check_warning = re.search(self.WARNINGS,
                                      content,
                                      flags=re.IGNORECASE)
            if check_warning:
                self._send_nclu_request(self.ABORT_CHANGES)
                raise ConfigurationWarning()
            else:
                return True
        except ConfigurationWarning as error:
            log.error(error)
            raise error
        except Exception as error:
            log.error('Error: %s' % error)
            raise error

    def _search_commit_errors(self):
        """Look for errors fired when
        trying to commit configurations"""
        try:
            content = self._send_nclu_request(self.COMMIT)
            check_error = re.search(self.COMMIT_ERRORS,
                                    content,
                                    flags=re.IGNORECASE)
            if check_error:
                self._send_nclu_request(self.ABORT_CHANGES)
                raise CommitError()
            return content
        except CommitError as error:
            log.error(error)
            raise error
        except Exception as error:
            log.error(error)
            raise error

    def _check_pending(self):
        """Verify if exists any configuration in the staging area
           made by another user"""
        try:
            count = 0
            while count < self.MAX_WAIT:
                content = self._send_nclu_request(self.PENDING)

                check_concurrency = re.search(self.COMMIT_CONCURRENCY,
                                              content,
                                              flags=re.IGNORECASE)

                check_users = re.search(self.COMMON_USERS,
                                        content)

                if check_users or check_concurrency:
                    log.warning(
                        'The configuration staging for %s is been used' %
                        self.equipment.nome)
                    count += 1
                    if count >= self.MAX_WAIT:
                        raise MaxTimeWaitExceeded(self.equipment.nome)
                    sleep(self.SLEEP_WAIT_TIME)
                else:
                    return True
        except MaxTimeWaitExceeded as error:
            log.error(error)
            raise error
        except Exception as error:
            log.error('Error: %s' % error)
            raise error

    def configurations(self):
        """Apply the configurations in equipment
        and search for errors syntax, and if the configurations
        will cause problems in the equipment"""
        try:
            proceed = self._check_pending()
            if proceed:
                for cmd in self._command_list:
                    content = self._send_nclu_request({'cmd': cmd})
                    check_error = re.search(self.CLI_ERROR,
                                            content,
                                            flags=re.IGNORECASE)
                    check_existence = re.search(self.ALREADY_EXISTS,
                                                content,
                                                flags=re.IGNORECASE)
                    if check_error:
                        self._send_nclu_request(self.ABORT_CHANGES)
                        raise ConfigurationError(cmd)
                    elif check_existence:
                        log.info(
                            'The command "%s" already exists in %s' %
                            (cmd, self.equipment.nome))
                check_warnings = self._search_pending_warnings()
                if check_warnings:
                    content = self._search_commit_errors()
                    return content
        except ConfigurationError as error:
            log.error(error)
            raise error
        except Exception as error:
            log.error('Error: %s ' % error)
            raise error

    def copyScriptFileToConfig(self, filename, use_vrf='', destination=''):
        """Get the configurations needed for configure the equipment
              from the file generated

              The use_vrf and destination variables won't be used
              """
        try:
            success = self._get_conf_from_file(filename)
            if success:
                output = self.configurations()
                return output
        except Exception as error:
            log.error('Error: %s' % error)
            raise error

    def create_svi(self, svi_number, svi_description='no description'):
        """Create SVI in switch."""
        try:
            proceed = self._check_pending()
            if proceed:
                command = "add vlan %s alias %s" % (svi_number,
                                                    svi_description)
                self._send_nclu_request({'cmd': command})
                check_warnings = self._search_pending_warnings()
                if check_warnings:
                    output = self._search_commit_errors()
                    return output
        except Exception as error:
            log.error('Error: %s' % error)
            raise error

    def remove_svi(self, svi_number):
        """Delete SVI from switch."""
        try:
            proceed = self._check_pending()
            if proceed:
                command = "del vlan %s" % svi_number
                self._send_nclu_request({'cmd': command})
                check_warnings = self._search_pending_warnings()
                if check_warnings:
                    output = self._search_commit_errors()
                    return output
        except Exception as error:
            log.error('Error: %s' % error)
            raise error

    def ensure_privilege_level(self, privilege_level=None):
        """Cumulus don't use the concept of privilege level"""
        pass

    def close(self):
        """This configuration file won't use ssh connections"""
        del self._command_list[:]
        pass

    def exec_command(
            self,
            command,
            success_regex='',
            invalid_regex=None,
            error_regex=None):
        """The exec command will not be needed here"""
        pass
