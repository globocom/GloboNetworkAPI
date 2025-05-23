from ncclient import manager
from networkapi.plugins import exceptions
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.plugins.base import BasePlugin
import logging
from networkapi.system.facade import get_value
import paramiko
import requests, json, os
from django.db.utils import DatabaseError
from networkapi.system.exceptions import VariableDoesNotExistException



log = logging.getLogger(__name__)

class GenericNetconf(BasePlugin):
    session_manager = None
    alternative_variable_base_path_list = ['path_to_tftpboot']
    alternative_static_base_path_list = ['/mnt/scripts/tftpboot/']


    def __try_lock(self):
        """
        Try lock to equipment, not necessary in Ncclient
        """
        return True

    def connect(self):
        """

        Connects to equipment using NCClient to provide Netconf access

        :raises:
            IOError: If can't connect to host
            Exception: to any other unhandled exceptions
        :return: None
        """

        log.info("Connection to equipment method started")



        ### If equipment access was not provided, then search the access ###
        if self.equipment_access is None:
            try:
                log.info("Searching for equipment access...")
                self.equipment_access = EquipamentoAcesso.search(
                    None, self.equipment, 'netconf').uniqueResult()
            except Exception:
                ### Equipment access not found
                log.error('Access type %s not found for equipment %s.' %
                          ('netconf', self.equipment.nome))
                raise exceptions.InvalidEquipmentAccessException()
        ### End block ###

        #Bypassing connection
        try:
            pass

        # ### Getting device access data ###
        # device = self.equipment_access.fqdn
        # username = self.equipment_access.user
        # password = self.equipment_access.password
        # ### End block ###

        # ### Runs connection ###
        # try:
        #     log.info("Starting connection to '%s' using NCClient..." % device)
        #     # transport = paramiko.Transport((device, 22))
        #     # transport.get_security_options().kex = (
        #     #     'curve25519-sha256',
        #     #     'diffie-hellman-group14-sha1',
        #     #     'diffie-hellman-group-exchange-sha256',
        #     # )
        #     # transport.get_security_options().ciphers = (
        #     #     'aes128-ctr', 'aes256-ctr'
        #     # )

        #     self.session_manager =  manager.connect(
        #         host = device,
        #         port = self.connect_port,
        #         username = username,
        #         password = password,
        #         # hostkey_verify = False,
        #         # allow_agent=False,
        #         # look_for_keys=False,

        #     )
        #     log.info('Connection succesfully...')

        ### Exception handler
        except IOError, e:
            log.error('Could not connect to host %s: %s' % (device, e))
            raise exceptions.ConnectionException(device)
        except Exception, e:
            log.error('Error connecting to host %s:%s' % (device, e))

    def apply_config_to_equipment(self, config, use_vrf=None, tarqet='running'):

        log.info("Starting method to apply config on equipment... Config: '%s'" % config)
        try:
            if use_vrf is None:
                use_vrf = self.management_vrf

            log.info("Config to apply: '%s'" % config)

            response = self.connect.edit_config(tarqet=tarqet, config=config)
            log.info(response)

            return response

        except Exception, e:
            log.error('Error on apply config to equipment')

    def ensure_privilege_level(self, privilege_level=None):
        """
        Ensure privilege level verifying if the current user is super-user.

        :returns:
            Returns True if success, otherwise, raise an exception (it will NOT return a false result)
        """
        return True

    def check_configuration_has_content(self, command, file_path):
        pass

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

    def copyScriptFileToConfig(self, filename, use_vrf='', destination=''):
        """
        Receives the file path (usually in /mnt/scripts/tftpboot/networkapi/generated_config/interface/)
        where contains the command to be executed in the equipment
        But in this case, we will not copy a file. We will use the file to read the configuration and apply to
        equipment by Netconf

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
        log.info("Configuration for file '%s' is valid." % file_path)

        try:
            command_file = open(file_path, "r")
            command = command_file.read()

            # Check if Configuration is not empty and raises exception if not contain
            # self.check_configuration_has_content(command=command, file_path=file_path)

            # log.info("Load configuration from file {} successfully".format(file_path))

            return self.exec_command(command=command)

        except IOError as e:
            self.close()
            message = "Configuration file not found." # Message to client
            log.error("{} {}: {}".format(message, file_path, e)) # Message to log
            raise exceptions.APIException(message)

    def exec_command(self, command, success_regex='', invalid_regex=None, error_regex=None):
        """
        Execute a command in equipment by netconf
        """

        log.info("Trying to execute a configuration on host {}...".format(self.equipment_access.fqdn))

        try:
            self.__try_lock() # Do nothing, will be executed by the locked method of ncclient
            # with self.session_manager.locked(target='running'):
            #     self.session_manager.edit_config(target='running', config=command)

            response = requests.post(
                url="http://localhost:5000/deploy",
                headers={"Content-type": "application/json"},
                data=json.dumps({
                    "address": self.equipment_access.fqdn,
                    "username": self.equipment_access.user,
                    "password": self.equipment_access.password,
                    "configuration": command
                })
            )

            if response.status_code != 200:
                raise Exception

            result_message = "Configuration was executed successfully on {}.".format(self.equipment_access.fqdn)
            log.info(result_message)
            return result_message

        except Exception as e:
            message = "Error while excute netconf command on equipment %s" % self.equipment_access.fqdn
            log.error(message)
            log.error(e)

            raise exceptions.APIException(message)

    def close(self):
        """
        Disconnect session from the equipment

        :returns: True if success or raise an exception on any error
        """
        # log.info("Close connection started...")
        pass
        # try:
        #     if self.session_manager:
        #         self.session_manager.close_session()
        #         log.info('Connection closed successfully.')
        #         return True

        #     else:
        #         raise Exception("session_manager is None.")

        # except Exception as e:
        #     message = "Error while calling close session method on equipment %s" % self.equipment_access.fqdn
        #     log.error(message)
        #     log.error(e)

        #     raise exceptions.APIException(message)

