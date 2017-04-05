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
from string import split

from django.db.models import Q

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import IP_VERSION
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.datatable import build_query_to_datatable
from networkapi.infrastructure.ipaddr import IPAddress
from networkapi.infrastructure.ipaddr import IPv6Address
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.ip.models import Ip
from networkapi.ip.models import Ipv6
from networkapi.requisicaovips.models import RequisicaoVips
from networkapi.rest import RestResource
from networkapi.util import is_valid_boolean_param
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_minsize


def break_ip(ip):
    """
    Returns array of each octs and string with ip
    """

    if '.' in ip and ':' in ip:
        raise InvalidValueError(None, 'ip', ip)

    if '.' in ip:
        # IPv4
        blocks = split(ip, '.')

        if len(blocks) != 4:
            raise InvalidValueError(None, 'ip', ip)

        version = IP_VERSION.IPv4[0]

    elif ':' in ip:
        # IPv6
        blocks = split(ip, ':')

        if len(blocks) != 8:
            raise InvalidValueError(None, 'ip', ip)

        version = IP_VERSION.IPv6[0]

    else:
        raise InvalidValueError(None, 'ip', ip)

    # Make copy
    unchanged = blocks[:]

    for i, block in enumerate(blocks):
        if len(block) == 0:
            blocks[i] = '0'

    ip_str = ''
    if version == IP_VERSION.IPv4[0]:
        ip_str = blocks[0] + '.' + blocks[1] + \
            '.' + blocks[2] + '.' + blocks[3]

    else:
        # If IPv6, fill with 0 on the left
        for i, block in enumerate(unchanged):
            if len(block) != 4 and len(block) != 0:
                unchanged[i] = block.rjust(4, '0')
        ip_str = blocks[0] + ':' + blocks[1] + ':' + blocks[2] + ':' + blocks[3] + \
            ':' + blocks[4] + ':' + blocks[5] + \
            ':' + blocks[6] + ':' + blocks[7]

    return unchanged, ip_str, version


def get_vips(vips):
    """
    Join all properties needed
    """

    itens = []
    for vip in vips:
        vip_dict = dict()
        vip_dict['id'] = vip.id
        vip_dict['validate'] = vip.validado
        vip_dict['create'] = vip.vip_criado
        vip_dict['valid_l7'] = vip.filter_valid

        list_equips = []
        list_ips = []
        list_environment = []
        descricao_ipv4 = None
        descricao_ipv6 = None

        vip_map = vip.variables_to_map()

        list_environment.append(
            '%s - %s - %s' % (vip_map.get('finalidade', ''), vip_map.get('cliente', ''), vip_map.get('ambiente', '')))
        try:
            if vip.ip is not None:

                descricao_ipv4 = vip.ip.descricao
                list_ips.append(
                    '%s.%s.%s.%s' % (vip.ip.oct1, vip.ip.oct2, vip.ip.oct3, vip.ip.oct4))
                # list_environment.append("%s - %s - %s" % (vip.ip.networkipv4.vlan.ambiente.divisao_dc.nome,vip.ip.networkipv4.vlan.ambiente.ambiente_logico.nome,vip.ip.networkipv4.vlan.ambiente.grupo_l3.nome))

                equips = vip.ip.ipequipamento_set.all()

                for equip in equips:

                    if equip.equipamento.nome not in list_equips:

                        list_equips.append(equip.equipamento.nome)

            if vip.ipv6 is not None:

                descricao_ipv6 = vip.ipv6.description
                list_ips.append('%s:%s:%s:%s:%s:%s:%s:%s' % (vip.ipv6.block1, vip.ipv6.block2, vip.ipv6.block3,
                                                             vip.ipv6.block4, vip.ipv6.block5, vip.ipv6.block6, vip.ipv6.block7, vip.ipv6.block8))
                # list_environment.append("%s - %s - %s" % (vip.ipv6.networkipv6.vlan.ambiente.divisao_dc.nome,vip.ipv6.networkipv6.vlan.ambiente.ambiente_logico.nome,vip.ipv6.networkipv6.vlan.ambiente.grupo_l3.nome))

                equips = vip.ipv6.ipv6equipament_set.all()

                for equip in equips:

                    if equip.equipamento.nome not in list_equips:

                        list_equips.append(equip.equipamento.nome)
        except Exception, e:
            pass

        vip_dict['ipv4_description'] = descricao_ipv4
        vip_dict['ipv6_description'] = descricao_ipv6
        vip_dict['ips'] = list_ips
        vip_dict['environments'] = list_environment
        vip_dict['equipments'] = list_equips
        vip_dict['is_more'] = True if len(equips) > 3 else False
        itens.append(vip_dict)

    return itens


class RequestVipGetIdIpResource(RestResource):

    log = logging.getLogger('RequestVipGetIdIpResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to find all Vip Requests by search parameters.

        URLs: /requestvip/get_by_ip_id/
        """

        self.log.info('Find all Vip Requests')

        try:

            # Commons Validations
            # User permission
            if not has_perm(user, AdminPermission.VIPS_REQUEST, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(
                request.raw_post_data, ['searchable_columns', 'asorting_cols'])

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            vip_map = networkapi_map.get('vip')
            if vip_map is None:
                msg = u'There is no value to the vip tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            start_record = vip_map.get('start_record')
            end_record = vip_map.get('end_record')
            asorting_cols = vip_map.get('asorting_cols')
            searchable_columns = vip_map.get('searchable_columns')
            custom_search = vip_map.get('custom_search')

            id_vip = vip_map.get('id_vip')
            ip = vip_map.get('ip')
            created_vip = vip_map.get('create')
            if created_vip == 'True':
                create = True
            elif created_vip == 'False':
                create = None
            else:
                create = created_vip

            # Business Rules

            # Start with all

            vip = RequisicaoVips.objects.all()

            if id_vip is not None and ip is not None:
                raise InvalidValueError(
                    None, 'id_vip - ip', '%s - %s' % (id_vip, ip))

            if id_vip is not None:
                # If id_vip is valid, add to filter
                if not is_valid_int_greater_zero_param(id_vip, False):
                    raise InvalidValueError(None, 'id_vip', id_vip)
                else:
                    vip = vip.filter(id=id_vip)

            if create is not None:
                # if create is valid, add to filter
                if not is_valid_boolean_param(create, False):
                    raise InvalidValueError(None, 'vip_criado', create)
                else:
                    vip = vip.filter(vip_criado=create)

            if ip is not None:
                # If ip is valid
                if not is_valid_string_minsize(ip, 1, False):
                    raise InvalidValueError(None, 'ip', ip)
                else:
                    blocks, ip, version = break_ip(ip)
                    try:
                        IPAddress(ip)
                    except ValueError, e:
                        raise InvalidValueError(None, 'ip', ip)

                    # Filter octs
                    if version == IP_VERSION.IPv4[0]:
                        # IP v4
                        oct1 = oct2 = oct3 = oct4 = Q()

                        if len(blocks[0]) != 0:
                            oct1 = Q(ip__oct1=blocks[0])
                        if len(blocks[1]) != 0:
                            oct2 = Q(ip__oct2=blocks[1])
                        if len(blocks[2]) != 0:
                            oct3 = Q(ip__oct3=blocks[2])
                        if len(blocks[3]) != 0:
                            oct4 = Q(ip__oct4=blocks[3])

                        vip = vip.filter(oct1 & oct2 & oct3 & oct4)
                    else:
                        # IP v6
                        oct1 = oct2 = oct3 = oct4 = oct5 = oct6 = oct7 = oct8 = Q()

                        if len(blocks[0]) != 0:
                            oct1 = Q(ipv6__block1__iexact=blocks[0])
                        if len(blocks[1]) != 0:
                            oct2 = Q(ipv6__block2__iexact=blocks[1])
                        if len(blocks[2]) != 0:
                            oct3 = Q(ipv6__block3__iexact=blocks[2])
                        if len(blocks[3]) != 0:
                            oct4 = Q(ipv6__block4__iexact=blocks[3])
                        if len(blocks[4]) != 0:
                            oct5 = Q(ipv6__block5__iexact=blocks[4])
                        if len(blocks[5]) != 0:
                            oct6 = Q(ipv6__block6__iexact=blocks[5])
                        if len(blocks[6]) != 0:
                            oct7 = Q(ipv6__block7__iexact=blocks[6])
                        if len(blocks[7]) != 0:
                            oct8 = Q(ipv6__block8__iexact=blocks[7])

                        vip = vip.filter(
                            oct1 & oct2 & oct3 & oct4 & oct5 & oct6 & oct7 & oct8)

            vip = vip.distinct()

            vip = vip.order_by('-pk')

            # Datatable paginator
            vip, total = build_query_to_datatable(
                vip, asorting_cols, custom_search, searchable_columns, start_record, end_record)

            itens = get_vips(vip)

            vip_map = dict()
            vip_map['vips'] = itens
            vip_map['total'] = total

            return self.response(dumps_networkapi(vip_map))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except BaseException, e:
            return self.response_error(1)
