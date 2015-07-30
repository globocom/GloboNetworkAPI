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


from django.core.exceptions import ObjectDoesNotExist
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.rack.models import RackAplError, RackConfigError, RackNumberNotFoundError, Rack , RackError, EnvironmentRack
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.equipamento.models import Equipamento, EquipamentoAmbiente
from networkapi.rack.resource.GeraConfig import dic_fe_prod, dic_lf_spn, dic_vlan_core, dic_pods, dic_hosts_cloud
from networkapi.ip.models import NetworkIPv4, NetworkIPv6, Ip
from networkapi.interface.models import Interface, InterfaceNotFoundError
from networkapi.vlan.models import TipoRede, Vlan
from networkapi.ambiente.models import IP_VERSION, ConfigEnvironment, IPConfig, AmbienteLogico, DivisaoDc, GrupoL3, Ambiente
from networkapi.util import destroy_cache_function
from networkapi.filter.models import Filter
from networkapi import settings
import glob
import commands

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
    vlan.ativada = 1
    vlan.acl_valida = 0
    vlan.acl_valida_v6 = 0

    vlan.insert_vlan(user)

    return vlan

def criar_rede_ipv6(user, tipo_rede, variablestochangecore1, vlan):

    tiporede = TipoRede()
    net_id = tiporede.get_by_name(tipo_rede)
    network_type = tiporede.get_by_pk(net_id.id)

    network_ip = NetworkIPv6()
    network_ip.vlan = vlan
    network_ip.network_type = network_type
    network_ip.ambient_vip = None
    network_ip.active = 1
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
    network_ip.save(user)    
 
    return network_ip

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
    network_ip.active = 1

    destroy_cache_function([vlan.id])
    network_ip.save(user)
 
    return network_ip

def criar_ambiente(user, ambientes, ranges, acl_path=None, filter=None):

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

    environment.max_num_vlan_1 = ranges.get('MAX')
    environment.min_num_vlan_1 = ranges.get('MIN')
    environment.max_num_vlan_2 = ranges.get('MAX')
    environment.min_num_vlan_2 = ranges.get('MIN')

    environment.link = " "

    if filter is not None:
        try:
            filter_obj = Filter.objects.get(name__iexact=filter)
        except ObjectDoesNotExist, e:
            filter_obj = None
            pass

    environment.filter = filter_obj

    environment.create(user)

    return environment

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
        raise RackAplError (None, None, "Erro ao inserir os equipamentos")

    # Delete vlan's cache
    destroy_cache_function([rede.vlan_id])
    list_id_equip = []
    list_id_equip.append(equip.id)
    destroy_cache_function(list_id_equip, True)

    return 0

def ambiente_spn_lf(user, rack, environment_list):

    vlans, redes, ipv6 = dic_lf_spn(user, rack.numero)

    divisaoDC = ['BE', 'FE', 'BORDA', 'BORDACACHOS']
    spines = ['01', '02', '03', '04']

    grupol3 = GrupoL3()
    grupol3.nome = rack.nome
    grupol3.save(user)

    ambientes= dict()   
    ambientes['L3']= rack.nome

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

            env = criar_ambiente(user, ambientes, ranges)
            environment_list.append(env)

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

    return environment_list

def ambiente_prod(user, rack, environment_list):

    redes, ipv6 = dic_pods(rack.numero)

    divisao_aclpaths = [['BE','BECLOUD'],['BEFE','BEFE'],['BEBORDA','BEBORDA'],['BECACHOS','BECACHOS']]

    grupol3 = rack.nome
    ambiente_logico = "PRODUCAO"

    ambientes= dict()   
    ambientes['LOG']=ambiente_logico
    ambientes['L3']= grupol3

    ranges=dict()
    hosts=dict()
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

        env = criar_ambiente(user, ambientes, ranges, acl_path, "Servidores")
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

    return environment_list

def ambiente_cloud(user, rack, environment_list):

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
    env = criar_ambiente(user, ambientes, ranges, aclpath, "Servidores")
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
        variables['VLAN_NAME'] = "MNGT_"+amb+"_"+rack.nome
        
        vlan = criar_vlan(user, variables, ambientes)
        #criar rede
        criar_rede(user, "Rede invalida equipamentos", hosts.get(amb), vlan)
        criar_rede_ipv6(user, "Rede invalida equipamentos", ipv6.get(amb), vlan)

    return environment_list

def ambiente_prod_fe(user, rack, environment_list):

    redes, ranges, ipv6 = dic_fe_prod(rack.numero)

    ambientes= dict()
    ambientes['LOG']="PRODUCAO"
    ambientes['L3']= rack.nome
    ambientes['DC']="FE"

    redes['TIPO']= "Rede invalida equipamentos"
    ipv6['TIPO']= "Rede invalida equipamentos"

    acl_path = 'FECLOUD'

    #criar ambiente
    env = criar_ambiente(user, ambientes, ranges, acl_path, "Servidores")
    environment_list.append(env)

    #configuracao dos ambientes
    redes['VERSION']="ipv4"
    config_ambiente(user, redes, ambientes)

    ipv6['VERSION']="ipv6"
    config_ambiente(user, ipv6, ambientes)

    return environment_list

def ambiente_borda(user,rack, environment_list):

    ranges=dict()
    ranges['MAX']=None
    ranges['MIN']=None
    ranges_vlans = dict()
    ranges_vlans['BORDA_DSR_VLAN_MIN']= 366
    ranges_vlans['BORDA_DSR_VLAN_MAX']= 381
    ranges_vlans['BORDA_DMZ_VLAN_MIN']= 382
    ranges_vlans['BORDA_DMZ_VLAN_MAX']= 400
    ranges_vlans['BORDACACHOS_VLAN_MIN']= 401
    ranges_vlans['BORDACACHOS_VLAN_MAX']= 410

    ambientes=dict()   
    ambientes['LOG'] = "PRODUCAO"
    ambientes['L3']= rack.nome
    divisao_aclpaths = [['BORDA_DSR','BORDA-DSR'],['BORDA_DMZ','BORDA-DMZ'],['BORDACACHOS','BORDACACHOS']]

    for item in divisao_aclpaths:
        divisaodc = item[0]
        acl_path = item[1]

        vlan_min = divisaodc+"_VLAN_MIN"
        vlan_max = divisaodc+"_VLAN_MAX"
        ranges['MAX']= ranges_vlans.get(vlan_max)
        ranges['MIN']= ranges_vlans.get(vlan_min)

        ambientes['DC']= divisaodc
        env = criar_ambiente(user, ambientes,ranges, acl_path, "Servidores")
        environment_list.append(env)

    return environment_list

def aplicar(rack):

    path_config = settings.PATH_TO_CONFIG +'*'+rack.nome+'*'
    arquivos = glob.glob(path_config)

    #Get all files and search for equipments of the rack
    for var in arquivos: 
        name_equipaments = var.split('/')[-1][:-4]      
        for nome in name_equipaments:
            #Check if file is config relative to this rack
            if rack.nome in nome:
                #Apply config only in spines. Leaves already have all necessary config in startup
                if "ADD" in nome:
                    #Check if equipment in under maintenance. If so, does not aplly on it
                    try:
                        equip = Equipamento.get_by_name(nome)
                        if not equip.maintenance:
                            (erro, result) = commands.getstatusoutput("/usr/bin/backuper -T acl -b %s -e -i %s -w 300" % (var, nome))
                            if erro:
                                raise RackAplError(None, None, "Falha ao aplicar as configuracoes: %s" %(result))
                    except RackAplError, e:
                        raise e
                    except:
                        #Error equipment not found, do nothing
                        pass

def environment_rack(user, environment_list, rack):

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




class RackAplicarConfigResource(RestResource):

    log = Log('RackAplicarConfigResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to create the configuration file.

        URL: rack/aplicar-config/id_rack
        """
        try:

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

            environment_list = []

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
                network = criar_rede(user, "Ponto a ponto", variablestochangecore1, vlan)
            except:
                raise RackAplError(None, rack.nome, "Erro ao criar a rede da VLAN_SO")
            try:
                #inserir os Core
                inserir_equip(user, variablestochangecore1, network.id)           
                inserir_equip(user, variablestochangecore2, network.id)            
            except:
                raise RackAplError(None, rack.nome, "Erro ao inserir o core 1 e 2")
                
            #######################################################################                   Ambientes

            #BE - SPINE - LEAF
            environment_list = ambiente_spn_lf(user, rack, environment_list)

            #BE - PRODUCAO
            environment_list = ambiente_prod(user, rack, environment_list)

            #BE - Hosts - CLOUD
            environment_list = ambiente_cloud(user, rack, environment_list)
            
            #FE 
            environment_list = ambiente_prod_fe(user, rack, environment_list)

            #Borda
            environment_list = ambiente_borda(user, rack, environment_list)

            #######################################################################                   Backuper

            aplicar(rack)
            environment_rack(user, environment_list, rack)

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
            return self.response_error(379, rack_id)

        except RackError:
            return self.response_error(1)


