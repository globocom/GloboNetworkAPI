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
from django.db.transaction import commit_on_success
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from networkapi.rack.permissions import Read, Write
from networkapi.rack import facade, exceptions
from networkapi.rack.serializers import RackSerializer
from networkapi.api_rest import exceptions as api_exceptions



log = logging.getLogger(__name__)

class RackView(APIView):

    @permission_classes((IsAuthenticated, Write))
    @commit_on_success
    def post(self, *args, **kwargs):
        try:
            log.info("Add Rack")

            data_ = self.request.DATA
            if not data_:
                raise exceptions.InvalidInputException()

            rack_dict = dict()

            rack_dict['number'] = data_.get('number')
            rack_dict['name'] = data_.get('name')
            rack_dict['sw1_mac'] = data_.get('mac_address_sw1')
            rack_dict['sw2_mac'] = data_.get('mac_address_sw2')
            rack_dict['sw3_mac'] = data_.get('mac_address_ilo')

            if not data_.get('id_sw1'):
                rack_dict['sw1_id'] = None
            else:
                rack_dict['sw1_id'] = data_.get('id_sw1')
            if not data_.get('id_sw2'):
                rack_dict['sw2_id'] = None
            else:
                rack_dict['sw2_id'] = data_.get('id_sw2')
            if not data_.get('id_ilo'):
                rack_dict['sw3_id'] = None
            else:
                rack_dict['sw3_id'] = data_.get('id_ilo')

            rack = facade.save_rack(self.request.user, rack_dict)

            datas = dict()
            rack_serializer = RackSerializer(rack)
            datas['rack'] = rack_serializer.data

            return Response(datas, status=status.HTTP_201_CREATED)

        except (exceptions.RackNumberDuplicatedValueError, exceptions.RackNameDuplicatedError,
                exceptions.InvalidInputException) as exception:
            log.exception(exception)
            raise exception
        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException()

