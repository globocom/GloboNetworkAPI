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
from networkapi.infrastructure.script_utils import exec_script
from networkapi.log import Log
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.util import is_valid_string_minsize, is_valid_string_maxsize
from networkapi.vlan.models import Vlan, VlanNetworkError, VlanInactiveError
from networkapi.ip.models import NetworkIPv4, NetworkIPv6
from networkapi.ambiente.models import IPConfig, ConfigEnvironment, Ambiente, GrupoL3 
from networkapi.equipamento.models import Equipamento
from networkapi.distributedlock import distributedlock, LOCK_RACK
from networkapi import settings
import shutil 

PATH_TO_CONFIG = "/opt/app/GloboNetworkAPI/networkapi/rack/configuracao/"
PATH_TO_MV = "/opt/app/GloboNetworkAPI/networkapi/rack/delete/"
LEAF = "LF-CM"
OOB = "OOB-CM"
SPN = "SPN-CM"
FORMATO = ".cfg"

def desativar_remover_vlan_rede(user, rack):

    nome = "_"+rack.nome
    vlans = Vlan.objects.all()

    for vlan in vlans:

        if nome in vlan.nome:
            network_errors = []
         
            for net4 in vlan.networkipv4_set.all(): 
                for ip in net4.ip_set.all():
                    ip.delete(user)

                if net4.active: 
                    try: 
                        command = settings.NETWORKIPV4_REMOVE % int(net4.id) 
                        code, stdout, stderr = exec_script(command) 
                        if code == 0: 
                            net4.deactivate(user, True)
                        else: 
                            network_errors.append(str(net4.id)) 
                    except Exception, e: 
                        network_errors.append(str(net4.id)) 
                        pass

            for net6 in vlan.networkipv6_set.all():
                for ip6 in net6.ipv6_set.all():
                    ip6.delete(user)

                if net6.active:
                    try:
                        command = settings.NETWORKIPV6_REMOVE % int(net6.id)
                        code, stdout, stderr = exec_script(command)
                        if code == 0:
                            net6.deactivate(user, True)
                        else:
                            network_errors.append(str(net6.id))
                    except Exception, e:
                        network_errors.append(str(net6.id))
                        pass

            if network_errors:
                raise VlanNetworkError(None, message=', '.join(network_errors))

            if vlan.ativada:
                command = settings.VLAN_REMOVE % vlan.id
                code, stdout, stderr = exec_script(command)
                if code == 0:
                    vlan.remove(user)

            vlan.delete(user)            

def remover_ambiente(user, rack):

    ip_config_list = []

    config_ambs = ConfigEnvironment()
    ambientes_l3 = GrupoL3.objects.all()
    ambiente = Ambiente()
    ambientes = Ambiente.objects.all()

    nome_rack = "RACK_"+rack.nome

    nome_l3 = "RACK_"+rack.nome

    for amb in ambientes:
        if amb.grupo_l3.nome==nome_l3:
            id_amb_l3 = amb.grupo_l3.id
            ambiente.remove(user, amb.id)

    for amb_l3 in ambientes_l3:
        if amb_l3.nome == nome_rack:
            amb_l3.delete(user)

class RackDeleteResource(RestResource):

    log = Log('RackDeleteResource')

    def handle_delete(self, request, user, *args, **kwargs):
        """Treat requests POST to delete Rack.

        URL: rack/id_rack/
        """
        try:
            self.log.info("Remove Delete")

            # User permission
            if not has_perm(user, AdminPermission.SCRIPT_MANAGEMENT, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                raise UserNotAuthorizedError(None)

            rack_id = kwargs.get('id_rack')
            rack = Rack()
            rack = rack.get_by_pk(rack_id)

            # Mover os arquivos de configuracao que foram gerados
            try:
                for i in range(1,3):
                    nome_lf = LEAF+"-"+rack.nome+"-"+str(i)+FORMATO
                    nome_lf_b = PATH_TO_CONFIG+nome_lf
                    nome_lf_a = PATH_TO_MV+nome_lf
                    shutil.move(nome_lf_b, nome_lf_a)
                    nome_oob = OOB+"-0"+str(i)+"-CM-"+rack.nome+FORMATO
                    nome_oob_b = PATH_TO_CONFIG+nome_oob
                    nome_oob_a = PATH_TO_MV+nome_oob
                    shutil.move(nome_oob_b, nome_oob_a)
                for i in range(1,5):
                    nome_spn = SPN+"-"+str(i)+"-CM-"+rack.nome+FORMATO
                    nome_spn_b = PATH_TO_CONFIG+nome_spn
                    nome_spn_a = PATH_TO_MV+nome_spn
                    shutil.move(nome_spn_b, nome_spn_a)
            except:
                pass

            # Remover as Vlans, redes e ambientes
            try:
                desativar_remover_vlan_rede(user, rack)
                remover_ambiente(user, rack)
            except:
                raise RackError(None, u'Failed to remove the Vlans and Environments.')    
            
            # Remover Rack            
            with distributedlock(LOCK_RACK % rack_id):

                try:
                    rack.delete(user)
                except RackNumberNotFoundError, e:
                    raise e
                except Exception, e:
                    self.log.error(u'Failed to remove the Rack.')
                    raise RackError(e, u'Failed to remove the Rack.')                   
                
            return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RackNumberNotFoundError:
            return self.response_error(379, id_rack)

        except RackError:
            return self.response_error(1)

        except VlanNetworkError, e:
            return self.response_error(369, e.message)

        except VlanInactiveError, e:
            return self.response_error(368)

