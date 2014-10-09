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

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from networkapi.snippets.permissions import Read, Write
from django.db.transaction import commit_on_success
from rest_framework.response import Response
from networkapi.requisicaovips.models import ServerPool, ServerPoolMember
from networkapi.pools.serializers import ServerPoolSerializer, HealthcheckSerializer
from networkapi.infrastructure.datatable import build_query_to_datatable
from networkapi.healthcheckexpect.models import Healthcheck, HealthcheckExpect
from networkapi.ambiente.models import Ambiente
from networkapi.ip.models import Ip, Ipv6




@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, Read, Write))
@commit_on_success
def pool_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'POST':

        data = dict()

        start_record = request.DATA.get("start_record")
        end_record = request.DATA.get("end_record")
        asorting_cols = request.DATA.getlist("asorting_cols")
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

    elif request.method == 'POST':

        snippet_serializer = ServerPoolSerializer(data=request.DATA)

        if snippet_serializer.is_valid():
            snippet = snippet_serializer.object
            snippet.save(request.user)
            return Response(snippet_serializer.data, status=status.HTTP_201_CREATED)

        return Response(snippet_serializer.erros, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read, Write))
@commit_on_success
def healthcheck_list(request):
        data = dict()
        healthchecks = Healthcheck.objects.all()
        serializer_healthchecks = HealthcheckSerializer(healthchecks, many=True)
        data["healthchecks"] = serializer_healthchecks.data

        return Response(data)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, Read, Write))
@commit_on_success
def pool_insert(request):

    if request.method == 'POST':
        import json
        identifier = request.DATA.get('identifier')
        default_port = request.DATA.get('default_port')
        environment = request.DATA.get('environment')
        balancing = request.DATA.get('balancing')
        healthcheck = request.DATA.get('healthcheck')
        maxcom = request.DATA.get('maxcom')
        ip_list_full = json.loads(request.DATA.get('ip_list_full'))
        id_equips = request.DATA.getlist('id_equips')
        priorities = request.DATA.getlist('priorities')
        ports_reals = request.DATA.getlist('ports_reals')

        healthcheck_obj = Healthcheck.objects.get(id=healthcheck)
        ambiente_obj = Ambiente.get_by_pk(environment)

        sp = ServerPool(
            identifier=identifier,
            default_port=default_port,
            healthcheck=healthcheck_obj,
            ambiente_id_ambiente=ambiente_obj,
            pool_criado=True,
            lb_method=''
        )

        sp.save(request.user)

        ip_object = None;
        ipv6_object = None;

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



