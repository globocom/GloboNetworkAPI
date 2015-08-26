# -*- coding:utf-8 -*-

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

from networkapi.distributedlock import distributedlock, LOCK_VIP_IP_EQUIP

from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.roteiro.models import TipoRoteiro
from networkapi.api_deploy import exceptions
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.log import Log

from settings import TFTPBOOT_FILES_PATH, TFTP_SERVER_ADDR

import importlib
import os
import paramiko
import sys
import time
import re

SUPPORTED_EQUIPMENT_BRANDS = ["Cisco", "Huawei"]
TEMPLATE_TYPE = "interface_configuration"

log = Log(__name__)

def deploy_config_in_equipment_synchronous(rel_filename, equipment, lockvar, tftpserver=None, equipment_access=None):

	#validate filename
	path = os.path.abspath(TFTPBOOT_FILES_PATH+rel_filename)
	if not path.startswith(TFTPBOOT_FILES_PATH):
		raise exceptions.InvalidFilenameException(rel_filename)

	with distributedlock(lockvar):
		return applyConfig(equipment, rel_filename, equipment_access, tftpserver)

def create_connnection(equipment,equipment_access, port=22):

	if equipment_access==None:
		try:
			equipment_access = EquipamentoAcesso.search(None, equipment, "ssh").uniqueResult()
		except e:
			log.error("Access type %s not found for equipment %s." % ("ssh", equipment.nome))
			raise exceptions.InvalidEquipmentAccessException()

	device = equipment.nome
	username = equipment_access.user
	password = equipment_access.password

	remote_conn=paramiko.SSHClient()
	remote_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	try:
		remote_conn.connect(device,port=port,username=username,password=password)
	except IOError, e:
		log.error("Could not connect to host %s: %s" % (device, e))
		raise exceptions.ConnectionException(device)
	except Exception, e:
		log.error("Error connecting to host %s: %s" % (device, e))
		raise e

	return remote_conn

def load_module_for_equipment_config(equipment):
	marca = equipment.modelo.marca.nome
	module_name = "networkapi.api_deploy."+marca+".Generic"

	try:
		loaded_module = importlib.import_module(module_name, package=None)
	except Exception, e:
		log.error("Error importing module: %s - %s" % (module_name, e))
		raise exceptions.LoadEquipmentModuleException(module_name)

	return loaded_module

def applyConfig(equipment,filename, equipment_access=None,tftpserver=None,port=22):

    if tftpserver == None:
    	tftpserver = TFTP_SERVER_ADDR

	#marca = equipment.modelo.marca.nome
	
	equip_module = load_module_for_equipment_config(equipment)

	remote_conn = create_connnection(equipment, equipment_access)
	switch_output = equip_module.copyTftpToConfig(remote_conn,tftpserver,filename)
	remote_conn.close()
#	if(marca=='Cisco'):
#		switch_output = CiscoGeneric.copyTftpToConfig(remote_conn,tftpserver,filename)
#	elif(marca=='Huawei'):
#		switch_output = HuaweiGeneric.copyTftpToConfig(remote_conn,tftpserver,filename)
#	else: 
#		log.error('Equipment not supported.')
#		remote_conn.close()
	return switch_output
	
