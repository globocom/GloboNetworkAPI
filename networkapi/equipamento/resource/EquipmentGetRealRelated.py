# -*- coding: utf-8 -*-
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
import logging

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import VipPortToPool
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import mount_ipv4_string
from networkapi.util import mount_ipv6_string


class EquipmentGetRealRelated(RestResource):

    log = logging.getLogger('EquipmentGetRealRelateds')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to list all real related equipment.

        URLs: equipamento/get_real_related/<id_equip>
        """

        try:

            # User permission
            if not has_perm(user, AdminPermission.VIPS_REQUEST, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            id_equip = kwargs.get('id_equip')

            # Valid equipment ID
            if not is_valid_int_greater_zero_param(id_equip):
                self.log.error(
                    u'The id_equip parameter is not a valid value: %s.', id_equip)
                raise InvalidValueError(None, 'id_equip', id_equip)

            equipment = Equipamento.get_by_pk(id_equip)

            map_dicts = []

            # IPV4
            for ip_equip in equipment.ipequipamento_set.all():
                vip_dict = dict()

                ip = ip_equip.ip

                for server_pool_member in ip.serverpoolmember_set.all():
                    server_pool_id = server_pool_member.server_pool_id
                    vip_port_to_pool = VipPortToPool.objects.filter(
                        server_pool__id=server_pool_id)

                    for vptp in vip_port_to_pool:
                        vip = RequisicaoVips.get_by_pk(
                            vptp.requisicao_vip.id)

                        if vip.id not in vip_dict:
                            vip_dict = {str(vip.id): list()}

                        host_name = vip.variables_to_map()['host']

                        map_dicts.append({'server_pool_member_id': server_pool_member.id,
                                          'id_vip': vip.id,
                                          'host_name': host_name,
                                          'port_vip': vptp.port_vip,
                                          'port_real': server_pool_member.port_real,
                                          'ip': mount_ipv4_string(ip)})

            # IPV6
            for ip_equip in equipment.ipv6equipament_set.all():
                vip_dict = dict()

                ip = ip_equip.ip

                for server_pool_member in ip.serverpoolmember_set.all():
                    server_pool_id = server_pool_member.server_pool_id
                    vip_port_to_pool = VipPortToPool.objects.filter(
                        server_pool__id=server_pool_id)

                    for vptp in vip_port_to_pool:
                        vip = RequisicaoVips.get_by_pk(
                            vptp.requisicao_vip.id)

                        if vip.id not in vip_dict:
                            vip_dict = {str(vip.id): list()}

                        host_name = vip.variables_to_map()['host']

                        map_dicts.append({'server_pool_member_id': server_pool_member.id,
                                          'id_vip': vip.id,
                                          'host_name': host_name,
                                          'port_vip': vptp.port_vip,
                                          'port_real': server_pool_member.port_real,
                                          'ip': mount_ipv6_string(ip)})

            vip_map = dict()
            vip_map['vips'] = map_dicts
            vip_map['equip_name'] = equipment.nome

            # Return XML
            return self.response(dumps_networkapi(vip_map))

        except EquipamentoNotFoundError, e:
            return self.response_error(117, id_equip)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except (EquipamentoError, GrupoError):
            return self.response_error(1)
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except Exception, e:
            return self.response_error(1)
