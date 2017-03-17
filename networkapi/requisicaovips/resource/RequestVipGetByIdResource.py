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
"""
"""
import logging

from django.core.exceptions import ObjectDoesNotExist

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.requisicaovips.models import DsrL3_to_Vip
from networkapi.requisicaovips.models import InvalidHealthcheckValueError
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.requisicaovips.models import RequisicaoVipsNotFoundError
from networkapi.requisicaovips.models import ServerPool
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util.decorators import deprecated


class RequestVipGetByIdResource(RestResource):

    log = logging.getLogger('RequestVipGetByIdResource')

    @deprecated(new_uri='vip/request/get/<id>/')
    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to find all Vip Requests by id.

        URLs: /requestvip/getbyid/id_vip
        """

        self.log.info('Find Vip Request by id')

        try:
            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VIPS_REQUEST, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations
            # Valid id access
            id_vip = kwargs.get('id_vip')

            if not is_valid_int_greater_zero_param(id_vip):
                self.log.error(
                    u'Parameter id_vip is invalid. Value: %s.', id_vip)
                raise InvalidValueError(None, 'id_vip', id_vip)

            vip = RequisicaoVips.get_by_pk(id_vip)
            vip_map = vip.variables_to_map()

            """"""
            vip_port_list, reals_list, reals_priority, reals_weight = vip.get_vips_and_reals(
                vip.id)

            if reals_list:
                vip_map['reals'] = {'real': reals_list}
                vip_map['reals_prioritys'] = {'reals_priority': reals_priority}
                vip_map['reals_weights'] = {'reals_weight': reals_weight}

            if vip_port_list:
                vip_map['portas_servicos'] = {'porta': vip_port_list}

            """"""

            vip_map['id'] = id_vip
            vip_map['validado'] = vip.validado
            vip_map['vip_criado'] = vip.vip_criado
            vip_map['rule_id'] = vip.rule_id
            vip_map[
                'trafficreturn'] = vip.trafficreturn.nome_opcao_txt if vip.trafficreturn else ''
            try:
                dsrl3_to_vip_obj = DsrL3_to_Vip.get_by_vip_id(vip.id)
                vip_map['dsrl3'] = dsrl3_to_vip_obj.id_dsrl3
            except ObjectDoesNotExist, e:
                pass

            # Maxcon, lbmethod e hc
            vip_map['maxcon'] = 0
            vip_map['metodo_bal'] = ''
            vip_map['healthcheck'] = ''
            vip_map['healthcheck_type'] = ''

            pools = []
            pool_to_use = None

            id_pools = vip.vipporttopool_set.values_list(
                'server_pool_id', flat=True)
            if len(id_pools) > 0:
                pools = ServerPool.objects.filter(
                    id__in=id_pools).order_by('id')
                pool_to_use = pools[0]
                for pool in pools:
                    if pool.healthcheck:
                        hc = pool.healthcheck.healthcheck_type
                        if hc == 'HTTP':
                            pool_to_use = pool
                            break

            if pool_to_use:
                vip_map['maxcon'] = pool_to_use.default_limit
                vip_map['metodo_bal'] = pool_to_use.lb_method
                vip_map[
                    'servicedownaction'] = pool_to_use.servicedownaction.name if pool_to_use.servicedownaction else ''
                vip_map[
                    'healthcheck_type'] = pool.healthcheck.healthcheck_type if pool.healthcheck else ''
                if vip_map['healthcheck_type'] in ('HTTP', 'HTTPS'):
                    vip_map[
                        'healthcheck'] = pool.healthcheck.healthcheck_request if pool.healthcheck else ''

            if vip.healthcheck_expect is not None:
                vip_map['id_healthcheck_expect'] = vip.healthcheck_expect.id
                vip_map['expect_string'] = vip.healthcheck_expect.expect_string
                vip_map['match_list'] = vip.healthcheck_expect.match_list
            else:
                vip_map['expect_string'] = ''
                vip_map['match_list'] = ''

            list_equips = []
            list_ips = list()
            list_environment = []
            descricao_ipv4 = None
            descricao_ipv6 = None

            if vip.ip is not None:
                descricao_ipv4 = vip.ip.descricao
                list_ips.append(
                    '%s.%s.%s.%s' % (vip.ip.oct1, vip.ip.oct2, vip.ip.oct3, vip.ip.oct4))
                list_environment.append('%s - %s - %s' % (vip.ip.networkipv4.vlan.ambiente.divisao_dc.nome,
                                                          vip.ip.networkipv4.vlan.ambiente.ambiente_logico.nome, vip.ip.networkipv4.vlan.ambiente.grupo_l3.nome))
                equips = vip.ip.ipequipamento_set.all()

                for equip in equips:

                    if equip.equipamento.nome not in list_equips:

                        list_equips.append(equip.equipamento.nome)

            if vip.ipv6 is not None:
                descricao_ipv6 = vip.ipv6.description
                list_ips.append('%s:%s:%s:%s:%s:%s:%s:%s' % (vip.ipv6.block1, vip.ipv6.block2, vip.ipv6.block3,
                                                             vip.ipv6.block4, vip.ipv6.block5, vip.ipv6.block6, vip.ipv6.block7, vip.ipv6.block8))
                list_environment.append('%s - %s - %s' % (vip.ipv6.networkipv6.vlan.ambiente.divisao_dc.nome,
                                                          vip.ipv6.networkipv6.vlan.ambiente.ambiente_logico.nome, vip.ipv6.networkipv6.vlan.ambiente.grupo_l3.nome))
                equips = vip.ipv6.ipv6equipament_set.all()

                for equip in equips:

                    if equip.equipamento.nome not in list_equips:

                        list_equips.append(equip.equipamento.nome)

            vip_map['ipv4_description'] = descricao_ipv4
            vip_map['ipv6_description'] = descricao_ipv6
            vip_map['environments'] = list_environment
            vip_map['ips'] = list_ips
            vip_map['equipamento'] = list_equips
            # Business Rules

            # Start with alls
            returned_map = dict()
            returned_map['vip'] = [vip_map]

            return self.response(dumps_networkapi(returned_map))

        except RequisicaoVipsNotFoundError, e:
            self.log.error(e)
            return self.response_error(152)
        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except BaseException, e:
            self.log.error(e)
            return self.response_error(1)
