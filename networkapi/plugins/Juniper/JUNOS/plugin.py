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
import time
from exceptions import IOError
from networkapi.plugins.base import BasePlugin
from networkapi.plugins import exceptions
from networkapi.equipamento.models import EquipamentoAcesso
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.start_shell import StartShell
from jnpr.junos.exception import \
    ConnectError, \
    ConfigLoadError, \
    LockError, \
    UnlockError, \
    ConnectClosedError, \
    CommitError, \
    RpcError

log = logging.getLogger(__name__)


class JUNOS(BasePlugin):

    configuration = None
    quantity_of_times_to_try_lock = 3
    seconds_to_wait_to_try_lock = 10

    def __init__(self, **kwargs):
        super(JUNOS, self).__init__(connect_port=830, **kwargs)
        if 'quantity_of_times_to_try_lock' in kwargs:
            self.quantity_of_times_to_try_lock = kwargs.get('quantity_of_times_to_try_lock')

        if 'seconds_to_wait_to_try_lock' in kwargs:
            self.seconds_to_wait_to_try_lock = kwargs.get('seconds_to_wait_to_try_lock')

    def connect(self):

        """
        Connects to equipment via ssh using PyEz  and create connection with invoked shell object.

        :returns:
            True if success and False if fail
        """

        # Collect the credentials (user and password) for equipment
        if self.equipment_access is None:
            try:
                self.equipment_access = EquipamentoAcesso.search(
                    None, self.equipment, 'ssh').uniqueResult()
            except Exception:
                log.error("Access type {} not found for equipment {}.".format('ssh', self.equipment.nome))
                raise exceptions.InvalidEquipmentAccessException()

        log.info("Trying to connect on host {} ... ".format(self.equipment_access.fqdn))

        result = False
        try:
            self.remote_conn = Device(
                host=self.equipment_access.fqdn,
                user=self.equipment_access.user,
                passwd=self.equipment_access.password,
                port=self.connect_port)
            self.remote_conn.open()
            self.configuration = Config(self.remote_conn)

            if self.remote_conn.connected:
                result = True
        except ConnectError as e:
            log.error("Could not connect to juniper host {}: {}".format(
                self.equipment_access.fqdn, e))
        except Exception, e:
            log.error("Error connecting to host {}: {}".format(self.equipment_access.fqdn, e))

        if self.remote_conn.connected:
            log.info("The connection on host {} was opened successfully!".format(self.equipment_access.fqdn))
        else:
            log.error("An unknown error occurred to connect host {}. Connection result: {}".format(
                self.equipment_access.fqdn, self.remote_conn.connected))

        return result

    def close(self):

        """
        Disconnect to equipment via ssh using PyEz.

        :returns:
            True if close successfully or false if fail it
        """

        log.info("Trying to close connection on host {} ... ".format(self.equipment_access.fqdn))

        try:
            self.remote_conn.close()
        except ConnectClosedError, e:
            log.error("Cannot close connection on host {}: {}".format(self.equipment_access.fqdn, e))
        except Exception, e:
            log.error("Found an unexpected error at closing connection on host {}: {}".format(
                self.equipment_access.fqdn, e))

        if not self.remote_conn.connected:
            log.info("The connection was closed successfully! Host: {} ".format(
                self.equipment_access.fqdn, self.remote_conn.connected))
            return True
        else:
            log.error(
                "An unknown error occurred to close de connection on host {}. Connection close result: {} ".format(
                    self.equipment_access.fqdn, self.remote_conn.connected))

            return False

    def copyScriptFileToConfig(self, filename, use_vrf='', destination=''):

        """
        Receives the file path (usually in /mnt/scripts/tftpboot/networkapi/generated_config/interface/)
        where contains the command to be executed in the equipment

        :param str filename: must contain the full path and file name
        :param str use_vrf: not used
        :param str destination: not used

        :returns:
            String message of result
        """

        command = None

        log.info("Trying to load configuration from file to be executed on host {} ... ".format(
            self.equipment_access.fqdn))

        try:
            command_file = open(filename, "r")
            command = command_file.read()
        except IOError, e:
            log.error("File not found {}: {}".format(filename, e))
            self.close()
        except Exception, e:
            log.error("Unexpected error occurred {}: {}".format(filename, e))
            self.close()

        if command is not None:
            log.info("Load configuration from file {} successfully!".format(filename))
        else:
            log.error("An unknown error occurred to load configuration file {} for host {}".format(
                filename, self.equipment_access.fqdn))

        return self.exec_command(command)

    def exec_command(self, command, success_regex='', invalid_regex=None, error_regex=None):

        """
        Execute a junos command 'set' in the equipment.

        :param str command: junos command 'set'
        :param str success_regex: not used
        :param str invalid_regex: not used
        :param str error_regex: not used

        :returns:
            String message of result (in result_message variable)
        """

        log.info("Trying to execute a configuration on host {} ... ".format(self.equipment_access.fqdn))

        result_message = None

        if not self.plugin_try_lock():
            result_message = "Configuration could not be locked. Anybody else locked?"
            log.error("{} {}".format(result_message, self.equipment_access.fqdn))
            self.close()
            return result_message
        else:
            log.info("Configuration was locked in host {} successfully".format(
                self.equipment_access.fqdn))

        try:
            # self.configuration.lock()  #
            self.configuration.rollback()  # For a clean configuration
            self.configuration.load(command, format='set')
            self.configuration.commit_check()
            self.configuration.commit()
            self.configuration.unlock()

            result_message = "Configuration junos was executed successfully on host {}".format(
                self.equipment_access.fqdn)
            log.info("{} {}".format(result_message, self.equipment_access.fqdn))

        except LockError as e:
            result_message = "Configuration could not be locked on host {}.".format(self.equipment_access.fqdn)
            log.error("{} {} {}".format(result_message, self.equipment_access.fqdn, e))
            self.close()
        except UnlockError as e:
            result_message = "Configuration could not be unlocked on host {}. " \
                             "A rollback will be executed".format(self.equipment_access.fqdn)
            log.error("{} {} {}".format(result_message, self.equipment_access.fqdn, e))
            self.configuration.rollback()
            self.close()
        except ConfigLoadError as e:
            result_message = "Configuration could not be loaded on host {}. " \
                             "A rollback and unlock will be executed.".format(self.equipment_access.fqdn)
            log.error("{} {} {}".format(result_message, self.equipment_access.fqdn, e))
            self.configuration.rollback()
            self.configuration.unlock()
            self.close()
        except CommitError as e:
            result_message = "Configuration could not be commited on host {}. " \
                             "A rollback and unlock will be executed.".format(self.equipment_access.fqdn)
            log.error("{} {} {}".format(result_message, self.equipment_access.fqdn, e))
            self.configuration.rollback()
            self.configuration.unlock()
            self.close()
        except RpcError as e:
            result_message = "Configuration database locked on host {}".format(self.equipment_access.fqdn)
            log.error("{} {} {}".format(result_message, self.equipment_access.fqdn, e))
            self.close()
        except Exception as e:
            result_message = "An unexpected error occurred during configuration on host {}. " \
                             "A rollback and unlock will be executed.".format(self.equipment_access.fqdn)
            log.error("{} {} {}".format(result_message, self.equipment_access.fqdn, e))
            self.configuration.rollback()
            self.configuration.unlock()
            self.close()

        log.info(
            "Execute configuration on host {}. Result message: '{}'".format(
                self.equipment_access.fqdn, result_message))

        return result_message

    def ensure_privilege_level(self, privilege_level=None):

        """
        Ensure privilege level.
        This function only verify is the current user is a super-user, otherwise raises an exception
        """

        log.info("Trying to ensure privilege level for user {} on host {} ... ".format(
            self.equipment_access.user, self.equipment_access.fqdn))

        # Note about StartShell timeout: duration of time in seconds must wait for the expected result
        ss = StartShell(self.remote_conn, timeout=2)
        ss.open()
        output = ss.run('cli -c "show cli authorization"')

        # output is a tuple [bool, string], example:
        # (False, u'cli -c "show cli authorization"\r\r\nCurrent user: \'root        \' class \'super-user\ ....)
        # This string will be parsed to get the user class:
        result = output[1].split('\n')  # get the target part and split it by \n
        current_user_class = result[1].split("'")[3]  # get the target part, split again by ' and get the target part
        if current_user_class != 'super-user':
            log.error("{} {}".format("User {} has no privileges", self.equipment_access.user, self.equipment_access.fqdn))
            self.close()
            return False
        else:
            log.info("The privilege for user {}, on host {}, was satisfied! ".format(
                self.equipment_access.user, self.equipment_access.fqdn))
            return True

    def plugin_try_lock(self):

        for x in range(self.quantity_of_times_to_try_lock):
            try:
                self.configuration.lock()
                return True
            except (LockError, RpcError, Exception), e:
                # Keep looping ...
                log.warning(
                    "Configuration still could not be locked on host {}. "
                    "Automatic try in {} seconds - {}/{} {}".format(
                        self.equipment_access.fqdn,
                        self.seconds_to_wait_to_try_lock,
                        x+1,
                        self.quantity_of_times_to_try_lock,
                        e))
                time.sleep(self.seconds_to_wait_to_try_lock)

        return False
