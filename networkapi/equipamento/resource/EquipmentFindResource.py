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

"""
"""

from django.db.models import Q
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.grupo.models import GrupoError
from networkapi.infrastructure.xml_utils import dumps_networkapi, loads
from networkapi.log import Log
from networkapi.rest import RestResource
from networkapi.util import is_valid_string_minsize, is_valid_int_greater_zero_param, is_valid_boolean_param,\
    cache_function
from networkapi.exception import InvalidValueError
from networkapi.infrastructure.ipaddr import IPAddress
from string import split
from networkapi.ambiente.models import IP_VERSION, Ambiente
from networkapi.infrastructure.datatable import build_query_to_datatable
from django.forms.models import model_to_dict
from networkapi.equipamento.models import Equipamento, EquipamentoError
from networkapi.ip.models import Ip, Ipv6
from networkapi import ambiente
from networkapi.environment_settings import EQUIPMENT_CACHE_TIME


def break_ip(ip):
    """
    Returns array of each octs and string with ip
    """

    if "." in ip and ":" in ip:
        raise InvalidValueError(None, 'ip', ip)

    if "." in ip:
        # IPv4
        blocks = split(ip, ".")

        if len(blocks) != 4:
            raise InvalidValueError(None, 'ip', ip)

        version = IP_VERSION.IPv4[0]

    elif ":" in ip:
        # IPv6
        blocks = split(ip, ":")

        if len(blocks) != 8:
            raise InvalidValueError(None, 'ip', ip)

        version = IP_VERSION.IPv6[0]

    else:
        raise InvalidValueError(None, 'ip', ip)

    # Make copy
    unchanged = blocks[:]

    for i, block in enumerate(blocks):
        if len(block) == 0:
            blocks[i] = "0"

    ip_str = ""
    if version == IP_VERSION.IPv4[0]:
        ip_str = blocks[0] + "." + blocks[1] + \
            "." + blocks[2] + "." + blocks[3]

    else:
        # If IPv6, fill with 0 on the left
        for i, block in enumerate(unchanged):
            if len(block) != 4 and len(block) != 0:
                unchanged[i] = block.rjust(4, "0")
        ip_str = blocks[0] + ":" + blocks[1] + ":" + blocks[2] + ":" + blocks[3] + \
            ":" + blocks[4] + ":" + blocks[5] + \
            ":" + blocks[6] + ":" + blocks[7]

    return unchanged, ip_str, version


def get_equips(equipments):
    """
    Join all properties needed
    """

    itens = []
    for equip in equipments:
        equip_dict = prepares_equips(equip)
        itens.append(equip_dict)

    return itens


@cache_function(EQUIPMENT_CACHE_TIME, True)
def prepares_equips(equip):
    equip_dict = dict()
    equip_dict = model_to_dict(equip)
    equip_dict["tipo_equipamento"] = equip.tipo_equipamento.tipo_equipamento

    group_list = []
    for g in equip.grupos.all():
        group_dict = dict()
        group_dict["nome"] = g.nome
        group_list.append(group_dict)

    ips_list = []
    env_list = []
    for ipe in equip.ipequipamento_set.all():

        ipp = Ip.objects.select_related().get(id=ipe.ip.id)

        ip_dict = dict()
        ip_dict["ip"] = str(
            ipp.oct1) + "." + str(ipp.oct2) + "." + str(ipp.oct3) + "." + str(ipp.oct4)
        ip_dict["vlan"] = ipp.networkipv4.vlan.nome
        ip_dict["ambiente"] = ipp.networkipv4.vlan.ambiente.divisao_dc.nome + "-" + \
            ipp.networkipv4.vlan.ambiente.ambiente_logico.nome + \
            "-" + ipp.networkipv4.vlan.ambiente.grupo_l3.nome
        env_list.append(ipp.networkipv4.vlan.ambiente.id)

        ips_list.append(ip_dict)

    for ipv6e in equip.ipv6equipament_set.all():

        ipp = Ipv6.objects.select_related().get(id=ipv6e.ip.id)

        ipv6_dict = dict()
        ipv6_dict["ip"] = ipp.block1 + ":" + ipp.block2 + ":" + ipp.block3 + ":" + \
            ipp.block4 + ":" + ipp.block5 + ":" + \
            ipp.block6 + ":" + ipp.block7 + ":" + ipp.block8
        ipv6_dict["vlan"] = ipp.networkipv6.vlan.nome
        ipv6_dict["ambiente"] = ipp.networkipv6.vlan.ambiente.divisao_dc.nome + "-" + \
            ipp.networkipv6.vlan.ambiente.ambiente_logico.nome + \
            "-" + ipp.networkipv6.vlan.ambiente.grupo_l3.nome
        env_list.append(ipp.networkipv6.vlan.ambiente.id)

        ips_list.append(ipv6_dict)

    for env in equip.equipamentoambiente_set.all():
        if not env.ambiente.id in env_list:

            ambiente = Ambiente.objects.select_related().get(
                id=env.ambiente.id)

            ip_dict = dict()
            ip_dict["ip"] = "-"
            ip_dict["vlan"] = "-"
            ip_dict["ambiente"] = ambiente.divisao_dc.nome + "-" + \
                ambiente.ambiente_logico.nome + "-" + ambiente.grupo_l3.nome
            ips_list.append(ip_dict)

    equip_dict["grupos"] = group_list
    equip_dict["ips"] = ips_list

    if len(ips_list) > 3:
        equip_dict["is_more"] = True
    else:
        equip_dict["is_more"] = False

    if len(group_list) > 3:
        equip_dict["is_more_group"] = True
    else:
        equip_dict["is_more_group"] = False

    return equip_dict


class EquipmentFindResource(RestResource):

    log = Log('EquipmentFindResource')

    def handle_post(self, request, user, *args, **kwargs):
        """Handles POST requests to find all Equipments by search parameters.

        URLs: /equipment/find/
        """

        self.log.info('Find all Equipments')

        try:

            # Commons Validations

            # User permission
            if not has_perm(user, AdminPermission.EQUIPMENT_MANAGEMENT, AdminPermission.READ_OPERATION):
                self.log.error(
                    u'User does not have permission to perform the operation.')
                return self.not_authorized()

            # Business Validations

            # Load XML data
            xml_map, attrs_map = loads(
                request.raw_post_data, ["searchable_columns", "asorting_cols"])

            # XML data format
            networkapi_map = xml_map.get('networkapi')
            if networkapi_map is None:
                msg = u'There is no value to the networkapi tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)
            equipment_map = networkapi_map.get('equipamento')
            if equipment_map is None:
                msg = u'There is no value to the equipment tag of XML request.'
                self.log.error(msg)
                return self.response_error(3, msg)

            # Get XML data
            start_record = equipment_map.get("start_record")
            end_record = equipment_map.get("end_record")
            asorting_cols = equipment_map.get("asorting_cols")
            searchable_columns = equipment_map.get("searchable_columns")
            custom_search = equipment_map.get("custom_search")

            name = equipment_map.get("nome")
            iexact = equipment_map.get("exato")
            environment = equipment_map.get("ambiente")
            equip_type = equipment_map.get("tipo_equipamento")
            group = equipment_map.get("grupo")
            ip = equipment_map.get("ip")

            # Business Rules

            # Start with alls
            equip = Equipamento.objects.select_related().all()

            if name is not None:
                # If name is valid, add to filter
                if not is_valid_string_minsize(name, 3, False):
                    raise InvalidValueError(None, 'nome', name)
                else:
                    # Iexact must be valid to add name to filter
                    if not is_valid_boolean_param(iexact, False):
                        raise InvalidValueError(None, 'exato', iexact)
                    else:
                        if (iexact is None) or (iexact == "False") or (iexact == "0"):
                            iexact = False

                        if iexact:
                            equip = equip.filter(nome=name)
                        else:
                            equip = equip.filter(nome__icontains=name)

            # If environment is valid, add to filter
            if environment is not None:
                if not is_valid_int_greater_zero_param(environment, False):
                    raise InvalidValueError(None, 'ambiente', environment)
                else:
                    equip = equip.filter(
                        equipamentoambiente__ambiente__pk=environment)

            if equip_type is not None:
                # If equip_type is valid, add to filter
                if not is_valid_int_greater_zero_param(equip_type, False):
                    raise InvalidValueError(
                        None, 'tipo_equipamento', equip_type)
                else:
                    equip = equip.filter(tipo_equipamento__pk=equip_type)

            if group is not None:
                # If equip_type is valid, add to filter
                if not is_valid_int_greater_zero_param(group, False):
                    raise InvalidValueError(None, 'grupo', group)
                else:
                    equip = equip.filter(grupos__pk=group)

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
                            oct1 = Q(ipequipamento__ip__oct1=blocks[0])
                        if len(blocks[1]) != 0:
                            oct2 = Q(ipequipamento__ip__oct2=blocks[1])
                        if len(blocks[2]) != 0:
                            oct3 = Q(ipequipamento__ip__oct3=blocks[2])
                        if len(blocks[3]) != 0:
                            oct4 = Q(ipequipamento__ip__oct4=blocks[3])

                        equip = equip.filter(oct1 & oct2 & oct3 & oct4)
                    else:
                        # IP v6
                        oct1 = oct2 = oct3 = oct4 = oct5 = oct6 = oct7 = oct8 = Q()

                        if len(blocks[0]) != 0:
                            oct1 = Q(
                                ipv6equipament__ip__block1__iexact=blocks[0])
                        if len(blocks[1]) != 0:
                            oct2 = Q(
                                ipv6equipament__ip__block2__iexact=blocks[1])
                        if len(blocks[2]) != 0:
                            oct3 = Q(
                                ipv6equipament__ip__block3__iexact=blocks[2])
                        if len(blocks[3]) != 0:
                            oct4 = Q(
                                ipv6equipament__ip__block4__iexact=blocks[3])
                        if len(blocks[4]) != 0:
                            oct5 = Q(
                                ipv6equipament__ip__block5__iexact=blocks[4])
                        if len(blocks[5]) != 0:
                            oct6 = Q(
                                ipv6equipament__ip__block6__iexact=blocks[5])
                        if len(blocks[6]) != 0:
                            oct7 = Q(
                                ipv6equipament__ip__block7__iexact=blocks[6])
                        if len(blocks[7]) != 0:
                            oct8 = Q(
                                ipv6equipament__ip__block8__iexact=blocks[7])

                        equip = equip.filter(
                            oct1 & oct2 & oct3 & oct4 & oct5 & oct6 & oct7 & oct8)

            equip = equip.distinct()

            # Datatable paginator
            equip, total = build_query_to_datatable(
                equip, asorting_cols, custom_search, searchable_columns, start_record, end_record)

            itens = get_equips(equip)

            equipment_map = dict()
            equipment_map["equipamento"] = itens
            equipment_map["total"] = total

            return self.response(dumps_networkapi(equipment_map))

        except InvalidValueError, e:
            self.log.error(
                u'Parameter %s is invalid. Value: %s.', e.param, e.value)
            return self.response_error(269, e.param, e.value)
        except (EquipamentoError, GrupoError):
            return self.response_error(1)
        except BaseException, e:
            return self.response_error(1)
