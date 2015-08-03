# -*- coding:utf-8 -*-

"""
 Licensed to the Apache Software Foundation (ASF) under one or more
 contributor license agreements.  See the NOTICE file distributed with
 this work for additional information regarding copyright ownership.
 The ASF licenses this file to You under the Apache License, Version 2.0
 (the "License"); you may not use this file except in compliance with
 the License.  You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 """
from django.forms import model_to_dict
from networkapi.api_pools.views import reals_can_associate_server_pool
from networkapi.distributedlock import distributedlock, LOCK_VIP
from networkapi.error_message_utils import error_messages
from networkapi.exception import EnvironmentEnvironmentVipNotFoundError
from networkapi.ambiente.models import EnvironmentEnvironmentVip, Ambiente, EnvironmentVip
from networkapi.log import Log
from networkapi.api_vip_request.serializers import RequestVipSerializer, VipPortToPoolSerializer
from networkapi.requisicaovips.models import RequisicaoVips, VipPortToPool, ServerPool
from networkapi.util import is_valid_int_greater_zero_param, convert_boolean_to_int
from networkapi.api_vip_request import exceptions
from networkapi.api_rest import exceptions as api_exceptions


log = Log(__name__)


def get_by_pk(pk):
    """
    Get Vip Request By Pk

    :param pk: Identifier For Vip Request

    :return: Dict

    """

    if not is_valid_int_greater_zero_param(pk):
        raise exceptions.InvalidIdVipRequestException()

    vip_request = RequisicaoVips.objects.get(id=pk)

    data = vip_request.variables_to_map()
    data['id'] = vip_request.id
    data['validado'] = convert_boolean_to_int(vip_request.validado)
    data['vip_criado'] = convert_boolean_to_int(vip_request.vip_criado)
    data['id_ip'] = vip_request.ip_id
    data['id_ipv6'] = vip_request.ipv6_id
    data['id_healthcheck_expect'] = vip_request.healthcheck_expect_id
    data['l7_filter'] = vip_request.l7_filter
    data['rule_id'] = vip_request.rule_id

    pools = []

    vip_to_ports_query = VipPortToPool.objects.filter(requisicao_vip=vip_request)

    for vip_port in vip_to_ports_query:

        pools_members = []

        server_pool = vip_port.server_pool
        pool_raw = model_to_dict(server_pool)
        pool_raw["port_vip"] = vip_port.port_vip
        pool_raw["port_vip_id"] = vip_port.id

        for pool_member in server_pool.serverpoolmember_set.all():
            pools_member_raw = model_to_dict(pool_member)
            ipv4 = pool_member.ip
            ipv6 = pool_member.ipv6
            ip_equipment_set = ipv4 and ipv4.ipequipamento_set or ipv6 and ipv6.ipv6equipament_set
            ip_equipment_obj = ip_equipment_set.select_related().uniqueResult()
            healthcheck_type = pool_member.healthcheck and pool_member.healthcheck.healthcheck_type or ''
            pools_member_raw['healthcheck'] = {'healthcheck_type': healthcheck_type}
            pools_member_raw['equipment_name'] = ip_equipment_obj.equipamento.nome
            ip_formatted = ip_equipment_obj.ip.ip_formated

            if ipv4:
                pools_member_raw["ip"] = {'ip_formated': ip_formatted}
            else:
                pools_member_raw["ipv6"] = {'ip_formated': ip_formatted}

            pools_members.append(pools_member_raw)

        pool_raw['server_pool_members'] = pools_members
        pools.append(pool_raw)

    data["pools"] = pools

    return data


def save(request):
    """
    Save Vip Request

    :param request: Request
    :return: Data Serialized Post Save
    """

    data = request.DATA
    user = request.user

    req_vip_serializer = RequestVipSerializer(
        data=data
    )

    if not req_vip_serializer.is_valid():
        log.error(req_vip_serializer.errors)
        raise api_exceptions.ValidationException()

    obj_req_vip = req_vip_serializer.object

    # valid if pools member can linked by environment/environment vip relationship rule
    server_pool_ips_can_associate_with_vip_request(obj_req_vip)

    obj_req_vip.filter_valid = True
    obj_req_vip.validado = False
    set_l7_filter_for_vip(obj_req_vip)
    obj_req_vip.set_new_variables(data)
    obj_req_vip.save(user)

    for v_port in obj_req_vip.vip_ports_to_pools:
        v_port.requisicao_vip = obj_req_vip
        v_port.save(user)

    return req_vip_serializer.data


def update(request, pk):
    """
    Update Vip Request

    :param request:
    :param pk: Identifier Vip Request
    :return: Data Serialized Post Update
    """

    data = request.DATA
    user = request.user

    if not is_valid_int_greater_zero_param(pk):
        raise exceptions.InvalidIdVipRequestException()

    vip_ports = data.get("vip_ports_to_pools")

    req_vip_serializer = RequestVipSerializer(
        data=data
    )

    if not req_vip_serializer.is_valid():
        log.error(req_vip_serializer.errors)
        raise api_exceptions.ValidationException()

    RequisicaoVips.objects.get(pk=pk)

    with distributedlock(LOCK_VIP % pk):

        obj_req_vip = req_vip_serializer.object
        obj_req_vip.id = pk
        obj_req_vip.filter_valid = True
        obj_req_vip.validado = False
        set_l7_filter_for_vip(obj_req_vip)
        obj_req_vip.set_new_variables(data)
        obj_req_vip.save(user)

        vip_port_serializer = VipPortToPoolSerializer(data=vip_ports, many=True)

        if not vip_port_serializer.is_valid():
            raise api_exceptions.ValidationException("Invalid Port Vip To Pool")

        vip_port_to_pool_pks = [port['id'] for port in vip_ports if port.get('id')]

        vip_port_to_pool_to_remove = VipPortToPool.objects.filter(
            requisicao_vip=obj_req_vip
        ).exclude(
            id__in=vip_port_to_pool_pks
        )

        # valid if pools member can linked by environment/environment vip relationship rule
        server_pool_ips_can_associate_with_vip_request(obj_req_vip, vip_port_to_pool_to_remove)

        for v_port_to_del in vip_port_to_pool_to_remove:
            v_port_to_del.delete(user)

        for vip_port in vip_ports:
            vip_port_obj = VipPortToPool()
            vip_port_obj.id = vip_port.get('id')
            vip_port_obj.server_pool = ServerPool(id=vip_port.get('server_pool'))
            vip_port_obj.port_vip = vip_port.get('port_vip')
            vip_port_obj.requisicao_vip = obj_req_vip
            vip_port_obj.save(user)

        return req_vip_serializer.data


def set_l7_filter_for_vip(obj_req_vip):

    if obj_req_vip.rule:
        obj_req_vip.l7_filter = '\n'.join(
            obj_req_vip.rule.rulecontent_set.all().values_list(
                'content',
                flat=True
            )
        )


def _get_server_pool_list(vip_request):

    server_pool_list = set()

    # server pool already related
    for vip_pool in vip_request.vipporttopool_set.all():
        server_pool_list.add(vip_pool.server_pool)

    # server pool to add
    for vip_pool in vip_request.vip_ports_to_pools:
        server_pool_list.add(vip_pool.server_pool)

    return list(server_pool_list)


def _reals_can_associate_server_pool_by_environment_vip_on_request_vip(server_pool, server_pool_member_list, environment_vip):

    try:
        environment_list_related = EnvironmentEnvironmentVip.get_environment_list_by_environment_vip(environment_vip)

        ipv4_list, ipv6_list = [], []

        for server_pool_member in server_pool_member_list:
            if server_pool_member.ip:
                ipv4_list.append(server_pool_member.ip)
            else:
                ipv6_list.append(server_pool_member.ipv6)

        for ipv4 in ipv4_list:
            environment = Ambiente.objects.filter(vlan__networkipv4__ip=ipv4).uniqueResult()
            if environment not in environment_list_related:
                raise api_exceptions.EnvironmentEnvironmentVipNotBoundedException(
                    error_messages.get(396) % (environment.name, ipv4.ip_formated, environment_vip.name)
                )

        for ipv6 in ipv6_list:
            environment = Ambiente.objects.filter(vlan__networkipv6__ipv6=ipv6).uniqueResult()
            if environment not in environment_list_related:
                raise api_exceptions.EnvironmentEnvironmentVipNotBoundedException(
                    error_messages.get(396) % (server_pool.environment.name, ipv6.ip_formated, environment_vip.name)
                )

    except Exception, error:
        log.error(error)
        raise error


def _get_server_pool_list_by_vip_port_to_pool(vip_port_to_pool_to_remove):
    server_pool_exclude_list = set()

    for vip_port_to_pool in vip_port_to_pool_to_remove:
        server_pool_exclude_list.add(vip_port_to_pool.server_pool)

    return list(server_pool_exclude_list)


def server_pool_ips_can_associate_with_vip_request(vip_request, vip_port_to_pool_to_remove=[]):

    try:
        environment_vip = EnvironmentVip.get_by_values(vip_request.finalidade, vip_request.cliente, vip_request.ambiente)

        server_pool_list_add_list = _get_server_pool_list(vip_request)
        server_pool_list_remove_list = _get_server_pool_list_by_vip_port_to_pool(vip_port_to_pool_to_remove)

        for server_pool in server_pool_list_add_list:

            if server_pool not in server_pool_list_remove_list:
                server_pool_member_list = server_pool.serverpoolmember_set.all()
                _reals_can_associate_server_pool_by_environment_vip_on_request_vip(server_pool, server_pool_member_list, environment_vip)

    except Exception, error:
        log.error(error)
        raise error


def _get_validation_params(ip, server_pool, env_vip_description, ip_type='ipv4'):

    if ip_type == 'ipv4':
        env = ip.networkipv4.vlan.ambiente
        env_description = '{} - {} - {}'.format(env.divisao_dc.nome, env.ambiente_logico.nome, env.grupo_l3.nome)
    else:
        env = ip.networkipv6.vlan.ambiente
        env_description = '{} - {} - {}'.format(env.divisao_dc.nome, env.ambiente_logico.nome, env.grupo_l3.nome)

    return [ip.ip_formated, server_pool.identifier, env_description, env_vip_description]