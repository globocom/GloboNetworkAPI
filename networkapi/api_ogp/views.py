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
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_ogp import serializers
from networkapi.api_ogp.facade.v3 import ogp as facade_ogp
from networkapi.api_ogp.facade.v3 import ogpg as facade_ogpg
from networkapi.api_ogp.facade.v3 import ot as facade_ot
from networkapi.api_ogp.permissions import Read
from networkapi.api_ogp.permissions import Write
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.settings import SPECS
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate


log = logging.getLogger(__name__)


class ObjectGroupPermView(APIView):

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of Object Group Permissions by ids or dict
        """

        try:

            if not kwargs.get('ogp_ids'):
                obj_model = facade_ogp.get_ogps_by_search(self.search)
                ogps = obj_model['query_set']
                only_main_property = False
            else:
                ogp_ids = kwargs.get('ogp_ids').split(';')
                ogps = facade_ogp.get_ogps_by_ids(ogp_ids)
                only_main_property = True
                obj_model = None

            serializer_class = serializers.ObjectGroupPermissionV3Serializer

            # serializer Object Group Permissions
            serializer_ogp = serializer_class(
                ogps,
                many=True,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude
            )

            # prepare serializer with customized properties
            response = render_to_json(
                serializer_ogp,
                main_property='ogps',
                obj_model=obj_model,
                request=request,
                only_main_property=only_main_property
            )

            return Response(response, status=status.HTTP_200_OK)

        except Exception as exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('ogp_post')
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Creates list of Object Group Permissions
        """

        data = request.DATA

        json_validate(SPECS.get('ogp_post')).validate(data)

        response = list()
        for ogp in data['ogps']:
            ogp = facade_ogp.create_ogp(ogp)
            response.append({'id': ogp.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('ogp_put')
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Update Object Group Permissions
        """
        ogps = request.DATA
        json_validate(SPECS.get('ogp_put')).validate(ogps)
        response = list()
        for ogp in ogps['ogps']:
            ogp = facade_ogp.update_ogp(ogp)
            response.append({
                'id': ogp.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Delete Object Group Permissions
        """

        ogp_ids = kwargs['ogp_ids'].split(';')
        response = {}
        for id in ogp_ids:
            facade_ogp.delete_ogp(id)

        return Response(response, status=status.HTTP_200_OK)


class ObjectGroupPermGeneralView(APIView):

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of Object Group Permissions General by ids or dict
        """

        try:

            if not kwargs.get('ogpg_ids'):
                obj_model = facade_ogpg.get_ogpgs_by_search(self.search)
                ogpgs = obj_model['query_set']
                only_main_property = False
            else:
                ogpg_ids = kwargs.get('ogpg_ids').split(';')
                ogpgs = facade_ogpg.get_ogpgs_by_ids(ogpg_ids)
                only_main_property = True
                obj_model = None

            serializer_class = serializers.\
                ObjectGroupPermissionGeneralV3Serializer

            # serializer Object Group Permissions General
            serializer_ogpg = serializer_class(
                ogpgs,
                many=True,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude
            )

            # prepare serializer with customized properties
            response = render_to_json(
                serializer_ogpg,
                main_property='ogpgs',
                obj_model=obj_model,
                request=request,
                only_main_property=only_main_property
            )

            return Response(response, status=status.HTTP_200_OK)

        except Exception as exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('ogpg_post')
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Creates list of Object Group Permissions General
        """

        data = request.DATA

        json_validate(SPECS.get('ogpg_post')).validate(data)

        response = list()
        for ogpg in data['ogpgs']:
            ogpg = facade_ogpg.create_ogpg(ogpg)
            response.append({'id': ogpg.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('ogp_put')
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Update Object Group Permissions General
        """
        ogpgs = request.DATA
        json_validate(SPECS.get('ogpg_put')).validate(ogpgs)
        response = list()
        for ogpg in ogpgs['ogpgs']:
            ogpg = facade_ogpg.update_ogpg(ogpg)
            response.append({
                'id': ogpg.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Delete Object Group Permissions General
        """

        ogpg_ids = kwargs['ogpg_ids'].split(';')
        response = {}
        for id in ogpg_ids:
            facade_ogpg.delete_ogpg(id)

        return Response(response, status=status.HTTP_200_OK)


class ObjectTypeView(APIView):

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of Object Type by ids or dict
        """

        try:

            if not kwargs.get('ot_ids'):
                obj_model = facade_ot.get_ots_by_search(self.search)
                ots = obj_model['query_set']
                only_main_property = False
            else:
                ot_ids = kwargs.get('ot_ids').split(';')
                ots = facade_ot.get_ots_by_ids(ot_ids)
                only_main_property = True
                obj_model = None

            serializer_class = serializers.ObjectTypeV3Serializer

            # serializer Object Group Permissions General
            serializer_ot = serializer_class(
                ots,
                many=True,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude
            )

            # prepare serializer with customized properties
            response = render_to_json(
                serializer_ot,
                main_property='ots',
                obj_model=obj_model,
                request=request,
                only_main_property=only_main_property
            )

            return Response(response, status=status.HTTP_200_OK)

        except Exception as exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
