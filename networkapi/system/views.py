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
from networkapi.system.facade import save_variable, get_all_variables, delete_variable, get_by_name
from networkapi.system.exceptions import *
from networkapi.system.serializers import VariableSerializer
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.system import exceptions
from django.core.exceptions import ObjectDoesNotExist
from networkapi.util import is_valid_int_greater_zero_param



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

        var = False

        try:
            get_by_name(name)
            var = True
        except:
            pass

        if var:
            raise exceptions.VariableDuplicateNotExistException()

        variable = save_variable(request.user, name, value, description)

        data = dict()
        variable_serializer = VariableSerializer(variable)
        data['variable'] = variable_serializer.data

        return Response(data, status=status.HTTP_201_CREATED)

    except (exceptions.InvalidIdNameException, exceptions.InvalidIdValueException,
            exceptions.VariableDuplicateNotExistException)as exception:
        log.exception(exception)
        raise exception

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()

@api_view(['GET'])
@permission_classes((IsAuthenticated, Read))
def get_all(request):
    try:
        log.info("GET ALL VARIABLES")

        variable_query = get_all_variables()
        serializer_variable = VariableSerializer(variable_query, many=True)

        return Response(serializer_variable.data)

    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise api_exceptions.ObjectDoesNotExistException('Variable Does Not Exist')

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.NetworkAPIException()

@api_view(['DELETE'])
@permission_classes((IsAuthenticated, Write))
def delete(request, variable_id):
    try:
        log.info("DELETE VARIABLE")

        if not is_valid_int_greater_zero_param(variable_id, False):
            raise api_exceptions.ValidationException('Variable id invalid.')

        delete_variable(request.user, variable_id)
        data = dict()
        data['variable'] = "ok"

        return Response(data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist, exception:
        log.error(exception)
        raise exceptions.VariableDoesNotExistException()

    except Exception, exception:
        log.exception(exception)
        raise api_exceptions.ValidationException('Variable id invalid.')
