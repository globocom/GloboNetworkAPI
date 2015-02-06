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
from networkapi.api_healthcheck.permissions import Write
from networkapi.log import Log
from networkapi.healthcheckexpect.models import Healthcheck
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_pools import exceptions
from networkapi.api_pools.serializers import HealthcheckSerializer
from django.core.exceptions import ObjectDoesNotExist
from networkapi.requisicaovips.models import ServerPool


log = Log(__name__)

@api_view(['POST'])
@permission_classes((IsAuthenticated, Write))
@commit_on_success
def insert(request):

    try:
        # TODO: ADD VALIDATION

        healthcheck_type = request.DATA.get('healthcheck_type')
        healthcheck_request = request.DATA.get('healthcheck_request')
        healthcheck_expect = request.DATA.get('healthcheck_expect')
        old_healthcheck_id = request.DATA.get('old_healthcheck_id')

        try:
            #Query HealthCheck table for one equal this
            hc_check = Healthcheck.objects.get(healthcheck_expect=healthcheck_expect, healthcheck_type=healthcheck_type, healthcheck_request=healthcheck_request)

            #If a HealthCheck like this already exists, return it
            hc_serializer = HealthcheckSerializer(hc_check, many=False)

        #Else, add a new one
        except ObjectDoesNotExist:

            hc = Healthcheck(
                identifier='',
                healthcheck_type=healthcheck_type,
                healthcheck_request=healthcheck_request,
                healthcheck_expect=healthcheck_expect,
                destination=''
            )

            hc.save(request.user)

            #Check if someone is using the old healthcheck
            #If not, delete it to keep the database clean
            if old_healthcheck_id is not None:
                pools_using_healthcheck = ServerPool.objects.filter(healthcheck=old_healthcheck_id).count()

                if pools_using_healthcheck == 0:
                    Healthcheck.objects.filter(id=old_healthcheck_id).delete()

            hc_serializer = HealthcheckSerializer(hc, many=False)

        return Response(hc_serializer.data)

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()
