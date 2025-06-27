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
import os

from networkapi.api_deploy import exceptions
from networkapi.api_equipment.exceptions import AllEquipmentsAreInMaintenanceException
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.distributedlock import distributedlock
from networkapi.equipamento.models import Equipamento, EquipamentoAcesso
from networkapi.extra_logging import local
from networkapi.extra_logging import NO_REQUEST_ID
from networkapi.plugins.factory import PluginFactory
from networkapi.settings import CONFIG_FILES_PATH
from networkapi.settings import CONFIG_FILES_REL_PATH
from networkapi.settings import TFTP_SERVER_ADDR
from networkapi.settings import TFTPBOOT_FILES_PATH
# import pkgutil
# import re
# import sys
# import time
# import paramiko
# from networkapi.distributedlock import LOCK_VIP_IP_EQUIP
# from networkapi.equipamento.models import EquipamentoAcesso
# from networkapi.equipamento.models import EquipamentoRoteiro
# from networkapi.roteiro.models import TipoRoteiro

log = logging.getLogger(__name__)


def _applyconfig(equipment, filename, equipment_access=None, source_server=None, port=22):
    """Apply configuration file on equipment

    Args:
            equipment: networkapi.equipamento.Equipamento()
            filename: relative file path from TFTPBOOT_FILES_PATH to apply in equipment
            equipment_access: networkapi.equipamento.EquipamentoAcesso() to use
            source_server: source TFTP server address
            port: ssh tcp port

    Returns:
            equipment output

    Raises:
    """

    if equipment.maintenance is True:
        return 'Equipment is in maintenance mode. No action taken.'

    if source_server is None:
        source_server = TFTP_SERVER_ADDR

    # TODO: Handle exceptions from the following methods and generate response
    # for the caller
    # tipo_acesso = EquipamentoAcesso.search(None,
    #                                     equipment,
    #                                     ).uniqueResult()
    # if tipo_acesso is None:
    #     return 'Equipment has no Access.'

    equip_plugin = PluginFactory.factory(equipment)
    equip_plugin.connect()
    equip_plugin.ensure_privilege_level()
    vrf = equip_plugin.equipment_access.vrf.internal_name if equip_plugin.equipment_access.vrf else None
    equip_output = equip_plugin.copyScriptFileToConfig(filename, use_vrf=vrf)
    equip_plugin.close()

    return equip_output


def create_file_from_script(script, prefix_name=''):
    """Creates a file with script content

    Args:
            script: string with commands script
            prefix_name: prefix to use in filename

    Returns:
            file name created with path relative to networkapi.settings.TFTPBOOT_FILES_PATH

    Raises:
            IOError: if cannot write file
    """

    if prefix_name == '':
        prefix_name = 'script_reqid_'

    # validate filename
    path = os.path.abspath(CONFIG_FILES_PATH + prefix_name)
    if not path.startswith(CONFIG_FILES_PATH):
        raise exceptions.InvalidFilenameException(prefix_name)

    request_id = getattr(local, 'request_id', NO_REQUEST_ID)
    filename_out = prefix_name + str(request_id)
    filename_to_save = CONFIG_FILES_PATH + filename_out

    # Save new file
    try:
        file_handle = open(filename_to_save, 'w')
        file_handle.write(script)
        file_handle.close()
    except IOError, e:
        log.error('Error writing to config file: %s' % filename_to_save)
        raise e

    return CONFIG_FILES_REL_PATH + filename_out


def deploy_config_in_equipment_synchronous(rel_filename, equipment, lockvar,
                                           tftpserver=None,
                                           equipment_access=None):
    """Apply configuration file on equipment

    Args:
            rel_filename: relative file path from TFTPBOOT_FILES_PATH to apply
                          in equipment
            equipment: networkapi.equipamento.Equipamento() or Equipamento().id
            lockvar: distributed lock variable to use when applying config to
                     equipment
            equipment_access: networkapi.equipamento.EquipamentoAcesso() to use
            tftpserver: source TFTP server address

    Returns:
            equipment output

    Raises:
    """

    # validate filename
    path = os.path.abspath(TFTPBOOT_FILES_PATH + rel_filename)
    if not path.startswith(TFTPBOOT_FILES_PATH):
        raise exceptions.InvalidFilenameException(rel_filename)

    if type(equipment) is int:
        equipment = Equipamento.get_by_pk(equipment)
    elif type(equipment) is Equipamento:
        pass
    else:
        log.error('Invalid data for equipment')
        raise api_exceptions.NetworkAPIException()

    if equipment.maintenance:
        raise AllEquipmentsAreInMaintenanceException()

    with distributedlock(lockvar):
        return _applyconfig(
            equipment, rel_filename, equipment_access, tftpserver)


def deploy_config_in_equipment(rel_filename, equipment, tftpserver=None,
                               equipment_access=None):
    """Apply configuration file on equipment

    Args:
            rel_filename: relative file path from TFTPBOOT_FILES_PATH to apply
                          in equipment
            equipment: networkapi.equipamento.Equipamento() or Equipamento().id
            lockvar: distributed lock variable to use when applying config to
                     equipment
            equipment_access: networkapi.equipamento.EquipamentoAcesso() to use
            tftpserver: source TFTP server address

    Returns:
            equipment output

    Raises:
    """

    # validate filename
    path = os.path.abspath(TFTPBOOT_FILES_PATH + rel_filename)
    if not path.startswith(TFTPBOOT_FILES_PATH):
        raise exceptions.InvalidFilenameException(rel_filename)

    if type(equipment) is int:
        equipment = Equipamento.get_by_pk(equipment)
    elif type(equipment) is Equipamento:
        pass
    else:
        log.error('Invalid data for equipment')
        raise api_exceptions.NetworkAPIException()

    if equipment.maintenance:
        raise AllEquipmentsAreInMaintenanceException()

    return _applyconfig(
        equipment, rel_filename, equipment_access, tftpserver)
