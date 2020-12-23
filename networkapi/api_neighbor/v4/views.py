# -*- coding: utf-8 -*-
# Create your views here.
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_neighbor.v4 import facade
from networkapi.api_neighbor.v4 import serializers
from networkapi.api_neighbor.v4.permissions import DeployCreate
from networkapi.api_neighbor.v4.permissions import DeployDelete
from networkapi.api_neighbor.v4.permissions import Read
from networkapi.api_neighbor.v4.permissions import Write
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate

log = logging.getLogger(__name__)


class NeighborDBView(CustomAPIView):
    log.info("Creates neighbors using just one call")

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, **kwargs):
        """Returns a list of Neighbors by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_neighbor_v4_by_search(self.search)
            objects = obj_model['query_set']
            only_main_property = False
        else:
            ids = kwargs.get('obj_ids').split(';')
            objects = facade.get_neighbor_v4_by_ids(ids)
            only_main_property = True
            obj_model = None

        serializer = serializers.NeighborV4V4Serializer(
            objects,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        data = render_to_json(
            serializer,
            main_property='neighbors',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('neighbor_post')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create new Neighbor."""

        objects = request.DATA
        json_validate(SPECS.get('neighbor_post')).validate(objects)
        response = list()

        for obj in objects.get('neighbors'):
            created_obj = facade.create_neighbor(obj, request.user)
            response.append({'id': created_obj.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('neighbor_v4_put_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request):
        """Update Neighbors."""

        objects = request.DATA
        json_validate(SPECS.get('neighbor_v4_put_v4')).validate(objects)
        response = list()
        for obj in objects['neighbors']:

            created_obj = facade.update_neighbor_v4(obj, request.user)
            response.append({
                'id': created_obj.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, **kwargs):
        """Delete Neighbors."""

        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_neighbor_v4(obj_ids)

        return Response({}, status=status.HTTP_200_OK)


class NeighborV4DBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of NeighborV4's by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_neighbor_v4_by_search(self.search)
            objects = obj_model['query_set']
            only_main_property = False
        else:
            ids = kwargs.get('obj_ids').split(';')
            objects = facade.get_neighbor_v4_by_ids(ids)
            only_main_property = True
            obj_model = None

        # serializer
        serializer = serializers.NeighborV4V4Serializer(
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
            main_property='neighbors',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('neighbor_v4_post_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create new NeighborV4."""

        objects = request.DATA
        simple = request.GET.get('simple', None)

        response = list()
        for obj in objects['neighbors']:
            if not simple:
                json_validate(SPECS.get('neighbor_v4_post_v4')).validate(objects)
                created_obj = facade.create_neighbor_v4(obj, request.user)
                response.append({'id': created_obj.id})
            else:
                response += facade.create_neighbor_simple(obj, request.user)

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('neighbor_v4_put_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Update NeighborV4."""

        objects = request.DATA
        json_validate(SPECS.get('neighbor_v4_put_v4')).validate(objects)
        response = list()
        for obj in objects['neighbors']:

            created_obj = facade.update_neighbor_v4(obj, request.user)
            response.append({
                'id': created_obj.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Delete NeighborV4."""

        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_neighbor_v4(obj_ids)

        return Response({}, status=status.HTTP_200_OK)


class NeighborV6DBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of NeighborV6's by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_neighbor_v6_by_search(self.search)
            objects = obj_model['query_set']
            only_main_property = False
        else:
            ids = kwargs.get('obj_ids').split(';')
            objects = facade.get_neighbor_v6_by_ids(ids)
            only_main_property = True
            obj_model = None

        # serializer
        serializer = serializers.NeighborV6V4Serializer(
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
            main_property='neighbors',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('neighbor_v6_post_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create new NeighborV6."""

        objects = request.DATA

        simple = request.GET.get('simple', None)

        response = list()
        for obj in objects['neighbors']:
            if not simple:
                json_validate(SPECS.get('neighbor_v6_post_v4')).validate(objects)
                created_obj = facade.create_neighbor_v6(obj, request.user)
                response.append({'id': created_obj.id})
            else:
                response += facade.create_neighbor_simple_v6(obj, request.user)

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('neighbor_v6_put_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Update NeighborV6."""

        objects = request.DATA
        json_validate(SPECS.get('neighbor_v6_put_v4')).validate(objects)
        response = list()
        for obj in objects['neighbors']:

            created_obj = facade.update_neighbor_v6(obj, request.user)
            response.append({
                'id': created_obj.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Delete NeighborV6."""

        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_neighbor_v6(obj_ids)

        return Response({}, status=status.HTTP_200_OK)


class NeighborV4DeployView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write, DeployCreate))
    def post(self, request, *args, **kwargs):
        """
        Creates list of NeighborV4 in equipments
        :url /api/v4/neighborv4/deploy/<neighbor_ids>/
        :param neighbor_ids=<neighbor_ids>
        """

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        for obj_id in obj_ids:
            facade.deploy_neighbor_v4(obj_id)
            response.append({
                'id': obj_id,
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write, DeployDelete))
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of NeighborV4 in equipments
        :url /api/v4/neighborv4/deploy/<neighbor_ids>/
        :param neighbor_ids=<neighbor_ids>
        """

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        for obj_id in obj_ids:
            facade.undeploy_neighbor_v4(obj_id)
            response.append({
                'id': obj_id,
            })

        return Response(response, status=status.HTTP_200_OK)


class NeighborV6DeployView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write, DeployCreate))
    def post(self, request, *args, **kwargs):
        """
        Creates list of NeighborV4 in equipments
        :url /api/v4/neighborv6/deploy/<neighbor_ids>/
        :param neighbor_ids=<neighbor_ids>
        """

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        for obj_id in obj_ids:
            facade.deploy_neighbor_v6(obj_id)
            response.append({
                'id': obj_id,
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write, DeployDelete))
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of NeighborV4 in equipments
        :url /api/v4/neighborv6/deploy/<neighbor_ids>/
        :param neighbor_ids=<neighbor_ids>
        """

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        for obj_id in obj_ids:
            facade.undeploy_neighbor_v6(obj_id)
            response.append({
                'id': obj_id,
            })

        return Response(response, status=status.HTTP_200_OK)
