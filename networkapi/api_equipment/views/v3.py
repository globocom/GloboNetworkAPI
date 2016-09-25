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
import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_equipment import facade
from networkapi.api_equipment import serializers
from networkapi.api_equipment.permissions import Read
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
# from django.db.transaction import commit_on_success


log = logging.getLogger(__name__)


class EquipmentView(APIView):

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Return list of equipments

        :param rights_write(optional): Right of Write - Filter by rights of write
        :param environment(optional): Id of environment - Filter by environment
        :param ipv4(optional): Id of ipv4 - Filter by id ipv4
        :param ipv6(optional): Id of ipv6 - Filter by id ipv6
        :param is_router(optional): Boolean (True|False) - Filter for routers
        :param name(optional): Name of Equipment
        """

        try:

            rights_write = request.GET.get("rights_write")
            environment = request.GET.get("environment")
            ipv4 = request.GET.get("ipv4")
            ipv6 = request.GET.get("ipv6")
            is_router = request.GET.get("is_router")
            name = request.GET.get("name")

            # get equipments queryset
            eqpts_query = facade.get_equipments(
                user=request.user,
                rights_read=1,
                environment=environment,
                ipv4=ipv4,
                ipv6=ipv6,
                rights_write=rights_write,
                name=name,
                is_router=is_router,
                search=self.search
            )

            # serializer equipments
            eqpt_serializers = serializers.EquipmentV3Serializer(
                eqpts_query['query_set'],
                many=True,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude
            )

            # prepare serializer with customized properties
            data = render_to_json(
                eqpt_serializers,
                main_property='equipments',
                obj_model=eqpts_query,
                request=request,
                only_main_property=False
            )

            return Response(data)
        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException()
