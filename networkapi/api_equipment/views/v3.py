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

from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_equipment import facade
from networkapi.api_equipment import serializers
from networkapi.api_rest import exceptions as api_exceptions
# from django.db.transaction import commit_on_success


log = logging.getLogger(__name__)


class EquipmentEnvView(APIView):

    def get(self, request, *args, **kwargs):
        try:
            env_id = kwargs.get("env_id")

            data = dict()
            eqpts_query = facade.get_equipments_by_user(request.user, env_id)
            eqpt_serializers = serializers.EquipmentV3Serializer(eqpts_query, many=True)

            data["equipments"] = eqpt_serializers.data

            return Response(data)
        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException()
