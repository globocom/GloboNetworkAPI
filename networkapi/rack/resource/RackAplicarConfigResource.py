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
from networkapi.rack.resource.GeraConfig import dic_fe_prod, dic_lf_spn, dic_vlan_core, dic_pods, dic_hosts_cloud
from networkapi.ip.models import NetworkIPv4, NetworkIPv6, Ip, IpEquipamento
from networkapi.interface.models import Interface, InterfaceNotFoundError
from networkapi.vlan.models import TipoRede, Vlan
from networkapi.ambiente.models import IP_VERSION, ConfigEnvironment, IPConfig, AmbienteLogico, DivisaoDc, GrupoL3, AmbienteError, Ambiente, AmbienteNotFoundError
from networkapi.settings import NETWORKIPV4_CREATE, NETWORKIPV6_CREATE, VLAN_CREATE
from networkapi.util import destroy_cache_function
from networkapi import settings

def get_core_name(rack):

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

def criar_vlan(user, variablestochangecore1, ambientes):

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

def criar_rede_ipv6(user, tipo_rede, variablestochangecore1, vlan):

    tiporede = TipoRede()
    net_id = tiporede.get_by_name(tipo_rede)
    network_type = tiporede.get_by_pk(net_id.id)

    network_ip = NetworkIPv6()
    network_ip.vlan = vlan
    network_ip.network_type = network_type
    network_ip.ambient_vip = None
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
    
    #destroy_cache_function([vlan.id])
    network_ip.save(user)    

    #ativar a rede
    # Make command
    command = NETWORKIPV6_CREATE % int(network_ip.id)
    code, stdout, stderr = exec_script(command)
    if code == 0:
        # Change column 'active = 1'
        net = NetworkIPv6.get_by_pk(network_ip.id)
        net.activate(user)
    else:
        return self.response_error(2, stdout + stderr)
 
    return network_ip.id

def criar_rede(user, tipo_rede, variablestochangecore1, vlan):

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

def criar_ambiente(user, ambientes, ranges):

    #ambiente cloud
    environment = Ambiente()
    environment.grupo_l3 = GrupoL3()
    environment.ambiente_logico = AmbienteLogico()
    environment.divisao_dc = DivisaoDc()

    environment.grupo_l3.id = environment.grupo_l3.get_by_name(ambientes.get('L3')).id
    environment.ambiente_logico.id = environment.ambiente_logico.get_by_name(ambientes.get('LOG')).id
    environment.divisao_dc.id = environment.divisao_dc.get_by_name(ambientes.get('DC')).id

    environment.acl_path = None
    environment.ipv4_template = None
    environment.ipv6_template = None

    environment.max_num_vlan_1 = ranges.get('MAX')
    environment.min_num_vlan_1 = ranges.get('MIN')
    environment.max_num_vlan_2 = ranges.get('MAX')
    environment.min_num_vlan_2 = ranges.get('MIN')

    environment.link = " "

    environment.create(user)

def config_ambiente(user, hosts, ambientes):
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

    ip_config.save(user)

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

    config_environment.save(user)

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

def ambiente_spn_lf(user, rack):

    vlans, redes, ipv6 = dic_lf_spn(user, rack.numero)

    divisaoDC = ['BE', 'FE', 'BORDA', 'BORDACACHOS']
    spines = ['01', '02', '03', '04']

    grupol3 = GrupoL3()
    grupol3.nome = "RACK_"+rack.nome
    grupol3.save(user)

    ambientes= dict()   
    ambientes['L3']= "RACK_"+rack.nome

    ranges=dict()
    hosts=dict()
    hosts['TIPO']= "Ponto a ponto"
    ipv6['TIPO']= "Ponto a ponto"

    for divisaodc in divisaoDC: 
        ambientes['DC']=divisaodc
        for i in spines: 

            ambientes['LOG']= "SPINE"+i+"LEAF"

            #cadastro dos ambientes
            vlan_name = "VLAN"+divisaodc+"LEAF"
            ranges['MAX'] = vlans.get(vlan_name)[rack.numero][int(i[1])-1]+119 
            ranges['MIN'] = vlans.get(vlan_name)[rack.numero][int(i[1])-1]

            criar_ambiente(user, ambientes, ranges)

            #configuracao do ambiente
            rede = "SPINE"+i[1]+"ipv4"
            hosts['REDE'] = redes.get(rede)
            hosts['PREFIX'] = "31"

            ambientes['LOG']= "SPINE"+i+"LEAF"
            hosts['VERSION']="ipv4"
            config_ambiente(user, hosts, ambientes)

            rede_ipv6 = "SPINE"+i[1]+"ipv6"
            ipv6['REDE']= ipv6.get(rede_ipv6)
            ipv6['PREFIX']="127"
            ipv6['VERSION']="ipv6"
            config_ambiente(user, ipv6, ambientes)

def ambiente_prod(user, rack):

    redes, ipv6 = dic_pods(rack.numero)

    divisaoDC = ['BE', 'BEFE', 'BEBORDA', 'BECACHOS']
    grupol3 = "RACK_"+rack.nome
    ambiente_logico = "PRODUCAO"

    ambientes= dict()   
    ambientes['LOG']=ambiente_logico
    ambientes['L3']= grupol3

    ranges=dict()
    hosts=dict()
    hosts['TIPO']= "Rede invalida equipamentos"
    ipv6['TIPO']= "Rede invalida equipamentos"

    for divisaodc in divisaoDC:

        ambientes['DC']=divisaodc

        #criar ambiente
        vlan_min = divisaodc+"_VLAN_MIN"
        vlan_max = divisaodc+"_VLAN_MAX"
        ranges['MAX']= redes.get(vlan_max)
        ranges['MIN']= redes.get(vlan_min)

        criar_ambiente(user, ambientes, ranges)

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

def ambiente_cloud(user, rack):

    hosts, ipv6 = dic_hosts_cloud(rack.numero)

    ambientes= dict()
    ambientes['DC']="BE"
    ambientes['LOG']="MNGT_NETWORK"
    ambientes['L3']= "RACK_"+rack.nome    
 
    ranges=dict()
    ranges['MAX']= hosts.get('VLAN_MNGT_FILER')
    ranges['MIN']=hosts.get('VLAN_MNGT_BE')

    #criar ambiente cloud
    criar_ambiente(user, ambientes, ranges)

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
        variables['VLAN_NAME'] = "MNGT_"+amb+"_"+rack.nome
        
        vlan = criar_vlan(user, variables, ambientes)
        #criar rede
        criar_rede(user, "Rede invalida equipamentos", hosts.get(amb), vlan)
        criar_rede_ipv6(user, "Rede invalida equipamentos", ipv6.get(amb), vlan)

def ambiente_prod_fe(user, rack):

    redes, ranges, ipv6 = dic_fe_prod(rack.numero)

    ambientes= dict()
    ambientes['LOG']="PRODUCAO"
    ambientes['L3']= "RACK_"+rack.nome
    ambientes['DC']="FE"

    redes['TIPO']= "Rede invalida equipamentos"
    ipv6['TIPO']= "Rede invalida equipamentos"

    #criar ambiente
    criar_ambiente(user, ambientes, ranges)

    #configuracao dos ambientes
    redes['VERSION']="ipv4"
    config_ambiente(user, redes, ambientes)

    ipv6['VERSION']="ipv6"
    config_ambiente(user, ipv6, ambientes)

def ambiente_borda(user,rack):

    redes, ipv6 = dic_borda(rack.numero)

    ranges=dict()
    ranges['MAX']=None
    ranges['MIN']=None

    ambientes=dict()   
    ambientes['LOG'] = "PRODUCAO"
    ambientes['L3']= "RACK_"+rack.nome
    amb_list= ['BORDA_DSR','BORDA_DMZ', 'BORDACACHOS']

    for amb in amb_list:
        ambientes['DC']=amb
        criar_ambiente(user, ambientes,ranges)

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
            if not rack.config:
                raise RackAplError(None, rack.nome, "Os arquivos de configuracao devem ser gerados antes.")

            if rack.create_vlan_amb:
                raise RackAplError(None, rack.nome, "As vlans, redes e ambientes ja foram criados.")

            #variaveis
            name_core1, name_core2 =  get_core_name(rack)
            
            variablestochangecore1 = {}
            variablestochangecore2 = {}
            variablestochangecore1 = dic_vlan_core(variablestochangecore1, rack.numero, name_core1, rack.nome)
            variablestochangecore2 = dic_vlan_core(variablestochangecore2, rack.numero, name_core2, rack.nome)

            #######################################################################           VLAN Gerencia SO
            ambientes=dict()
            ambientes['DC']=settings.DIVISAODC_MGMT
            ambientes['LOG']=settings.AMBLOG_MGMT
            ambientes['L3']=settings.GRPL3_MGMT
    
            try: 
                #criar e ativar a vlan
                vlan = criar_vlan(user, variablestochangecore1, ambientes)
            except:
                raise RackAplError(None, rack.nome, "Erro ao criar a VLAN_SO.")
            try:
                #criar e ativar a rede
                rede_id = criar_rede(user, "Ponto a ponto", variablestochangecore1, vlan)
            except:
                raise RackAplError(None, rack.nome, "Erro ao criar a rede da VLAN_SO")
            try:
                #inserir os Core
                inserir_equip(user, variablestochangecore1, rede_id)           
                inserir_equip(user, variablestochangecore2, rede_id)            
            except:
                raise RackAplError(None, rack.nome, "Erro ao inserir o core 1 e 2")
                
            #######################################################################                  Ambientes

            #BE - SPINE - LEAF
            ambiente_spn_lf(user, rack)

            #BE - PRODUCAO
            ambiente_prod(user, rack)            

            #BE - Hosts - CLOUD
            ambiente_cloud(user, rack)
            
            #FE 
            ambiente_prod_fe(user, rack)

            #######################################################################   Atualizar flag na tabela

            rack.__dict__.update(id=rack.id, create_vlan_amb=True)
            rack.save(user)
            
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


