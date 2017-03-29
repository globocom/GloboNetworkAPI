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

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from networkapi.api_equipment import facade
from networkapi.api_equipment.permissions import Read
from networkapi.api_equipment.permissions import Write
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.distributedlock import LOCK_EQUIPMENT
from networkapi.settings import SPECS
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import create_lock
from networkapi.util.geral import CustomResponse
from networkapi.util.geral import destroy_lock
from networkapi.util.geral import get_app
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate
# from networkapi.util.decorators import permission_obj_apiview

serializers = get_app('api_equipment', module_label='serializers')

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

            if not kwargs.get('obj_id'):
                rights_write = request.GET.get('rights_write')
                environment = request.GET.get('environment')
                ipv4 = request.GET.get('ipv4')
                ipv6 = request.GET.get('ipv6')
                is_router = request.GET.get('is_router')
                environment_sdn_controller = request.GET.get('environment_sdn_controller')
                name = request.GET.get('name')

                # get equipments queryset
                obj_model = facade.get_equipments(
                    user=request.user,
                    rights_read=1,
                    environment=environment,
                    ipv4=ipv4,
                    ipv6=ipv6,
                    rights_write=rights_write,
                    name=name,
                    is_router=is_router,
                    environment_sdn_controller=environment_sdn_controller,
                    search=self.search
                )
                equipments = obj_model['query_set']
                only_main_property = False

            else:
                obj_ids = kwargs.get('obj_id').split(';')
                equipments = facade.get_equipment_by_ids(obj_ids)
                only_main_property = True
                obj_model = None

            # serializer equipments
            eqpt_serializers = serializers.EquipmentV3Serializer(
                equipments,
                many=True,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude,
                kind=self.kind
            )

            # prepare serializer with customized properties
            data = render_to_json(
                eqpt_serializers,
                main_property='equipments',
                obj_model=obj_model,
                request=request,
                only_main_property=only_main_property
            )

            return CustomResponse(data, status=status.HTTP_200_OK, request=request)
        except Exception, exception:
            log.exception(exception)
            raise api_exceptions.NetworkAPIException()

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('equipment_post')
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Creates list of equipments
        """

        data = request.DATA

        json_validate(SPECS.get('equipment_post')).validate(data)

        response = list()
        for equipment in data['equipments']:
            eqpt = facade.create_equipment(equipment, request.user)
            response.append({'id': eqpt.id})

        return CustomResponse(response, status=status.HTTP_201_CREATED, request=request)

    @permission_classes_apiview((IsAuthenticated, Write))
    # @permission_obj_apiview([write_obj_permission])
    @logs_method_apiview
    @raise_json_validate('equipment_put')
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Updates list of equipments
        """
        data = request.DATA

        json_validate(SPECS.get('equipment_put')).validate(data)

        locks_list = create_lock(data['equipments'], LOCK_EQUIPMENT)
        try:
            response = list()
            for equipment in data['equipments']:
                eqpt = facade.update_equipment(equipment, request.user)
                response.append({'id': eqpt.id})
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return CustomResponse(response, status=status.HTTP_200_OK, request=request)

    @permission_classes_apiview((IsAuthenticated, Write))
    # @permission_obj_apiview([delete_obj_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of equipments
        """

        obj_ids = kwargs['obj_id'].split(';')
        locks_list = create_lock(obj_ids, LOCK_EQUIPMENT)
        try:
            facade.delete_equipment(obj_ids)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return CustomResponse({}, status=status.HTTP_200_OK, request=request)
