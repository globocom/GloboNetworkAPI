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
from networkapi.snippets.permissions import Read, Write
from networkapi.requisicaovips.models import ServerPool
from networkapi.pools.serializers import ServerPoolSerializer
from networkapi.infrastructure.datatable import build_query_to_datatable
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.util import is_valid_list_int_greater_zero_param
from networkapi.log import Log
from networkapi.pools.exceptions import InvalidIdPoolException

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
