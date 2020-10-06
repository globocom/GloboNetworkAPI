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
    log_tag = "[JUNOS PLUGIN]"  # Used to help the syslog filtering

    def __init__(self, **kwargs):
        super(JUNOS, self).__init__(connect_port=830, **kwargs)
        if 'quantity_of_times_to_try_lock' in kwargs:
            self.quantity_of_times_to_try_lock = kwargs.get('quantity_of_times_to_try_lock')

        if 'seconds_to_wait_to_try_lock' in kwargs:
            self.seconds_to_wait_to_try_lock = kwargs.get('seconds_to_wait_to_try_lock')

    def connect(self):

        """
        Connects to equipment via ssh using PyEz  and create connection with invoked shell object.
        """

        # Collect the credentials (user and password) for equipment
        if self.equipment_access is None:
            try:
                self.equipment_access = EquipamentoAcesso.search(
                    None, self.equipment, 'ssh').uniqueResult()
            except Exception:
                log.error("{} Access type {} not found for equipment {}.".format(
                    self.log_tag, 'ssh', self.equipment.nome))
                raise exceptions.InvalidEquipmentAccessException()

        try:
            self.remote_conn = Device(
                host=self.equipment_access.fqdn,
                user=self.equipment_access.user,
                passwd=self.equipment_access.password,
                port=self.connect_port)
            self.remote_conn.open()
            self.configuration = Config(self.remote_conn)

        except ConnectError as e:
            log.error("{} Could not connect to juniper host {}: {}".format(
                self.log_tag, self.equipment_access.fqdn, e))
            raise exceptions.ConnectionException(self.equipment_access.fqdn)
        except Exception, e:
            log.error("{} Error connecting to host {}: {}".format(
                self.log_tag, self.equipment_access.fqdn, e))
            raise Exception(e)

    def close(self):

        """
        Disconnect to equipment via ssh using PyEz.

        Raises:
            ConnectClosedError: if PyEz lib cannot close connection
            IOError: if cannot connect to host
            Exception: for other unhandled exceptions
        """

        try:
            self.remote_conn.close()
        except ConnectClosedError, e:
            log.error("{} Cannot close connection on host {}: {}".format(
                self.log_tag, self.equipment_access.fqdn, e))
        except Exception, e:
            log.error("{} Found an unexpected error at closing connection on host {}: {}".format(
                self.log_tag, self.equipment_access.fqdn, e))

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

        try:
            command_file = open(filename, "r")
            command = command_file.read()
        except IOError, e:
            log.error("{} File not found {}: {}".format(self.log_tag, filename, e))
            self.close()
        except Exception, e:
            log.error("{} Unexpected error occurred {}: {}".format(self.log_tag, filename, e))
            self.close()

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

        result_message = None

        if not self.plugin_try_lock():
            result_message = "Configuration could not be locked. Anybody else locked?"
            log.error("{} {} {}".format(self.log_tag, result_message, self.equipment_access.fqdn))
            self.close()
            return result_message
        else:
            log.info("{} Configuration was locked in host {} successfully".format(
                self.log_tag, self.equipment_access.fqdn))

        try:
            # self.configuration.lock()  #
            self.configuration.rollback()  # For a clean configuration
            self.configuration.load(command, format='set')
            self.configuration.commit_check()
            self.configuration.commit()
            self.configuration.unlock()

            result_message = "Configuration junos was executed successfully on host {}".format(
                self.equipment_access.fqdn)
            log.info("{} {} {}".format(self.log_tag, result_message, self.equipment_access.fqdn))

        except LockError as e:
            result_message = "Configuration could not be locked on host {}.".format(self.equipment_access.fqdn)
            log.error("{} {} {} {}".format(self.log_tag, result_message, self.equipment_access.fqdn, e))
            self.close()
        except UnlockError as e:
            result_message = "Configuration could not be unlocked on host {}. " \
                             "A rollback will be executed".format(self.equipment_access.fqdn)
            log.error("{} {} {} {}".format(self.log_tag, result_message, self.equipment_access.fqdn, e))
            self.configuration.rollback()
            self.close()
        except ConfigLoadError as e:
            result_message = "Configuration could not be loaded on host {}. " \
                             "A rollback and unlock will be executed.".format(self.equipment_access.fqdn)
            log.error("{} {} {}".format(self.log_tag, result_message, self.equipment_access.fqdn, e))
            self.configuration.rollback()
            self.configuration.unlock()
            self.close()
        except CommitError as e:
            result_message = "Configuration could not be commited on host {}. " \
                             "A rollback and unlock will be executed.".format(self.equipment_access.fqdn)
            log.error("{} {} {}".format(self.log_tag, result_message, self.equipment_access.fqdn, e))
            self.configuration.rollback()
            self.configuration.unlock()
            self.close()
        except RpcError as e:
            result_message = "Configuration database locked on host {}".format(self.equipment_access.fqdn)
            log.error("{} {} {} {}".format(self.log_tag, result_message, self.equipment_access.fqdn, e))
            self.close()
        except Exception as e:
            result_message = "An unexpected error occurred during configuration on host {}. " \
                             "A rollback and unlock will be executed.".format(self.equipment_access.fqdn)
            log.error("{} {} {}".format(self.log_tag, result_message, self.equipment_access.fqdn, e))
            self.configuration.rollback()
            self.configuration.unlock()
            self.close()

        return result_message

    def ensure_privilege_level(self, privilege_level=None):

        """
        Ensure privilege level.
        This function only verify is the current user is a super-user, otherwise raises an exception
        """

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
            log.error("{} {} {}".format(self.log_tag, "User has no privileges", self.equipment_access.fqdn))
            self.close()
            raise Exception

    def plugin_try_lock(self):

        for x in range(self.quantity_of_times_to_try_lock):
            try:
                self.configuration.lock()
                return True
            except (LockError, RpcError, Exception), e:
                # Keep looping ...
                log.warning(
                    "{} Configuration still could not be locked on host {}. "
                    "Automatic try in {} seconds - {}/{} ".format(
                        e, self.log_tag,
                        self.equipment_access.fqdn,
                        self.seconds_to_wait_to_try_lock,
                        x+1,
                        self.quantity_of_times_to_try_lock))
                time.sleep(self.seconds_to_wait_to_try_lock)

        return False

    def create_svi(self, svi_number, svi_description='no description'):
        pass

    def remove_svi(self, svi_number):
        pass

    def get_state_member(self, status):
        pass

    def set_state_member(self, status):
        pass

    def create_member(self, status):
        pass

    def remove_member(self, status):
        pass

    def get_restrictions(self, status):
        pass

    def partial_update_vip(self, **kwargs):
        pass

    def get_name_eqpt(self, **kwargs):
        pass

    def update_pool(self, **kwargs):
        pass

    def create_pool(self, **kwargs):
        pass

    def delete_pool(self, **kwargs):
        pass
