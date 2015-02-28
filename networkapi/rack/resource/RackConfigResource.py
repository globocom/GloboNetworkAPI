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
from networkapi.distributedlock import distributedlock, LOCK_RACK


def gera_config(num_rack, id_equip, tipo_equip):

    rot_equip = EquipamentoRoteiro.search(None, id_equip)
    nome_rot = None
    var = False

    for rot in rot_equip:
        if (rot.roteiro.tipo_roteiro.tipo=="acl"):#trocar: "configuracao"
            nome_rot = rot.roteiro.roteiro
    if not nome_rot==None:
        #var = Script(num_rack, nome_rot, tipo_equip)
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

            if not rack.id_sw1==None:
                var1 = gera_config(rack.numero, rack.id_sw1.id, 'SWITCH1')
            if not rack.id_sw2==None:            
                var2 = gera_config(rack.numero, rack.id_sw2.id, 'SWITCH2')
            if not rack.id_ilo==None:
                var3 = gera_config(rack.numero, rack.id_ilo.id, 'CONSOLE')

            #if not is_valid_int_greater_zero_param(var3):
             #   self.log.error(
              #      u'Parameter id_vlan is invalid. Value: %s.', var3)
               # raise InvalidValueError(None, 'id_sw1', var3)

            rack.__dict__.update(id=rack_id, config_sw1=var1, config_sw2=var2, config_ilo=var3)
            rack.save(user) 
            
            return self.response(dumps_networkapi({}))

        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)

        except UserNotAuthorizedError:
            return self.not_authorized()

        except RackNumberNotFoundError:
            return self.response_error(379, id_rack)

        except RackError:
            return self.response_error(1)
