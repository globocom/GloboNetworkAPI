from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from networkapi.api_route_map.v4 import facade
from networkapi.api_route_map.v4 import serializers
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate
from networkapi.api_route_map.v4.permissions import Read
from networkapi.api_route_map.v4.permissions import Write
import logging

log = logging.getLogger(__name__)

class RouteMapDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of Route Map's by ids ou dict."""

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
        """Create new Route Map."""

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
        """Update Route Map."""

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
        """Delete Route Map."""

        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_route_map(obj_ids)

        return Response({}, status=status.HTTP_200_OK)


class RouteMapEntryDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of Route Map Entry's by ids ou dict."""

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
        """Create new Route Map Entry."""

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
        """Update Route Map Entry."""

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
        """Delete Route Map Entry."""

        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_route_map_entry(obj_ids)

        return Response({}, status=status.HTTP_200_OK)