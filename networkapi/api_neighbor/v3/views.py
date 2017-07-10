# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_neighbor.v3 import facade
from networkapi.api_neighbor.v3 import permissions
from networkapi.api_neighbor.v3 import serializers
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate

log = logging.getLogger(__name__)


class NeighborView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate()
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of neighbors by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_neighbor_by_search(self.search)
            neighbors = obj_model['query_set']
            only_main_property = False
        else:
            obj_ids = kwargs.get('obj_ids').split(';')
            neighbors = facade.get_neighbor_by_ids(obj_ids)
            only_main_property = True
            obj_model = None

        # serializer neighbors
        serializer_ip = serializers.NeighborSerializer(
            neighbors,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        data = render_to_json(
            serializer_ip,
            main_property='neighbors',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate()
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @commit_on_success
    def post(self, request, *args, **kwargs):

        pass

    @logs_method_apiview
    @raise_json_validate()
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @commit_on_success
    def put(self, request, *args, **kwargs):

        pass

    @logs_method_apiview
    @raise_json_validate()
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @commit_on_success
    def delete(self, request, *args, **kwargs):

        pass
