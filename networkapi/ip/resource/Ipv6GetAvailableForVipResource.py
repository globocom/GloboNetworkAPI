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

from django.db import transaction
from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import EnvironmentVip
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_GET_IPV6_AVAILABLE
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import TipoEquipamento
from networkapi.exception import EnvironmentVipNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import IpError
from networkapi.ip.models import IpNotAvailableError
from networkapi.ip.models import IpRangeAlreadyAssociation
from networkapi.ip.models import Ipv6
from networkapi.ip.models import Ipv6Equipament
from networkapi.ip.models import NetworkIPv6Error
from networkapi.ip.models import NetworkNotInEvip
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import is_valid_int_greater_zero_param


class Ipv6GetAvailableForVipResource(RestResource):

    log = logging.getLogger('Ipv6GetAvailableForVipResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles GET requests get an IP6 available for vip_request by evip_id.

        URL: ip/availableip6/vip/id_evip
        """

        self.log.info('Get an IP6 available for vip_request')

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

            with distributedlock(LOCK_GET_IPV6_AVAILABLE % id_evip):

                ipv6 = Ipv6()
                len_network = len(evip.networkipv6_set.all())

                if len_network <= 0:
                    raise NetworkNotInEvip(
                        None, 'Não há rede no ambiente vip fornecido')

                raise_not_found_balanceamento = False

                cont_network = 0
                cont_balanceador_not_found = 0

                for net in evip.networkipv6_set.all():

                    balanceador_found_flag = False
                    cont_network = cont_network + 1
                    list_ips_equips = list()

                    try:
                        ip_available = ipv6.get_available_ip6(net.id)
                        ip_new = Ipv6()

                        ip_available = ip_available.split(':')
                        ip_new.block1 = ip_available[0]
                        ip_new.block2 = ip_available[1]
                        ip_new.block3 = ip_available[2]
                        ip_new.block4 = ip_available[3]
                        ip_new.block5 = ip_available[4]
                        ip_new.block6 = ip_available[5]
                        ip_new.block7 = ip_available[6]
                        ip_new.block8 = ip_available[7]
                        ip_new.description = name

                        for env_equipment in net.vlan.ambiente.equipamentoambiente_set.all():
                            equipment = env_equipment.equipamento
                            if equipment.tipo_equipamento == TipoEquipamento.get_tipo_balanceador():

                                if equipment.id not in list_ips_equips:

                                    list_ips_equips.append(equipment.id)

                                    if ip_new.id is None:
                                        ip_new.save_ipv6(
                                            equipment.id, user, net)
                                    else:
                                        new_ip_equip = Ipv6Equipament()
                                        new_ip_equip.ip = ip_new
                                        new_ip_equip.equipamento = equipment
                                        new_ip_equip.save()

                                    balanceador_found_flag = True

                        if not balanceador_found_flag:
                            cont_balanceador_not_found = cont_balanceador_not_found + \
                                1
                        else:
                            break

                        if cont_balanceador_not_found == len_network:
                            raise_not_found_balanceamento = True
                            raise IpNotAvailableError(None, 'Não há ipv6 disponivel para as redes associadas com o '
                                                            'Ambiente Vip: %s - %s - %s, pois não existe equipamentos '
                                                            'do Tipo Balanceador nessas redes.'
                                                      % (evip.finalidade_txt, evip.cliente_txt, evip.ambiente_p44_txt))

                    except (IpNotAvailableError, IpRangeAlreadyAssociation), e:
                        cont_balanceador_not_found = cont_balanceador_not_found + 1
                        if raise_not_found_balanceamento:
                            raise IpNotAvailableError(None, e.message)
                        elif len_network == cont_network:
                            raise IpNotAvailableError(None, 'Não há ipv6 disponivel para as redes associdas com o '
                                                            'Ambiente Vip: %s - %s - %s'
                                                      % (evip.finalidade_txt, evip.cliente_txt, evip.ambiente_p44_txt))

                transaction.commit()
                return self.response(dumps_networkapi({'ip': model_to_dict(ip_new)}))

        except NetworkNotInEvip, e:
            return self.response_error(321, 'ipv6')
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
        except (IpError, NetworkIPv6Error, EquipamentoError, GrupoError), e:
            return self.response_error(1)
