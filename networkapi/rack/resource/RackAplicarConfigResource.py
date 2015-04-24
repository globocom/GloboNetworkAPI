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


from netaddr import *
from django.forms.models import model_to_dict
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.rack.models import RackAplError, RackConfigError, RackNumberNotFoundError, RackNumberDuplicatedValueError, Rack , RackError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.infrastructure.script_utils import exec_script
from networkapi.infrastructure.ipaddr import IPNetwork, IPv6Network, IPv4Network
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.equipamento.models import Equipamento, EquipamentoRoteiro
from networkapi.distributedlock import distributedlock, LOCK_RACK
from networkapi.rack.resource.GeraConfig import dic_lf_spn, dic_vlan_core
from networkapi.ip.models import NetworkIPv4, Ip, IpEquipamento
from networkapi.interface.models import Interface, InterfaceNotFoundError
from networkapi.vlan.models import TipoRede, Vlan
from networkapi.ambiente.models import IP_VERSION, ConfigEnvironment, IPConfig, AmbienteLogico, DivisaoDc, GrupoL3, AmbienteError, Ambiente, AmbienteNotFoundError
from networkapi.settings import NETWORKIPV4_CREATE, VLAN_CREATE
from networkapi.util import destroy_cache_function


def get_core_name(rack):

    name_core1 = None
    name_core2 = None

    try:
        interfaces2 = Interface.search(rack.id_ilo.id)
        for interface2 in interfaces2:
            sw = interface2.get_switch_and_router_interface_from_host_interface(None)
            if sw.equipamento.nome.split('-')[0]=='OOB':
                if sw.equipamento.nome.split('-')[2]=='01':
                    name_core1 = sw.equipamento.nome
                elif sw.equipamento.nome.split('-')[2]=='02':
                    name_core2 = sw.equipamento.nome
    except InterfaceNotFoundError:
        raise RackAplError(None,rack.nome,"Erro ao buscar os nomes do Core associado ao Switch de gerencia.")

    return name_core1, name_core2



def criar_vlan(user, variablestochangecore1):

    #get environment
    ambiente = Ambiente()
    divisaodc = DivisaoDc()
    divisaodc = divisaodc.get_by_name("NA")
    ambiente_log = AmbienteLogico()
    ambiente_log = ambiente_log.get_by_name("NA")
    ambiente = ambiente.search(divisaodc.id, ambiente_log.id)
    for  amb in ambiente:
        if amb.grupo_l3.nome=="REDENOVODC":
            id_ambiente = amb

    # set vlan
    vlan = Vlan()
    vlan.acl_file_name = None
    vlan.acl_file_name_v6 = None
    vlan.num_vlan = variablestochangecore1.get("VLAN_SO")
    vlan.nome = variablestochangecore1.get("VLAN_NAME")
    vlan.descricao = ""
    vlan.ambiente = id_ambiente
    vlan.ativada = 0
    vlan.acl_valida = 0
    vlan.acl_valida_v6 = 0

    vlan.insert_vlan(user)

    #ativar a vlan
    vlan_command = VLAN_CREATE % int(vlan.id)
    code, stdout, stderr = exec_script(vlan_command)
    if code == 0:
        vlan.activate(user)
    else:
        return self.response_error(2, stdout + stderr)

    return vlan


def criar_rede(user, variablestochangecore1, vlan):

    tiporede = TipoRede()
    net_id = tiporede.get_by_name("Ponto a ponto")
    network_type = tiporede.get_by_pk(net_id.id)

    network_ip = NetworkIPv4()
    network_ip.oct1, network_ip.oct2, network_ip.oct3, network_ip.oct4 = str(variablestochangecore1["REDE_IP"]).split('.')
    network_ip.block = variablestochangecore1["REDE_MASK"]
    network_ip.mask_oct1, network_ip.mask_oct2, network_ip.mask_oct3, network_ip.mask_oct4 = variablestochangecore1["NETMASK"].split('.')
    network_ip.broadcast = variablestochangecore1["BROADCAST"]
    network_ip.vlan = vlan
    network_ip.network_type = network_type
    network_ip.ambient_vip = None

    destroy_cache_function([vlan.id])
    network_ip.save(user)

    #ativar a rede
    # Make command
    command = NETWORKIPV4_CREATE % int(network_ip.id)
    code, stdout, stderr = exec_script(command)
    if code == 0:
        # Change column 'active = 1'
        net = NetworkIPv4.get_by_pk(network_ip.id)
        net.activate(user)
    else:
        return self.response_error(2, stdout + stderr)
 
    return network_ip.id


def inserir_equip(user, variablestochangecore, rede_id):
    
    ip = Ip()    
    ip.descricao = None
    ip.oct1, ip.oct2, ip.oct3, ip.oct4 = str(variablestochangecore["IPCORE"]).split('.')
    equip = Equipamento.get_by_name(variablestochangecore["EQUIP_NAME"])
    rede = NetworkIPv4.get_by_pk(rede_id)
    ip.save_ipv4(equip.id, user, rede)

    if ip.id is None:
        return self.response_error(2, stdout + stderr)

    # Delete vlan's cache
    destroy_cache_function([rede.vlan_id])
    list_id_equip = []
    list_id_equip.append(equip.id)
    destroy_cache_function(list_id_equip, True)

    return 0


def configurar_ambiente(user, rack):

    vlans, redes = dic_lf_spn(user, rack.numero)

    grupol3 = GrupoL3()
    grupol3.nome = "RACK_"+rack.nome
    grupol3.save(user)

    divisaoDC = ['BE', 'FE', 'BORDA', 'BORDACACHOS']
    amb_id = dict()

    #cadastro dos ambientes
    for divisaodc in divisaoDC: 
        environment = Ambiente() 
        environment.grupo_l3 = GrupoL3() 
        environment.ambiente_logico = AmbienteLogico() 
        environment.divisao_dc = DivisaoDc() 
        environment.grupo_l3.id = grupol3.id
        environment.ambiente_logico.id = environment.ambiente_logico.get_by_name("SPINELEAF").id 
        environment.divisao_dc.id = environment.divisao_dc.get_by_name(divisaodc).id
        environment.acl_path = None 
        environment.ipv4_template = None
        environment.ipv6_template = None 
        vlan_name = "VLAN"+divisaodc+"LEAF"
        environment.max_num_vlan_1 = vlans.get(divisaodc)[0] 
        environment.min_num_vlan_1 = vlans.get(divisaodc)[1] - 1
        environment.max_num_vlan_2 = vlans.get(divisaodc)[0] 
        environment.min_num_vlan_2 = vlans.get(divisaodc)[1] - 1
        environment.link = None 
 
        environment.create(user)
        
        amb_id[divisaodc] = environment.id


    #configuracao dos ambientes
    subSPINE = ["subSPINE1ipv4", "subSPINE2ipv4", "subSPINE3ipv4", "subSPINE4ipv4"]
    for divisaodc in divisaoDC:
        for sub in subSPINE:
            ip_config = IPConfig()
            ip_config.subnet = str(redes.get(sub)[rack.numero])
            ip_config.new_prefix = "31"
            ip_config.type = IP_VERSION.IPv4[0]
            tiporede = TipoRede()
            tipo = tiporede.get_by_name("Ponto a ponto")
            ip_config.network_type = tipo

            ip_config.save(user)

            config_environment = ConfigEnvironment()
            config_environment.environment = Ambiente().get_by_pk(amb_id.get(divisaodc))
            config_environment.ip_config = ip_config

            config_environment.save(user)

    #raise RackAplError(None, None, amb_id)


class RackAplicarConfigResource(RestResource):

    log = Log('RackAplicarConfigResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to create the configuration file.

        URL: rack/aplicar-config/id_rack
        """
        try:

            self.log.info("APLICAR")

            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            rack_id = kwargs.get('id_rack')
            rack = Rack()
            rack = rack.get_by_pk(rack_id)

            #Validar configuracao
            if not rack.config_sw1:
                raise RackAplError(None, rack.nome, "Os arquivos de configuracao devem ser gerados antes.")

            #variaveis
            name_core1, name_core2 =  get_core_name(rack)
            """
            variablestochangecore1 = {}
            variablestochangecore2 = {}
            variablestochangecore1 = dic_vlan_core(variablestochangecore1, rack.numero, name_core1, rack.nome)
            variablestochangecore2 = dic_vlan_core(variablestochangecore2, rack.numero, name_core2, rack.nome)

            #VLAN Gerencia SO
            try: 
                #criar e ativar a vlan
                vlan = criar_vlan(user, variablestochangecore1)
            except:
                raise RackAplError(None, rack.nome, "Erro ao criar a VLAN_SO.")
            try:
                #criar e ativar a rede
                rede_id = criar_rede(user, variablestochangecore1, vlan)
            except:
                raise RackAplError(None, rack.nome, "Erro ao criar a rede da VLAN_SO")
            try:
                #inserir os Core
                inserir_equip(user, variablestochangecore1, rede_id)           
                inserir_equip(user, variablestochangecore2, rede_id)            
            except:
                raise RackAplError(None, rack.nome, "Erro ao inserir o core 1 e 2")
            """
            #ambientes
            #BE - SPINE - LEAF
            configurar_ambiente(user, rack)
            
            #Atualizar flag na tabela
            #rack.__dict__.update(id=rack.id, create_vlan_amb=True)
            #rack.save(user)
            
            success_map = dict()
            success_map['rack_conf'] = True
            map = dict()
            map['sucesso'] = success_map

            return self.response(dumps_networkapi(map))

        except RackConfigError, e:
            return self.response_error(382, e.param, e.value)

        except RackAplError, e:
            return self.response_error(383, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RackNumberNotFoundError:
            return self.response_error(379, id_rack)

        except RackError:
            return self.response_error(1)


