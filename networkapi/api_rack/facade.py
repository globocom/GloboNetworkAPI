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

import ast
import json
import logging
import operator
import re
from django.core.exceptions import ObjectDoesNotExist
from netaddr import IPNetwork
from requests.exceptions import RequestException
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.ambiente import models as models_env
from networkapi.api_environment import facade as facade_env
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.vlan import models as models_vlan
from networkapi.api_vlan.facade import v3 as facade_vlan_v3
from networkapi.equipamento.models import Equipamento, EquipamentoRoteiro
from networkapi.interface.models import Interface, InterfaceNotFoundError
from networkapi.ip.models import IpEquipamento, Ip
from networkapi.rack.models import Rack, Datacenter, DatacenterRooms, RackConfigError, RackError, RackNumberNotFoundError
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.api_rack import serializers as rack_serializers
from networkapi.api_rack import exceptions, autoprovision
from networkapi.system import exceptions as var_exceptions
from networkapi.system.facade import get_value as get_variable
from networkapi.api_rest.exceptions import ValidationAPIException, ObjectDoesNotExistException, NetworkAPIException

if int(get_variable('use_foreman')):
    from foreman.client import Foreman, ForemanException

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

    log.info("Update Fabric Config")
    fabric = DatacenterRooms().get_dcrooms(idt=fabric_id)

    try:
        fabriconfig = ast.literal_eval(fabric.config)
    except:
        fabriconfig = dict()

    fabric_dict = fabric_dict.get("config")

    if fabric_dict.get("Ambiente"):
        if fabriconfig.get("Ambiente"):
            try:
                fabriconfig.get("Ambiente").append(fabric_dict.get("Ambiente"))
            except:
                fabriconfig["Ambiente"] = [fabriconfig.get("Ambiente")]
                fabriconfig.get("Ambiente").append(fabric_dict.get("Ambiente"))
        else:
            fabriconfig["Ambiente"] = [fabric_dict.get("Ambiente")]
    if fabric_dict.get("BGP"):
        fabriconfig["BGP"] = fabric_dict.get("BGP")
    if fabric_dict.get("VLT"):
        fabriconfig["VLT"] = fabric_dict.get("VLT")
    if fabric_dict.get("Gerencia"):
        fabriconfig["Gerencia"] = fabric_dict.get("Gerencia")
    if fabric_dict.get("Channel"):
        fabriconfig["Channel"] = fabric_dict.get("Channel")

    fabric.config = fabriconfig
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
    rack.dcroom = DatacenterRooms().get_dcrooms(idt=rack_dict.get('fabric_id')) if rack_dict.get('fabric_id') else None

    if not rack.nome:
        raise exceptions.InvalidInputException("O nome do Rack não foi informado.")

    rack.save_rack()
    return rack

def update_rack(rack_id, rack):

    try:
        rack_obj = Rack()
        rack_obj = rack_obj.get_rack(idt=rack_id)

        rack_obj.nome = rack.get("name")
        rack_obj.numero = rack.get("number")
        rack_obj.mac_sw1 = rack.get("mac_sw1")
        rack_obj.mac_sw2 = rack.get("mac_sw2")
        rack_obj.mac_ilo = rack.get("mac_ilo")
        rack_obj.id_sw1 = Equipamento().get_by_pk(int(rack.get("id_sw1")))
        rack_obj.id_sw2 = Equipamento().get_by_pk(int(rack.get("id_sw2")))
        rack_obj.id_ilo = Equipamento().get_by_pk(int(rack.get("id_ilo")))
        rack_obj.dcroom = DatacenterRooms().get_dcrooms(idt=rack.get('fabric_id')) if rack.get('fabric_id') \
            else None

        rack_obj.save()

        return rack_obj

    except (exceptions.RackNumberDuplicatedValueError,
            exceptions.RackNameDuplicatedError,
            exceptions.InvalidInputException) as e:
        log.exception(e)
        raise Exception(e)
    except Exception, e:
        log.exception(e)
        raise Exception(e)

def get_rack(fabric_id=None, rack_id=None):

    rack_obj = Rack()

    try:
        if fabric_id:
            rack = rack_obj.get_rack(dcroom_id=fabric_id)
            rack_list = rack_serializers.RackSerializer(rack, many=True).data if rack else list()
        elif rack_id:
            rack = rack_obj.get_rack(idt=rack_id)
            rack_list = [rack_serializers.RackSerializer(rack).data] if rack else list()
        else:
            rack = rack_obj.get_rack()
            rack_list = rack_serializers.RackSerializer(rack, many=True).data if rack else list()

        return rack_list

    except (ObjectDoesNotExist, Exception), e:
        raise Exception(e)

def delete_rack(rack_id):

    rack_obj = Rack()
    rack = rack_obj.get_rack(idt=rack_id)

    error_vlans = list()
    error_envs = list()

    envs_ids = models_env.Ambiente.objects.filter(dcroom=rack.dcroom.id,
                                                  grupo_l3__nome=str(rack.nome)
                                                  ).values_list('id', flat=True)

    log.debug("rack envs. Qtd: %s - Envs: %s" % (str(len(envs_ids)), str(envs_ids)))

    vlans_ids = models_vlan.Vlan.objects.filter(nome__icontains=rack.nome
                                                ).values_list('id', flat=True)

    log.debug("rack vlan. Qtd: %s - VLans: %s" % (str(len(vlans_ids)), str(vlans_ids)))

    for idt in vlans_ids:
        try:
            facade_vlan_v3.delete_vlan(idt)
        except (models_vlan.VlanError,
                models_vlan.VlanErrorV3,
                ValidationAPIException,
                ObjectDoesNotExistException,
                Exception,
                NetworkAPIException), e:
            error_vlans.append({'vlan_id': idt, 'error': e})

    try:
        facade_env.delete_environment(envs_ids)
    except (models_env.AmbienteUsedByEquipmentVlanError,
            models_env.AmbienteError,
            Exception), e:
        error_envs.append({'env_error': e})

    if error_vlans:
        log.debug("Vlans não removidas: %s" % str(error_vlans))
        raise Exception("Vlans não removidas: %s" % str(error_vlans))
    if error_envs:
        log.debug("Envs não removidos: %s" % str(error_envs))
        raise Exception("Envs não removidos: %s" % str(error_envs))

    rack.del_rack()

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
    log.debug("gerar_arquivo_config")

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

    return True

def _create_spnlfenv(rack):
    log.debug("_create_spnlfenv")

    envfathers = models_env.Ambiente.objects.filter(dcroom=int(rack.dcroom.id),
                                                    father_environment__isnull=True,
                                                    grupo_l3__nome=str(rack.dcroom.name),
                                                    ambiente_logico__nome="SPINES")
    log.debug(str(envfathers))

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
                amb_log_dict.nome = amb_log_name
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
                'configs': config,
                'fabric_id': rack.dcroom.id
            }
            try:
                environment_spn_lf = facade_env.create_environment(obj)
                environment_spn_lf_list.append(environment_spn_lf)
            except:
                log.debug("Environment object: %s" % str(obj))
    return environment_spn_lf_list

def _create_spnlfvlans(rack, user):
    log.debug("_create_spnlfvlans")

    spn_lf_envs = models_env.Ambiente.objects.filter(dcroom=int(rack.dcroom.id),
                                                     father_environment__isnull=False,
                                                     grupo_l3__nome=str(rack.dcroom.name),
                                                     ambiente_logico__nome__in=["SPINE01LEAF",
                                                                                "SPINE02LEAF",
                                                                                "SPINE03LEAF",
                                                                                "SPINE04LEAF"])
    log.debug(str(spn_lf_envs))

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
    for env in spn_lf_envs:
        log.debug(str(env))
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
        try:
            facade_vlan_v3.create_vlan(obj, user)
        except:
            log.debug("Vlan object: %s" % str(obj))

def _create_prod_envs(rack, user):
    log.debug("_create_prod_envs")

    prod_envs = models_env.Ambiente.objects.filter(dcroom=int(rack.dcroom.id),
                                                   father_environment__isnull=True,
                                                   grupo_l3__nome=str(rack.dcroom.name),
                                                   ambiente_logico__nome="PRODUCAO"
                                                   ).exclude(divisao_dc__nome="BO_DMZ")

    log.debug(str(prod_envs))

    try:
        id_grupo_l3 = models_env.GrupoL3().get_by_name(rack.nome).id
    except:
        grupo_l3_dict = models_env.GrupoL3()
        grupo_l3_dict.nome = rack.nome
        grupo_l3_dict.save()
        id_grupo_l3 = grupo_l3_dict.id
        pass

    if rack.dcroom.config:
        fabricconfig = rack.dcroom.config
        log.debug(str(type(fabricconfig)))
    else:
        log.debug("sem configuracoes do fabric %s" % str(rack.dcroom.id))
        fabricconfig = list()

    try:
        fabricconfig = json.loads(fabricconfig)
        log.debug("type -ast: %s" % str(type(fabricconfig)))
    except:
        pass

    try:
        fabricconfig = ast.literal_eval(fabricconfig)
        log.debug("config -ast: %s" % str(fabricconfig))
    except:
        pass

    environment = list()
    for env in prod_envs:

        father_id = env.id

        for fab in fabricconfig.get("Ambiente"):
            if int(fab.get("id"))==int(father_id):
                details = fab.get("details")

        config_subnet = list()
        for net in env.configs:
            log.debug(str(net.ip_config.subnet))
            log.debug(str(type(net.ip_config.subnet)))
            cidr = IPNetwork(str(net.ip_config.subnet))
            prefix = int(net.ip_config.new_prefix)
            bloco = list(cidr.subnet(int(prefix)))[int(rack.numero)]
            log.debug(str(details))
            if details[0].get(str(net.ip_config.type)):
                log.debug("if")
                new_prefix = details[0].get(str(net.ip_config.type)).get("new_prefix")
            else:
                new_prefix = 31 if net.ip_config.type=="v4" else 127
            network = {
                'subnet': str(bloco),
                'type': net.ip_config.type,
                'network_type': net.ip_config.network_type.id,
                'new_prefix': new_prefix
            }
            config_subnet.append(network)

        obj = {
            'grupo_l3': id_grupo_l3,
            'ambiente_logico': env.ambiente_logico.id,
            'divisao_dc': env.divisao_dc.id,
            'acl_path': env.acl_path,
            'ipv4_template': env.ipv4_template,
            'ipv6_template': env.ipv6_template,
            'link': env.link,
            'min_num_vlan_2': env.min_num_vlan_1,
            'max_num_vlan_2': env.max_num_vlan_1,
            'min_num_vlan_1': env.min_num_vlan_1,
            'max_num_vlan_1': env.max_num_vlan_1,
            'vrf': env.vrf,
            'father_environment': father_id,
            'default_vrf': env.default_vrf.id,
            'configs': config_subnet,
            'fabric_id': rack.dcroom.id
        }
        environment.append(facade_env.create_environment(obj))
        log.debug("Environment object: %s" % str(environment))

    return environment

def _create_prod_vlans(rack, user):
    log.debug("_create_prod_vlans")

    env = models_env.Ambiente.objects.filter(dcroom=int(rack.dcroom.id),
                                             divisao_dc__nome="BE",
                                             grupo_l3__nome=str(rack.nome),
                                             ambiente_logico__nome="PRODUCAO"
                                             ).uniqueResult()

    log.debug(str(env))

    if rack.dcroom.config:
        fabricconfig = rack.dcroom.config
        log.debug(str(type(fabricconfig)))
    else:
        log.debug("sem configuracoes do fabric %s" % str(rack.dcroom.id))
        fabricconfig = list()

    try:
        fabricconfig = json.loads(fabricconfig)
        log.debug("type -ast: %s" % str(type(fabricconfig)))
    except:
        pass

    try:
        fabricconfig = ast.literal_eval(fabricconfig)
        log.debug("config -ast: %s" % str(fabricconfig))
    except:
        pass

    environment = None
    father_id = env.id
    fabenv = None

    log.debug("debug")
    for fab in fabricconfig.get("Ambiente"):
        log.debug("debug for fab")
        if int(fab.get("id"))==int(env.father_environment.id):
            fabenv = fab.get("details")
    if not fabenv:
        log.debug("Sem configuracoes para os ambientes filhos - BE, BEFE, BEBO, BECA do ambiente id=%s" %str())
        return 0

    log.debug(str(fabenv))
    for amb in fabenv:
        try:
            id_div = models_env.DivisaoDc().get_by_name(amb.get("name")).id
        except:
            div_dict = models_env.DivisaoDc()
            div_dict.nome = amb.get("name")
            div_dict.save()
            id_div = div_dict.id
            pass

        config_subnet = list()
        for net in env.configs:
            for net_dict in amb.get("config"):
                if net_dict.get("type")==net.ip_config.type:
                    cidr = IPNetwork(net.ip_config.subnet)
                    prefixo = net_dict.get("mask")
                    bloco = list(cidr.subnet(int(prefixo)))[-2]
                    network = {
                        'subnet': str(bloco),
                        'type': str(net.ip_config.type),
                        'network_type': int(net.ip_config.network_type.id),
                        'new_prefix': int(net_dict.get("new_prefix"))
                    }
                    config_subnet.append(network)

        obj = {
            'grupo_l3': env.grupo_l3.id,
            'ambiente_logico': env.ambiente_logico.id,
            'divisao_dc': id_div,
            'acl_path': env.acl_path,
            'ipv4_template': env.ipv4_template,
            'ipv6_template': env.ipv6_template,
            'link': env.link,
            'min_num_vlan_2': amb.get("min_num_vlan_1"),
            'max_num_vlan_2': amb.get("max_num_vlan_1"),
            'min_num_vlan_1': amb.get("min_num_vlan_1"),
            'max_num_vlan_1': amb.get("max_num_vlan_1"),
            'vrf': env.vrf,
            'father_environment': father_id,
            'default_vrf': env.default_vrf.id,
            'configs': config_subnet,
            'fabric_id': rack.dcroom.id
        }
        environment = facade_env.create_environment(obj)
        log.debug("Environment object: %s" % str(environment))

    return environment

def _create_lflf_vlans(rack, user):
    log.debug("_create_lflf_vlans")

    env_lf = models_env.Ambiente.objects.filter(dcroom=int(rack.dcroom.id),
                                                father_environment__isnull=True,
                                                grupo_l3__nome=str(rack.dcroom.name),
                                                ambiente_logico__nome="LEAF-LEAF")
    log.debug(str(env_lf))
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

    for env in env_lf:
        env_id = env.id
        vlan_number = int(env.min_num_vlan_1)
        vlan_name = "VLAN_LFxLF_" + env.divisao_dc.nome + "_" + env.grupo_l3.nome

        for net in env.configs:
            bloco = net.ip_config.subnet
            prefix = bloco.split('/')[-1]
            network = {
                'prefix': prefix,
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
        try:
            facade_vlan_v3.create_vlan(obj, user)
        except:
            log.debug("Vlan object: %s" % str(obj))

def _create_oobvlans(rack, user):
    log.debug("_create_oobvlans")

    env_oob = models_env.Ambiente.objects.filter(dcroom=int(rack.dcroom.id),
                                                 divisao_dc__nome="OOB",
                                                 grupo_l3__nome=str(rack.dcroom.name),
                                                 ambiente_logico__nome="GERENCIA").uniqueResult()
    log.debug(str(env_oob))
    vlan = None
    for env in [env_oob]:
        vlan_base = env.min_num_vlan_1
        vlan_number = int(vlan_base) + int(rack.numero)
        vlan_name = "VLAN_" + env.ambiente_logico.nome + "_" + rack.nome

        network = dict()
        for config in env.configs:
            network = {
                'new_prefix': str(config.ip_config.new_prefix),
                'network_type': config.ip_config.network_type.id
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
    log.info("Rack Environments")

    rack = Rack().get_rack(idt=rack_id)
    if rack.create_vlan_amb:
        raise Exception("Os ambientes e Vlans já foram alocados.")

    # spine x leaf
    _create_spnlfenv(rack)
    _create_spnlfvlans(rack, user)

    # leaf x leaf
    _create_lflf_vlans(rack, user)

    # producao/cloud
    _create_prod_envs(rack, user)
    _create_prod_vlans(rack, user)

    # redes de gerencia OOB
    _create_oobvlans(rack, user)

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

        ip = _buscar_ip(switch.id)
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

