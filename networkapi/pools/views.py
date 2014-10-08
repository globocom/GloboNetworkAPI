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
from snippets.permissions import Read, Write
from django.db.transaction import commit_on_success
from rest_framework.response import Response
from networkapi.requisicaovips.models import ServerPool
from pools.serializers import ServerPoolSerializer
from infrastructure.datatable import build_query_to_datatable


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
