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


def gera_config(rack, equip):

    num_rack = rack.numero
    if equip=='Sw1':
        id_equip = rack.id_sw1.id
        nome_equip = rack.id_sw1.nome
    elif equip=='Sw2':
        id_equip = rack.id_sw2.id
        nome_equip = rack.id_sw2.nome
    else:
        id_equip = rack.id_ilo.id
        nome_equip = rack.id_ilo.nome

    nome_rot = None
    nome_rot_spn_core1 = None
    nome_rot_spn_core2 = None
    int_equip1 = None
    int_equip2 = None
    int_spn_core1 = None
    int_spn_core2 = None
    nome_spn_core1 = None
    nome_spn_core2 = None
    id_spn_core1 = None
    id_spn_core2 = None
    var = False

    #Interface
    interfaces = Interface.search(id_equip)
    for interface in interfaces:
        try:
            sw = interface.get_switch_and_router_interface_from_host_interface(None)
            if int_equip1 == None: 
                int_equip1 = interface.interface
                nome_spn_core1 = sw.equipamento.nome
                id_spn_core1 = sw.equipamento.id
                int_spn_core1 =  sw.interface
            else:
                int_equip2 = interface.interface
                nome_spn_core2 = sw.equipamento.nome
                id_spn_core2 = sw.equipamento.id
                int_spn_core2 =  sw.interface  
        except InterfaceNotFoundError:
            pass

    #Roteiros
    rot_equip = EquipamentoRoteiro.search(None, id_equip)
    for rot in rot_equip:
        if (rot.roteiro.tipo_roteiro.tipo=="backup"):#trocar: "configuracao"
            nome_rot = rot.roteiro.roteiro
    rot_spn_core1 = EquipamentoRoteiro.search(None, id_spn_core1)
    for rot1 in rot_spn_core1:
        if (rot1.roteiro.tipo_roteiro.tipo=="backup"):#trocar: "configuracao"
            nome_rot_spn_core1 = rot1.roteiro.roteiro
    rot_spn_core2 = EquipamentoRoteiro.search(None, id_spn_core2)
    for rot2 in rot_spn_core2:
        if (rot2.roteiro.tipo_roteiro.tipo=="backup"):#trocar: "configuracao"
            nome_rot_spn_core2 = rot2.roteiro.roteiro

    #int1 = str(id_spn_core2) +'-'+ nome_rot_spn_core2 #str(id_spn_core2)
    #raise InvalidValueError(None, 'int1', int1)

    if not nome_rot==None and not int_equip1==None and not nome_spn_core1==None and not int_spn_core1==None and not int_equip2==None and not nome_spn_core2==None and not int_spn_core2==None and not nome_rot_spn_core1==None and not nome_rot_spn_core2==None:
       #var = Script(num_rack, nome_equip, nome_rot, int_equip1, nome_spn_core1, int_spn_core1, nome_rot_spn_core1, int_equip2, nome_spn_core2, int_spn_core2, nome_rot_spn_core2)
       var = True

    return var


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
            var1 = False
	    var2 = False
            var3 = False
 
            #if not is_valid_int_greater_zero_param(rack.numero):
             #   self.log.error(
              #      u'Parameter id_vlan is invalid. Value: %s.', rack.numero)
               # raise InvalidValueError(None, 'str', rack.numero)

            if not rack.id_sw1==None:
                var1 = gera_config(rack, 'Sw1')
            if not rack.id_sw2==None:            
                var2 = gera_config(rack, 'Sw2')
            if not rack.id_ilo==None:
                var3 = gera_config(rack, 'Ilo')

            rack.__dict__.update(id=rack_id, config_sw1=var1, config_sw2=var2, config_ilo=var3)
            rack.save(user) 

            success_map = dict()
            success_map['equip1'] = str(var1)
            success_map['equip2'] = str(var2)
            success_map['equip3'] = str(var3)
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
