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

from .... import exceptions
from ....base import BasePlugin
from time import sleep
from django.template import Template
from django.template import Context
import logging
import re
import os
from networkapi.equipamento import models as eqpt_models
from networkapi.settings import BGP_CONFIG_FILES_PATH
from networkapi.settings import BGP_CONFIG_TOAPPLY_REL_PATH
from networkapi.settings import BGP_CONFIG_TEMPLATE_PATH
from networkapi.infrastructure.ipaddr import IPAddress
from networkapi.api_deploy import exceptions
from networkapi.api_equipment.exceptions import \
    AllEquipmentsAreInMaintenanceException
from networkapi.extra_logging import local
from networkapi.extra_logging import NO_REQUEST_ID
from networkapi.settings import TFTPBOOT_FILES_PATH

log = logging.getLogger(__name__)


class Generic(BasePlugin):
    TEMPLATE_NEIGHBOR_V4_ADD = 'neighbor_v4_add'
    TEMPLATE_NEIGHBOR_V4_REMOVE = 'neighbor_v4_remove'
    TEMPLATE_NEIGHBOR_V6_ADD = 'neighbor_v6_add'
    TEMPLATE_NEIGHBOR_V6_REMOVE = 'neighbor_v6_remove'

    MAX_TRIES = 10
    RETRY_WAIT_TIME = 5
    WAIT_FOR_CLI_RETURN = 1
    CURRENTLY_BUSY_WAIT = 'Currently busy with copying a file'
    INVALID_REGEX = '([Ii]nvalid)|overlaps with'
    WARNING_REGEX = 'config ignored|Warning'
    ERROR_REGEX = '[Ee][Rr][Rr][Oo][Rr]|[Ff]ail|\%|utility is occupied'

    admin_privileges = 15
    VALID_TFTP_PUT_MESSAGE = 'bytes successfully copied'

    def __init__(self, equipment=None, neighbor=None, virtual_interface=None,
                 asn=None, vrf=None):

        super(Generic, self).__init__()

        self.equipment = equipment
        self.neighbor = neighbor
        self.equipment_access = None
        self.virtual_interface = virtual_interface
        self.asn = asn
        self.vrf = vrf

    def _operate_equipment(self, _get_template_name):

        self.connect()
        self._ensure_privilege_level()
        template_name = _get_template_name()
        file_to_deploy = self._generate_config_file(template_name)
        self._deploy_config_in_equipment(file_to_deploy)
        self.close()

    def deploy_neighbor(self):

        self._operate_equipment(self._get_template_deploy_name)

    def undeploy_neighbor(self):

        self._operate_equipment(self._get_template_undeploy_name)

    def _get_template_deploy_name(self):

        ip_version = IPAddress(self.neighbor.get('remote_ip')).version

        if ip_version == 4:
            return self.TEMPLATE_NEIGHBOR_V4_ADD
        return self.TEMPLATE_NEIGHBOR_V6_ADD

    def _get_template_undeploy_name(self):

        ip_version = IPAddress(self.neighbor.get('remote_ip')).version

        if ip_version == 4:
            return self.TEMPLATE_NEIGHBOR_V4_REMOVE
        return self.TEMPLATE_NEIGHBOR_V6_REMOVE

    def _generate_config_file(self, template_type):
        """Load a template and write a file with the rended output.

        Args: 2-dimension dictionary with equipments information for template
              rendering equipment to render template to template type to load.

        Returns: filename with relative path to settings.TFTPBOOT_FILES_PATH
        """

        config_to_be_saved = ''
        request_id = getattr(local, 'request_id', NO_REQUEST_ID)

        filename_out = 'network_equip%s_config_%s' % (self.equipment.id,
                                                      request_id)

        filename_to_save = BGP_CONFIG_FILES_PATH + filename_out
        rel_file_to_deploy = BGP_CONFIG_TOAPPLY_REL_PATH + filename_out

        try:
            template_file = self._load_template_file(template_type)
            key_dict = self._generate_template_dict()
            config_to_be_saved += template_file.render(Context(key_dict))
        except KeyError, exception:
            log.error('Erro: %s ' % exception)
            raise exceptions.InvalidKeyException(exception)

        # Save new file
        try:
            file_handle = open(filename_to_save, 'w')
            file_handle.write(config_to_be_saved)
            file_handle.close()
        except IOError, e:
            log.error('Error writing to config file: %s' % filename_to_save)
            raise e

        return rel_file_to_deploy

    def _get_equipment_template(self, template_type):

        try:
            return eqpt_models.EquipamentoRoteiro.search(
                None, self.equipment.id, template_type).uniqueResult()
        except:
            log.error('Template type %s not found.' % template_type)
            raise exceptions.BGPTemplateException()

    def _load_template_file(self, template_type):
        """Load template file with specific type related to equipment.

        template_type: Type of template to be loaded

        Returns: template string
        """

        equipment_template = self._get_equipment_template(template_type)

        filename_in = BGP_CONFIG_TEMPLATE_PATH + \
                      '/' + equipment_template.roteiro.roteiro

        # Read contents from file
        try:
            file_handle = open(filename_in, 'r')
            template_file = Template(file_handle.read())
            file_handle.close()
        except IOError, e:
            log.error('Error opening template file for read: %s' % filename_in)
            raise Exception(e)
        except Exception, e:
            log.error('Syntax error when parsing template: %s ' % e)
            raise Exception(e)
            # TemplateSyntaxError

        return template_file

    def _deploy_config_in_equipment(self, rel_filename):

        # validate filename
        path = os.path.abspath(TFTPBOOT_FILES_PATH + rel_filename)
        if not path.startswith(TFTPBOOT_FILES_PATH):
            raise exceptions.InvalidFilenameException(rel_filename)

        # if type(self.equipment) is not Equipamento:
        #     log.error('Invalid data for equipment')
        #     raise api_exceptions.NetworkAPIException()

        if self.equipment.maintenance:
            raise AllEquipmentsAreInMaintenanceException()

        return self._applyconfig(rel_filename)

    def _applyconfig(self, filename):

        if self.equipment.maintenance is True:
            return 'Equipment is in maintenance mode. No action taken.'

        self._copy_script_file_to_config(filename)

    def _generate_template_dict(self):

        key_dict = {}
        key_dict['AS_NUMBER'] = self.asn.get('name')
        key_dict['VRF_NAME'] = self.vrf.get('vrf')
        key_dict['VIRTUAL_INTERFACE'] = self.virtual_interface.get('name')
        key_dict['REMOTE_IP'] = self.neighbor.get('remote_ip')
        key_dict['REMOTE_AS'] = self.neighbor.get('remote_as')
        key_dict['PASSWORD'] = self.neighbor.get('password')
        key_dict['TIMER_KEEPALIVE'] = self.neighbor.get('timer_keepalive')
        key_dict['TIMER_TIMEOUT'] = self.neighbor.get('timer_timeout')
        key_dict['DESCRIPTION'] = self.neighbor.get('description')
        key_dict['SOFT_RECONFIGURATION'] = \
             self.neighbor.get('soft_reconfiguration')
        key_dict['NEXT_HOP_SELF'] = self.neighbor.get('next_hop_self')
        key_dict['REMOVE_PRIVATE_AS'] = self.neighbor.get('remove_private_as')
        key_dict['COMMUNITY'] = self.neighbor.get('community')

        return key_dict

    def _copy_script_file_to_config(self, filename, use_vrf=None,
                                    destination='running-config'):
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
        while (not file_copied and retries < self.MAX_TRIES):
            if retries is not 0:
                sleep(self.RETRY_WAIT_TIME)

            try:
                log.info('try: %s - sending command: %s' % (retries, command))
                self.channel.send('%s\n' % command)
                recv = self._wait_string(self.VALID_TFTP_PUT_MESSAGE)
                file_copied = 1
            except exceptions.CurrentlyBusyErrorException:
                retries += 1

        # not capable of configuring after max retries
        if retries is self.MAX_TRIES:
            raise exceptions.CurrentlyBusyErrorException()

        return recv

    def _ensure_privilege_level(self, privilege_level=None):

        if privilege_level is None:
            privilege_level = self.admin_privileges

        self.channel.send('\n')
        recv = self._wait_string('>|#')
        self.channel.send('show privilege\n')
        recv = self._wait_string('Current privilege level is')
        level = re.search(
            'Current privilege level is ([0-9]+).*', recv, re.DOTALL).group(1)

        level = (level.split(' '))[-1]
        if int(level) < privilege_level:
            self.channel.send('enable\n')
            recv = self._wait_string('Password:')
            self.channel.send('%s\n' % self.equipment_access.enable_pass)
            recv = self._wait_string('#')

    def _wait_string(self, wait_str_ok_regex='', wait_str_invalid_regex=None,
                     wait_str_failed_regex=None):

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
