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
from django.forms.models import model_to_dict

from networkapi.admin_permission import AdminPermission
from networkapi.ambiente.models import IP_VERSION
from networkapi.auth import has_perm
from networkapi.exception import InvalidValueError
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.datatable import build_query_to_datatable
from networkapi.infrastructure.ipaddr import IPNetwork
from networkapi.infrastructure.xml_utils import dumps_networkapi
from networkapi.infrastructure.xml_utils import loads
from networkapi.rest import RestResource
from networkapi.settings import VLAN_CACHE_TIME
from networkapi.util import cache_function
from networkapi.util import is_valid_boolean_param
from networkapi.util import is_valid_int_greater_equal_zero_param
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.util import is_valid_string_minsize
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanError


def break_network(network):
    """
    Returns array of each octs and string with network
    """

    if '.' in network and ':' in network:
        raise InvalidValueError(None, 'rede', network)

    if '.' in network:
        # NetworkIPv4
        blocks = split(network, '.')

        if len(blocks) != 4:
            raise InvalidValueError(None, 'rede', network)

        last = split(blocks[3], '/')
        if len(last) == 2:
            blocks[3] = last[0]
            blocks.append(last[1])

        if len(blocks) != 5:
            raise InvalidValueError(None, 'rede', network)

        version = IP_VERSION.IPv4[0]

    elif ':' in network:
        # NetworkIPv6
        blocks = split(network, ':')

        if len(blocks) != 8:
            raise InvalidValueError(None, 'rede', network)

        last = split(blocks[7], '/')
        if len(last) == 2:
            blocks[7] = last[0]
            blocks.append(last[1])

        if len(blocks) != 9:
            raise InvalidValueError(None, 'rede', network)

        version = IP_VERSION.IPv6[0]

    else:
        raise InvalidValueError(None, 'rede', network)

    # Make copy
    unchanged = blocks[:]

    for i, block in enumerate(blocks):
        if len(block) == 0:
            blocks[i] = '0'

    network_str = ''
    if version == IP_VERSION.IPv4[0]:
        network_str = blocks[0] + '.' + blocks[1] + \
            '.' + blocks[2] + '.' + blocks[3]
        if blocks[4] != '0':
            network_str = network_str + '/' + blocks[4]
    else:
        # If Network IPv6, fill with 0 on the left
        for i, block in enumerate(unchanged):
            if len(block) != 4 and len(block) != 0 and i != 8:
                unchanged[i] = block.rjust(4, '0')
        network_str = blocks[0] + ':' + blocks[1] + ':' + blocks[2] + ':' + blocks[
            3] + ':' + blocks[4] + ':' + blocks[5] + ':' + blocks[6] + ':' + blocks[7]
        if blocks[8] != '0':
            network_str = network_str + '/' + blocks[8]

    return unchanged, network_str, version


def get_networks(vlans, half=True):
    """
    Join networks of vlan
    """

    itens = []
    for vlan in vlans:
        vlan_dict = prepares_network(vlan, half)
        itens.append(vlan_dict)

    return itens

#@cache_function(VLAN_CACHE_TIME)


def prepares_network(vlan, half):
    vlan_dict = dict()
    if not half:
        vlan_dict = model_to_dict(vlan)
        vlan_dict['ambiente_name'] = vlan.ambiente.divisao_dc.nome + ' - ' + \
            vlan.ambiente.ambiente_logico.nome + \
            ' - ' + vlan.ambiente.grupo_l3.nome

    vlan_dict['is_more'] = False
    netv4_itens = []
    for netv4 in vlan.networkipv4_set.all():
        net_dict = dict()
        net = str(netv4.oct1) + '.' + str(netv4.oct2) + '.' + \
            str(netv4.oct3) + '.' + str(netv4.oct4) + '/' + str(netv4.block)
        net_dict['network'] = IPNetwork(net).exploded
        net_dict['id'] = netv4.id
        if not half:
            net_dict['tipo_rede_name'] = netv4.network_type.tipo_rede

            equip_itens = []
            for ip in netv4.ip_set.all():
                for ip_equip in ip.ipequipamento_set.all():
                    if not ip_equip.equipamento.nome in equip_itens:
                        for equip_amb in ip_equip.equipamento.equipamentoambiente_set.all():
                            if equip_amb.ambiente == vlan.ambiente and equip_amb.is_router:
                                equip_itens.append(ip_equip.equipamento.nome)

            if len(equip_itens) == 0:
                equip_itens.append('&nbsp;')
            elif len(equip_itens) > 3:
                vlan_dict['is_more'] = True

            net_dict['equipamentos'] = equip_itens

        netv4_itens.append(net_dict)

    netv6_itens = []
    for netv6 in vlan.networkipv6_set.all():
        net_dict = dict()
        net = str(netv6.block1) + ':' + str(netv6.block2) + ':' + str(netv6.block3) + ':' + str(netv6.block4) + ':' + \
            str(netv6.block5) + ':' + str(netv6.block6) + ':' + \
            str(netv6.block7) + ':' + \
            str(netv6.block8) + '/' + str(netv6.block)
        net_dict['network'] = IPNetwork(net).compressed
        net_dict['id'] = netv6.id
        if not half:
            net_dict['tipo_rede_name'] = netv6.network_type.tipo_rede

            equip_itens = []
            for ip in netv6.ipv6_set.all():
                for ip_equip in ip.ipv6equipament_set.all():
                    if not ip_equip.equipamento.nome in equip_itens:
                        for equip_amb in ip_equip.equipamento.equipamentoambiente_set.all():
                            if equip_amb.ambiente == vlan.ambiente and equip_amb.is_router:
                                equip_itens.append(ip_equip.equipamento.nome)

            if len(equip_itens) == 0:
                equip_itens.append('&nbsp;')
            elif len(equip_itens) > 3:
                vlan_dict['is_more'] = True

            net_dict['equipamentos'] = equip_itens

        netv6_itens.append(net_dict)

    vlan_dict['id'] = vlan.id
    vlan_dict['redeipv4'] = netv4_itens
    vlan_dict['redeipv6'] = netv6_itens

    if (len(netv4_itens) > 1):
        if(vlan_dict['is_more'] is True) or (len(netv4_itens) > 3):
            vlan_dict['more_than_three'] = True
    if (len(netv6_itens) > 1):
        if(vlan_dict['is_more'] is True) or (len(netv6_itens) > 3):
            vlan_dict['more_than_three'] = True

    if len(netv4_itens) > 3:
        vlan_dict['is_more'] = True
    if len(netv6_itens) > 3:
        vlan_dict['is_more'] = True

    return vlan_dict


def get_networks_simple(vlans):
    """
    Join networks of vlan
    """

    itens = []
    for vlan in vlans:
        vlan_dict = prepares_network_simple(vlan)
        itens.append(vlan_dict)

    return itens


def prepares_network_simple(vlan):
    vlan_dict = dict()

    netv4_itens = []
    for netv4 in vlan.networkipv4_set.all():
        net_dict = dict()
        net = str(netv4.oct1) + '.' + str(netv4.oct2) + '.' + \
            str(netv4.oct3) + '.' + str(netv4.oct4) + '/' + str(netv4.block)
        net_dict['network'] = IPNetwork(net).exploded
        net_dict['id'] = netv4.id

        netv4_itens.append(net_dict)

    netv6_itens = []
    for netv6 in vlan.networkipv6_set.all():
        net_dict = dict()
        net = str(netv6.block1) + ':' + str(netv6.block2) + ':' + str(netv6.block3) + ':' + str(netv6.block4) + ':' + \
            str(netv6.block5) + ':' + str(netv6.block6) + ':' + \
            str(netv6.block7) + ':' + \
            str(netv6.block8) + '/' + str(netv6.block)
        net_dict['network'] = IPNetwork(net).compressed
        net_dict['id'] = netv6.id
        netv6_itens.append(net_dict)

    vlan_dict['id'] = vlan.id
    vlan_dict['redeipv4'] = netv4_itens
    vlan_dict['redeipv6'] = netv6_itens

    return vlan_dict


def verify_subnet(vlan, network_ip, version):
    if version == IP_VERSION.IPv4[0]:
        key = 'redeipv4'
    else:
        key = 'redeipv6'

    # One vlan may have many networks, iterate over it
    for net in vlan[key]:
        ip_net = IPNetwork(net['network'])
        # If some network, inside this vlan, is subnet of network search param
        if ip_net in network_ip:
            # This vlan must be in vlans founded, dont need to continue
            # checking
            return True
        # If some network, inside this vlan, is supernet of network search
        # param
        if network_ip in ip_net:
            # This vlan must be in vlans founded, dont need to continue
            # checking
            return True

    # If dont found any subnet return None
    return False


class VlanFindResource(RestResource):

    log = logging.getLogger('VlanFindResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to find all VLANs by search parameters.

        URLs: /vlan/find/
        """

        self.log.info('Find all VLANs')

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.VLAN_MANAGEMENT, AdminPermission.READ_OPERATION):
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
            vlan_map = networkapi_map.get('vlan')
            if vlan_map is None:
                msg = u'There is no value to the vlan tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            start_record = vlan_map.get('start_record')
            end_record = vlan_map.get('end_record')
            asorting_cols = vlan_map.get('asorting_cols')
            searchable_columns = vlan_map.get('searchable_columns')
            custom_search = vlan_map.get('custom_search')

            number = vlan_map.get('numero')
            name = vlan_map.get('nome')
            iexact = vlan_map.get('exato')
            environment = vlan_map.get('ambiente')
            net_type = vlan_map.get('tipo_rede')
            network = vlan_map.get('rede')
            ip_version = vlan_map.get('versao')
            subnet = vlan_map.get('subrede')
            acl = vlan_map.get('acl')

            # Business Rules

            # Start with alls
            vlans = Vlan.objects.all().prefetch_related(
                'networkipv4_set', 'networkipv6_set')

            if number is not None:
                # If number is valid, add to filter
                if not is_valid_int_greater_zero_param(number, False):
                    raise InvalidValueError(None, 'numero', number)
                else:
                    vlans = vlans.filter(num_vlan=number)

            if name is not None:
                # If name is valid, add to filter
                if not is_valid_string_minsize(name, 1, False):
                    raise InvalidValueError(None, 'nome', name)
                else:
                    # Iexact must be valid to add name to filter
                    if not is_valid_boolean_param(iexact, False):
                        raise InvalidValueError(None, 'exato', iexact)
                    else:
                        if (iexact is None) or (iexact == 'False') or (iexact == '0'):
                            iexact = False

                        if iexact:
                            vlans = vlans.filter(nome=name)
                        else:
                            vlans = vlans.filter(nome__icontains=name)

            # If environment is valid, add to filter
            if environment is not None:
                if not is_valid_int_greater_zero_param(environment, False):
                    raise InvalidValueError(None, 'ambiente', environment)
                else:
                    vlans = vlans.filter(ambiente__pk=environment)

            if net_type is not None:
                # If net_type is valid, add to filter
                if not is_valid_int_greater_zero_param(net_type, False):
                    raise InvalidValueError(None, 'tipo_rede', net_type)
                else:
                    q1 = Q(networkipv4__network_type__id=net_type)
                    q2 = Q(networkipv6__network_type__id=net_type)
                    vlans = vlans.filter(q1 | q2)

            if acl is not None:
                # If acl is valid, add to filter
                if not is_valid_boolean_param(acl, False):
                    raise InvalidValueError(None, 'acl', acl)
                else:
                    if (acl is None) or (acl == 'False') or (acl == '0'):
                        acl = False
                    # If acl is true, only show vlans with false acl_valida
                    if acl:
                        vlans = vlans.filter(acl_valida=False)

            # If ip_version is valid
            if not is_valid_int_greater_equal_zero_param(ip_version):
                raise InvalidValueError(None, 'versao', ip_version)
            else:
                if ip_version == '0':
                    vlans = vlans.filter(
                        Q(networkipv6__isnull=True) | Q(networkipv4__isnull=False))
                elif ip_version == '1':
                    vlans = vlans.filter(
                        Q(networkipv4__isnull=True) | Q(networkipv6__isnull=False))

            if network is not None:
                # If network is valid
                if not is_valid_string_minsize(network, 1, False):
                    raise InvalidValueError(None, 'rede', network)
                else:
                    blocks, network, version = break_network(network)
                    try:
                        network_ip = IPNetwork(network)
                    except ValueError, e:
                        raise InvalidValueError(None, 'rede', network)

                # If subnet is valid, add to filter
                if not (subnet == '0' or subnet == '1'):
                    raise InvalidValueError(None, 'subrede', subnet)
                else:
                    # If subnet is 0, only filter network octs
                    if subnet == '0':

                        # Filter octs
                        if version == IP_VERSION.IPv4[0]:
                            # Network IP v4
                            oct1 = Q()
                            oct2 = Q()
                            oct3 = Q()
                            oct4 = Q()
                            blk = Q()

                            if len(blocks[0]) != 0:
                                oct1 = Q(networkipv4__oct1=blocks[0])
                            if len(blocks[1]) != 0:
                                oct2 = Q(networkipv4__oct2=blocks[1])
                            if len(blocks[2]) != 0:
                                oct3 = Q(networkipv4__oct3=blocks[2])
                            if len(blocks[3]) != 0:
                                oct4 = Q(networkipv4__oct4=blocks[3])
                            if len(blocks[4]) != 0:
                                blk = Q(networkipv4__block=blocks[4])

                            vlans = vlans.filter(
                                oct1 & oct2 & oct3 & oct4 & blk)
                        else:
                            # Network IP v6
                            oct1 = Q()
                            oct2 = Q()
                            oct3 = Q()
                            oct4 = Q()
                            oct5 = Q()
                            oct6 = Q()
                            oct7 = Q()
                            oct8 = Q()
                            blk = Q()

                            if len(blocks[0]) != 0:
                                oct1 = Q(networkipv6__block1__iexact=blocks[0])
                            if len(blocks[1]) != 0:
                                oct2 = Q(networkipv6__block2__iexact=blocks[1])
                            if len(blocks[2]) != 0:
                                oct3 = Q(networkipv6__block3__iexact=blocks[2])
                            if len(blocks[3]) != 0:
                                oct4 = Q(networkipv6__block4__iexact=blocks[3])
                            if len(blocks[4]) != 0:
                                oct5 = Q(networkipv6__block5__iexact=blocks[4])
                            if len(blocks[5]) != 0:
                                oct6 = Q(networkipv6__block6__iexact=blocks[5])
                            if len(blocks[6]) != 0:
                                oct7 = Q(networkipv6__block7__iexact=blocks[6])
                            if len(blocks[7]) != 0:
                                oct8 = Q(networkipv6__block8__iexact=blocks[7])
                            if len(blocks[8]) != 0:
                                blk = Q(networkipv6__block=blocks[8])

                            vlans = vlans.filter(
                                oct1 & oct2 & oct3 & oct4 & oct5 & oct6 & oct7 & oct8 & blk)
                    # If subnet is 1
                    else:

                        if version == IP_VERSION.IPv4[0]:
                            expl = split(network_ip.network.exploded, '.')
                        else:
                            expl = split(network_ip.network.exploded, ':')

                        expl.append(str(network_ip.prefixlen))

                        if blocks != expl:
                            raise InvalidValueError(None, 'rede', network)

                        # First, get all vlans filtered until now
                        itens = get_networks_simple(vlans)

                        ids_exclude = []
                        # Then iterate over it to verify each vlan
                        for vlan in itens:

                            is_subnet = verify_subnet(
                                vlan, network_ip, version)
                            if not is_subnet:
                                ids_exclude.append(vlan['id'])

                        vlans = vlans.exclude(id__in=ids_exclude)

            # Custom order
            if asorting_cols:
                if 'ambiente' in asorting_cols:
                    vlans = vlans.order_by(
                        'ambiente__divisao_dc__nome', 'ambiente__ambiente_logico__nome', 'ambiente__grupo_l3__nome')
                    asorting_cols.remove('ambiente')
                if '-ambiente' in asorting_cols:
                    vlans = vlans.order_by(
                        '-ambiente__divisao_dc__nome', '-ambiente__ambiente_logico__nome', '-ambiente__grupo_l3__nome')
                    asorting_cols.remove('-ambiente')
                if 'tipo_rede' in asorting_cols:
                    vlans = vlans.order_by(
                        'networkipv4__network_type__tipo_rede', 'networkipv6__network_type__tipo_rede')
                    asorting_cols.remove('tipo_rede')
                if '-tipo_rede' in asorting_cols:
                    vlans = vlans.order_by(
                        '-networkipv4__network_type__tipo_rede', '-networkipv6__network_type__tipo_rede')
                    asorting_cols.remove('-tipo_rede')
                if 'network' in asorting_cols:
                    vlans = vlans.order_by('networkipv4__oct1', 'networkipv4__oct2', 'networkipv4__oct3', 'networkipv4__oct4', 'networkipv4__block', 'networkipv6__block1', 'networkipv6__block2',
                                           'networkipv6__block3', 'networkipv6__block4', 'networkipv6__block5', 'networkipv6__block6', 'networkipv6__block7', 'networkipv6__block8', 'networkipv6__block')
                    asorting_cols.remove('network')
                if '-network' in asorting_cols:
                    vlans = vlans.order_by('-networkipv4__oct1', '-networkipv4__oct2', '-networkipv4__oct3', '-networkipv4__oct4', '-networkipv4__block', '-networkipv6__block1', '-networkipv6__block2',
                                           '-networkipv6__block3', '-networkipv6__block4', '-networkipv6__block5', '-networkipv6__block6', '-networkipv6__block7', '-networkipv6__block8', '-networkipv6__block')
                    asorting_cols.remove('-network')

            vlans = vlans.distinct()

            # Datatable paginator
            vlans, total = build_query_to_datatable(
                vlans, asorting_cols, custom_search, searchable_columns, start_record, end_record)
            vlans = vlans.prefetch_related('ambiente',
                                           'networkipv4_set__network_type',
                                           'networkipv4_set__ip_set__ipequipamento_set__equipamento__equipamentoambiente_set__ambiente',
                                           'networkipv6_set__network_type',
                                           'networkipv6_set__ipv6_set__ipv6equipament_set__equipamento__equipamentoambiente_set__ambiente')

            itens = get_networks(vlans, False)

            vlan_map = dict()
            vlan_map['vlan'] = itens
            vlan_map['total'] = total

            return self.response(dumps_networkapi(vlan_map))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except (VlanError, GrupoError):
            return self.response_error(1)
        except BaseException, e:
            return self.response_error(1)
