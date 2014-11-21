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

from django.db.transaction import commit_on_success
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from networkapi.log import Log
from networkapi.distributedlock import distributedlock, LOCK_VIP
from networkapi.api_vip_request.permissions import Read, Write
from networkapi.requisicaovips.models import ServerPool, VipPortToPool, \
    RequisicaoVips
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.pools import exceptions as pool_exceptions
from networkapi.api_vip_request import exceptions
from networkapi.ambiente.models import EnvironmentVip, Ambiente
from networkapi.api_vip_request.serializers import EnvironmentOptionsSerializer, \
    RequesVipSerializer, VipPortToPoolSerializer
from networkapi.equipamento.models import Equipamento, EquipamentoNotFoundError, \
    EquipamentoError
from networkapi.ip.models import IpNotFoundByEquipAndVipError
from networkapi.exception import InvalidValueError, EnvironmentVipNotFoundError

log = Log(__name__)


@api_view(['POST'])
@permission_classes((IsAuthenticated, Read))
@commit_on_success
def add_pools(request):
    """
    Add Pools For Vip Request.
    """
    try:
        pool_ids = request.DATA.get('pool_ids')
        vip_request_id = request.DATA.get('vip_request_id')

        vip_request_obj = RequisicaoVips.objects.get(id=vip_request_id)

        for pool_id in pool_ids:

            pool_obj = ServerPool.objects.get(id=pool_id)

            vip_port_pool_obj = VipPortToPool(
                requisicao_vip=vip_request_obj,
                server_pool=pool_obj,
                port_vip=pool_obj.default_port
            )

            vip_port_pool_obj.save(request.user)

        return Response(status=status.HTTP_201_CREATED)

    except RequisicaoVips.DoesNotExist, exception:
        log.error(exception)
        raise exceptions.VipRequestDoesNotExistException()

    except ServerPool.DoesNotExist, exception:
        log.error(exception)
        raise pool_exceptions.PoolDoesNotExistException()

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST'])
@permission_classes((IsAuthenticated, Write))
@commit_on_success
def delete(request):
    """
    Delete Vip Request And Optional Related Pools.
    """
    try:
        ids = request.DATA.get('ids')
        delete_pools = request.DATA.get('delete_pools', True)

        if delete_pools:
            vports_pool = VipPortToPool.objects.filter(
                requisicao_vip__id__in=ids
            )

            for vport in vports_pool:

                server_pool = vport.server_pool

                related = VipPortToPool.objects.filter(
                    server_pool=server_pool
                ).exclude(
                    requisicao_vip=vport.requisicao_vip
                )

                if related:
                    raise pool_exceptions.PoolConstraintVipException()

                vport.delete(request.user)

                for member in server_pool.serverpoolmember_set.all():
                    member.delete(request.user)

                server_pool.delete(request.user)

        vips_request = RequisicaoVips.objects.filter(id__in=ids)
        for vrequest in vips_request:
            vrequest.delete(request.user)

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
@commit_on_success
def list_environment_by_environment_vip(request, environment_vip_id):

    try:

        env_vip = EnvironmentVip.objects.get(id=environment_vip_id)

        environment_query = Ambiente.objects.filter(
            Q(vlan__networkipv4__ambient_vip=env_vip) |
            Q(vlan__networkipv6__ambient_vip=env_vip)
        ).distinct()

        serializer_environment = EnvironmentOptionsSerializer(
            environment_query,
            many=True
        )

        return Response(serializer_environment.data)

    except EnvironmentVip.DoesNotExist, exception:
        log.error(exception)
        raise api_exceptions.ObjectDoesNotExistException('Environment Vip Does Not Exist')

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


def _set_l7_filter_for_vip(obj_req_vip):

    if obj_req_vip.rule:
        obj_req_vip.l7_filter = '\n'.join(
            obj_req_vip.rule.rulecontent_set.all().values_list(
                'content',
                flat=True
            )
        )


@api_view(['POST', 'PUT'])
@permission_classes((IsAuthenticated, Write))
@commit_on_success
def save(request, pk=None):

    try:

        data = request.DATA
        user = request.user

        vip_ports = data.get("vip_ports_to_pools")

        req_vip_serializer = RequesVipSerializer(
            data=data
        )

        if not req_vip_serializer.is_valid():
            raise api_exceptions.ValidationException("Invalid Vip Request")

        if request.method == "POST":

            obj_req_vip = req_vip_serializer.object

            obj_req_vip.filter_valid = True
            obj_req_vip.validado = False
            _set_l7_filter_for_vip(obj_req_vip)
            obj_req_vip.set_new_variables(data)
            obj_req_vip.save(user)

            if vip_ports:

                for v_port in obj_req_vip.vip_ports_to_pools:
                    v_port.requisicao_vip = obj_req_vip
                    v_port.save(user)
            else:
                _validate_reals(data)
                obj_req_vip.save_vips_and_ports(data, user)

            return Response(
                data=req_vip_serializer.data,
                status=status.HTTP_201_CREATED
            )

        elif request.method == "PUT":

            obj_req_vip = RequisicaoVips.objects.get(pk=pk)

            with distributedlock(LOCK_VIP % pk):

                obj_req_vip = req_vip_serializer.object
                obj_req_vip.id = pk
                obj_req_vip.filter_valid = True
                obj_req_vip.validado = False
                _set_l7_filter_for_vip(obj_req_vip)
                obj_req_vip.set_new_variables(data)
                obj_req_vip.save(user)

                if vip_ports:

                    vip_port_serializer = VipPortToPoolSerializer(data=vip_ports, many=True)

                    if not vip_port_serializer.is_valid():
                        raise api_exceptions.ValidationException("Invalid Port Vip To Pool")

                    vip_port_to_pool_pks = [port['id'] for port in vip_ports if port.get('id')]

                    vip_port_to_pool_to_remove = VipPortToPool.objects.filter(
                        requisicao_vip=obj_req_vip
                    ).exclude(
                        id__in=vip_port_to_pool_pks
                    )

                    for v_port_to_del in vip_port_to_pool_to_remove:
                        v_port_to_del.delete(user)

                    for vip_port in vip_ports:
                        vip_port_obj = VipPortToPool()
                        vip_port_obj.id = vip_port.get('id')
                        vip_port_obj.server_pool = ServerPool(id=vip_port.get('server_pool'))
                        vip_port_obj.port_vip = vip_port.get('port_vip')
                        vip_port_obj.requisicao_vip = obj_req_vip
                        vip_port_obj.save(user)

                else:
                    _validate_reals(data)
                    obj_req_vip.delete_vips_and_reals(user)
                    obj_req_vip.save_vips_and_ports(data, user)

                return Response(data=req_vip_serializer.data)

    except RequisicaoVips.DoesNotExist, exception:
        log.error(exception)
        raise exceptions.VipRequestDoesNotExistException()

    except api_exceptions.ValidationException, exception:
        log.error(exception)
        raise exception

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


def _validate_reals(data):

    try:

        reals_data = data.get('reals')

        if reals_data is not None:

            finalidade = data.get('finalidade')
            cliente = data.get('cliente')
            ambiente = data.get('ambiente')

            evip = EnvironmentVip.get_by_values(
                finalidade,
                cliente,
                ambiente
            )

            for real in reals_data.get('real'):

                real_ip = real.get('real_ip')
                real_name = real.get('real_name')

                if real_name:
                    equip = Equipamento.get_by_name(real_name)
                else:
                    message = u'The real_name parameter is not a valid value'
                    log.error(message)
                    raise api_exceptions.ValidationException(message)

                RequisicaoVips.valid_real_server(real_ip, equip, evip, False)

    except EnvironmentVipNotFoundError, exception:
        log.error(exception.message)
        raise api_exceptions.ValidationException(exception.message)

    except EquipamentoError, exception:
        log.error(exception.message)
        raise api_exceptions.ValidationException(exception.message)

    except EquipamentoNotFoundError, exception:
        log.error(exception.message)
        raise api_exceptions.ValidationException(exception.message)

    except IpNotFoundByEquipAndVipError, exception:
        log.error(exception.message)
        raise api_exceptions.ValidationException(exception.message)

    except InvalidValueError, exception:
        log.error(u'Invalid Ip Type')
        raise api_exceptions.ValidationException(u'Invalid Ip Type')
