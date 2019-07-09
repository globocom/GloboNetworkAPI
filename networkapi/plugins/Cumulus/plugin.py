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

import request
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

import socket
from json import dumps
from time import sleep

from rest_framework import status
from CumulusExceptions import *
from networkapi.equipamento.models import EquipamentoAcesso
from ..base import BasePlugin
from .. import exceptions
from networkapi.api_rest import exceptions as api_exceptions


log = logging.getLogger(__name__)


class CumulusPlugin(BasePlugin):
    """
    Base plugin to  interact with Cumulus API
    """
    # httplib2 configurations
    HTTP = httplib2.Http('.cache', disable_ssl_certificate_validation=True)
    HEADERS = {'Content-Type': 'application/json; charset=UTF-8'}
    httplib2.RETRIES = 3
    # Cumulus commands to control the staging area
    COMMIT = {'cmd': 'commit'}
    ABORT_CHANGES = {'cmd': 'abort'}
    PENDING = {'cmd': 'pending'}
    # Expected strings when something occurs not expected occurs
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
    _command_list = []
    #device = None
    #username = None
    #password = None
    protocol = 'http'
    
    def __init__(self, **kwargs):

        try:
            if not isinstance(self.equipment_access, EquipamentoAcesso):
               info = 'equipment_access is None'
               log.info(info)
               raise TypeError(info)
        except (AttributeError, TypeError):
            self.equipment_access = self._get_equipment_access()

    def _get_equipment_access(self):

        try:
            access = None
            try:
                access = EquipamentoAcesso.search(
                    None, self.equipment, 'https').uniqueResult()
            except ObjectDoesNotExist:
                access = EquipamentoAcesso.search(
                    None, self.equipment, 'http').uniqueResult()
            return access

        except Exception:

            log.error('Access type %s not found for equipment %s.' %
                      ('https', self.equipment.nome))
            raise exceptions.InvalidEquipmentAccessException()

       # self.device = self.equipment_access.fqdn
       # self.HTTP.add_credentials(self.__get_auth())

    def _request(self, **kwargs):
        """ """
        values = {
            'method': 'post,'
            'path': '', 
            'data': None,
            'contentType': 'json',
            'verify': False
        }

        for value in values:
            if value in kwargs:
                values[value] = kwargs.get(value)
        
        headers = self._header(contentType=values['contentType'])
        uri = self._get_uri(path=values['path']

        log.debug(
            "Starting %s request to Cumulus switch  %s at %s. Data to be sent: %s" %
            (params["method"], self.equipment.nome, uri, params["data"])
        )

        try:
            # Raises AttributeError if method is not valid
            func = getattr(requests, values["method"])
            request = func(
                uri,
                auth=self._get_auth(),
                headers=headers,
                verify=values["verify"],
                data=values["data"]
            )

            request.raise_for_status()

            if request.status_code==200 and request.content=='':
                return

            try:
                return json.loads(request.text)
            except Exception as exception:
                log.error("Response received from uri '%s': \n%s",
                          uri, request.text)
                log.error("Can't serialize as Json: %s" % exception)
                return

        except AttributeError:
            log.error('Request method must be valid HTTP request. '
                      'ie: GET, POST, PUT, DELETE')


    def _get_uri(self, host=None, path=""):

        if host is None:
            host = self._get_host()

        host = host.strip()
        path = path.strip()

        if host[len(host) - 1] == '/':
            host = host[0:len(host) - 1]
        if path[0] == '/':
            path = path[1:len(path)]
        self.uri = host + '/' + path

        return self.uri


    def _get_host(self):

        if not hasattr(self, 'host') or self.host is None:

            if not isinstance(self.equipment_access, EquipamentoAcesso):

                log.error('No fqdn could be found for equipment %s .' %
                          (self.equipment.nome))
                raise exceptions.InvalidEquipmentAccessException()

            self.host = self.equipment_access.fqdn.strip()
            if self.host.find('://') < 0:
                self.host = self.protocol + '://' + self.host

        return self.host



    def _get_auth(self):
        return self._auth()


    def _auth(self):
        """
        Authentication method
        """
        return HTTPBasicAuth(
                self.equipment_access.user,
                self.equipment_access.password
        )
  
    
    def _header(self, contentType):
        """
        Get header to be used into HTTP requests
        """
        types = {'json':'application/json; charset=UTF-8'}

        return {'content-type': types[contentType]}


    def connect(self):
        """Use the connect function of the superclass to get
        the informations for access the device"""
        self._get_info()

    def _getConfFromFile(self, filename):
        """Get the configurations needed to be applied
            and insert into a list"""
        try:
            with open(filename, 'r+') as lines:
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


    def _send_request(self, method='', data=None):
        """Implement the pulgin communication with Cumulus switches"""

        allowed_methods = ["post"]
        
        if method not in allowed_methods:
            log.error('Invalid method sent to Cumulus switch')
            raise exceptions.ValueInvalid()
        
        path = '/nclu/v1/rpc'
        
        try:
            count = 0
            resp, content = self._request(
                    method="post", path=path, data=json.dumps(data), contentType='json'
                    )
            return content
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

    def _search_pending_warnings(self):
        """Validate if exists any warnings in the staging configuration"""
        try:
            content = self._send_request(self.PENDING)
            check_warning = re.search(self.WARNINGS,
                                      content,
                                      flags=re.IGNORECASE)
            if check_warning:
                self._send_request(self.ABORT_CHANGES)
                raise ConfigurationWarning()
        except ConfigurationWarning as error:
            log.error(error)
            raise error
        except Exception as error:
            log.error('Error: %s' % error)
            raise error
        return True

    def _search_commit_errors(self):
        """Look for errors fired when
        trying to commit configurations"""
        try:
            content = self._send_request(self.COMMIT)
            check_error = re.search(self.COMMIT_ERRORS,
                                    content,
                                    flags=re.IGNORECASE)
            if check_error:
                self._send_request(self.ABORT_CHANGES)
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
                content = self._send_request(self.PENDING)

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
            self._check_pending()
            for cmd in self._command_list:
                content = self._send_request({'cmd': cmd})
                check_error = re.search(self.CLI_ERROR,
                                        content,
                                        flags=re.IGNORECASE)
                check_existence = re.search(self.ALREADY_EXISTS,
                                            content,
                                            flags=re.IGNORECASE)
                if check_error:
                    self._send_request(self.ABORT_CHANGES)
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
            log.error('Error: ' % error)
            raise error

    def copyScriptFileToConfig(self, filename, use_vrf=None, destination=None):
        """Get the configurations needed for configure the equipment
              from the file generated

              The use_vrf and destination variables won't be used
              """
        try:
            success = self._getConfFromFile(filename)
            if success:
                output = self.configurations()
                return output
        except Exception as error:
            log.error('Error: %s' % error)
            raise error

    def create_svi(self, svi_number, svi_description):
        """Create SVI in switch."""
        try:
            proceed = self._check_pending()
            if proceed:
                command = "add vlan %s alias %s" % (svi_number,
                                                    svi_description)
                self._send_request({'cmd': command})
                check_warnings = self._search_pending_warnings()
                if check_warnings:
                    content = self._search_commit_errors()
                    return content
        except Exception as error:
            log.error('Error: %s' % error)
            raise error

    def remove_svi(self, svi_number):
        """Delete SVI from switch."""
        try:
            proceed = self._check_pending()
            if proceed:
                command = "del vlan %s" % svi_number
                content = self._send_request({'cmd': command})
                check_warnings = self._search_pending_warnings()
                if check_warnings:
                    content = self._search_commit_errors()
                    return content
        except Exception as error:
            log.error('Error: %s' % error)
            raise error

    def ensure_privilege_level(self, privilege_level=None):
        """Cumulus don't use the concept of privilege level"""
        pass

    def close(self):
        """This configuration file won't use ssh connections"""
        pass

    def exec_command(
            self,
            command,
            success_regex=None,
            invalid_regex=None,
            error_regex=None):
        """The exec command will not be needed here"""
        pass
