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
import os.path
from exceptions import IOError
from networkapi.plugins.base import BasePlugin
from networkapi.plugins import exceptions
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.system.facade import get_value
from networkapi.system.exceptions import VariableDoesNotExistException
from django.db.utils import DatabaseError
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

from jnpr.junos.device import logger as device_logger
from ncclient.transport.ssh import logger as ssh_logger
from ncclient.transport.session import logger as session_logger
from ncclient.operations.rpc import logger as rpc_logger

log = logging.getLogger(__name__)


class JUNOS(BasePlugin):

    configuration = None
    quantity_of_times_to_try_lock = 3
    seconds_to_wait_to_try_lock = 10

    # Variables defined at networkapi/database
    alternative_variable_base_path_list = ['path_to_tftpboot']
    detailed_log_level_var = 'detailed_junos_log_level'
    detailed_log_level_used = None

    alternative_static_base_path_list = ['/mnt/scripts/tftpboot/']
    ignore_warning_list = ['statement not found']

    def __init__(self, **kwargs):
        super(JUNOS, self).__init__(connect_port=830, **kwargs)
        if 'quantity_of_times_to_try_lock' in kwargs:
            self.quantity_of_times_to_try_lock = kwargs.get('quantity_of_times_to_try_lock')

        if 'seconds_to_wait_to_try_lock' in kwargs:
            self.seconds_to_wait_to_try_lock = kwargs.get('seconds_to_wait_to_try_lock')

        # Logger objects to be disabled. Remove or add objects to array below:
        loggers = [device_logger, ssh_logger, session_logger, rpc_logger]
        detailed_log_level_used = self.set_detailed_junos_log_level(loggers)
        log.info("Detailed Junos log level: {}".format(detailed_log_level_used))

    def connect(self):

        """
        Connects to equipment via ssh using PyEz
        and create connection with invoked shell object.

        :returns:
            True on success or raise an exception on any
            fail (will NOT return a false result, due project decision).
        """

        if self.equipment_access is None:
            try:
                # Collect the credentials (user and password) for equipment
                self.equipment_access = EquipamentoAcesso.search(None,
                                                                 self.equipment,
                                                                 'ssh').uniqueResult()
            except Exception as e:
                message = "Unknown error while accessing equipment {} in database.".format(
                    self.equipment.nome)
                log.error("{}: {}".format(message, e))
                raise exceptions.APIException(message)

        log.info("Trying to connect on host {} ... ".format(self.equipment_access.fqdn))

        try:
            self.remote_conn = Device(
                host=self.equipment_access.fqdn,
                user=self.equipment_access.user,
                passwd=self.equipment_access.password,
                port=self.connect_port)
            self.remote_conn.open()
            self.configuration = Config(self.remote_conn)

            if self.remote_conn.connected:
                log.info("The connection on host {} was opened successfully!".format(self.equipment_access.fqdn))
                return True

        except ConnectError as e:
            message = "Authentication failed trying to connect host {}.".format(self.equipment_access.fqdn)
            log.error("{}: {}".format(message, e))
            raise exceptions.ConnectionException(message)

        except Exception as e:
            message = "Unknown error while connecting to host {}.".format(self.equipment_access.fqdn)
            log.error("{}: {}".format(message, e))
            raise exceptions.APIException(message)

    def close(self):

        """
        Disconnect to equipment via ssh using PyEz.

        :returns:
            True on success or raise an exception on any fail (will NOT return a false result, due project decision).
        """

        log.info("Trying to close connection on host {} ... ".format(self.equipment_access.fqdn))

        try:
            if self.remote_conn is not None:
                self.remote_conn.close()
                log.info("The connection was closed successfully on host {}!".format(self.equipment_access.fqdn))
                return True
            else:
                log.warning("To connection couldn't be closed because object is None")

        except ConnectClosedError as e:
            message = "Cannot close connection on juniper host {}.".format(self.equipment_access.fqdn)
            log.error("{}: {}".format(message, e))
            raise exceptions.APIException(message)

        except Exception as e:
            message = "Unknown error while closing connection on host {}.".format(self.equipment_access.fqdn)
            log.error("{}: {}".format(message, e))
            raise exceptions.APIException(message)

    def copyScriptFileToConfig(self, filename, use_vrf='', destination=''):

        """
        Receives the file path (usually in /mnt/scripts/tftpboot/networkapi/generated_config/interface/)
        where contains the command to be executed in the equipment

        :param str filename: must contain the full path and file name
        :param str use_vrf: not used
        :param str destination: not used

        :returns:
            Returns a success message, otherwise, raise an exception. That means will NOT return a false result.
        """

        log.info("Trying to load file configuration for host {} ...".format(self.equipment_access.fqdn))

        # 'filename' was defined in super class, but in plugin junos the 'file_path' will be used instead
        file_path = filename
        file_path = self.check_configuration_file_exists(file_path)

        try:

            command_file = open(file_path, "r")
            command = command_file.read()
            log.info("Load configuration from file {} successfully!".format(file_path))
            return self.exec_command(command)

        except IOError as e:
            self.close()
            message = "Configuration file not found."  # Message to client
            log.error("{} {}: {}".format(message, file_path, e))  # Message to log
            raise exceptions.APIException(message)
        # Caution using generic exception here (like Exception). May cause unexpected exception overlaps

    def exec_command(self, command, success_regex='', invalid_regex=None, error_regex=None):

        """
        Execute a junos command 'set' in the equipment.

        :param str command: junos command 'set'
        :param str success_regex: not used
        :param str invalid_regex: not used
        :param str error_regex: not used

        :returns:
            Returns a success message, otherwise, raise an exception. That means will NOT return a false result.
        """

        log.info("Trying to execute a configuration on host {} ... ".format(self.equipment_access.fqdn))

        try:
            self.__try_lock()
            self.configuration.rollback()
            self.configuration.load(command, format='set', ignore_warning=self.ignore_warning_list)
            self.configuration.commit_check()
            self.configuration.commit()
            self.configuration.unlock()

            result_message = "Configuration junos was executed successfully on {}".format(self.equipment_access.fqdn)
            log.info(result_message)
            return result_message

        except LockError as e:
            self.close()
            message = "Couldn't lock host {}.".format(self.equipment_access.fqdn)
            log.error("{}: {}".format(message, e))
            raise exceptions.APIException(message)

        except UnlockError as e:
            message = "Couldn't unlock host {}.".format(self.equipment_access.fqdn)
            log.error("{} (rollback and close will be tried for safety): {}".format(message, e))
            self.configuration.rollback()
            self.close()
            raise exceptions.APIException(message)

        except ConfigLoadError as e:
            message = "Couldn't load configuration on host {}. Please check template syntax.".format(
                self.equipment_access.fqdn)
            log.error("{} (rollback, unlock and close will be tried for safety): {}".format(message, e))
            self.configuration.rollback()
            self.configuration.unlock()
            self.close()
            raise exceptions.APIException(message)

        except CommitError as e:
            message = "Couldn't commit configuration on host {}.".format(self.equipment_access.fqdn)
            log.error("{} (rollback, unlock and close will be tried for safety): {}".format(message, e))
            self.configuration.rollback()
            self.configuration.unlock()
            self.close()
            raise exceptions.APIException(message)

        except RpcError as e:
            message = "A remote procedure call exception occurred on host {} ".format(self.equipment_access.fqdn)
            log.error("{} (close will be tried for safety): {}".format(message, e))
            self.close()
            raise exceptions.APIException(message)
        # Caution to use generic exception here, may cause overlaps in specific exceptions in try_lock()
        # except Exception, e:

    def ensure_privilege_level(self, privilege_level=None):

        """
        Ensure privilege level verifying if the current user is super-user.

        :returns:
            Returns True if success, otherwise, raise an exception (it will NOT return a false result)
        """

        log.info("Trying to ensure privilege level for user {} on host {} ... ".format(
            self.equipment_access.user, self.equipment_access.fqdn))

        try:
            # timeout: duration of time in seconds must wait for the expected result
            ss = StartShell(self.remote_conn, timeout=2)
            ss.open()
            output = ss.run('cli -c "show cli authorization"')

            # output is a tuple [bool, string], example:
            # (False, u'cli -c "show cli authorization"\r\r\nCurrent user: \'root        \' class \'super-user\ ....)
            # This string will be parsed to get the user class:

            # get the target part and split it by \n
            result = output[1].split('\n')

            # get the target part; split by '; and get the target part
            current_user_class = result[1].split("'")[3]

            if current_user_class != 'super-user':
                message = "Couldn't validate user privileges on host {}.".format(self.equipment_access.fqdn)
                log.error("{}. User {} class is '{}' and need to be 'super-user'"
                          "(close connection will be executed for safety)"
                          .format(message, self.equipment_access.user, current_user_class))
                self.close()
                raise exceptions.APIException(message)
            else:
                log.info("The privilege for user {} ('super-user') was satisfied on host {}!".format(
                    self.equipment_access.user, self.equipment_access.fqdn))
                return True

        except Exception as e:
            message = "Unknown error while verifying user privilege on host {} ".format(self.equipment_access.fqdn)
            log.error("(close connection will be executed for safety): {}".format(message, e))
            self.close()
            raise exceptions.APIException(message)

    def __try_lock(self):

        """
        Try to lock equipment.

        :returns:
            Returns True if success, otherwise, raise an exception. That means will NOT return a false result.
        """

        log.info("Trying to lock host {} ...".format(self.equipment_access.fqdn))

        for x in range(self.quantity_of_times_to_try_lock):
            try:
                self.configuration.lock()
                log.info("Host {} was locked successfully!".format(self.equipment_access.fqdn))
                return True
            except LockError as e:
                count = x + 1
                log.warning(
                    "Host {} could not be locked. Automatic try in {} seconds ({}/{}): {}".format(
                        self.equipment_access.fqdn,
                        self.seconds_to_wait_to_try_lock,
                        count,
                        self.quantity_of_times_to_try_lock,
                        e))
                time.sleep(self.seconds_to_wait_to_try_lock)

            except Exception as e:
                log.error("Unknown error while trying to lock c the equipment on host {}: {}".format(
                    self.equipment_access.fqdn, e))

        message = "Errors occurred in all attempts to lock {}. Anybody has locked?".format(self.equipment_access.fqdn)
        log.error(message)
        raise exceptions.APIException(message)

    def check_configuration_file_exists(self, file_path):

        """
        This function try to find and build (if necessary) the configuration file path. The priorities are:
        (1) build the full path from system variable base and relative file path ('file_path'); or
        (2) build the full path from static variable base and relative file path ('file_path'); or
        (3) return the relative path it self ('file_path')

        :param str file_path: Relative path, examples:
            'networkapi/plugins/Juniper/JUNOS/samples/sample_command.txt' or
            'networkapi/generated_config/interface/int-d_24823_config_ROR9BX3ATQG93TALJAMO2G'

        :return: Return a valid configuration file path string. Ex.:
        'networkapi/plugins/Juniper/JUNOS/samples/sample_command.txt' or
        '/mnt/scripts/tftpboot/networkapi/generated_config/interface/int-d_24823_config_ROR9BX3ATQG93TALJAMO2G'
        """

        log.info("Checking configuration file exist: {}".format(file_path))

        # Check in system variables
        for variable in self.alternative_variable_base_path_list:
            try:
                base_path = get_value(variable)
                if base_path != "":
                    result_path = base_path + file_path
                    if os.path.isfile(result_path):
                        log.info("Configuration file {} was found by system variable {}!".format(result_path, variable))
                        return result_path
            except (DatabaseError, VariableDoesNotExistException):
                # DatabaseError means that variable table do not exist
                pass
            except Exception as e:
                log.warning("Unknown error while calling networkapi.system.facade.get_value({}): {} {} ".format(
                    variable, e.__class__, e))

        # Check possible static variables
        for static_path in self.alternative_static_base_path_list:
            result_path = static_path + file_path
            if os.path.isfile(result_path):
                log.info("Configuration file {} was found by static variable {}!".format(result_path, static_path))
                return result_path

        # Check if relative path is valid (for dev tests)
        if os.path.isfile(file_path):
            log.info("Configuration file {} was found by relative path".format(file_path))
            return file_path

        message = "An error occurred while finding configuration file."
        log.error("{} Could not find in: relative path ('{}'), system variables ({}) or static paths ({})".format(
            message, file_path, self.alternative_variable_base_path_list, self.alternative_static_base_path_list))
        raise exceptions.APIException(message)

    def set_detailed_junos_log_level(self, loggers):

        """
        Used to disable logs from detailed and specific libs used in Junos plugin, for example:
        If 'ERROR' is defined, higher log messages will be disabled, like 'WARNING', 'INFO' and 'DEBUG'.

        :param str loggers: Array of logger objects
        :return: A valid level error ('ERROR', 'INFO', etc.), otherwise None
        """

        default_log_level = 'ERROR'
        log_level = None

        # Trying to get the variable from networkapi.
        try:
            log_level = get_value(self.detailed_log_level_var)
        except DatabaseError as e:
            log.warning("Database error while getting '{}' variable: {}".format(
                self.detailed_log_level_var, e))
        except VariableDoesNotExistException as e:
            log.warning("Variable '{}' does not exist: {}".format(
                self.detailed_log_level_var, e))
        except Exception as e:
            log.warning("Unknown error while getting '{}' variable: {} ".format(
                self.detailed_log_level_var, e))

        # If could not get the value earlier, a default value will be used
        if log_level is None or log_level == "":
            log.warning("Could not get '{}' variable from networkapi. ".format(
                self.detailed_log_level_var, default_log_level))
            log_level = default_log_level

        # Trying to set the level to each log object.
        for logger in loggers:
            try:
                logger.setLevel(log_level)
            except Exception as e:
                log.error("Invalid log level '{}'. The default {} will be used: {}".format(
                    log_level, default_log_level, e))
                log_level = default_log_level  # to be used at next iteration too
                logger.setLevel(log_level)

        return log_level
