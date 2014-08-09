# -*- coding:utf-8 -*-
"""
Title: Infrastructure NetworkAPI
Author: avanzolin / S2it
Copyright: ( c )  2009 globo.com todos os direitos reservados.
"""

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.exception import InvalidValueError
from networkapi.requisicaovips.models import RequisicaoVips,\
    RequisicaoVipsNotFoundError


class RequestVipGetByIdResource(RestResource):

    log = Log('RequestVipGetByIdResource')

    def handle_get(self, request, user, *args, **kwargs):
        """Handles GET requests to find all Vip Requests by id.

        URLs: /requestvip/getbyid/id_vip
        """

        self.log.info('Find Vip Request by id')

        try:
            # Commons Validations

            # User permission
            if not has_perm(
                    user,
                    AdminPermission.VIPS_REQUEST,
                    AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations
            # Valid id access
            id_vip = kwargs.get('id_vip')

            if not is_valid_int_greater_zero_param(id_vip):
                self.log.error(
                    u'Parameter id_vip is invalid. Value: %s.',
                    id_vip)
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

            if vip.healthcheck_expect is not None:
                vip_map['id_healthcheck_expect'] = vip.healthcheck_expect.id
                vip_map['expect_string'] = vip.healthcheck_expect.expect_string
                vip_map['match_list'] = vip.healthcheck_expect.match_list
            else:
                vip_map['expect_string'] = ""
                vip_map['match_list'] = ""

            list_equips = []
            list_ips = list()
            list_environment = []
            descricao_ipv4 = None
            descricao_ipv6 = None

            if vip.ip is not None:
                descricao_ipv4 = vip.ip.descricao
                list_ips.append(
                    "%s.%s.%s.%s" %
                    (vip.ip.oct1,
                     vip.ip.oct2,
                     vip.ip.oct3,
                     vip.ip.oct4))
                list_environment.append(
                    "%s - %s - %s" %
                    (vip.ip.networkipv4.vlan.ambiente.divisao_dc.nome,
                     vip.ip.networkipv4.vlan.ambiente.ambiente_logico.nome,
                     vip.ip.networkipv4.vlan.ambiente.grupo_l3.nome))
                equips = vip.ip.ipequipamento_set.all()

                for equip in equips:

                    if equip.equipamento.nome not in list_equips:

                        list_equips.append(equip.equipamento.nome)

            if vip.ipv6 is not None:
                descricao_ipv6 = vip.ipv6.description
                list_ips.append(
                    "%s:%s:%s:%s:%s:%s:%s:%s" %
                    (vip.ipv6.block1,
                     vip.ipv6.block2,
                     vip.ipv6.block3,
                     vip.ipv6.block4,
                     vip.ipv6.block5,
                     vip.ipv6.block6,
                     vip.ipv6.block7,
                     vip.ipv6.block8))
                list_environment.append(
                    "%s - %s - %s" %
                    (vip.ipv6.networkipv6.vlan.ambiente.divisao_dc.nome,
                     vip.ipv6.networkipv6.vlan.ambiente.ambiente_logico.nome,
                     vip.ipv6.networkipv6.vlan.ambiente.grupo_l3.nome))
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

        except RequisicaoVipsNotFoundError as e:
            return self.response_error(152)
        except InvalidValueError as e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.',
                e.param,
                e.value)
            return self.response_error(269, e.param, e.value)
        except BaseException as e:
            return self.response_error(1)
