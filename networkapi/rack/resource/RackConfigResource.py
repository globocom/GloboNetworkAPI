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
from networkapi.exception import InvalidValueError
from networkapi.rack.models import RackNumberNotFoundError, RackNumberDuplicatedValueError, Rack , RackError, InvalidMacValueError
from networkapi.infrastructure.xml_utils import loads, dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param, is_valid_string_minsize, is_valid_string_maxsize
from networkapi.equipamento.models import Equipamento, EquipamentoRoteiro
from networkapi.interface.models import Interface, InterfaceNotFoundError
from networkapi.distributedlock import distributedlock, LOCK_RACK
from networkapi.rack.resource.GeraConfig import autoprovision_splf
from networkapi.ip.models import Ip, IpEquipamento

def gera_config(rack):

    num_rack = rack.numero
    id_lf1 = rack.id_sw1.id
    name_lf1 = rack.id_sw1.nome
    id_lf2 = rack.id_sw2.id
    name_lf2 = rack.id_sw2.nome
    id_oob = rack.id_ilo.id
    name_oob = rack.id_ilo.nome

    name_sp1=None   
    name_sp2=None   
    name_sp3=None   
    name_sp4=None   
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
    ip_mgmtlf1=None
    ip_mgmtlf2=None
    int_oob_mgmtlf1=None
    int_oob_mgmtlf2=None

    PATH_TO_GUIDE = "/opt/app/GloboNetworkAPI/networkapi/rack/roteiros/"
    PATH_TO_CONFIG = "/opt/app/GloboNetworkAPI/networkapi/rack/configuracao/"

    msg = ""

    #Interface leaf01
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
        except InterfaceNotFoundError:
            msg = "Erro ao buscar as interfaces do Leaf 01."

    #Interface leaf02
    interfaces = Interface.search(id_lf2)
    for interface in interfaces:
        try:
            sw = interface.get_switch_and_router_interface_from_host_interface(None)
            if sw.equipamento.nome.split('-')[2]=='3':
                int_lf2_sp3 = interface.interface
                name_sp3 = sw.equipamento.nome
                id_spn3 = sw.equipamento.id
                int_sp3 =  sw.interface
            elif sw.equipamento.nome.split('-')[2]=='4':
                int_lf2_sp4 = interface.interface
                name_sp4 = sw.equipamento.nome
                id_spn4 = sw.equipamento.id
                int_sp4 =  sw.interface
            elif sw.equipamento.nome.split('-')[0]=='OOB':
                int_oob_mgmtlf2 = sw.interface
        except InterfaceNotFoundError:
            msg = "Erro ao buscar as interfaces do Leaf 02."

    #Roteiro LF
    try:
        rot_equip = EquipamentoRoteiro.search(None, id_lf1)
        for rot in rot_equip:
            if (rot.roteiro.tipo_roteiro.tipo=="CONFIGURACAO"):
                roteiro_leaf = rot.roteiro.roteiro
        roteiro_leaf = roteiro_leaf.lower()+".txt"
    except:
        msg = "Erro ao buscar o roteiro do Leaf."
    FILEINLF=PATH_TO_GUIDE+roteiro_leaf

    #Roteiro SPN
    try:
        rot_equip2 = EquipamentoRoteiro.search(None, id_spn1)
        for rot2 in rot_equip2:
            if (rot2.roteiro.tipo_roteiro.tipo=="CONFIGURACAO"):
                roteiro_spine = rot2.roteiro.roteiro
        roteiro_spine = roteiro_spine.lower()+".txt"
    except:
        msg = "Erro ao buscar o roteiro do Spine."

    FILEINSP=PATH_TO_GUIDE+roteiro_spine    


    #Ip LF
    try:
        ipLF = IpEquipamento()
        ips = ipLF.list_by_equip(id_lf1)
        for ip in ips:
            ip_mgmtlf1 = Ip.get_by_pk(ip.ip.id)
        if not ip_mgmtlf1==None:
            ip_mgmtlf1 = str(ip_mgmtlf1.oct1)+'.'+str(ip_mgmtlf1.oct2)+'.'+str(ip_mgmtlf1.oct3)+'.'+str(ip_mgmtlf1.oct4)
    except:
        msg = "Erro ao buscar o ip de gerencia do leaf 01"

    #Ip LF02
    try:
        ips2 = ipLF.list_by_equip(id_lf2)
        for ip2 in ips2:
            ip_mgmtlf2 = Ip.get_by_pk(ip2.ip.id)
        if not ip_mgmtlf2==None:
            ip_mgmtlf2 = str(ip_mgmtlf2.oct1)+'.'+str(ip_mgmtlf2.oct2)+'.'+str(ip_mgmtlf2.oct3)+'.'+str(ip_mgmtlf2.oct4)
    except:
        msg = "Erro ao buscar o ip de gerencia do leaf 02"

    """
    #Ip OOB
    ips3 = ipLF.list_by_equip(id_oob)
    for ip3 in ips3:
        ip_mgmt = Ip.get_by_pk(ip3.ip.id)
    if not ip_mgmt==None:
        ip_mgmt = str(ip_mgmt.oct1)+'.'+str(ip_mgmt.oct2)+'.'+str(ip_mgmt.oct3)+'.'+str(ip_mgmt.oct4) 
    """

    if name_lf1==None or name_lf2==None or name_oob==None or name_sp1==None or name_sp2==None or name_sp3==None or name_sp4==None or int_sp1==None or int_sp2==None or int_sp3==None or int_sp4==None or int_lf1_sp1==None or int_lf1_sp2==None or int_lf2_sp3==None or int_lf2_sp4==None or roteiro_leaf==None or roteiro_spine==None or ip_mgmtlf1==None or ip_mgmtlf2==None or int_oob_mgmtlf1==None or int_oob_mgmtlf2==None:
        return msg
    else:
        msg = autoprovision_splf(num_rack, FILEINLF, FILEINSP, name_lf1, name_lf2, name_oob, name_sp1, name_sp2, name_sp3, name_sp4, ip_mgmtlf1, ip_mgmtlf2, int_oob_mgmtlf1, int_oob_mgmtlf2, int_sp1, int_sp2, int_sp3, int_sp4, int_lf1_sp1, int_lf1_sp2, int_lf2_sp3, int_lf2_sp4)
        return msg



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

            #chamada script  
            msg = gera_config(rack)
            if msg==None:
                var = True

            rack.__dict__.update(id=rack_id, config_sw1=var)
            rack.save(user) 

            success_map = dict()
            success_map['rack_conf'] = msg
           
            map = dict()
            map['sucesso'] = success_map
                        
            return self.response(dumps_networkapi(map))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RackNumberNotFoundError:
            return self.response_error(379, id_rack)

        except RackError:
            return self.response_error(1)

        except InterfaceNotFoundError:
            return self.response_error(141)
