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
from networkapi.equipamento.models import EquipamentoError, TipoEquipamento
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import XMLError, dumps_networkapi, \
    loads
from networkapi.ip.models import Ip, IpNotAvailableError, IpError, NetworkNotInEvip, IpRangeAlreadyAssociation, IpEquipamento
import logging
from networkapi.rest import RestResource, UserNotAuthorizedError
from networkapi.exception import InvalidValueError, EnvironmentVipNotFoundError
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.ambiente.models import EnvironmentVip
from django.forms.models import model_to_dict


class Ipv4GetAvailableForVipResource(RestResource):

    log = logging.getLogger('Ipv4GetAvailableForVipResource')

    def handle_post(self, request, user, *args, **kwargs):
        '''Handles GET requests get an IP4 available for vip_request by evip_id.

        URL: ip/availableip6/vip/id_evip/
        '''

        self.log.info('Get an IP4 available for vip_request')

        try:
            # User permission
            if not has_perm(user, AdminPermission.IPS, AdminPermission.WRITE_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')

            ip_map = networkapi_map.get('ip_map')

            # Get XML data
            id_evip = ip_map.get('id_evip')
            name = ip_map.get('name')

            if not is_valid_int_greater_zero_param(id_evip):
                self.log.error(
                    u'Parameter id_evip is invalid. Value: %s.', id_evip)
                raise InvalidValueError(None, 'id_evip', id_evip)

            # Business Rules
            evip = EnvironmentVip.get_by_pk(id_evip)

            ipv4 = Ip()

            len_network = len(evip.networkipv4_set.all())
            raise_not_found_balanceamento = False

            if (len_network <= 0):
                raise NetworkNotInEvip(
                    None, 'Não há rede no ambiente vip fornecido')

            cont_network = 0
            cont_balanceador_not_found = 0

            for net in evip.networkipv4_set.all():

                balanceador_found_flag = False
                cont_network = cont_network + 1
                list_ips_equips = list()

                try:
                    ip_available = ipv4.get_available_ip(net.id)

                    ip_new = Ip()
                    ip_available = ip_available.exploded
                    ip_available = ip_available.split(".")
                    ip_new.oct1 = ip_available[0]
                    ip_new.oct2 = ip_available[1]
                    ip_new.oct3 = ip_available[2]
                    ip_new.oct4 = ip_available[3]
                    ip_new.descricao = name

                    for env_equipment in net.vlan.ambiente.equipamentoambiente_set.all():
                        equipment = env_equipment.equipamento
                        if equipment.tipo_equipamento == TipoEquipamento.get_tipo_balanceador():

                            if equipment.id not in list_ips_equips:

                                list_ips_equips.append(equipment.id)

                                if ip_new.id is None:
                                    ip_new.save_ipv4(equipment.id, user, net)
                                else:
                                    new_ip_equip = IpEquipamento()
                                    new_ip_equip.ip = ip_new
                                    new_ip_equip.equipamento = equipment
                                    new_ip_equip.save()

                                balanceador_found_flag = True

                    if not balanceador_found_flag:
                        cont_balanceador_not_found = cont_balanceador_not_found + 1
                    else:
                        break

                    if cont_balanceador_not_found == len_network:
                        raise_not_found_balanceamento = True
                        raise IpNotAvailableError(None, "Não há ipv4 disponivel para as redes associdas com o Ambiente Vip: %s - %s - %s, pois não existe equipamentos do Tipo Balanceador nessas redes." % (
                            evip.finalidade_txt, evip.cliente_txt, evip.ambiente_p44_txt))

                except (IpNotAvailableError, IpRangeAlreadyAssociation), e:
                    cont_balanceador_not_found = cont_balanceador_not_found + 1
                    if raise_not_found_balanceamento:
                        raise IpNotAvailableError(None, e.message)
                    elif len_network == cont_network:
                        raise IpNotAvailableError(None, "Não há ipv4 disponivel para as redes associdas com o Ambiente Vip: %s - %s - %s" % (
                            evip.finalidade_txt, evip.cliente_txt, evip.ambiente_p44_txt))

            return self.response(dumps_networkapi({"ip": model_to_dict(ip_new)}))

        except NetworkNotInEvip, e:
            return self.response_error(321, 'ipv4')
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except IpNotAvailableError, e:
            return self.response_error(150, e.message)
        except EnvironmentVipNotFoundError:
            return self.response_error(283)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
        except (IpError, EquipamentoError, GrupoError), e:
            return self.response_error(1)
