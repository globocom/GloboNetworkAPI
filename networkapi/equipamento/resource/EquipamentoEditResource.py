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
from __future__ import with_statement

import logging

from django.db.models import Count

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_EQUIPMENT
from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoError
from networkapi.equipamento.models import EquipamentoNameDuplicatedError
from networkapi.equipamento.models import EquipamentoNotFoundError
from networkapi.equipamento.models import EquipTypeCantBeChangedError
from networkapi.equipamento.models import Modelo
from networkapi.equipamento.models import ModeloNotFoundError
from networkapi.equipamento.models import TipoEquipamento
from networkapi.equipamento.models import TipoEquipamentoNotFoundError
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.infrastructure.xml_utils import XMLError
from networkapi.ip.models import Ip
from networkapi.ip.models import IpEquipamento
from networkapi.ip.models import Ipv6
from networkapi.ip.models import Ipv6Equipament
from networkapi.ip.models import NetworkIPv4
from networkapi.ip.models import NetworkIPv6
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.rest import RestResource
from networkapi.rest import UserNotAuthorizedError
from networkapi.util import destroy_cache_function
from networkapi.util import is_valid_boolean_param
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_regex
from networkapi.util import is_valid_string_maxsize
from networkapi.util import is_valid_string_minsize
from networkapi.vlan.models import Vlan


class EquipamentoEditResource(RestResource):

    log = logging.getLogger('EquipamentoResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Trata uma requisicao POST para editar um equipamento.

        URL: equipmento/edit/
        """
        try:
            # Load XML data
            xml_map, attrs_map = loads(request.raw_post_data)

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            equip_map = networkapi_map.get('equipamento')
            if equip_map is None:
                msg = u'There is no value to the ip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            equip_id = equip_map.get('id_equip')
            id_modelo = equip_map.get('id_modelo')
            nome = equip_map.get('nome')
            id_tipo_equipamento = equip_map.get('id_tipo_equipamento')
            maintenance = equip_map.get('maintenance')

            # Valid equip_id
            if not is_valid_int_greater_zero_param(equip_id):
                self.log.error(
                    u'Parameter equip_id is invalid. Value: %s.', equip_id)
                raise InvalidValueError(None, 'equip_id', equip_id)

            # Valid id_modelo
            if not is_valid_int_greater_zero_param(id_modelo):
                self.log.error(
                    u'Parameter id_modelo is invalid. Value: %s.', id_modelo)
                raise InvalidValueError(None, 'id_modelo', id_modelo)

            # Valid id_tipo_equipamento
            if not is_valid_int_greater_zero_param(id_tipo_equipamento):
                self.log.error(
                    u'Parameter id_tipo_equipamento is invalid. Value: %s.', id_tipo_equipamento)
                raise InvalidValueError(
                    None, 'id_tipo_equipamento', id_tipo_equipamento)

            # Valid nome
            if not is_valid_string_minsize(nome, 3) or not is_valid_string_maxsize(nome, 80) or not is_valid_regex(nome, '^[A-Z0-9-_]+$'):
                self.log.error(u'Parameter nome is invalid. Value: %s', nome)
                raise InvalidValueError(None, 'nome', nome)

            # Business Rules

            # New equipment
            equip = Equipamento()
            equip = equip.get_by_pk(equip_id)

            # maintenance is a new feature. Check existing value if not defined in request
            # Old calls does not send this field
            if maintenance is None:
                maintenance = equip.maintenance
            if not is_valid_boolean_param(maintenance):
                self.log.error(
                    u'The maintenance parameter is not a valid value: %s.', maintenance)
                raise InvalidValueError(None, 'maintenance', maintenance)

            if maintenance in ['1', 'True', True]:
                maintenance = True
            else:
                maintenance = False

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.WRITE_OPERATION, None, equip_id, AdminPermission.EQUIP_WRITE_OPERATION):
                raise UserNotAuthorizedError(
                    None, u'User does not have permission to perform the operation.')

            with distributedlock(LOCK_EQUIPMENT % equip_id):
                tipo_equip = TipoEquipamento.get_by_pk(id_tipo_equipamento)

                if equip.tipo_equipamento != tipo_equip:
                    # Environments with filters using current equip type, with
                    # equipment associated
                    envs = [eq_env.ambiente.id for eq_env in equip.equipamentoambiente_set.filter(
                        ambiente__filter__filterequiptype__equiptype=equip.tipo_equipamento)]

                    # Filters case 1 and 2

                    filters_ok = True

                    # Networks in environments with same ip range
                    nets_same_range = NetworkIPv4.objects.filter(vlan__ambiente__in=envs).values(
                        'oct1', 'oct2', 'oct3', 'oct4', 'block').annotate(count=Count('id')).filter(count__gt=1)

                    if len(nets_same_range) > 0:
                        for net_gp in nets_same_range:
                            nets_current_range = NetworkIPv4.objects.filter(vlan__ambiente__in=envs, oct1=net_gp[
                                                                            'oct1'], oct2=net_gp['oct2'], oct3=net_gp['oct3'], oct4=net_gp['oct4'], block=net_gp['block'])
                            filters_of_envs = [
                                net.vlan.ambiente.filter.id for net in nets_current_range]
                            for fil_ in filters_of_envs:
                                if TipoEquipamento.objects.filter(id=id_tipo_equipamento, filterequiptype__filter=fil_).count() == 0:
                                    filters_ok = False
                                    break

                            if not filters_ok:
                                raise EquipTypeCantBeChangedError(
                                    None, 'O tipo de equipamento não pode ser modificado pois existe um filtro em uso que não possui o novo tipo de equipamento informado.')

                    # Networks ipv6 in environments with same ipv6 range
                    nets_v6_same_range = NetworkIPv6.objects.filter(vlan__ambiente__in=envs).values(
                        'block1', 'block2', 'block3', 'block4', 'block5', 'block6', 'block7', 'block8', 'block').annotate(count=Count('id')).filter(count__gt=1)

                    if len(nets_v6_same_range) > 0:
                        for net_gp in nets_v6_same_range:
                            nets_current_range = NetworkIPv6.objects.filter(vlan__ambiente__in=envs, block1=net_gp['block1'], block2=net_gp['block2'], block3=net_gp[
                                                                            'block3'], block4=net_gp['block4'], block5=net_gp['block5'], block6=net_gp['block6'], block7=net_gp['block7'], block8=net_gp['block8'], block=net_gp['block'])
                            filters_of_envs = [
                                net.vlan.ambiente.filter.id for net in nets_current_range]
                            for fil_ in filters_of_envs:
                                if TipoEquipamento.objects.filter(id=id_tipo_equipamento, filterequiptype__filter=fil_).count() == 0:
                                    filters_ok = False
                                    break

                            if not filters_ok:
                                raise EquipTypeCantBeChangedError(
                                    None, 'O tipo de equipamento não pode ser modificado pois existe um filtro em uso que não possui o novo tipo de equipamento informado.')

                    # Filters case 1 and 2 end

                    # Filter case 3

                    # Get vlans with same number
                    vlans_same_number = Vlan.objects.filter(ambiente__in=envs).values(
                        'num_vlan').annotate(count=Count('id')).filter(count__gt=1)

                    if len(vlans_same_number) > 0:
                        for vlan_gp in vlans_same_number:
                            vlans_current_number = Vlan.objects.filter(
                                ambiente__in=envs, num_vlan=vlan_gp['num_vlan'])
                            filters_of_envs = [
                                vlan.ambiente.filter.id for vlan in vlans_current_number]
                            for fil_ in filters_of_envs:
                                if TipoEquipamento.objects.filter(id=id_tipo_equipamento, filterequiptype__filter=fil_).count() == 0:
                                    filters_ok = False
                                    break

                            if not filters_ok:
                                raise EquipTypeCantBeChangedError(
                                    None, 'O tipo de equipamento não pode ser modificado pois existe um filtro em uso que não possui o novo tipo de equipamento informado.')

                    # Filter case 3 end

                    # Test all vip requests if equip.tipo_equipamento is
                    # balancing

                    if equip.tipo_equipamento == TipoEquipamento.get_tipo_balanceador():
                        vips = RequisicaoVips.objects.all()
                        vip_ips = []
                        vip_ipsv6 = []
                        for vip in vips:
                            if vip.vip_criado:
                                if vip.ip is not None:
                                    if vip.ip.ipequipamento_set.filter(equipamento=equip.id).count() > 0:
                                        raise EquipTypeCantBeChangedError(
                                            None, 'O tipo de equipamento não pode ser modificado pois este equipamento é o balanceador associado com o vip criado %s.' % vip.id)
                                if vip.ipv6 is not None:
                                    if vip.ipv6.ipv6equipament_set.filter(equipamento=equip.id).count() > 0:
                                        raise EquipTypeCantBeChangedError(
                                            None, 'O tipo de equipamento não pode ser modificado pois este equipamento é o balanceador associado com o vip criado %s.' % vip.id)

                            else:
                                if vip.ip is not None:
                                    vip_ips.append(vip.ip.id)
                                if vip.ipv6 is not None:
                                    vip_ipsv6.append(vip.ipv6.id)

                        nets_using_balancer_in_vips_ = [
                            ip_.networkipv4 for ip_ in Ip.objects.filter(id__in=vip_ips)]
                        nets_using_balancer_in_vips = [ip_.networkipv4 for ip_ in Ip.objects.filter(
                            networkipv4__in=nets_using_balancer_in_vips_, ipequipamento__equipamento=equip.id)]
                        nets_v6_using_balancer_in_vips_ = [
                            ip_.networkipv6 for ip_ in Ipv6.objects.filter(id__in=vip_ipsv6)]
                        nets_v6_using_balancer_in_vips = [ip_.networkipv6 for ip_ in Ipv6.objects.filter(
                            networkipv6__in=nets_v6_using_balancer_in_vips_, ipv6equipament__equipamento=equip.id)]

                        for net in nets_using_balancer_in_vips:
                            net_str = str(net.oct1) + '.' + str(net.oct2) + '.' + \
                                str(net.oct3) + '.' + str(net.oct4) + \
                                '/' + str(net.block)
                            if IpEquipamento.objects.filter(ip__networkipv4=net, equipamento__tipo_equipamento=TipoEquipamento.get_tipo_balanceador()).exclude(equipamento=equip).count() == 0:
                                raise EquipTypeCantBeChangedError(
                                    None, 'O tipo de equipamento não pode ser modificado pois este equipamento é o único balanceador disponível na rede %s da vlan %s.' % (net_str, net.vlan.nome))

                        for net in nets_v6_using_balancer_in_vips:
                            net_str = str(net.block1) + ':' + str(net.block2) + ':' + str(net.block3) + ':' + str(net.block4) + ':' + str(
                                net.block5) + ':' + str(net.block6) + ':' + str(net.block7) + ':' + str(net.block8) + '/' + str(net.block)
                            if Ipv6Equipament.objects.filter(ip__networkipv6=net, equipamento__tipo_equipamento=TipoEquipamento.get_tipo_balanceador()).exclude(equipamento=equip).count() == 0:
                                raise EquipTypeCantBeChangedError(
                                    None, 'O tipo de equipamento não pode ser modificado pois este equipamento é o único balanceador disponível na rede %s da vlan %s.' % (net_str, net.vlan.nome))

                ip_equipamento_list = IpEquipamento.objects.filter(
                    equipamento=equip_id)
                ip6_equipamento_list = Ipv6Equipament.objects.filter(
                    equipamento=equip_id)

                # Delete vlan's cache
                key_list = []
                for eq in ip_equipamento_list:
                    vlan = eq.ip.networkipv4.vlan
                    vlan_id = vlan.id
                    key_list.append(vlan_id)

                for eq in ip6_equipamento_list:
                    vlan = eq.ip.networkipv6.vlan
                    vlan_id = vlan.id
                    key_list.append(vlan_id)

                destroy_cache_function(key_list)

                # Delete equipment's cache
                destroy_cache_function([equip_id], True)

                modelo = Modelo.get_by_pk(id_modelo)
                equip.edit(user, nome, tipo_equip, modelo, maintenance)

                return self.response(dumps_networkapi({}))

        except EquipTypeCantBeChangedError, e:
            return self.response_error(150, e.message)
        except InvalidValueError, e:
            return self.response_error(269, e.param, e.value)
        except TipoEquipamentoNotFoundError:
            return self.response_error(100)
        except ModeloNotFoundError:
            return self.response_error(101)
        except EquipamentoNotFoundError, e:
            return self.response_error(117, equip_id)
        except EquipamentoNameDuplicatedError, e:
            return self.response_error(e.message)
        except (EquipamentoError), e:
            return self.responde_error(1)
        except UserNotAuthorizedError:
            return self.not_authorized()
        except XMLError, x:
            self.log.error(u'Error reading the XML request.')
            return self.response_error(3, x)
