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


from django.forms.models import model_to_dict
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.rack.models import RackConfigError, RackNumberNotFoundError, RackNumberDuplicatedValueError, Rack , RackError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.equipamento.models import Equipamento, EquipamentoRoteiro
from networkapi.interface.models import Interface, InterfaceNotFoundError
from networkapi.distributedlock import distributedlock, LOCK_RACK
from networkapi.rack.resource.GeraConfig import autoprovision_splf, autoprovision_coreoob
from networkapi.ip.models import Ip, IpEquipamento

def gera_config(rack):

    num_rack=None
    id_lf1=None
    name_lf1=None
    id_lf2=None
    name_lf2=None
    id_oob=None

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

    roteiro_leaf=None   
    roteiro_spine=None
    roteiro_core=None

    ip_mgmtlf1=None
    ip_mgmtlf2=None

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
                if sw.equipamento.nome.split('-')[2]=='1': 
                    int_lf1_sp1 = interface.interface
                    name_sp1 = sw.equipamento.nome
                    id_spn1 = sw.equipamento.id
                    int_sp1 =  sw.interface
                elif sw.equipamento.nome.split('-')[2]=='2':
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
                if sw.equipamento.nome.split('-')[2]=='3':
                    int_lf2_sp3 = interface1.interface
                    name_sp3 = sw.equipamento.nome
                    id_spn3 = sw.equipamento.id
                    int_sp3 =  sw.interface
                elif sw.equipamento.nome.split('-')[2]=='4':
                    int_lf2_sp4 = interface1.interface
                    name_sp4 = sw.equipamento.nome
                    id_spn4 = sw.equipamento.id
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
                    if sw.equipamento.nome.split('-')[2]=='01':
                        int_oob_core1 = interface2.interface
                        name_core1 = sw.equipamento.nome
                        int_core1_oob =  sw.interface
                    elif sw.equipamento.nome.split('-')[2]=='02':
                        int_oob_core2 = interface2.interface
                        name_core2 = sw.equipamento.nome
                        int_core2_oob =  sw.interface
            except:
                pass 
    except InterfaceNotFoundError:
        raise RackConfigError(None,rack.nome,"Erro ao buscar as interfaces associadas ao Switch de gerencia.")

    if int_oob_core1==None or int_core1_oob==None or int_oob_core2==None or int_core2_oob==None:
        raise RackConfigError(None,rack.nome,"Erro: As interfaces do Switch de gerencia nao foram cadastradas.")

    #Roteiro LF
    try:
        rot_equip = EquipamentoRoteiro.search(None, id_lf1)
        for rot in rot_equip:
            if (rot.roteiro.tipo_roteiro.tipo=="CONFIGURACAO"):
                roteiro_leaf = rot.roteiro.roteiro
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do Leaf.")

    if roteiro_leaf==None:
        raise RackConfigError(None,rack.nome,"Erro: O Roteiro do Leaf nao esta cadastrado")

    FILEINLF = roteiro_leaf.lower()+".txt"


    #Roteiro SPN
    try:
        rot_equip2 = EquipamentoRoteiro.search(None, id_spn1)
        for rot2 in rot_equip2:
            if (rot2.roteiro.tipo_roteiro.tipo=="CONFIGURACAO"):
                roteiro_spine = rot2.roteiro.roteiro
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do Spine.")

    if roteiro_spine==None:
        raise RackConfigError(None,rack.nome,"Erro: O Roteiro do spine nao esta cadastrado")

    FILEINSP = roteiro_spine.lower()+".txt"

    #Roteiro Core
    try:
        rot_core = EquipamentoRoteiro.search(None, id_oob)
        for rot3 in rot_core:
            if (rot3.roteiro.tipo_roteiro.tipo=="CONFIGURACAO"):
                roteiro_core = rot3.roteiro.roteiro
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o roteiro do switch de gerencia.")

    if roteiro_core==None:
        raise RackConfigError(None,rack.nome,"Erro: O Roteiro do switch de gerencia nao esta cadastrado")

    FILEINCR = roteiro_core.lower()+".txt"


    #Ip LF
    try:
        ipLF = IpEquipamento()
        ips = ipLF.list_by_equip(id_lf1)
        for ip in ips:
            ip_mgmtlf1 = Ip.get_by_pk(ip.ip.id)
        if not ip_mgmtlf1==None:
            ip_mgmtlf1 = str(ip_mgmtlf1.oct1)+'.'+str(ip_mgmtlf1.oct2)+'.'+str(ip_mgmtlf1.oct3)+'.'+str(ip_mgmtlf1.oct4)
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o ip de gerencia do leaf 01.")

    if ip_mgmtlf1==None:
        raise RackConfigError(None,rack.nome,"Erro: Ip de gerencia do leaf 01 nao foi cadastrado.")

    #Ip LF02
    try:
        ips2 = ipLF.list_by_equip(id_lf2)
        for ip2 in ips2:
            ip_mgmtlf2 = Ip.get_by_pk(ip2.ip.id)
        if not ip_mgmtlf2==None:
            ip_mgmtlf2 = str(ip_mgmtlf2.oct1)+'.'+str(ip_mgmtlf2.oct2)+'.'+str(ip_mgmtlf2.oct3)+'.'+str(ip_mgmtlf2.oct4)
    except:
        raise RackConfigError(None,rack.nome,"Erro ao buscar o ip de gerencia do leaf 02.")

    if ip_mgmtlf2==None:
        raise RackConfigError(None,rack.nome,"Erro: Ip de gerencia do leaf 02 nao foi cadastrado.")



    #chamada gera_config.py
    var1 = autoprovision_splf(num_rack, FILEINLF, FILEINSP, name_lf1, name_lf2, name_oob, name_sp1, name_sp2, name_sp3, name_sp4, ip_mgmtlf1, ip_mgmtlf2, int_oob_mgmtlf1, int_oob_mgmtlf2, int_sp1, int_sp2, int_sp3, int_sp4, int_lf1_sp1, int_lf1_sp2, int_lf2_sp3, int_lf2_sp4)

    var2 = autoprovision_coreoob(num_rack, FILEINCR, name_core1, name_core2, name_oob, int_oob_core1, int_oob_core2, int_core1_oob, int_core2_oob )

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
