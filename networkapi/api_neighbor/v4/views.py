# -*- coding: utf-8 -*-
# Create your views here.
from networkapi.api_rest.exceptions import ValidationAPIException
from django.db.transaction import commit_on_success

from networkapi.api_neighbor.v4.exceptions import NeighborAlreadyCreated
from networkapi.api_neighbor.v4.exceptions import NeighborNotCreated
from networkapi.util.geral import destroy_lock
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.distributedlock import LOCK_NEIGHBOR
from networkapi.util.geral import create_lock
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from networkapi.api_neighbor.v4 import facade
from networkapi.api_neighbor.v4 import serializers
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_obj_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate
from networkapi.api_neighbor.v4.permissions import Read
from networkapi.api_neighbor.v4.permissions import Write
from networkapi.api_neighbor.v4.permissions import DeployCreate
from networkapi.api_neighbor.v4.permissions import DeployDelete
import logging

log = logging.getLogger(__name__)


class NeighborDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of Neighbors by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_neighbor_by_search(self.search)
            neighbors = obj_model['query_set']
            only_main_property = False
        else:
            neighbor_ids = kwargs.get('obj_ids').split(';')
            neighbors = facade.get_neighbor_by_ids(neighbor_ids)
            only_main_property = True
            obj_model = None

        # serializer Neighbors
        serializer_neighbor = serializers.NeighborV4Serializer(
            neighbors,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        data = render_to_json(
            serializer_neighbor,
            main_property='neighbors',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('neighbor_post_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create new Neighbor."""

        neighbors = request.DATA
        json_validate(SPECS.get('neighbor_post_v4')).validate(neighbors)
        response = list()
        for neighbor in neighbors['neighbors']:

            neighbor_obj = facade.create_neighbor(neighbor)
            response.append({'id': neighbor_obj.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('neighbor_put_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Update Neighbor."""

        neighbors = request.DATA
        json_validate(SPECS.get('neighbor_put_v4')).validate(neighbors)
        response = list()
        for neighbor in neighbors['neighbors']:

            neighbor_obj = facade.update_neighbor(neighbor)
            response.append({
                'id': neighbor_obj.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Delete Neighbor."""

        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_neighbor(obj_ids)

        return Response({}, status=status.HTTP_200_OK)


class NeighborDeployView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write, DeployCreate))
    def post(self, request, *args, **kwargs):
        """
        Creates list of neighbor in equipments
        :url /api/v4/neighbor/deploy/<neighbor_ids>/
        :param neighbor_ids=<neighbor_ids>
        """

        neighbor_ids = kwargs['obj_ids'].split(';')
        neighbors = facade.get_neighbor_by_ids(neighbor_ids)
        neighbor_serializer = serializers.NeighborV4Serializer(neighbors,
                                                               many=True)

        locks_list = create_lock(neighbor_serializer.data, LOCK_NEIGHBOR)
        try:
            response = facade.deploy_neighbors(neighbor_serializer.data)
        except NeighborAlreadyCreated as e:
            raise ValidationAPIException(str(e))
        except Exception, exception:
            log.error(exception)
            raise NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write, DeployDelete))
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of neighbor in equipments
        :url /api/v4/neighbor/deploy/<neighbor_ids>/
        :param neighbor_ids=<neighbor_ids>
        """

        neighbor_ids = kwargs['obj_ids'].split(';')
        neighbors = facade.get_neighbor_by_ids(neighbor_ids)
        neighbor_serializer = serializers.NeighborV4Serializer(neighbors,
                                                               many=True)

        locks_list = create_lock(neighbor_serializer.data, LOCK_NEIGHBOR)
        try:
            response = facade.undeploy_neighbors(neighbor_serializer.data)
        except NeighborNotCreated as e:
            raise ValidationAPIException(str(e))
        except Exception, exception:
            log.error(exception)
            raise NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return Response(response, status=status.HTTP_200_OK)

