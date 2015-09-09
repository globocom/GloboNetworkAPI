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

from django.template import Context, Template
from networkapi.log import Log

from networkapi.extra_logging import local, NO_REQUEST_ID

from networkapi.ip.models import Ip, IpNotFoundError, IpEquipamento
from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.infrastructure import ipaddr
from networkapi.api_network import exceptions
from networkapi.settings import NETWORK_CONFIG_FILES_PATH,\
							 NETWORK_CONFIG_TOAPPLY_REL_PATH, NETWORK_CONFIG_TEMPLATE_PATH
from networkapi.api_deploy.facade import deploy_config_in_equipment_synchronous
from networkapi.distributedlock import distributedlock,LOCK_VLAN, \
								 LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT, LOCK_NETWORK_IPV4
from networkapi.ip.models import NetworkIPv4, NetworkIPv6


log = Log(__name__)

TEMPLATE_TYPEv4= "ipv4_network_configuration"
TEMPLATE_TYPEv6= "ipv6_network_configuration"

def deploy_networkIPv4_configuration(user, networkipv4, equipment_list):

	data = dict()
	gateway_redundancy = False

	#lock network id to prevent multiple requests to same id

	with distributedlock(LOCK_NETWORK_IPV4 % networkipv4.id):
		with distributedlock(LOCK_VLAN % networkipv4.vlan.id):
			if networkipv4.active == 1:
				data["output"] = "Network already active. Nothing to do."
				log.info(data["output"])
				return data
			if networkipv4.vlan.ativada == 0:
				pass
				#TODO activate L2 vlan

			#load dict with all equipment attributes
			dict_ips = get_dict_v4_to_use_in_configuration_deploy(user, networkipv4, equipment_list)
			status_deploy = dict()
			#TODO implement threads
			for equipment in equipment_list:
				#generate config file
				file_to_deploy = _generate_config_file(dict_ips, equipment, TEMPLATE_TYPEv4)
				#deploy config file in equipments
				lockvar = LOCK_EQUIPMENT_DEPLOY_CONFIG_NETWORK_SCRIPT % (equipment.id)
				status_deploy[equipment.id] = deploy_config_in_equipment_synchronous(file_to_deploy, equipment, lockvar)
			
			networkipv4.active = 1
			networkipv4.save(user)

			return status_deploy

def _generate_config_file(dict_ips, equipment, template_type):

	config_to_be_saved = ""
	request_id = getattr(local, 'request_id', NO_REQUEST_ID)
	filename_out = "network_equip"+str(equipment.id)+"_config_"+str(request_id)
	filename_to_save = NETWORK_CONFIG_FILES_PATH+filename_out
	rel_file_to_deploy = NETWORK_CONFIG_TOAPPLY_REL_PATH+filename_out

	try:
		network_template_file = _load_template_file(equipment.id, template_type)
		key_dict = _generate_template_dict(dict_ips, equipment)
		config_to_be_saved += network_template_file.render( Context(key_dict) )
	except KeyError, exception:
		log.error("Erro: %s " % exception)
		raise exceptions.InvalidKeyException(exception)

	#Save new file
	try:
		file_handle = open(filename_to_save, 'w')
		file_handle.write(config_to_be_saved)
		file_handle.close()
	except IOError, e:
		log.error("Error writing to config file: %s" % filename_to_save)
		raise e

	return rel_file_to_deploy

def _generate_template_dict(dict_ips, equipment):

	key_dict = {}
	#TODO Separate differet vendor support if needed for gateway redundancy
	key_dict["VLAN_NUMBER"] = dict_ips["vlan_num"]
	key_dict["VLAN_NAME"] = dict_ips["vlan_name"]
	key_dict["IP"] = dict_ips[equipment]["ip"]
	key_dict["USE_GW_RED"] = dict_ips["gateway_redundancy"]
	key_dict["GW_RED_ADDR"] = dict_ips["gateway"]
	key_dict["GW_RED_PRIO"] = dict_ips[equipment]["prio"]
	key_dict["CIDR_BLOCK"] = dict_ips["cidr_block"]
	key_dict["NETWORK_MASK"] = dict_ips["mask"]
	key_dict["NETWORK_WILDMASK"] = dict_ips["wildmask"]
	key_dict["IP_VERSION"] = dict_ips["ip_version"]
	key_dict["FIRST_NETWORK"] = dict_ips["first_network"]
	#key_dict["ACL_IN"] = ""
	#key_dict["ACL_OUT"] = ""

	return key_dict

def get_dict_v4_to_use_in_configuration_deploy(user, networkipv4, equipment_list):

	try:
		gateway_ip = Ip.get_by_octs_and_net(networkipv4.oct1, networkipv4.oct2,
			networkipv4.oct3, networkipv4.oct4+1, networkipv4)
	except IpNotFoundError:
		log.error("Equipment IPs not correctly registered. \
			Router equipments should have first IP of network allocated for them.")
		raise exceptions.IncorrectRedundantGatewayRegistryException()

	ips = IpEquipamento.objects.filter(ip=gateway_ip, equipamento__in=equipment_list)
	if len(ips) != len(equipment_list):
		log.error("Equipment IPs not correctly registered. \
			Router equipments should have first IP of network allocated for them.")
		raise exceptions.IncorrectRedundantGatewayRegistryException()

	if networkipv4.vlan.vrf is not None and networkipv4.vlan.vrf is not '':
		dict_ips["vrf"] = networkipv4.vlan.vrf
	elif networkipv4.vlan.ambiente.vrf is not None:
		dict_ips["vrf"] = networkipv4.vlan.ambiente.vrf

	dict_ips = dict()
	dict_ips["gateway"] = "%d.%d.%d.%d" % (gateway_ip.oct1, gateway_ip.oct2, gateway_ip.oct3, gateway_ip.oct4) 
	dict_ips["ip_version"] = "IPV4"
	dict_ips["equipments"] = dict()
	dict_ips["vlan_num"] = networkipv4.vlan.num_vlan
	dict_ips["vlan_name"] = networkipv4.vlan.nome
	dict_ips["cidr_block"] = networkipv4.block
	dict_ips["mask"] = "%d.%d.%d.%d" % (networkipv4.mask_oct1, networkipv4.mask_oct2, networkipv4.mask_oct3, networkipv4.mask_oct4)
	dict_ips["wildmask"] = "%d.%d.%d.%d" % (255-networkipv4.mask_oct1, 255-networkipv4.mask_oct2, 255-networkipv4.mask_oct3, 255-networkipv4.mask_oct4)

	#Check if there are any other active network in the vlan
	#this is used because some equipemnts remove all the L3 config
	#when applying some commands, so they can only be applyed at the first time
	nets = NetworkIPv4.objects.filter(vlan=networkipv4.vlan)
	dict_ips["first_network"] = True
	for network in nets:
		if network.active == True:
			dict_ips["first_network"] = False

	netsv6 = NetworkIPv6.objects.filter(vlan=networkipv4.vlan)
	for network in netsv6:
		if network.active == True:
			dict_ips["first_network"] = False

	#Allocate IPs for routers when there are multiple gateways
	if len(equipment_list) > 1:
		dict_ips["gateway_redundancy"] = True
		equip_number = 0
		for equipment in equipment_list:
			ip = IpEquipamento.objects.filter(equipamento=equipment, ip__networkipv4=networkipv4).exclude(ip=gateway_ip)
			if ip == []:
				log.error("Error: Equipment IPs not correctly registered. \
					In case of multiple gateways, they should have an IP other than the gateway registered.")
				raise exceptions.IncorrectNetworkRouterRegistryException
			dict_ips[equipment] = dict()
			dict_ips[equipment]["ip"] = "%s.%s.%s.%s" % (ip.oct1, ip.oct2, ip.oct3, ip.oct4) 
			dict_ips[equipment]["prio"] = 100+equip_number
			equip_number += 1
	else:
		dict_ips["gateway_redundancy"] = False
		dict_ips[equipment_list[0]] = dict()
		dict_ips[equipment_list[0]]["ip"] = dict_ips["gateway"]
		dict_ips[equipment_list[0]]["prio"] = 100

	return dict_ips

def _load_template_file(equipment_id, template_type):
    try:
        equipment_template = (EquipamentoRoteiro.search(None, equipment_id, template_type)).uniqueResult()
    except:
        log.error("Template type %s not found." % template_type)
        raise exceptions.NetworkTemplateException()

    filename_in = NETWORK_CONFIG_TEMPLATE_PATH+"/"+equipment_template.roteiro.roteiro

    # Read contents from file
    try:
        file_handle = open(filename_in, 'r')
        template_file = Template ( file_handle.read() )
        file_handle.close()
    except IOError, e:
        log.error("Error opening template file for read: %s" % filename_in)
        raise e
    except Exception, e:
        log.error("Syntax error when parsing template: %s " % e)
        raise e
        #TemplateSyntaxError

    return template_file
