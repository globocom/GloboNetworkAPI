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

import re
import json
import logging
from networkapi.equipamento.models import Equipamento, EquipamentoRoteiro
from networkapi.interface.models import Interface, InterfaceNotFoundError
from networkapi.ip.models import Ip, IpEquipamento
from networkapi.rack.models import Rack, Datacenter, DatacenterRooms
from networkapi.system.facade import get_value as get_variable
from networkapi.api_rack import exceptions, serializers
from django.core.exceptions import ObjectDoesNotExist
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
        if not ip_sw==None:
            if regexp.search(ip_sw.networkipv4.vlan.ambiente.ambiente_logico.nome) is not None:
                return str(ip_sw.oct1)+'.'+str(ip_sw.oct2)+'.'+str(ip_sw.oct3)+'.'+str(ip_sw.oct4)

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
            lf1["id"] = rack.id_sw1.id
            lf1["nome"] = rack.id_sw1.nome
            lf1["mac"] = rack.mac_sw1
            lf1["marca"] = rack.id_sw1.modelo.marca.nome
            lf1["modelo"] = rack.id_sw1.modelo.nome
            equips.append(lf1)
            lf2["id"] = rack.id_sw2.id
            lf2["nome"] = rack.id_sw2.nome
            lf2["mac"] = rack.mac_sw2
            lf2["marca"] = rack.id_sw2.modelo.marca.nome
            lf2["modelo"] = rack.id_sw2.modelo.nome
            equips.append(lf2)
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


        dcsigla = "".join([c[0] for c in dcname.split(" ")]) if len(dcname.split(" ")) >= 2 else (dcname[:3])
        radical = "-"+dcsigla+"-"+nome_rack+"-"
        prefixspn = "SPN"
        prefixlf = "LF"
        prefixoob = "OOB"

        # Interface e Roteiro
        for equip in equips:
            try:
                interfaces = Interface.search(equip.get("id"))
                equip["interfaces"] = []
                for interface in interfaces:
                    dic = dict()
                    try:
                        sw = interface.get_switch_and_router_interface_from_host_interface(None)
                        if  (sw.equipamento.nome[:2] in [prefixlf, prefixoob[:2]]):
                            dic["nome"] = sw.equipamento.nome
                            dic["id"] = sw.equipamento.id
                            dic["interface"] =  sw.interface
                            dic["eq_interface"] = interface.interface
                            dic["roteiro"] = buscar_roteiro(sw.equipamento.id, "CONFIGURACAO")
                            equip["interfaces"].append(dic)
                    except:
                        pass
            except:
                raise Exception("Erro ao buscar o roteiro de configuracao ou as interfaces associadas ao equipamento: "
                                "%s." % (equip.get("nome")))
            try:
                equip["roteiro"] = buscar_roteiro(equip.get("id"), "CONFIGURACAO")
                equip["ip_mngt"] = buscar_ip(equip.get("id"))
            except:
                raise Exception("Erro ao buscar os roteiros do equipamento: %s" %(equip.get("nome")))

        try:
            NETWORKAPI_USE_FOREMAN = int(get_variable("use_foreman"))
            NETWORKAPI_FOREMAN_URL = get_variable("foreman_url")
            NETWORKAPI_FOREMAN_USERNAME = get_variable("foreman_username")
            NETWORKAPI_FOREMAN_PASSWORD = get_variable("foreman_password")
            FOREMAN_HOSTS_ENVIRONMENT_ID = get_variable("foreman_hosts_environment_id")
        except ObjectDoesNotExist:
            raise var_exceptions.VariableDoesNotExistException("Erro buscando as variáveis relativas ao Foreman.")

       #begin - Create Foreman entries for rack switches
        if NETWORKAPI_USE_FOREMAN:
            foreman = Foreman(NETWORKAPI_FOREMAN_URL, (NETWORKAPI_FOREMAN_USERNAME, NETWORKAPI_FOREMAN_PASSWORD),
                              api_version=2)

            #for each switch, check the switch ip against foreman know networks, finds foreman hostgroup
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

                switch_cadastrado=0
                for subnet in foreman.subnets.index()['results']:
                    network = IPNetwork(ip+'/'+subnet['mask']).network
                    #check if switches ip network is the same as subnet['subnet']['network'] e subnet['subnet']['mask']
                    if network.__str__() == subnet['network']:
                        subnet_id = subnet['id']
                        hosts = foreman.hosts.index(search=switch_nome)['results']
                        if len(hosts) == 1:
                            foreman.hosts.destroy(id=hosts[0]['id'])
                        elif len(hosts) > 1:
                            raise Exception("Could not create entry for %s. There are multiple "
                                                                    "entries with the same name." % (switch_nome))

                        #Lookup foreman hostgroup
                        #By definition, hostgroup should be Marca+"_"+Modelo
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
                        switch_cadastrado=1
                if not switch_cadastrado:
                    raise Exception("Unknown error. Could not create entry for %s in foreman." % (switch_nome))

        #end - Create Foreman entries for rack switches

        var1 = autoprovision_splf(equips)
        var2 = autoprovision_coreoob(equips)

        if var1 and var2:
            return True

        return False



#################################################### old
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


