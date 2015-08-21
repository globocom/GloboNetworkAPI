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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from networkapi.log import Log
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_network.permissions import Read, Write
from networkapi.api_network.serializers import NetworkIPv4Serializer

from networkapi.ip.models import NetworkIPv4

log = Log(__name__)


@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def list_networksIPv4(request):
    try:

        environment_vip = ''

        if request.QUERY_PARAMS.has_key("environment_vip"):
            environment_vip = str(request.QUERY_PARAMS["environment_vip"])

        networkIPv4_obj = NetworkIPv4.objects.all()

        if environment_vip:
            networkIPv4_obj = networkIPv4_obj.filter(ambient_vip__id=environment_vip)

        serializer_options = NetworkIPv4Serializer(
            networkIPv4_obj,
            many=True
        )

        return Response(serializer_options.data)

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()

