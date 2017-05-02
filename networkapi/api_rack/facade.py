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

import ast
import json
import logging
import operator
import re
from networkapi.equipamento.models import Equipamento, EquipamentoRoteiro
from networkapi.interface.models import Interface, InterfaceNotFoundError
from networkapi.ip.models import Ip, IpEquipamento
from networkapi.rack.models import Rack, Datacenter, DatacenterRooms, RackConfigError
from networkapi.system.facade import get_value as get_variable
from networkapi.api_rack import exceptions, serializers, autoprovision
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from netaddr import IPNetwork
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response



log = logging.getLogger(__name__)

def save_dc(dc_dict):

    dc = Datacenter()

    dc.dcname = dc_dict.get('dcname')
    dc.address = dc_dict.get('address')

    dc.save_dc()
    return dc


def save_dcrooms(dcrooms_dict):

    dcrooms = DatacenterRooms()

    dcrooms.dc = Datacenter().get_dc(idt=dcrooms_dict.get('dc'))
    dcrooms.name = dcrooms_dict.get('name')
    dcrooms.racks = dcrooms_dict.get('racks')
    dcrooms.spines = dcrooms_dict.get('spines')
    dcrooms.leafs = dcrooms_dict.get('leafs')
    dcrooms.config = dcrooms_dict.get('config')

    dcrooms.save_dcrooms()
    return dcrooms


def edit_dcrooms(dcroom_id, dcrooms_dict):

    dcrooms = DatacenterRooms().get_dcrooms(idt=dcroom_id)

    if dcrooms_dict.get('name'):
        dcrooms.name = dcrooms_dict.get('name')
    if dcrooms_dict.get('racks'):
        dcrooms.racks = dcrooms_dict.get('racks')
    if dcrooms_dict.get('spines'):
        dcrooms.spines = dcrooms_dict.get('spines')
    if dcrooms_dict.get('leafs'):
        dcrooms.leafs = dcrooms_dict.get('leafs')
    if dcrooms_dict.get('config'):
        dcrooms.config = dcrooms_dict.get('config')

    dcrooms.save_dcrooms()
    return dcrooms


def save_rack_dc(rack_dict):

    rack = Rack()

    rack.nome = rack_dict.get('name')
    rack.numero = rack_dict.get('number')
    rack.mac_sw1 = rack_dict.get('mac_sw1')
    rack.mac_sw2 = rack_dict.get('mac_sw2')
    rack.mac_ilo = rack_dict.get('mac_ilo')
    rack.id_sw1 = Equipamento().get_by_pk(rack_dict.get('id_sw1'))
    rack.id_sw2 = Equipamento().get_by_pk(rack_dict.get('id_sw2'))
    rack.id_sw3 = Equipamento().get_by_pk(rack_dict.get('id_ilo'))
    rack.dcroom = DatacenterRooms().get_dcrooms(idt=rack_dict.get('dcroom')) if rack_dict.get('dcroom') else None

    if not rack.nome:
        raise exceptions.InvalidInputException("O nome do Rack não foi informado.")

    rack.save_rack()
    return rack


def buscar_roteiro(id_sw, tipo):

    roteiros = EquipamentoRoteiro.search(None, id_sw)
    for rot in roteiros:
        if (rot.roteiro.tipo_roteiro.tipo==tipo):
            roteiro_eq = rot.roteiro.roteiro
    roteiro_eq = roteiro_eq.lower()
    if not '.txt' in roteiro_eq:
        roteiro_eq=roteiro_eq+".txt"

    return roteiro_eq


def buscar_ip(id_sw):
    '''Retuns switch IP that is registered in a management environment
    '''

    ip_sw=None

    ips_equip = IpEquipamento().list_by_equip(id_sw)
    regexp = re.compile(r'GERENCIA')

    mgnt_ip = None
    for ip_equip in ips_equip:
        ip_sw = ip_equip.ip
        if not ip_sw == None:
            if regexp.search(ip_sw.networkipv4.vlan.ambiente.ambiente_logico.nome) is not None:
                return str(ip_sw.oct1) + '.' + str(ip_sw.oct2) + '.' + str(ip_sw.oct3) + '.' + str(ip_sw.oct4)

    return ""


def gerar_arquivo_config(ids):

    for id in ids:
        rack = Rack().get_rack(idt=id)
        equips = list()
        lf1 = dict()
        lf2 = dict()
        oob = dict()

        #Equipamentos
        num_rack = rack.numero
        try:
            nome_rack = rack.nome.upper()
            lf1["sw"] = 1
            lf1["id"] = rack.id_sw1.id
            lf1["nome"] = rack.id_sw1.nome
            lf1["mac"] = rack.mac_sw1
            lf1["marca"] = rack.id_sw1.modelo.marca.nome
            lf1["modelo"] = rack.id_sw1.modelo.nome
            equips.append(lf1)
            lf2["sw"] = 2
            lf2["id"] = rack.id_sw2.id
            lf2["nome"] = rack.id_sw2.nome
            lf2["mac"] = rack.mac_sw2
            lf2["marca"] = rack.id_sw2.modelo.marca.nome
            lf2["modelo"] = rack.id_sw2.modelo.nome
            equips.append(lf2)
            oob["sw"] = 3
            oob["id"] = rack.id_ilo.id
            oob["nome"] = rack.id_ilo.nome
            oob["mac"] = rack.mac_ilo
            oob["marca"] = rack.id_ilo.modelo.marca.nome
            oob["modelo"] = rack.id_ilo.modelo.nome
            equips.append(oob)
            dcroom = rack.dcroom
            dcname = rack.dcroom.dc.dcname
        except:
            raise Exception("Erro: Informações incompletas. Verifique o cadastro do Datacenter, da Sala e do Rack")


        dcsigla = "".join([c[0] for c in dcname.split(" ")]) if len(dcname.split(" ")) >= 2 else dcname[:3]
        radical = "-" + dcsigla + "-" + nome_rack + "-"
        prefixspn = "SPN"
        prefixlf = "LF-"
        prefixoob = "OOB"

        # Interface e Roteiro
        for equip in equips:
            try:
                interfaces = Interface.search(equip.get("id"))
                equip["interfaces"] = list()
                for interface in interfaces:
                    dic = dict()
                    try:
                        sw = interface.get_switch_and_router_interface_from_host_interface(None)
                        if  (sw.equipamento.nome[:3] in [prefixlf, prefixoob, prefixspn]):
                            dic["nome"] = sw.equipamento.nome
                            dic["id"] = sw.equipamento.id
                            dic["ip_mngt"] = buscar_ip(sw.equipamento.id)
                            dic["interface"] = sw.interface
                            dic["eq_interface"] = interface.interface
                            dic["roteiro"] = buscar_roteiro(sw.equipamento.id, "CONFIGURACAO")
                            equip["interfaces"].append(dic)
                    except:
                        pass
            except:
                raise Exception("Erro ao buscar o roteiro de configuracao ou as interfaces associadas ao equipamento: "
                                "%s." % equip.get("nome"))
            try:
                equip["roteiro"] = buscar_roteiro(equip.get("id"), "CONFIGURACAO")
                equip["ip_mngt"] = buscar_ip(equip.get("id"))
            except:
                raise Exception("Erro ao buscar os roteiros do equipamento: %s" % equip.get("nome"))

        try:
            NETWORKAPI_USE_FOREMAN = int(get_variable("use_foreman"))
            NETWORKAPI_FOREMAN_URL = get_variable("foreman_url")
            NETWORKAPI_FOREMAN_USERNAME = get_variable("foreman_username")
            NETWORKAPI_FOREMAN_PASSWORD = get_variable("foreman_password")
            FOREMAN_HOSTS_ENVIRONMENT_ID = get_variable("foreman_hosts_environment_id")
        except ObjectDoesNotExist:
            raise var_exceptions.VariableDoesNotExistException("Erro buscando as variáveis relativas ao Foreman.")

        # begin - Create Foreman entries for rack switches
        if NETWORKAPI_USE_FOREMAN:
            foreman = Foreman(NETWORKAPI_FOREMAN_URL, (NETWORKAPI_FOREMAN_USERNAME, NETWORKAPI_FOREMAN_PASSWORD),
                              api_version=2)

            # for each switch, check the switch ip against foreman know networks, finds foreman hostgroup
            # based on model and brand and inserts the host in foreman
            # if host already exists, delete and recreate with new information
            for equip in equips:
                #Get all foremand subnets and compare with the IP address of the switches until find it
                switch_nome = equip.get("nome")
                switch_modelo = equip.get("modelo")
                switch_marca = equip.get("marca")
                mac = equip.get("mac")
                ip = equip.get("ip_mngt")

                if mac == None:
                    raise Exception("Could not create entry for %s. There is no mac address." % (switch_nome))

                if ip == None:
                    raise RackConfigError(None, rack.nome,
                                          ("Could not create entry for %s. There is no management IP." % (switch_nome)))

                switch_cadastrado = 0
                for subnet in foreman.subnets.index()['results']:
                    network = IPNetwork(ip+'/'+subnet['mask']).network
                    # check if switches ip network is the same as subnet['subnet']['network'] e subnet['subnet']['mask']
                    if network.__str__() == subnet['network']:
                        subnet_id = subnet['id']
                        hosts = foreman.hosts.index(search=switch_nome)['results']
                        if len(hosts) == 1:
                            foreman.hosts.destroy(id=hosts[0]['id'])
                        elif len(hosts) > 1:
                            raise Exception("Could not create entry for %s. There are multiple "
                                                                    "entries with the same name." % (switch_nome))

                        # Lookup foreman hostgroup
                        # By definition, hostgroup should be Marca+"_"+Modelo
                        hostgroup_name = switch_marca+"_"+switch_modelo
                        hostgroups = foreman.hostgroups.index(search=hostgroup_name)
                        if len(hostgroups['results']) == 0:
                            raise Exception("Could not create entry for %s.Could not find hostgroup %s in foreman." %
                                                  (switch_nome, hostgroup_name))
                        elif len(hostgroups['results'])>1:
                            raise Exception("Could not create entry for %s. Multiple hostgroups %s found in Foreman."
                                            %(switch_nome,hostgroup_name))
                        else:
                            hostgroup_id = hostgroups['results'][0]['id']

                        host = foreman.hosts.create(host={'name': switch_nome, 'ip': ip, 'mac': mac,
                                                          'environment_id': FOREMAN_HOSTS_ENVIRONMENT_ID,
                                                          'hostgroup_id': hostgroup_id, 'subnet_id': subnet_id,
                                                          'build': 'true', 'overwrite': 'true'})
                        switch_cadastrado = 1

                if not switch_cadastrado:
                    raise Exception("Unknown error. Could not create entry for %s in foreman." % (switch_nome))

        # end - Create Foreman entries for rack switches

        log.info(str(equips))
        var1 = autoprovision.autoprovision_splf(rack, equips)
        var2 = autoprovision.autoprovision_coreoob(rack, equips)

        if var1 and var2:
            return True
        return False


def dic_vlan_core(variablestochangecore, rack, name_core, name_rack):
    """
    variablestochangecore: list
    rack: Numero do Rack
    name_core: Nome do Core
    name_rack: Nome do rack
    """

    core = int(name_core.split("-")[2])

    try:
        # valor base para as vlans e portchannels
        BASE_SO = int(get_variable("base_so"))
        # rede para conectar cores aos racks
        SO_OOB_NETipv4 = IPNetwork(get_variable("net_core"))
        # Vlan para cadastrar
        vlan_so_name = get_variable("vlan_so_name")
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável BASE_SO ou SO_OOB_NETipv4.")

    variablestochangecore["VLAN_SO"] = str(BASE_SO+rack)
    variablestochangecore["VLAN_NAME"] = vlan_so_name+name_rack
    variablestochangecore["VLAN_NUM"] = str(BASE_SO+rack)

    # Rede para cadastrar
    subSO_OOB_NETipv4 = list(SO_OOB_NETipv4.subnet(25))
    variablestochangecore["REDE_IP"] = str(subSO_OOB_NETipv4[rack]).split("/")[0]
    variablestochangecore["REDE_MASK"] = str(subSO_OOB_NETipv4[rack].prefixlen)
    variablestochangecore["NETMASK"] = str(subSO_OOB_NETipv4[rack].netmask)
    variablestochangecore["BROADCAST"] = str(subSO_OOB_NETipv4[rack].broadcast)

    # cadastro ip
    ip = 124 + core
    variablestochangecore["EQUIP_NAME"] = name_core
    variablestochangecore["IPCORE"] = str(subSO_OOB_NETipv4[rack][ip])

    # ja cadastrado
    variablestochangecore["IPHSRP"] = str(subSO_OOB_NETipv4[rack][1])
    variablestochangecore["NUM_CHANNEL"] = str(BASE_SO+rack)

    return variablestochangecore


def dic_lf_spn(rack):

    CIDREBGP = dict()
    CIDRBE = dict()
    ########
    VLANBELEAF = dict()
    VLANFELEAF = dict()
    VLANBORDALEAF = dict()
    VLANBORDACACHOSLEAF = dict()
    ########
    VLANBELEAF[rack] = list()
    VLANFELEAF[rack] = list()
    VLANBORDALEAF[rack] = list()
    VLANBORDACACHOSLEAF[rack] = list()

    ipv4_spn1 = dict()
    ipv4_spn2 = dict()
    ipv4_spn3 = dict()
    ipv4_spn4 = dict()
    redev6_spn1 = dict()
    redev6_spn2 = dict()
    redev6_spn3 = dict()
    redev6_spn4 = dict()

    try:
        BASE_RACK = int(get_variable("base_rack"))
        VLANBE = int(get_variable("vlanbe"))
        VLANFE = int(get_variable("vlanfe"))
        VLANBORDA = int(get_variable("vlanborda"))
        VLANBORDACACHOS = int(get_variable("vlanbordacachos"))
        VLANBETORxTOR = int(get_variable("vlanbetorxtor"))
        # CIDR sala 01 => 10.128.0.0/12
        CIDRBE[0] = IPNetwork(get_variable("cidr_sl01"))
        CIDREBGP[0] = IPNetwork(get_variable("cidr_bgp"))
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável BASE_RACK ou VLAN<BE,FE,BORDA,"
                                                           "CACHOS,TORxTOR> ou CIDR<BE,EBGP>.")

    SPINE1ipv4 = IPNetwork(get_variable("net_spn01"))
    SPINE2ipv4 = IPNetwork(get_variable("net_spn02"))
    SPINE3ipv4 = IPNetwork(get_variable("net_spn03"))
    SPINE4ipv4 = IPNetwork(get_variable("net_spn04"))
    # REDE subSPINE1ipv4[rack]
    subSPINE1ipv4 = list(SPINE1ipv4.subnet(31))
    subSPINE2ipv4 = list(SPINE2ipv4.subnet(31))
    subSPINE3ipv4 = list(SPINE3ipv4.subnet(31))
    subSPINE4ipv4 = list(SPINE4ipv4.subnet(31))

    SPINE1ipv6 = IPNetwork(get_variable("net_spn01_v6"))
    SPINE2ipv6 = IPNetwork(get_variable("net_spn02_v6"))
    SPINE3ipv6 = IPNetwork(get_variable("net_spn03_v6"))
    SPINE4ipv6 = IPNetwork(get_variable("net_spn04_v6"))
    subSPINE1ipv6 = list(SPINE1ipv6.subnet(127))
    subSPINE2ipv6 = list(SPINE2ipv6.subnet(127))
    subSPINE3ipv6 = list(SPINE3ipv6.subnet(127))
    subSPINE4ipv6 = list(SPINE4ipv6.subnet(127))

    # Vlans BE RANGE
    VLANBELEAF[rack].append(VLANBE+rack)
    # rede subSPINE1ipv4[rack]
    VLANBELEAF[rack].append(VLANBE+rack+BASE_RACK)
    VLANBELEAF[rack].append(VLANBE+rack+2*BASE_RACK)
    VLANBELEAF[rack].append(VLANBE+rack+3*BASE_RACK)
    # Vlans FE RANGE
    VLANFELEAF[rack].append(VLANFE+rack)
    VLANFELEAF[rack].append(VLANFE+rack+BASE_RACK)
    VLANFELEAF[rack].append(VLANFE+rack+2*BASE_RACK)
    VLANFELEAF[rack].append(VLANFE+rack+3*BASE_RACK)
    # Vlans BORDA RANGE
    VLANBORDALEAF[rack].append(VLANBORDA+rack)
    VLANBORDALEAF[rack].append(VLANBORDA+rack+BASE_RACK)
    VLANBORDALEAF[rack].append(VLANBORDA+rack+2*BASE_RACK)
    VLANBORDALEAF[rack].append(VLANBORDA+rack+3*BASE_RACK)
    # Vlans BORDACACHOS RANGE
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS+rack)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS+rack+BASE_RACK)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS+rack+2*BASE_RACK)
    VLANBORDACACHOSLEAF[rack].append(VLANBORDACACHOS+rack+3*BASE_RACK)

    # ########## BD ############
    vlans = dict()
    vlans['VLANBELEAF'] = VLANBELEAF
    vlans['VLANFELEAF'] = VLANFELEAF
    vlans['VLANBORDALEAF'] = VLANBORDALEAF
    vlans['VLANBORDACACHOSLEAF'] = VLANBORDACACHOSLEAF
    vlans['BE'] = [VLANBE, VLANFE]
    vlans['FE'] = [VLANFE, VLANBORDA]
    vlans['BORDA'] = [VLANBORDA, VLANBORDACACHOS]
    vlans['BORDACACHOS'] = [VLANBORDACACHOS, VLANBETORxTOR]

    ipv4_spn1['REDE_IP'] = str(subSPINE1ipv4[rack].ip)
    ipv4_spn1['REDE_MASK'] = subSPINE1ipv4[rack].prefixlen
    ipv4_spn1['NETMASK'] = str(subSPINE1ipv4[rack].netmask)
    ipv4_spn1['BROADCAST'] = str(subSPINE1ipv4[rack].broadcast)

    ipv4_spn2['REDE_IP'] = str(subSPINE2ipv4[rack].ip)
    ipv4_spn2['REDE_MASK'] = subSPINE2ipv4[rack].prefixlen
    ipv4_spn2['NETMASK'] = str(subSPINE2ipv4[rack].netmask)
    ipv4_spn2['BROADCAST'] = str(subSPINE2ipv4[rack].broadcast)

    ipv4_spn3['REDE_IP'] = str(subSPINE3ipv4[rack].ip)
    ipv4_spn3['REDE_MASK'] = subSPINE3ipv4[rack].prefixlen
    ipv4_spn3['NETMASK'] = str(subSPINE3ipv4[rack].netmask)
    ipv4_spn3['BROADCAST'] = str(subSPINE3ipv4[rack].broadcast)

    ipv4_spn4['REDE_IP'] = str(subSPINE4ipv4[rack].ip)
    ipv4_spn4['REDE_MASK'] = subSPINE4ipv4[rack].prefixlen
    ipv4_spn4['NETMASK'] = str(subSPINE4ipv4[rack].netmask)
    ipv4_spn4['BROADCAST'] = str(subSPINE4ipv4[rack].broadcast)

    redev6_spn1['REDE_IP'] = str(subSPINE1ipv6[rack].ip)
    redev6_spn1['REDE_MASK'] = subSPINE1ipv6[rack].prefixlen
    redev6_spn1['NETMASK'] = str(subSPINE1ipv6[rack].netmask)
    redev6_spn1['BROADCAST'] = str(subSPINE1ipv6[rack].broadcast)

    redev6_spn2['REDE_IP'] = str(subSPINE2ipv6[rack].ip)
    redev6_spn2['REDE_MASK'] = subSPINE2ipv6[rack].prefixlen
    redev6_spn2['NETMASK'] = str(subSPINE2ipv6[rack].netmask)
    redev6_spn2['BROADCAST'] = str(subSPINE2ipv6[rack].broadcast)

    redev6_spn3['REDE_IP'] = str(subSPINE3ipv6[rack].ip)
    redev6_spn3['REDE_MASK'] = subSPINE3ipv6[rack].prefixlen
    redev6_spn3['NETMASK'] = str(subSPINE3ipv6[rack].netmask)
    redev6_spn3['BROADCAST'] = str(subSPINE3ipv6[rack].broadcast)

    redev6_spn4['REDE_IP'] = str(subSPINE4ipv6[rack].ip)
    redev6_spn4['REDE_MASK'] = subSPINE4ipv6[rack].prefixlen
    redev6_spn4['NETMASK'] = str(subSPINE4ipv6[rack].netmask)
    redev6_spn4['BROADCAST'] = str(subSPINE4ipv6[rack].broadcast)

    redes = dict()
    redes['SPINE1ipv4'] = str(SPINE1ipv4)
    redes['SPINE1ipv4_net'] = ipv4_spn1
    redes['SPINE2ipv4'] = str(SPINE2ipv4)
    redes['SPINE2ipv4_net'] = ipv4_spn2
    redes['SPINE3ipv4'] = str(SPINE3ipv4)
    redes['SPINE3ipv4_net'] = ipv4_spn3
    redes['SPINE4ipv4'] = str(SPINE4ipv4)
    redes['SPINE4ipv4_net'] = ipv4_spn4

    ipv6 = dict()
    ipv6['SPINE1ipv6'] = str(SPINE1ipv6)
    ipv6['SPINE1ipv6_net'] = redev6_spn1
    ipv6['SPINE2ipv6'] = str(SPINE2ipv6)
    ipv6['SPINE2ipv6_net'] = redev6_spn2
    ipv6['SPINE3ipv6'] = str(SPINE3ipv6)
    ipv6['SPINE3ipv6_net'] = redev6_spn3
    ipv6['SPINE4ipv6'] = str(SPINE4ipv6)
    ipv6['SPINE4ipv6_net'] = redev6_spn4

    return vlans, redes, ipv6


def dic_pods(rack):

    subnetsRackBEipv4 = dict()
    subnetsRackBEipv4[rack] = list()

    PODSBEipv4 = dict()
    redesPODSBEipv4 = dict()
    PODSBEFEipv4 = dict()
    redesPODSBEFEipv4 = dict()
    PODSBEBOipv4 = dict()
    redesPODSBEBOipv4 = dict()
    PODSBECAipv4 = dict()
    redesPODSBECAipv4 = dict()

    PODSBEipv4[rack] = list()
    redesPODSBEipv4[rack] = list()
    PODSBEFEipv4[rack] = list()
    redesPODSBEFEipv4[rack] = list()
    PODSBEBOipv4[rack] = list()
    redesPODSBEBOipv4[rack] = list()
    PODSBECAipv4[rack] = list()
    redesPODSBECAipv4[rack] = list()

    PODSBEipv6 = dict()
    redesPODSBEipv6 = dict()
    PODSBEFEipv6 = dict()
    redesPODSBEFEipv6 = dict()
    PODSBEBOipv6 = dict()
    redesPODSBEBOipv6 = dict()
    PODSBECAipv6 = dict()
    redesPODSBECAipv6 = dict()
    subnetsRackBEipv6 = dict()

    PODSBEipv6[rack] = list()
    redesPODSBEipv6[rack] = list()
    PODSBEFEipv6[rack] = list()
    redesPODSBEFEipv6[rack] = list()
    PODSBEBOipv6[rack] = list()
    redesPODSBEBOipv6[rack] = list()
    PODSBECAipv6[rack] = list()
    redesPODSBECAipv6[rack] = list()
    subnetsRackBEipv6[rack] = list()

    try:
        # CIDR sala 01 => 10.128.0.0/12
        CIDRBEipv4 = IPNetwork(get_variable("cidr_be_v4"))
        CIDRBEipv6 = IPNetwork(get_variable("cidr_be_v6"))
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável CIDR<BEv4,BEv6>.")

    #          ::::::: SUBNETING FOR RACK NETWORKS - /19 :::::::

    # Redes p/ rack => 10.128.0.0/19, 10.128.32.0/19 , ... ,10.143.224.0/19
    subnetsRackBEipv4[rack] = splitnetworkbyrack(CIDRBEipv4, 19, rack)
    subnetsRackBEipv6[rack] = splitnetworkbyrack(CIDRBEipv6, 55, rack)

    # PODS BE => /20
    subnetteste = subnetsRackBEipv4[rack]
    subnetteste_ipv6 = subnetsRackBEipv6[rack]

    PODSBEipv4[rack] = splitnetworkbyrack(subnetteste, 20, 0)
    PODSBEipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 57, 0)
    # => 256 redes /28
    # Vlan 2 a 129
    redesPODSBEipv4[rack] = list(PODSBEipv4[rack].subnet(28))
    redesPODSBEipv6[rack] = list(PODSBEipv6[rack].subnet(64))
    # PODS BEFE => 10.128.16.0/21
    PODSBEFEipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(subnetteste, 20, 1), 21, 0)
    PODSBEFEipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 57, 1)
    # => 128 redes /28
    #  Vlan 130 a 193
    redesPODSBEFEipv4[rack] = list(PODSBEFEipv4[rack].subnet(28))
    redesPODSBEFEipv6[rack] = list(PODSBEFEipv6[rack].subnet(64))
    # PODS BEBO => 10.128.24.0/22
    PODSBEBOipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(subnetteste, 20, 1), 21, 1), 22, 0)
    PODSBEBOipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 57, 2)
    # => 64 redes /28
    # Vlan 194 a 257
    redesPODSBEBOipv4[rack] = list(PODSBEBOipv4[rack].subnet(28))
    redesPODSBEBOipv6[rack] = list(PODSBEBOipv6[rack].subnet(64))
    # PODS BECA => 10.128.28.0/23
    PODSBECAipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(subnetteste, 20, 1),
                                                                                  21, 1), 22, 1), 23, 0)
    PODSBECAipv6[rack] = splitnetworkbyrack(splitnetworkbyrack(subnetteste_ipv6, 57, 3), 58, 0)
    # => 32 redes /28
    # Vlan 258 a 289
    redesPODSBECAipv4[rack] = list(PODSBECAipv4[rack].subnet(28))
    redesPODSBECAipv6[rack] = list(PODSBECAipv6[rack].subnet(64))

    redes = dict()
    ipv6 = dict()
    redes['BE_VLAN_MIN'] = int(get_variable("be_vlan_min"))
    redes['BE_VLAN_MAX'] = int(get_variable("be_vlan_max"))
    redes['BE_PREFIX'] = str(redesPODSBEipv4[rack][0].prefixlen)
    redes['BE_REDE'] = str(PODSBEipv4[rack])
    ipv6['BE_PREFIX'] = str(redesPODSBEipv6[rack][0].prefixlen)
    ipv6['BE_REDE'] = str(PODSBEipv6[rack])

    redes['BEFE_VLAN_MIN'] = int(get_variable("befe_vlan_min"))
    redes['BEFE_VLAN_MAX'] = int(get_variable("befe_vlan_max"))
    redes['BEFE_PREFIX'] = str(redesPODSBEFEipv4[rack][0].prefixlen)
    redes['BEFE_REDE'] = str(PODSBEFEipv4[rack])
    ipv6['BEFE_PREFIX'] = str(redesPODSBEFEipv6[rack][0].prefixlen)
    ipv6['BEFE_REDE'] = str(PODSBEFEipv6[rack])

    redes['BEBORDA_VLAN_MIN'] = int(get_variable("beborda_vlan_min"))
    redes['BEBORDA_VLAN_MAX'] = int(get_variable("beborda_vlan_max"))
    redes['BEBORDA_PREFIX'] = str(redesPODSBEBOipv4[rack][0].prefixlen)
    redes['BEBORDA_REDE'] = str(PODSBEBOipv4[rack])
    ipv6['BEBORDA_PREFIX'] = str(redesPODSBEBOipv6[rack][0].prefixlen)
    ipv6['BEBORDA_REDE'] = str(PODSBEBOipv6[rack])

    redes['BECACHOS_VLAN_MIN'] = int(get_variable("becachos_vlan_min"))
    redes['BECACHOS_VLAN_MAX'] = int(get_variable("becachos_vlan_max"))
    redes['BECACHOS_PREFIX'] = str(redesPODSBECAipv4[rack][0].prefixlen)
    redes['BECACHOS_REDE'] = str(PODSBECAipv4[rack])
    ipv6['BECACHOS_PREFIX'] = str(redesPODSBECAipv6[rack][0].prefixlen)
    ipv6['BECACHOS_REDE'] = str(PODSBECAipv6[rack])

    return redes, ipv6


def dic_hosts_cloud(rack):

    subnetsRackBEipv4 = dict()
    subnetsRackBEipv4[rack] = list()
    redesHostsipv4 = dict()
    redesHostsipv4[rack] = list()
    redeHostsBEipv4 = dict()
    redeHostsBEipv4[rack] = list()
    redeHostsFEipv4 = dict()
    redeHostsFEipv4[rack] = list()
    redeHostsBOipv4 = dict()
    redeHostsBOipv4[rack] = list()
    redeHostsCAipv4 = dict()
    redeHostsCAipv4[rack] = list()
    redeHostsFILERipv4 = dict()
    redeHostsFILERipv4[rack] = list()

    subnetsRackBEipv6 = dict()
    subnetsRackBEipv6[rack] = list()
    redesHostsipv6 = dict()
    redesHostsipv6[rack] = list()
    redeHostsBEipv6 = dict()
    redeHostsBEipv6[rack] = list()
    redeHostsFEipv6 = dict()
    redeHostsFEipv6[rack] = list()
    redeHostsBOipv6 = dict()
    redeHostsBOipv6[rack] = list()
    redeHostsCAipv6 = dict()
    redeHostsCAipv6[rack] = list()
    redeHostsFILERipv6 = dict()
    redeHostsFILERipv6[rack] = list()

    hosts = dict()
    BE = dict()
    FE = dict()
    BO = dict()
    CA = dict()
    FILER = dict()
    ipv6 = dict()
    BE_ipv6 = dict()
    FE_ipv6 = dict()
    BO_ipv6 = dict()
    CA_ipv6 = dict()
    FILER_ipv6 = dict()

    try:
        # CIDR sala 01 => 10.128.0.0/12
        CIDRBEipv4 = IPNetwork(get_variable("cidr_be_v4"))
        CIDRBEipv6 = IPNetwork(get_variable("cidr_be_v6"))
        hosts['VLAN_MNGT_BE'] = int(get_variable("vlan_mngt_be"))
        hosts['VLAN_MNGT_FE'] = int(get_variable("vlan_mngt_fe"))
        hosts['VLAN_MNGT_BO'] = int(get_variable("vlan_mngt_bo"))
        hosts['VLAN_MNGT_CA'] = int(get_variable("vlan_mngt_ca"))
        hosts['VLAN_MNGT_FILER'] = int(get_variable("vlan_mngt_filer"))
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável VLAN_MNGT<BE,FE,BO,CA,FILER> ou "
                                                           "CIDR<BEv4,BEv6>.")

    subnetsRackBEipv4[rack] = splitnetworkbyrack(CIDRBEipv4, 19, rack)  # 10.128.32.0/19
    subnetteste = subnetsRackBEipv4[rack]  # 10.128.32.0/19

    subnetsRackBEipv6[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(CIDRBEipv6, 55, rack), 57, 3),
                                                 58, 1)
    subnetteste_ipv6 = splitnetworkbyrack(subnetsRackBEipv6[rack], 61, 7)

    # VLANS CLoud
    # ambiente BE - MNGT_NETWORK - RACK_AAXX
    # 10.128.30.0/23
    # vlans MNGT_BE/FE/BO/CA/FILER
    # PODS BE => /20
    # Hosts => 10.128.30.0/23
    redesHostsipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(
        subnetteste, 20, 1), 21, 1), 22, 1), 23, 1)
    redesHostsipv6[rack] = subnetteste_ipv6
    # Hosts BE => 10.128.30.0/24 => 256 endereços
    redeHostsBEipv4[rack] = splitnetworkbyrack(redesHostsipv4[rack], 24, 0)
    redeHostsBEipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 64, 3)
    # Hosts FE => 10.128.31.0/25 => 128 endereços
    redeHostsFEipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(redesHostsipv4[rack], 24, 1), 25, 0)
    redeHostsFEipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 64, 4)
    # Hosts BO => 10.128.31.128/26 => 64 endereços
    redeHostsBOipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(redesHostsipv4[rack], 24, 1),
                                                                  25, 1), 26, 0)
    redeHostsBOipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 64, 5)
    # Hosts CA => 10.128.31.192/27 => 32 endereços
    redeHostsCAipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(
        redesHostsipv4[rack], 24, 1), 25, 1), 26, 1), 27, 0)
    redeHostsCAipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 64, 6)
    # Hosts FILER => 10.128.15.224/27 => 32 endereços
    redeHostsFILERipv4[rack] = splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(splitnetworkbyrack(
        redesHostsipv4[rack], 24, 1), 25, 1), 26, 1), 27, 1)
    redeHostsFILERipv6[rack] = splitnetworkbyrack(subnetteste_ipv6, 64, 7)

    hosts['PREFIX'] = str(redesHostsipv4[rack].prefixlen)
    hosts["REDE"] = str(redesHostsipv4[rack])
    BE['REDE_IP'] = str(redeHostsBEipv4[rack].ip)
    BE['REDE_MASK'] = redeHostsBEipv4[rack].prefixlen
    BE['NETMASK'] = str(redeHostsBEipv4[rack].netmask)
    BE['BROADCAST'] = str(redeHostsBEipv4[rack].broadcast)
    hosts['BE'] = BE
    FE['REDE_IP'] = str(redeHostsFEipv4[rack].ip)
    FE['REDE_MASK'] = redeHostsFEipv4[rack].prefixlen
    FE['NETMASK'] = str(redeHostsFEipv4[rack].netmask)
    FE['BROADCAST'] = str(redeHostsFEipv4[rack].broadcast)
    hosts['FE'] = FE
    BO['REDE_IP'] = str(redeHostsBOipv4[rack].ip)
    BO['REDE_MASK'] = redeHostsBOipv4[rack].prefixlen
    BO['NETMASK'] = str(redeHostsBOipv4[rack].netmask)
    BO['BROADCAST'] = str(redeHostsBOipv4[rack].broadcast)
    hosts['BO'] = BO
    CA['REDE_IP'] = str(redeHostsCAipv4[rack].ip)
    CA['REDE_MASK'] = redeHostsCAipv4[rack].prefixlen
    CA['NETMASK'] = str(redeHostsCAipv4[rack].netmask)
    CA['BROADCAST'] = str(redeHostsCAipv4[rack].broadcast)
    hosts['CA'] = CA
    FILER['REDE_IP'] = str(redeHostsFILERipv4[rack].ip)
    FILER['REDE_MASK'] = redeHostsFILERipv4[rack].prefixlen
    FILER['NETMASK'] = str(redeHostsFILERipv4[rack].netmask)
    FILER['BROADCAST'] = str(redeHostsFILERipv4[rack].broadcast)
    hosts['FILER'] = FILER

    ipv6['PREFIX'] = str(redesHostsipv6[rack].prefixlen)
    ipv6['REDE'] = str(redesHostsipv6[rack])
    BE_ipv6['REDE_IP'] = str(redeHostsBEipv6[rack].ip)
    BE_ipv6['REDE_MASK'] = redeHostsBEipv6[rack].prefixlen
    BE_ipv6['NETMASK'] = str(redeHostsBEipv6[rack].netmask)
    BE_ipv6['BROADCAST'] = str(redeHostsBEipv6[rack].broadcast)
    ipv6['BE'] = BE_ipv6
    FE_ipv6['REDE_IP'] = str(redeHostsFEipv6[rack].ip)
    FE_ipv6['REDE_MASK'] = redeHostsFEipv6[rack].prefixlen
    FE_ipv6['NETMASK'] = str(redeHostsFEipv6[rack].netmask)
    FE_ipv6['BROADCAST'] = str(redeHostsFEipv6[rack].broadcast)
    ipv6['FE'] = FE_ipv6
    BO_ipv6['REDE_IP'] = str(redeHostsBOipv6[rack].ip)
    BO_ipv6['REDE_MASK'] = redeHostsBOipv6[rack].prefixlen
    BO_ipv6['NETMASK'] = str(redeHostsBOipv6[rack].netmask)
    BO_ipv6['BROADCAST'] = str(redeHostsBOipv6[rack].broadcast)
    ipv6['BO'] = BO_ipv6
    CA_ipv6['REDE_IP'] = str(redeHostsCAipv6[rack].ip)
    CA_ipv6['REDE_MASK'] = redeHostsCAipv6[rack].prefixlen
    CA_ipv6['NETMASK'] = str(redeHostsCAipv6[rack].netmask)
    CA_ipv6['BROADCAST'] = str(redeHostsCAipv6[rack].broadcast)
    ipv6['CA'] = CA_ipv6
    FILER_ipv6['REDE_IP'] = str(redeHostsFILERipv6[rack].ip)
    FILER_ipv6['REDE_MASK'] = redeHostsFILERipv6[rack].prefixlen
    FILER_ipv6['NETMASK'] = str(redeHostsFILERipv6[rack].netmask)
    FILER_ipv6['BROADCAST'] = str(redeHostsFILERipv6[rack].broadcast)
    ipv6['FILER'] = FILER_ipv6
    return hosts, ipv6


def dic_fe_prod(rack):

    CIDRFEipv4 = dict()
    CIDRFEipv4[rack] = list()
    CIDRFEipv6 = dict()
    CIDRFEipv6[rack] = list()

    subnetsRackFEipv4 = dict()
    subnetsRackFEipv4[rack] = list()
    subnetsRackFEipv6 = dict()
    subnetsRackFEipv6[rack] = list()

    podsFEipv4 = dict()
    podsFEipv4[rack] = list()
    podsFEipv6 = dict()
    podsFEipv6[rack] = list()

    ipv6 = dict()
    ranges = dict()
    redes = dict()

    try:
        # CIDR sala 01 => 172.20.0.0/14
        # Sumário do rack => 172.20.0.0/21
        CIDRFEipv4[0] = IPNetwork(get_variable("cidr_fe_v4"))
        # CIDRFE[1] = IPNetwork('172.20.1.0/14')
        CIDRFEipv6[0] = IPNetwork(get_variable("cidr_fe_v6"))
    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável VLAN_MNGT<BE,FE,BO,CA,FILER> ou "
                                                           "CIDR<FEv4,FEv6>.")

    # Sumário do rack => 172.20.0.0/21
    subnetsRackFEipv4[rack] = splitnetworkbyrack(CIDRFEipv4[0], 21, rack)
    subnetsRackFEipv6[rack] = splitnetworkbyrack(CIDRFEipv6[0], 57, rack)

    podsFEipv4[rack] = splitnetworkbyrack(subnetsRackFEipv4[rack], 28, 0)
    podsFEipv6[rack] = splitnetworkbyrack(subnetsRackFEipv6[rack], 64, 3)

    ranges['MAX'] = int(get_variable("fe_vlan_min"))
    ranges['MIN'] = int(get_variable("fe_vlan_max"))
    redes['PREFIX'] = podsFEipv4[rack].prefixlen
    redes['REDE'] = str(subnetsRackFEipv4[rack])

    ipv6['PREFIX'] = podsFEipv6[rack].prefixlen
    ipv6['REDE'] = str(subnetsRackFEipv6[rack])
    return redes, ranges, ipv6


def _get_core_name(rack):

    name_core1 = None
    name_core2 = None

    try:
        interfaces2 = Interface.search(rack.id_ilo.id)
        for interface2 in interfaces2:
            try:
                sw = interface2.get_switch_and_router_interface_from_host_interface(None)

                if sw.equipamento.nome.split('-')[0]=='OOB':
                    if sw.equipamento.nome.split('-')[2]=='01':
                        name_core1 = sw.equipamento.nome
                    elif sw.equipamento.nome.split('-')[2]=='02':
                        name_core2 = sw.equipamento.nome

            except InterfaceNotFoundError:
                next

    except e:
        raise RackAplError(None,rack.nome,"Erro ao buscar os nomes do Core associado ao Switch de gerencia %s" % rack.id_ilo.id)

    return name_core1, name_core2


def _criar_vlan(user, variablestochangecore1, ambientes, active=1):

    #get environment
    ambiente = Ambiente()
    divisaodc = DivisaoDc()
    divisaodc = divisaodc.get_by_name(ambientes.get('DC'))
    ambiente_log = AmbienteLogico()
    ambiente_log = ambiente_log.get_by_name(ambientes.get('LOG'))
    ambiente = ambiente.search(divisaodc.id, ambiente_log.id)
    for  amb in ambiente:
        if amb.grupo_l3.nome==ambientes.get('L3'):
            id_ambiente = amb
    # set vlan
    vlan = Vlan()
    vlan.acl_file_name = None
    vlan.acl_file_name_v6 = None
    vlan.num_vlan = variablestochangecore1.get("VLAN_NUM")
    vlan.nome = variablestochangecore1.get("VLAN_NAME")
    vlan.descricao = ""
    vlan.ambiente = id_ambiente
    vlan.ativada = active
    vlan.acl_valida = 0
    vlan.acl_valida_v6 = 0

    vlan.insert_vlan(user)

    return vlan


def _criar_rede_ipv6(user, tipo_rede, variablestochangecore1, vlan, active=1):

    tiporede = TipoRede()
    net_id = tiporede.get_by_name(tipo_rede)
    network_type = tiporede.get_by_pk(net_id.id)

    network_ip = NetworkIPv6()
    network_ip.vlan = vlan
    network_ip.network_type = network_type
    network_ip.ambient_vip = None
    network_ip.active = active
    network_ip.block = variablestochangecore1.get("REDE_MASK")

    while str(variablestochangecore1.get("REDE_IP")).endswith(":"):
        variablestochangecore1['REDE_IP'] = variablestochangecore1['REDE_IP'][:-1]

    while str(variablestochangecore1.get("NETMASK")).endswith(":"):
        variablestochangecore1['NETMASK'] = variablestochangecore1['NETMASK'][:-1]

    len_ip_ipv6 = len(str(variablestochangecore1.get("REDE_IP")).split(':'))
    len_mask = len(str(variablestochangecore1.get("NETMASK")).split(':'))

    while(8-len_ip_ipv6>0):#8-6=2--8-7=1--8-8=0
        len_ip_ipv6 = len_ip_ipv6 + 1
        variablestochangecore1['REDE_IP'] = variablestochangecore1.get("REDE_IP")+":0"

    while(8-len_mask>0):
        len_mask = len_mask + 1
        variablestochangecore1['NETMASK'] = variablestochangecore1.get("NETMASK")+":0"

    network_ip.block1, network_ip.block2, network_ip.block3, network_ip.block4, network_ip.block5, network_ip.block6, network_ip.block7, network_ip.block8 = str(variablestochangecore1.get("REDE_IP")).split(':')
    network_ip.mask1, network_ip.mask2, network_ip.mask3, network_ip.mask4, network_ip.mask5, network_ip.mask6, network_ip.mask7, network_ip.mask8 = str(variablestochangecore1.get("NETMASK")).split(':')

    destroy_cache_function([vlan.id])
    network_ip.save()

    return network_ip


def _criar_rede(user, tipo_rede, variablestochangecore1, vlan, active=1):

    tiporede = TipoRede()
    net_id = tiporede.get_by_name(tipo_rede)
    network_type = tiporede.get_by_pk(net_id.id)

    network_ip = NetworkIPv4()
    network_ip.oct1, network_ip.oct2, network_ip.oct3, network_ip.oct4 = str(variablestochangecore1.get("REDE_IP")).split('.')
    network_ip.block = variablestochangecore1.get("REDE_MASK")
    network_ip.mask_oct1, network_ip.mask_oct2, network_ip.mask_oct3, network_ip.mask_oct4 = str(variablestochangecore1.get("NETMASK")).split('.')
    network_ip.broadcast = variablestochangecore1.get("BROADCAST")
    network_ip.vlan = vlan
    network_ip.network_type = network_type
    network_ip.ambient_vip = None
    network_ip.active = active

    destroy_cache_function([vlan.id])
    network_ip.save()

    return network_ip


def _criar_ambiente(user, ambientes, ranges, acl_path=None, filter=None, vrf=None):

    #ambiente cloud
    environment = Ambiente()
    environment.grupo_l3 = GrupoL3()
    environment.ambiente_logico = AmbienteLogico()
    environment.divisao_dc = DivisaoDc()

    environment.grupo_l3.id = environment.grupo_l3.get_by_name(ambientes.get('L3')).id
    environment.ambiente_logico.id = environment.ambiente_logico.get_by_name(ambientes.get('LOG')).id
    environment.divisao_dc.id = environment.divisao_dc.get_by_name(ambientes.get('DC')).id

    environment.acl_path = acl_path
    environment.ipv4_template = None
    environment.ipv6_template = None
    if vrf is not None:
        environment.vrf = vrf

    environment.max_num_vlan_1 = ranges.get('MAX')
    environment.min_num_vlan_1 = ranges.get('MIN')
    environment.max_num_vlan_2 = ranges.get('MAX')
    environment.min_num_vlan_2 = ranges.get('MIN')

    environment.link = " "

    if filter is not None:
        try:
            filter_obj = Filter.objects.get(name__iexact=filter)
            environment.filter = filter_obj
        except ObjectDoesNotExist:
            pass


    environment.create(user)

    return environment


def _config_ambiente(user, hosts, ambientes):
    #ip_config
    ip_config = IPConfig()
    ip_config.subnet = hosts.get("REDE")
    ip_config.new_prefix = hosts.get("PREFIX")
    if hosts.get("VERSION")=="ipv4":
        ip_config.type = IP_VERSION.IPv4[0]
    elif hosts.get("VERSION")=="ipv6":
        ip_config.type = IP_VERSION.IPv6[0]
    tiporede = TipoRede()
    tipo = tiporede.get_by_name(hosts.get("TIPO"))
    ip_config.network_type = tipo

    ip_config.save()

    #ambiente
    config_environment = ConfigEnvironment()
    amb_log = AmbienteLogico()
    div = DivisaoDc()
    amb_log = amb_log.get_by_name(ambientes.get("LOG"))
    div = div.get_by_name(ambientes.get("DC"))
    for j in Ambiente().search(div.id, amb_log.id):
        if j.grupo_l3.nome==ambientes.get("L3"):
            config_environment.environment = j

    config_environment.ip_config = ip_config

    config_environment.save()


def _inserir_equip(user, variablestochangecore, rede_id):

    ip = Ip()
    ip.descricao = None
    ip.oct1, ip.oct2, ip.oct3, ip.oct4 = str(variablestochangecore["IPCORE"]).split('.')
    equip = Equipamento.get_by_name(variablestochangecore["EQUIP_NAME"])
    rede = NetworkIPv4.get_by_pk(rede_id)
    ip.save_ipv4(equip.id, user, rede)

    if ip.id is None:
        raise RackAplError (None, None, "Erro ao inserir os equipamentos")

    # Delete vlan's cache
    destroy_cache_function([rede.vlan_id])
    list_id_equip = []
    list_id_equip.append(equip.id)
    destroy_cache_function(list_id_equip, True)

    return 0


def _ambiente_spn_lf(user, rack, environment_list):

    vlans, redes, ipv6 = dic_lf_spn(user, rack.numero)

    divisaoDC = ['BE', 'FE', 'BORDA', 'BORDACACHOS']
    vrfNames = ['BEVrf', 'FEVrf', 'BordaVrf', 'BordaCachosVrf']
    spines = ['01', '02', '03', '04']

    grupol3 = GrupoL3()
    grupol3.nome = rack.nome
    grupol3.save()

    ambientes= dict()
    ambientes['L3']= rack.nome

    ranges=dict()
    hosts=dict()
    hosts['TIPO']= "Ponto a ponto"
    ipv6['TIPO']= "Ponto a ponto"

    for divisaodc, vrf in zip(divisaoDC, vrfNames):
        ambientes['DC']=divisaodc
        for i in spines:

            ambientes['LOG']= "SPINE"+i+"LEAF"
            rede = "SPINE"+i[1]+"ipv4"
            rede_ipv6 = "SPINE"+i[1]+"ipv6"

            #cadastro dos ambientes
            vlan_name = "VLAN"+divisaodc+"LEAF"
            ranges['MAX'] = vlans.get(vlan_name)[rack.numero][int(i[1])-1]+119
            ranges['MIN'] = vlans.get(vlan_name)[rack.numero][int(i[1])-1]

            env = criar_ambiente(user, ambientes, ranges, None, None, vrf)
            environment_list.append(env)
            vlan = dict()
            vlan['VLAN_NUM'] = vlans.get(vlan_name)[rack.numero][int(i[1])-1]
            vlan['VLAN_NAME'] = "VLAN_"+"SPN"+i[1]+'LF'+"_"+divisaodc
            vlan = criar_vlan(user, vlan, ambientes)
            criar_rede(user, hosts['TIPO'], redes.get(rede+'_net'), vlan)
            criar_rede_ipv6(user, ipv6['TIPO'], ipv6.get(rede_ipv6+'_net'), vlan)

            #configuracao do ambiente
            hosts['REDE'] = redes.get(rede)
            hosts['PREFIX'] = "31"

            ambientes['LOG']= "SPINE"+i+"LEAF"
            hosts['VERSION']="ipv4"
            config_ambiente(user, hosts, ambientes)

            ipv6['REDE']= ipv6.get(rede_ipv6)
            ipv6['PREFIX']="127"
            ipv6['VERSION']="ipv6"
            config_ambiente(user, ipv6, ambientes)

    return environment_list


def _ambiente_prod(user, rack, environment_list):

    redes, ipv6 = dic_pods(rack.numero)

    divisao_aclpaths = [['BE','BECLOUD'],['BEFE','BEFE'],['BEBORDA','BEBORDA'],['BECACHOS','BECACHOS']]

    grupol3 = rack.nome
    ambiente_logico = "PRODUCAO"

    ambientes= dict()
    ambientes['LOG']=ambiente_logico
    ambientes['L3']= grupol3

    ranges=dict()
    hosts=dict()
    vlans=dict()

    try:
        base_vlan = int(get_variable("num_vlan_acl_be"))
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável  NUM_VLAN_ACL_BE")

    hosts['TIPO']= "Rede invalida equipamentos"
    ipv6['TIPO']= "Rede invalida equipamentos"

    for item in divisao_aclpaths:
        divisaodc = item[0]
        acl_path = item[1]

        ambientes['DC']=divisaodc

        #criar ambiente
        vlan_min = divisaodc+"_VLAN_MIN"
        vlan_max = divisaodc+"_VLAN_MAX"
        ranges['MAX']= redes.get(vlan_max)
        ranges['MIN']= redes.get(vlan_min)

        env = criar_ambiente(user, ambientes, ranges, acl_path, "Servidores", "BEVrf")
        environment_list.append(env)

        #configuracao dos ambientes
        prefix = divisaodc+"_PREFIX"
        rede = divisaodc+"_REDE"

        hosts['PREFIX']= redes.get(prefix)
        hosts['REDE']= redes.get(rede)
        hosts['VERSION']="ipv4"
        config_ambiente(user, hosts, ambientes)

        ipv6['PREFIX']=ipv6.get(prefix)
        ipv6['REDE']=ipv6.get(rede)
        ipv6['VERSION']="ipv6"
        config_ambiente(user, ipv6, ambientes)

        vlans['VLAN_NUM'] = base_vlan
        base_vlan += 1
        vlans['VLAN_NAME'] = "ACL_"+divisaodc+"_"+ambientes.get('L3')
        criar_vlan(user, vlans, ambientes, 1)

    return environment_list


def _ambiente_cloud(user, rack, environment_list):

    hosts, ipv6 = dic_hosts_cloud(rack.numero)

    ambientes= dict()
    ambientes['DC']="BE"
    ambientes['LOG']="MNGT_NETWORK"
    ambientes['L3']= rack.nome

    ranges=dict()
    ranges['MAX']= hosts.get('VLAN_MNGT_FILER')
    ranges['MIN']=hosts.get('VLAN_MNGT_BE')
    aclpath = 'BECLOUD'

    #criar ambiente cloud
    env = criar_ambiente(user, ambientes, ranges, aclpath, "Servidores", "BEVrf")
    environment_list.append(env)

    #configuracao do ambiente
    hosts['TIPO']= "Rede invalida equipamentos"
    hosts['VERSION']= "ipv4"
    config_ambiente(user, hosts, ambientes)
    #ipv6
    ipv6['TIPO']= "Rede invalida equipamentos"
    ipv6['VERSION']="ipv6"
    config_ambiente(user, ipv6, ambientes)

    #inserir vlans
    amb_cloud = ['BE','FE','BO','CA','FILER']
    variables=dict()
    for amb in amb_cloud:
        numero = "VLAN_MNGT_"+amb
        variables['VLAN_NUM'] = hosts.get(numero)
        variables['VLAN_NAME'] = "DOM0_"+amb+"_"+rack.nome

        vlan = criar_vlan(user, variables, ambientes, 0)
        #criar rede
        criar_rede(user, "Rede invalida equipamentos", hosts.get(amb), vlan, 0)
        criar_rede_ipv6(user, "Rede invalida equipamentos", ipv6.get(amb), vlan, 0)

    return environment_list


def _ambiente_prod_fe(user, rack, environment_list):

    redes, ranges, ipv6 = dic_fe_prod(rack.numero)

    ambientes= dict()
    ambientes['LOG']="PRODUCAO"
    ambientes['L3']= rack.nome
    ambientes['DC']="FE"

    redes['TIPO']= "Rede invalida equipamentos"
    ipv6['TIPO']= "Rede invalida equipamentos"

    acl_path = 'FECLOUD'

    #criar ambiente
    env = criar_ambiente(user, ambientes, ranges, acl_path, "Servidores", "FEVrf")
    environment_list.append(env)

    #configuracao dos ambientes
    redes['VERSION']="ipv4"
    config_ambiente(user, redes, ambientes)

    ipv6['VERSION']="ipv6"
    config_ambiente(user, ipv6, ambientes)

    vlans=dict()
    try:
        vlans['VLAN_NUM'] = int(get_variable("num_vlan_acl_fe"))
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável  NUM_VLAN_ACL_FE")

    vlans['VLAN_NAME'] = "ACL_"+ambientes.get('DC')+"_"+ambientes.get('L3')
    criar_vlan(user, vlans, ambientes, 1)

    return environment_list

def _ambiente_borda(user,rack, environment_list):

    ranges=dict()
    ranges['MAX']=None
    ranges['MIN']=None
    ranges_vlans = dict()

    try:
        ranges_vlans['BORDA_DSR_VLAN_MIN'] = int(get_variable("borda_dsr_vlan_min"))
        ranges_vlans['BORDA_DSR_VLAN_MAX'] = int(get_variable("borda_dsr_vlan_max"))
        ranges_vlans['BORDA_DMZ_VLAN_MIN'] = int(get_variable("borda_dmz_vlan_min"))
        ranges_vlans['BORDA_DMZ_VLAN_MAX'] = int(get_variable("borda_dmz_vlan_max"))
        ranges_vlans['BORDACACHOS_VLAN_MIN'] = int(get_variable("bordacachos_vlan_min"))
        ranges_vlans['BORDACACHOS_VLAN_MAX'] = int(get_variable("bordacachos_vlan_max"))
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException("Erro buscando as variáveis BORDA<DSR,DMZ,CACHOS>_VLAN_<MAX,MIN>.")
    try:
        base_vlan = int(get_variable("num_vlan_acl_bordadsr"))
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException("Erro buscando a variável  NUM_VLAN_ACL_BORDADSR")

    ambientes=dict()
    vlans = dict()
    ambientes['LOG'] = "PRODUCAO"
    ambientes['L3']= rack.nome
    divisao_aclpaths = [['BORDA_DSR','BORDA-DSR', 'BordaVrf'],['BORDA_DMZ','BORDA-DMZ', 'BordaVrf'],['BORDACACHOS','BORDACACHOS', 'BordaCachosVrf']]

    for item in divisao_aclpaths:
        divisaodc = item[0]
        acl_path = item[1]
        vrf = item[2]

        vlan_min = divisaodc+"_VLAN_MIN"
        vlan_max = divisaodc+"_VLAN_MAX"
        ranges['MAX']= ranges_vlans.get(vlan_max)
        ranges['MIN']= ranges_vlans.get(vlan_min)

        ambientes['DC']= divisaodc
        env = criar_ambiente(user, ambientes,ranges, acl_path, "Servidores", vrf)
        environment_list.append(env)

        vlans['VLAN_NUM'] = base_vlan
        base_vlan += 1
        vlans['VLAN_NAME'] = "ACL_"+divisaodc+"_"+ambientes.get('L3')
        criar_vlan(user, vlans, ambientes, 1)

    return environment_list


def _environment_rack(user, environment_list, rack):

    #Insert all environments in environment rack table
    #Insert rack switches in rack environments
    for env in environment_list:
        try:
            ambienteRack = EnvironmentRack()
            ambienteRack.ambiente = env
            ambienteRack.rack = rack
            ambienteRack.create(user)
        except EnvironmentRackDuplicatedError:
            pass

        for switch in [rack.id_sw1, rack.id_sw2]:
            try:
                equipamento_ambiente = EquipamentoAmbiente()
                equipamento_ambiente.ambiente = env
                equipamento_ambiente.equipamento = switch
                equipamento_ambiente.is_router = True
                equipamento_ambiente.create(user)
            except EquipamentoAmbienteDuplicatedError:
                pass


def alocar_ambiente_vlan(id):

    rack = Rack().get_rack(idt=id)

    #variaveis
    name_core1, name_core2 =  _get_core_name(rack)

    environment_list = list()

    variablestochangecore1 = dict()
    variablestochangecore2 = dict()
    variablestochangecore1 = dic_vlan_core(variablestochangecore1, rack.numero, name_core1, rack.nome)
    variablestochangecore2 = dic_vlan_core(variablestochangecore2, rack.numero, name_core2, rack.nome)

    #######################################################################           VLAN Gerencia SO
    ambientes=dict()
    try:
        DIVISAODC_MGMT = get_variable("divisaodc_mngt")
        AMBLOG_MGMT = get_variable("amblog_mngt")
        GRPL3_MGMT = get_variable("grpl3_mngt")
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException("Erro buscando as variáveis <DIVISAODC,AMBLOG,GRPL3>_MGMT.")

    ambientes['DC']=DIVISAODC_MGMT
    ambientes['LOG']=AMBLOG_MGMT
    ambientes['L3']=GRPL3_MGMT

    try:
        #criar vlan
        vlan = _criar_vlan(user, variablestochangecore1, ambientes)
    except:
        raise RackAplError(None, rack.nome, "Erro ao criar a VLAN_SO.")
    try:
        #criar rede
        network = _criar_rede(user, "Rede invalida equipamentos", variablestochangecore1, vlan)
    except:
        raise RackAplError(None, rack.nome, "Erro ao criar a rede da VLAN_SO")
    try:
        #inserir os Core
        _inserir_equip(user, variablestochangecore1, network.id)
        _inserir_equip(user, variablestochangecore2, network.id)
    except:
        raise RackAplError(None, rack.nome, "Erro ao inserir o core 1 e 2")

    #######################################################################                   Ambientes

    #BE - SPINE - LEAF
    try:
        environment_list = _ambiente_spn_lf(user, rack, environment_list)
    except:
        raise RackAplError(None, rack.nome, "Erro ao criar os ambientes e alocar as vlans do Spine-leaf.")

    #BE - PRODUCAO
    try:
        environment_list = _ambiente_prod(user, rack, environment_list)
    except ObjectDoesNotExist, e:
        raise var_exceptions.VariableDoesNotExistException(e)
    except:
        raise RackAplError(None, rack.nome, "Erro ao criar os ambientes de produção.")

    #BE - Hosts - CLOUD
    try:
        environment_list = _ambiente_cloud(user, rack, environment_list)
    except:
        raise RackAplError(None, rack.nome, "Erro ao criar os ambientes e alocar as vlans da Cloud.")

    #FE
    try:
        environment_list = _ambiente_prod_fe(user, rack, environment_list)
    except ObjectDoesNotExist, e:
        raise var_exceptions.VariableDoesNotExistException(e)
    except:
        raise RackAplError(None, rack.nome, "Erro ao criar os ambientes de FE.")

    #Borda
    try:
        environment_list = _ambiente_borda(user, rack, environment_list)
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException()
    except:
        raise RackAplError(None, rack.nome, "Erro ao criar os ambientes de Borda.")

    #######################################################################                   Backuper

    _environment_rack(user, environment_list, rack)

    rack.__dict__.update(id=rack.id, create_vlan_amb=True)
    rack.save()

    return rack


# ################################################### old
def save_rack(rack_dict):

    rack = Rack()

    rack.nome = rack_dict.get('name')
    rack.numero = rack_dict.get('number')
    rack.mac_sw1 = rack_dict.get('sw1_mac')
    rack.mac_sw2 = rack_dict.get('sw2_mac')
    rack.mac_ilo = rack_dict.get('sw3_mac')
    id_sw1 = rack_dict.get('sw1_id')
    id_sw2 = rack_dict.get('sw2_id')
    id_sw3 = rack_dict.get('sw3_id')

    if not rack.nome:
        raise exceptions.InvalidInputException("O nome do Rack não foi informado.")
    if Rack.objects.filter(nome__iexact=rack.nome):
        raise exceptions.RackNameDuplicatedError()
    if Rack.objects.filter(numero__iexact=rack.numero):
        raise exceptions.RackNumberDuplicatedValueError()

    if not id_sw1:
        raise exceptions.InvalidInputException("O Leaf de id %s não existe." % id_sw1)
    if not id_sw2:
        raise exceptions.InvalidInputException("O Leaf de id %s não existe." % id_sw2)
    if not id_sw3:
        raise exceptions.InvalidInputException("O OOB de id %s não existe." % id_sw3)

    rack.id_sw1 = Equipamento.get_by_pk(int(id_sw1))
    rack.id_sw2 = Equipamento.get_by_pk(int(id_sw2))
    rack.id_ilo = Equipamento.get_by_pk(int(id_sw3))

    rack.save()
    return rack

def get_by_pk(user, idt):

    try:
        return Rack.objects.filter(id=idt).uniqueResult()
    except ObjectDoesNotExist, e:
        raise exceptions.RackNumberNotFoundError("Rack id %s nao foi encontrado" % (idt))
    except Exception, e:
        log.error(u'Failure to search the Rack.')
        raise exceptions.RackError("Failure to search the Rack. %s" % (e))

@api_view(['GET'])
def available_rack_number(request):

    log.info("Available Rack Number")

    data = dict()
    rack_anterior = 0

    for rack in Rack.objects.order_by('numero'):
        if rack.numero == rack_anterior:
            rack_anterior = rack_anterior + 1
        else:
            data['rack_number'] = rack_anterior if not rack_anterior > 119 else -1
            return Response(data, status=status.HTTP_200_OK)

    return Response(data, status=status.HTTP_200_OK)


