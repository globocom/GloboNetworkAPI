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
import logging
from networkapi.api_vlan.permissions import Read, Write
from networkapi.system.facade import save_variable
from networkapi.system.serializers import VariableSerializer
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.system import exceptions



log = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes((IsAuthenticated, Write))
@commit_on_success
def save(request):
    try:
        log.info("POST VARIABLE")

        name = request.DATA.get('name')
        value = request.DATA.get('value')
        description = request.DATA.get('description')

        variable = save_variable(request.user, name, value, description)

        data = dict()
        variable_serializer = VariableSerializer(variable)
        data['variable'] = variable_serializer.data

        return Response(data, status=status.HTTP_201_CREATED)

    except (exceptions.InvalidIdNameException, exceptions.InvalidIdValueException)as exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()
