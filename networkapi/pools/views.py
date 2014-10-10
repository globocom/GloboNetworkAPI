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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from networkapi.requisicaovips.models import ServerPool, ServerPoolMember
from networkapi.pools.serializers import ServerPoolSerializer, HealthcheckSerializer, ServerPoolMemberSerializer
from networkapi.healthcheckexpect.models import Healthcheck, HealthcheckExpect
from networkapi.ambiente.models import Ambiente
from networkapi.ip.models import Ip, Ipv6
from networkapi.infrastructure.datatable import build_query_to_datatable
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.util import is_valid_list_int_greater_zero_param
from networkapi.log import Log
from networkapi.pools.exceptions import InvalidIdPoolException
from networkapi.pools.permissions import Read, Write

log = Log(__name__)


@api_view(['POST'])
@permission_classes((IsAuthenticated, Read))
@commit_on_success
def pool_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    try:

        data = dict()

        start_record = request.DATA.get("start_record")
        end_record = request.DATA.get("end_record")
        asorting_cols = request.DATA.get("asorting_cols")
        searchable_columns = request.DATA.get("searchable_columns")
        custom_search = request.DATA.get("custom_search")
        query_pools = ServerPool.objects.all()

        server_pools, total = build_query_to_datatable(
            query_pools,
            asorting_cols,
            custom_search,
            searchable_columns,
            start_record,
            end_record
        )

        serializer_pools = ServerPoolSerializer(server_pools, many=True)

        data["pools"] = serializer_pools.data
        data["total"] = total

        return Response(data)

    except Exception, e:
        log.error(e.message)
        raise NetworkAPIException


@api_view(['POST'])
@permission_classes((IsAuthenticated, Write))
@commit_on_success
def delete(request):
    """
    Delete Pools by list id.
    """

    try:

        ids = request.DATA.get('ids')

        is_valid_list_int_greater_zero_param(ids)

        for _id in ids:
            try:
                server_pool = ServerPool.objects.get(id=_id)
                server_pool.delete(request.user)

            except ServerPool.DoesNotExist:
                pass

        return Response(status=status.HTTP_204_NO_CONTENT)

    except ValueError, e:
        log.error(e.message)
        raise InvalidIdPoolException

    except Exception, e:
        log.error(e.message)
        raise NetworkAPIException


@api_view(['POST'])
@permission_classes((IsAuthenticated, Write))
@commit_on_success
def remove(request):
    """
    Remove Pools by list id running script and update to not created.
    """

    try:

        ids = request.DATA.get('ids')

        is_valid_list_int_greater_zero_param(ids)

        for _id in ids:
            try:

                server_pool = ServerPool.objects.get(id=_id)
                server_pool.pool_created = False
                server_pool.save(request.user)

            except ServerPool.DoesNotExist:
                pass

        return Response()

    except ValueError, e:
        log.error(e.message)
        raise InvalidIdPoolException

    except Exception, e:
        log.error(e.message)
        raise NetworkAPIException


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read, Write))
@commit_on_success
def healthcheck_list(request):
        data = dict()
        healthchecks = Healthcheck.objects.all()
        serializer_healthchecks = HealthcheckSerializer(healthchecks, many=True)
        data["healthchecks"] = serializer_healthchecks.data

        return Response(data)


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read, Write))
@commit_on_success
def get_by_pk(request, id_server_pool):

        data = dict()
        server_pool = ServerPool.objects.get(pk=id_server_pool)
        server_pool_members = ServerPoolMember.objects.filter(server_pool=id_server_pool)

        serializer_server_pool = ServerPoolSerializer(server_pool)
        serializer_server_pool_member = ServerPoolMemberSerializer(server_pool_members, many=True)

        data["server_pool"] = serializer_server_pool.data
        data["server_pool_members"] = serializer_server_pool_member.data

        return Response(data)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, Read, Write))
@commit_on_success
def pool_insert(request):

    if request.method == 'POST':

        identifier = request.DATA.get('identifier')
        default_port = request.DATA.get('default_port')
        environment = request.DATA.get('environment')
        balancing = request.DATA.get('balancing')
        healthcheck = request.DATA.get('healthcheck')
        maxcom = request.DATA.get('maxcom')
        ip_list_full = request.DATA.get('ip_list_full')
        priorities = request.DATA.get('priorities')
        ports_reals = request.DATA.get('ports_reals')

        healthcheck_obj = Healthcheck.objects.get(id=healthcheck)
        ambiente_obj = Ambiente.get_by_pk(environment)

        sp = ServerPool(
            identifier=identifier,
            default_port=default_port,
            healthcheck=healthcheck_obj,
            environment=ambiente_obj,
            pool_created=True,
            lb_method=''
        )

        sp.save(request.user)

        ip_object = None
        ipv6_object = None

        for i in range(0, len(ip_list_full)):

            if len(ip_list_full[i]['ip']) <= 15:
                ip_object = Ip.get_by_pk(ip_list_full[i]['id'])
            else:
                ipv6_object = Ipv6.get_by_pk(ip_list_full[i]['id'])

            spm = ServerPoolMember(
                server_pool=sp,
                identifier=identifier,
                ip=ip_object,
                ipv6=ipv6_object,
                priority=priorities[i],
                weight=0,
                limit=maxcom,
                port_real=ports_reals[i],
                healthcheck=healthcheck_obj
            )

            spm.save(request.user)

    return Response(status=status.HTTP_201_CREATED)
