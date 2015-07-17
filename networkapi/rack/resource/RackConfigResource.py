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


from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.rack.models import RackConfigError, RackNumberNotFoundError, Rack , RackError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.equipamento.models import EquipamentoRoteiro
from networkapi.interface.models import Interface, InterfaceNotFoundError
from networkapi.rack.resource.GeraConfig import autoprovision_splf, autoprovision_coreoob
from networkapi.ip.models import Ip, IpEquipamento

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

    ip_sw=None

    ips = IpEquipamento()
    ips = ips.list_by_equip(id_sw)

    for ip in ips:
        ip_sw = Ip.get_by_pk(ip.ip.id)

    if not ip_sw==None:
        ip_sw = str(ip_sw.oct1)+'.'+str(ip_sw.oct2)+'.'+str(ip_sw.oct3)+'.'+str(ip_sw.oct4)

    return ip_sw

def gera_config(rack):

    num_rack=None
    id_lf1=None
    name_lf1=None
    id_lf2=None
    name_lf2=None
    id_oob=None
    id_core1=None
    id_core2=None

    name_oob=None
    name_sp1=None   
    name_sp2=None   
    name_sp3=None   
    name_sp4=None   
    name_core1=None
    name_core2=None

    int_sp1=None
    int_sp2=None   
    int_sp3=None   
    int_sp4=None   
    int_lf1_sp1=None   
    int_lf1_sp2=None   
    int_lf2_sp3=None   
    int_lf2_sp4=None   

    ip_mgmtlf1=None
    ip_mgmtlf2=None
    ip_mgmtoob=None

    int_oob_mgmtlf1=None
    int_oob_mgmtlf2=None
    int_oob_core1=None  
    int_oob_core2=None  
    int_core1_oob=None  
    int_core2_oob=None  


    #Equipamentos
    num_rack = rack.numero
    try:
        id_lf1 = rack.id_sw1.id
        name_lf1 = rack.id_sw1.nome
        id_lf2 = rack.id_sw2.id
        name_lf2 = rack.id_sw2.nome
        id_oob = rack.id_ilo.id
        name_oob = rack.id_ilo.nome
    except:
        raise RackConfigError(None,rack.nome,"Erro: Rack incompleto.")


    #Interface leaf01
    try:
        interfaces = Interface.search(id_lf1)
        for interface in interfaces:
            try: 
                sw = interface.get_switch_and_router_interface_from_host_interface(None)
                if sw.equipamento.nome.split('-')[2]=='01' or sw.equipamento.nome.split('-')[2]=='1': 
                    int_lf1_sp1 = interface.interface
                    name_sp1 = sw.equipamento.nome
                    id_sp1 = sw.equipamento.id
                    int_sp1 =  sw.interface
                elif sw.equipamento.nome.split('-')[2]=='02' or sw.equipamento.nome.split('-')[2]=='2':
                    int_lf1_sp2 = interface.interface
                    name_sp2 = sw.equipamento.nome
                    id_sp2 = sw.equipamento.id
                    int_sp2 =  sw.interface 
                elif sw.equipamento.nome.split('-')[0]=='OOB':
                    int_oob_mgmtlf1 = sw.interface
            except:
                pass
    except InterfaceNotFoundError:
        raise RackConfigError(None,rack.nome,"Erro ao buscar as interfaces associadas ao Leaf 01.")

    if int_sp1==None or int_sp2==None or int_oob_mgmtlf1==None:
        raise RackConfigError(None,rack.nome,"Erro: As interfaces do Leaf01 nao foram cadastradas.")  

    #Interface leaf02
    try:
        interfaces1 = Interface.search(id_lf2)
        for interface1 in interfaces1:
            try:
                sw = interface1.get_switch_and_router_interface_from_host_interface(None)
                if sw.equipamento.nome.split('-')[2]=='03' or sw.equipamento.nome.split('-')[2]=='3':
                    int_lf2_sp3 = interface1.interface
                    name_sp3 = sw.equipamento.nome
                    id_sp3 = sw.equipamento.id
                    int_sp3 =  sw.interface
                elif sw.equipamento.nome.split('-')[2]=='04' or sw.equipamento.nome.split('-')[2]=='4':
                    int_lf2_sp4 = interface1.interface
                    name_sp4 = sw.equipamento.nome
                    id_sp4 = sw.equipamento.id
                    int_sp4 =  sw.interface
                elif sw.equipamento.nome.split('-')[0]=='OOB':
                    int_oob_mgmtlf2 = sw.interface
            except:
                pass
    except InterfaceNotFoundError:
        raise RackConfigError(None,rack.nome,"Erro ao buscar as interfaces associadas ao Leaf 02.")

    if int_sp3==None or int_sp4==None or int_oob_mgmtlf2==None:
        raise RackConfigError(None,rack.nome,"Erro: As interfaces do Leaf02 nao foram cadastradas.")

    #Interface OOB
    try:
        interfaces2 = Interface.search(id_oob)
        for interface2 in interfaces2:
            try:
                sw = interface2.get_switch_and_router_interface_from_host_interface(None)
                if sw.equipamento.nome.split('-')[0]=='OOB':
                    if sw.equipamento.nome.split('-')[2]=='01' or sw.equipamento.nome.split('-')[2]=='1':
                        int_oob_core1 = interface2.interface
                        name_core1 = sw.equipamento.nome
                        int_core1_oob =  sw.interface
                        id_core1 = sw.equipamento.id
                    elif sw.equipamento.nome.split('-')[2]=='02' or sw.equipamento.nome.split('-')[2]=='2':
                        int_oob_core2 = interface2.interface
                        name_core2 = sw.equipamento.nome
                        int_core2_oob =  sw.interface
                        id_core2 = sw.equipamento.id
            except:
                pass 
    except InterfaceNotFoundError:
        raise RackConfigError(None,rack.nome,"Erro ao buscar as interfaces associadas ao Switch de gerencia.")

    if int_oob_core1==None or int_core1_oob==None or int_oob_core2==None or int_core2_oob==None:
        raise RackConfigError(None,rack.nome,"Erro: As interfaces do Switch de gerencia nao foram cadastradas.")

    #Roteiro LF01
    try:
        FILEINLF1 = buscar_roteiro(id_lf1, "CONFIGURACAO")
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do Leaf 01.")

   #Roteiro LF02
    try:
        FILEINLF2 = buscar_roteiro(id_lf2, "CONFIGURACAO")    
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do Leaf 02.")

    #Roteiro SPN01
    try:
        FILEINSP1 = buscar_roteiro(id_sp1, "CONFIGURACAO")    
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do Spine 01.")

    #Roteiro SPN01
    try:
        FILEINSP1 = buscar_roteiro(id_sp1, "CONFIGURACAO")    
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do Spine 01.")

    #Roteiro SPN02
    try:
        FILEINSP2 = buscar_roteiro(id_sp2, "CONFIGURACAO")    
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do Spine 02.")

    #Roteiro SPN03
    try:
        FILEINSP3 = buscar_roteiro(id_sp3, "CONFIGURACAO")    
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do Spine 03.")

    #Roteiro SPN04
    try:
        FILEINSP4 = buscar_roteiro(id_sp4, "CONFIGURACAO")    
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do Spine 04.")

    #Roteiro Core 01
    try:
        FILEINCR1 = buscar_roteiro(id_core1, "CONFIGURACAO")    
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do Core 01.")

    #Roteiro Core 02
    try:
        FILEINCR2 = buscar_roteiro(id_core2, "CONFIGURACAO")    
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do Core 02.")

    #Roteiro OOB
    try:
        FILEINOOB = buscar_roteiro(id_oob, "CONFIGURACAO")    
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do switch de gerencia.")

    #Ip LF01
    try:
        ip_mgmtlf1 = buscar_ip(id_lf1)
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o ip de gerencia do leaf 01.")

    #Ip LF02
    try:
        ip_mgmtlf2 = buscar_ip(id_lf2)
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o ip de gerencia do leaf 02.")

    #Ip OOB
    try:
        ip_mgmtoob = buscar_ip(id_oob)
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o ip de gerencia do oob.")

    var1 = autoprovision_splf(num_rack, FILEINLF1, FILEINLF2, FILEINSP1, FILEINSP2, FILEINSP3, FILEINSP4, name_lf1, name_lf2, name_oob, name_sp1, name_sp2, name_sp3, name_sp4, ip_mgmtlf1, ip_mgmtlf2, int_oob_mgmtlf1, int_oob_mgmtlf2, int_sp1, int_sp2, int_sp3, int_sp4, int_lf1_sp1, int_lf1_sp2, int_lf2_sp3, int_lf2_sp4)

    var2 = autoprovision_coreoob(num_rack, FILEINCR1, FILEINCR2, FILEINOOB, name_core1, name_core2, name_oob, name_lf1, name_lf2, ip_mgmtoob, int_oob_core1, int_oob_core2, int_core1_oob, int_core2_oob )

    if var1 and var2:
        return True

    return False

class RackConfigResource(RestResource):

    log = Log('RackConfigResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Treat requests POST to create the configuration file.

        URL: rack/gerar-arq-config/id_rack
        """
        try:
            self.log.info("CONFIG")

            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            rack_id = kwargs.get('id_rack')
            rack = Rack()
            rack = rack.get_by_pk(rack_id)
            var = False

            #Chama o script para gerar os arquivos de configuracao
            var = gera_config(rack)

            rack.__dict__.update(id=rack_id, config=var)
            rack.save(user) 

            success_map = dict()
            success_map['rack_conf'] = var
            map = dict()
            map['sucesso'] = success_map
                        
            return self.response(dumps_networkapi(map))


        except RackConfigError, e:
            return self.response_error(382, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RackNumberNotFoundError:
            return self.response_error(379, id_rack)

        except RackError:
            return self.response_error(1)

        except InterfaceNotFoundError:
            return self.response_error(141)
