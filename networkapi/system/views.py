# -*- coding: utf-8 -*-
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
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.system import exceptions
from networkapi.system import facade
from networkapi.system.exceptions import *
from networkapi.system.permissions import Read
from networkapi.system.permissions import Write
from networkapi.system.serializers import VariableSerializer
from networkapi.util import is_valid_int_greater_zero_param


log = logging.getLogger(__name__)


class VariableView(APIView):

    @permission_classes((IsAuthenticated, Write))
    @commit_on_success
    def post(self, *args, **kwargs):
        try:
            log.info("VariableView")

            data = self.request.DATA

            try:
                name = data['name']
                value = data['value']
                description = data['description']
            except Exception:
                raise exceptions.InvalidInputException()

            var = False

            try:
                facade.get_by_name(name)
                var = True
            except:
                pass

            if var:
                raise exceptions.VariableDuplicateNotExistException()

            variable = facade.save_variable(
                self.request.user, name, value, description)

            data = dict()
            variable_serializer = VariableSerializer(variable)
            data['variable'] = variable_serializer.data

            return Response(data, status=status.HTTP_201_CREATED)

        except (exceptions.InvalidIdNameException, exceptions.InvalidIdValueException,
                exceptions.VariableDuplicateNotExistException, exceptions.VariableError)as exception:
            log.exception(exception)
            raise exception

        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException()

    @permission_classes((IsAuthenticated, Read))
    def get(self, *args, **kwargs):
        try:
            log.info('GET ALL VARIABLES')

            variable_query = facade.get_all_variables()
            serializer_variable = VariableSerializer(variable_query, many=True)

            return Response(serializer_variable.data)

        except ObjectDoesNotExist, exception:
            log.error(exception)
            raise api_exceptions.ObjectDoesNotExistException(
                'Variable Does Not Exist')

        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException()


class VariablebyPkView(APIView):

    @permission_classes((IsAuthenticated, Write))
    def delete(self, *args, **kwargs):
        try:
            log.info('DELETE VARIABLE')

            variable_id = kwargs['variable_id']

            if not is_valid_int_greater_zero_param(variable_id, False):
                raise api_exceptions.ValidationException(
                    'Variable id invalid.')

            facade.delete_variable(self.request.user, variable_id)
            data = dict()
            data['variable'] = 'ok'

            return Response(data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist, exception:
            log.error(exception)
            raise exceptions.VariableDoesNotExistException()

        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.ValidationException('Variable id invalid.')
