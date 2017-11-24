# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.api_route_map.v4 import exceptions
from networkapi.api_route_map.v4 import facade
from networkapi.api_route_map.v4 import serializers
from networkapi.api_route_map.v4.permissions import DeployCreate
from networkapi.api_route_map.v4.permissions import DeployDelete
from networkapi.api_route_map.v4.permissions import Read
from networkapi.api_route_map.v4.permissions import Write
from networkapi.distributedlock import LOCK_ROUTE_MAP
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import create_lock
from networkapi.util.geral import destroy_lock
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate

log = logging.getLogger(__name__)


class RouteMapDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of RouteMaps by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_route_map_by_search(self.search)
            objects = obj_model['query_set']
            only_main_property = False
        else:
            ids = kwargs.get('obj_ids').split(';')
            objects = facade.get_route_map_by_ids(ids)
            only_main_property = True
            obj_model = None

        # serializer
        serializer = serializers.RouteMapV4Serializer(
            objects,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        data = render_to_json(
            serializer,
            main_property='route_maps',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('route_map_post_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create new RouteMap."""

        objects = request.DATA
        json_validate(SPECS.get('route_map_post_v4')).validate(objects)
        response = list()
        for obj in objects['route_maps']:

            created_obj = facade.create_route_map(obj)
            response.append({'id': created_obj.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('route_map_put_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Update RouteMap."""

        objects = request.DATA
        json_validate(SPECS.get('route_map_put_v4')).validate(objects)
        response = list()
        for obj in objects['route_maps']:

            created_obj = facade.update_route_map(obj)
            response.append({
                'id': created_obj.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Delete RouteMap."""

        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_route_map(obj_ids)

        return Response({}, status=status.HTTP_200_OK)


class RouteMapEntryDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of RouteMapEntries by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_route_map_entry_by_search(self.search)
            objects = obj_model['query_set']
            only_main_property = False
        else:
            ids = kwargs.get('obj_ids').split(';')
            objects = facade.get_route_map_entry_by_ids(ids)
            only_main_property = True
            obj_model = None

        # serializer
        serializer = serializers.RouteMapEntryV4Serializer(
            objects,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        data = render_to_json(
            serializer,
            main_property='route_map_entries',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('route_map_entry_post_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create new RouteMapEntry."""

        objects = request.DATA
        json_validate(SPECS.get('route_map_entry_post_v4')).validate(objects)
        response = list()
        for obj in objects['route_map_entries']:

            created_obj = facade.create_route_map_entry(obj)
            response.append({'id': created_obj.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('route_map_entry_put_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Update RouteMapEntry."""

        objects = request.DATA
        json_validate(SPECS.get('route_map_entry_put_v4')).validate(objects)
        response = list()
        for obj in objects['route_map_entries']:

            created_obj = facade.update_route_map_entry(obj)
            response.append({
                'id': created_obj.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Delete RouteMapEntry."""

        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_route_map_entry(obj_ids)

        return Response({}, status=status.HTTP_200_OK)
