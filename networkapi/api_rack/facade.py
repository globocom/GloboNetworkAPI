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
import logging
import operator
import re
from django.core.exceptions import ObjectDoesNotExist
from netaddr import IPNetwork
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from networkapi.vlan import models as models_vlan
from networkapi.api_vlan.facade import v3 as facade_vlan_v3
from networkapi.equipamento.models import Equipamento, EquipamentoRoteiro
from networkapi.interface.models import Interface
from networkapi.ip.models import IpEquipamento
from networkapi.rack.models import Rack, Datacenter, DatacenterRooms
from networkapi.api_rack import serializers as rack_serializers
from networkapi.api_rack import exceptions, autoprovision


log = logging.getLogger(__name__)


def save_dc(dc_dict):

    dc = Datacenter()

    dc.dcname = dc_dict.get('dcname')
    dc.address = dc_dict.get('address')

    dc.save_dc()
    return dc


def listdc():

    dc_list = list()
    for dc in Datacenter().get_dc():
        dc_list.append(rack_serializers.DCSerializer(dc).data)

    dc_sorted = sorted(dc_list, key=operator.itemgetter('dcname'))

    for dcs in dc_sorted:
        fabric = DatacenterRooms().get_dcrooms(id_dc=dcs.get("id"))
        fabric_list = list()
        for i in fabric:
            fabric_list.append(rack_serializers.DCRoomSerializer(i).data)
        dcs["fabric"] = fabric_list

    return dc_sorted

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


def get_fabric(idt=None, name=None, id_dc=None):

    fabric_list = list()
    fabric_obj = DatacenterRooms()

    if idt:
        fabric = [fabric_obj.get_dcrooms(idt=idt)]
    elif name:
        fabric = fabric_obj.get_dcrooms(name=name)

    elif id_dc:
        fabric = fabric_obj.get_dcrooms(id_dc=id_dc)
    else:
        fabric = fabric_obj.get_dcrooms()


    for i in fabric:
        fabric_list.append(rack_serializers.DCRoomSerializer(i).data)

    return fabric_list


def update_fabric_config(fabric_id, fabric_dict):

    fabric = DatacenterRooms().get_dcrooms(idt=fabric_id)

    if fabric.config:
        envconfig = ast.literal_eval(fabric.config)
    else:
        envconfig = dict()

    if fabric_dict.get("Ambiente"):
        log.info("ambiente")
        if envconfig.get("Ambiente"):
            envconfig.get("Ambiente").append(fabric_dict.get("Ambiente"))
        else:
            envconfig["Ambiente"] = [fabric_dict.get("Ambiente")]
    """
    elif fabric_dict.get("BGP"):
        log.info("bgp")
        envconfig.get("BGP") = fabric_dict.get("BGP")
    elif fabric_dict.get("VLT"):
        log.info("vlt")
        envconfig.get("VLT") = fabric_dict.get("VLT")
    """

    fabric.config = envconfig
    fabric.save_dcrooms()
    return fabric

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


def get_rack(fabric_id=None):

    rack_obj = Rack()

    if fabric_id:
        rack = rack_obj.get_rack(dcroom_id=fabric_id)
    else:
        rack = rack_obj.get_rack()

    rack_list = rack_serializers.RackSerializer(rack, many=True).data if rack else list()

    return rack_list


def _buscar_roteiro(id_sw, tipo):

    roteiro_eq = None
    roteiros = EquipamentoRoteiro.search(None, id_sw)
    for rot in roteiros:
        if rot.roteiro.tipo_roteiro.tipo == tipo:
            roteiro_eq = rot.roteiro.roteiro
    roteiro_eq = roteiro_eq.lower()
    if '.txt' not in roteiro_eq:
        roteiro_eq = roteiro_eq + ".txt"

    return roteiro_eq


def _buscar_ip(id_sw):
    """
    Retuns switch IP that is registered in a management environment
    """

    ips_equip = IpEquipamento().list_by_equip(id_sw)
    regexp = re.compile(r'GERENCIA')

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

        # Equipamentos
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
            dcname = rack.dcroom.dc.dcname
        except:
            raise Exception("Erro: Informações incompletas. Verifique o cadastro do Datacenter, do Fabric e do Rack")

        dcsigla = "".join([c[0] for c in dcname.split(" ")]) if len(dcname.split(" ")) >= 2 else dcname[:3]
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
                        if sw.equipamento.nome[:3] in [prefixlf, prefixoob, prefixspn]:
                            dic["nome"] = sw.equipamento.nome
                            dic["id"] = sw.equipamento.id
                            dic["ip_mngt"] = _buscar_ip(sw.equipamento.id)
                            dic["interface"] = sw.interface
                            dic["eq_interface"] = interface.interface
                            dic["roteiro"] = _buscar_roteiro(sw.equipamento.id, "CONFIGURACAO")
                            equip["interfaces"].append(dic)
                    except:
                        pass
            except:
                raise Exception("Erro ao buscar o roteiro de configuracao ou as interfaces associadas ao equipamento: "
                                "%s." % equip.get("nome"))
            try:
                equip["roteiro"] = _buscar_roteiro(equip.get("id"), "CONFIGURACAO")
                equip["ip_mngt"] = _buscar_ip(equip.get("id"))
            except:
                raise Exception("Erro ao buscar os roteiros do equipamento: %s" % equip.get("nome"))

        autoprovision.autoprovision_splf(rack, equips)
        autoprovision.autoprovision_coreoob(rack, equips)

    return 1


def _create_spnlfenv(rack, envfathers):

    environment_spn_lf_list = list()
    spines = int(rack.dcroom.spines)
    fabric = rack.dcroom.name

    try:
        id_grupo_l3 = models_env.GrupoL3().get_by_name(fabric).id
    except:
        grupo_l3_dict = models_env.GrupoL3()
        grupo_l3_dict.nome = fabric
        grupo_l3_dict.save()
        id_grupo_l3 = grupo_l3_dict.id
        pass
    for env in envfathers:
        config_subnet = list()
        for net in env.configs:
            # verificar se o ambiente possui range associado.
            cidr = IPNetwork(net.ip_config.subnet)
            prefix = int(net.ip_config.new_prefix)
            network = {
                'cidr': list(cidr.subnet(prefix)),
                'type': net.ip_config.type,
                'network_type': net.ip_config.network_type.id
            }
            config_subnet.append(network)
        for spn in range(spines):
            amb_log_name = "SPINE0" + str(spn+1) + "LEAF"
            try:
                id_amb_log = models_env.AmbienteLogico().get_by_name(amb_log_name).id
            except:
                amb_log_dict = models_env.AmbienteLogico()
                amb_log_dict.nome = spine_name
                amb_log_dict.save()
                id_amb_log = amb_log_dict.id
                pass
            config = list()
            for sub in config_subnet:
                config_spn = {
                    'subnet': str(sub.get("cidr")[spn]),
                    'new_prefix': str(31) if str(sub.get("type"))[-1] is "4" else str(127),
                    'type': str(sub.get("type")),
                    'network_type': sub.get("network_type")
                }
                config.append(config_spn)
            obj = {
                'grupo_l3': id_grupo_l3,
                'ambiente_logico': id_amb_log,
                'divisao_dc': env.divisao_dc.id,
                'acl_path': env.acl_path,
                'ipv4_template': env.ipv4_template,
                'ipv6_template': env.ipv6_template,
                'link': env.link,
                'min_num_vlan_2': env.min_num_vlan_2,
                'max_num_vlan_2': env.max_num_vlan_2,
                'min_num_vlan_1': env.min_num_vlan_1,
                'max_num_vlan_1': env.max_num_vlan_1,
                'vrf': env.vrf,
                'father_environment': env.id,
                'default_vrf': env.default_vrf.id,
                'configs': config
            }
            environment_spn_lf = models_env.Ambiente().environment_spn_lf.create_v3(obj)
            log.debug("Environment object: %s" % str(obj))
            environment_spn_lf_list.append(environment_spn_lf)
    return environment_spn_lf_list


def _create_spnlfvlans(rack, spn_lf_envs_ids, user):

    rack_number = int(rack.numero)
    tipo_rede = "Ponto a ponto"
    try:
        id_network_type = models_vlan.TipoRede().get_by_name(tipo_rede).id
    except:
        network_type = models_vlan.TipoRede()
        network_type.tipo_rede = tipo_rede
        network_type.save()
        id_network_type = network_type.id
        pass
    for env in spn_lf_envs_ids:
        env_id = env.id
        vlan_base = env.min_num_vlan_1
        vlan_number = int(vlan_base) + int(rack_number)
        vlan_name = "VLAN_" + env.divisao_dc.nome + "_" + env.ambiente_logico.nome + "_" + rack.nome

        for net in env.configs:
            prefix = int(net.ip_config.new_prefix)
            network = {
                'prefix': prefix,  # str(list(cidr.subnet(prefix))[rack_number]),
                'network_type': id_network_type
            }
            if str(net.ip_config.type)[-1] is "4":
                create_networkv4 = network
            elif str(net.ip_config.type)[-1] is "6":
                create_networkv6 = network
        obj = {
            'name': vlan_name,
            'num_vlan': vlan_number,
            'environment': env_id,
            'default_vrf': env.default_vrf.id,
            'vrf': env.vrf,
            'create_networkv4': create_networkv4 if create_networkv4 else None,
            'create_networkv6': create_networkv6 if create_networkv6 else None
        }
        log.debug("Vlan object: %s" % str(obj))
        facade_vlan_v3.create_vlan(obj, user)


def _create_vlans_cloud(rack, env_mngtcloud, user):

    # se cadastrar o ambiente com os ambientes filhos, os ambientes filhos teriam cadastro errado
    # já que teria que inventar um range para poder cadastrar o prefix e o type
    #
    # se não cadastrar o filho, como vou saber como quebrar a rede entre os ambientes filhos?
    #
    # pro pop dá pra fazer (prefix iguais), pro dc não dá

    var = sorted(env_mngtcloud, key=operator.itemgetter('father_environment.id'))
    father = var[0]
    envs = var.remove(father)

    for j in envs:
        if j.father_environment:
            if int(j.father_environment) is not int(var[0].id):
                log.info("Ambientes não cadastrados corretamente")
                return None
        else:
            log.info("Ambientes não cadastrados corretamente")
            return None

    envs = sorted(envs, key=operator.itemgetter('divisao_dc.nome'))

    config = list()
    for net_father in father.configs:
        config["cidr"] = IPNetwork(net_father.ip_config.subnet)
        config["type"] = net_father.ip_config.type
        config["network_type"] = net_father.ip_config.network_type

    for env in envs:
        """
        for conf in env.configs:
            prefix = conf.ip_config.new_prefix
            type = conf.ip_config.type

            for net in net_father:
                config["cidr"] = splitnetworkbyrack(net.get("cidr"), , 0)
        net_father = net
        """
        env_id = env.id
        vlan_number = env.max_num_vlan_1
        vlan_name = "DOM_" + env.divisao_dc.nome + "_" + env.ambiente_logico.nome + "_" + rack.nome

        for net in env.configs:
            prefix = int(net.ip_config.new_prefix)
            network = {
                'prefix': prefix,  # str(list(cidr.subnet(prefix))[rack_number]),
                'network_type': id_network_type
            }
            if str(net.ip_config.type)[-1] is "4":
                create_networkv4 = network
            elif str(net.ip_config.type)[-1] is "6":
                create_networkv6 = network
        obj = {
            'name': vlan_name,
            'num_vlan': vlan_number,
            'environment': env_id,
            'default_vrf': env.default_vrf.id,
            'vrf': env.vrf,
            'create_networkv4': create_networkv4 if create_networkv4 else None,
            'create_networkv6': create_networkv6 if create_networkv6 else None
        }
        log.debug("Vlan object: %s" % str(obj))
        facade_vlan_v3.create_vlan(obj, user)


def _create_fe_envs(rack, env_fe):

    try:
        id_grupo_l3 = models_env.GrupoL3().get_by_name(rack.nome).id
    except:
        grupo_l3_dict = models_env.GrupoL3()
        grupo_l3_dict.nome = rack.nome
        grupo_l3_dict.save()
        id_grupo_l3 = grupo_l3_dict.id
        pass

    environment = None
    for env in env_fe:
        confs = list()
        for config in env.configs:
            net = IPNetwork(config.ip_config.subnet)
            network = {
                'subnet': list(net.subnet(config.ip_config.new_prefix))[int(rack.numero)],
                'new_prefix': str(27) if str(sub.get("type"))[-1] is "4" else str(64),
                'type': config.ip_config.type,
                'network_type': config.ip_config.network_type
            }
            confs.append(network)
        obj = {
            'grupo_l3': id_grupo_l3,
            'ambiente_logico': env.ambiente_logico,
            'divisao_dc': env.divisao_dc.id,
            'acl_path': env.acl_path,
            'ipv4_template': env.ipv4_template,
            'ipv6_template': env.ipv6_template,
            'link': env.link,
            'min_num_vlan_2': env.min_num_vlan_2,
            'max_num_vlan_2': env.max_num_vlan_2,
            'min_num_vlan_1': env.min_num_vlan_1,
            'max_num_vlan_1': env.max_num_vlan_1,
            'vrf': env.vrf,
            'father_environment': env.id,
            'default_vrf': env.default_vrf.id,
            'configs': confs
        }
        environment = models_env.Ambiente().environment.create_v3(obj)
        log.debug("Environment object: %s" % str(environment))
    return environment


def _create_oobvlans(rack, env_oob, user):

    vlan = None
    for env in env_oob:
        vlan_base = env.min_num_vlan_1
        vlan_number = int(vlan_base) + int(rack_number)
        vlan_name = "VLAN_" + env.ambiente_logico.nome + "_" + rack.nome

        network = dict()
        for config in env.configs:
            network = {
                'new_prefix': str(config.ip_config.new_prefix),
                'network_type': config.ip_config.network_type
            }
        obj = {
            'name': vlan_name,
            'num_vlan': vlan_number,
            'environment': env.id,
            'default_vrf': env.default_vrf.id,
            'vrf': env.vrf,
            'create_networkv4': network,
            'create_networkv6': None
        }
        log.debug("Vlan object: %s" % str(obj))
        vlan = facade_vlan_v3.create_vlan(obj, user)

    return vlan


def rack_environments_vlans(rack_id, user):

    rack = Rack().get_rack(idt=rack_id)

    # get fathers environments
    env_spn = list()
    env_be = list()
    env_fe = list()
    env_oob = list()
    environments = models_env.Ambiente.objects.filter(dcroom=int(rack.dcroom.id))
    for envs in environments:
        if envs.ambiente_logico.nome == "SPINES":
            env_spn.append(envs)
        elif envs.ambiente_logico.nome == "INTERNO-RACK":
            if envs.divisao_dc.nome[:2] == "BE":
                env_be.append(envs)
            elif envs.divisao_dc.nome[:2] == "FE":
                env_fe.append(envs)
        elif envs.ambiente_logico.nome == "HOSTS-CLOUD":
            env_mngtcloud.append(envs)
        elif envs.ambiente_logico.nome[:3] == "OOB":
            env_oob.append(envs)

    # externo:  spine x leaf
    spn_lf_envs_ids = _create_spnlfenv(rack, env_spn)
    _create_spnlfvlans(rack, spn_lf_envs_ids, user)

    # interno:  leaf x leaf (tor)
    _create_fe_envs(rack, env_fe)

    # producao/cloud
    # _create_vlans_cloud(rack, env_mngtcloud, user)

    # redes de gerencia OOB
    _create_oobvlans(rack, env_oob, user)

    rack.__dict__.update(id=rack.id, create_vlan_amb=True)
    rack.save()

    return rack


def api_foreman(rack):


    try:
        NETWORKAPI_FOREMAN_URL = get_variable("foreman_url")
        NETWORKAPI_FOREMAN_USERNAME = get_variable("foreman_username")
        NETWORKAPI_FOREMAN_PASSWORD = get_variable("foreman_password")
        FOREMAN_HOSTS_ENVIRONMENT_ID = get_variable("foreman_hosts_environment_id")
    except ObjectDoesNotExist:
        raise var_exceptions.VariableDoesNotExistException("Erro buscando as variáveis relativas ao Foreman.")

    foreman = Foreman(NETWORKAPI_FOREMAN_URL, (NETWORKAPI_FOREMAN_USERNAME, NETWORKAPI_FOREMAN_PASSWORD), api_version=2)

    # for each switch, check the switch ip against foreman know networks, finds foreman hostgroup
    # based on model and brand and inserts the host in foreman
    # if host already exists, delete and recreate with new information
    for [switch, mac] in [[rack.id_sw1, rack.mac_sw1], [rack.id_sw2, rack.mac_sw2], [rack.id_ilo, rack.mac_ilo]]:
        # Get all foremand subnets and compare with the IP address of the switches until find it
        if mac == None:
            raise RackConfigError(None, rack.nome, ("Could not create entry for %s. There is no mac address." %
                                                    switch.nome))

        ip = buscar_ip(switch.id)
        if ip == None:
            raise RackConfigError(None, rack.nome, ("Could not create entry for %s. There is no management IP." %
                                                    switch.nome))

        switch_cadastrado = 0
        for subnet in foreman.subnets.index()['results']:
            network = IPNetwork(ip + '/' + subnet['mask']).network
            # check if switches ip network is the same as subnet['subnet']['network'] e subnet['subnet']['mask']
            if network.__str__() == subnet['network']:
                subnet_id = subnet['id']
                hosts = foreman.hosts.index(search = switch.nome)['results']
                if len(hosts) == 1:
                    foreman.hosts.destroy(id = hosts[0]['id'])
                elif len(hosts) > 1:
                    raise RackConfigError(None, rack.nome, ("Could not create entry for %s. There are multiple entries "
                                                            "with the sam name." % switch.nome))

                # Lookup foreman hostgroup
                # By definition, hostgroup should be Marca+"_"+Modelo
                hostgroup_name = switch.modelo.marca.nome + "_" + switch.modelo.nome
                hostgroups = foreman.hostgroups.index(search = hostgroup_name)
                if len(hostgroups['results']) == 0:
                    raise RackConfigError(None, rack.nome, "Could not create entry for %s. Could not find hostgroup %s "
                                                           "in foreman." % (switch.nome, hostgroup_name))
                elif len(hostgroups['results'])>1:
                    raise RackConfigError(None, rack.nome, "Could not create entry for %s. Multiple hostgroups %s found"
                                                           " in Foreman." % (switch.nome, hostgroup_name))
                else:
                    hostgroup_id = hostgroups['results'][0]['id']

                host = foreman.hosts.create(host = {'name': switch.nome, 'ip': ip, 'mac': mac,
                                                    'environment_id': FOREMAN_HOSTS_ENVIRONMENT_ID,
                                                    'hostgroup_id': hostgroup_id, 'subnet_id': subnet_id,
                                                    'build': 'true', 'overwrite': 'true'})
                switch_cadastrado = 1

        if not switch_cadastrado:
            raise RackConfigError(None, rack.nome, "Unknown error. Could not create entry for %s in foreman." %
                                  switch.nome)

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
    except ObjectDoesNotExist:
        raise exceptions.RackNumberNotFoundError("Rack id %s nao foi encontrado" % idt)
    except Exception, e:
        log.error(u'Failure to search the Rack.')
        raise exceptions.RackError("Failure to search the Rack. %s" % e)


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