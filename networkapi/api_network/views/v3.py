# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_equipment import permissions as perm_eqpt
from networkapi.api_network.facade import v3 as facade
from networkapi.api_network.permissions import deploy_objv4_permission
from networkapi.api_network.permissions import deploy_objv6_permission
from networkapi.api_network.permissions import Read
from networkapi.api_network.permissions import Write
from networkapi.api_network.permissions import write_objv4_permission
from networkapi.api_network.permissions import write_objv6_permission
from networkapi.api_network.serializers import v3 as serializers
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import permission_obj_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate
log = logging.getLogger(__name__)


class NetworkIPv4View(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate()
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of networkv4 by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_networkipv4_by_search(self.search)
            networks = obj_model['query_set']
            only_main_property = False
        else:
            obj_ids = kwargs.get('obj_ids').split(';')
            networks = facade.get_networkipv4_by_ids(obj_ids)
            only_main_property = True
            obj_model = None

        # serializer networks
        serializer_net = serializers.NetworkIPv4V3Serializer(
            networks,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        data = render_to_json(
            serializer_net,
            main_property='networks',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('networkv4_post')
    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([write_objv4_permission])
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Creates list of networkv4
        """

        data = request.DATA

        json_validate(SPECS.get('networkv4_post')).validate(data)

        response = list()
        for networkv4 in data['networks']:
            vl = facade.create_networkipv4(networkv4, request.user)
            response.append({'id': vl.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([write_objv4_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of networkv4
        """

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_networkipv4(obj_ids, request.user)

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('networkv4_put')
    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([write_objv4_permission])
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Updates list of networkv4
        """

        data = request.DATA

        json_validate(SPECS.get('networkv4_put')).validate(data)

        response = list()
        for networkv4 in data['networks']:
            vl = facade.update_networkipv4(networkv4, request.user)
            response.append({'id': vl.id})

        return Response(response, status=status.HTTP_200_OK)


class NetworkIPv6View(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of networkv6 by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_networkipv6_by_search(self.search)
            networks = obj_model['query_set']
            only_main_property = False
        else:
            obj_ids = kwargs.get('obj_ids').split(';')
            networks = facade.get_networkipv6_by_ids(obj_ids)
            only_main_property = True
            obj_model = None

        # serializer networks
        serializer_net = serializers.NetworkIPv6V3Serializer(
            networks,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        data = render_to_json(
            serializer_net,
            main_property='networks',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('networkv6_post')
    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([write_objv6_permission])
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Creates list of networkv6
        """

        data = request.DATA

        json_validate(SPECS.get('networkv6_post')).validate(data)

        response = list()
        for networkv6 in data['networks']:
            vl = facade.create_networkipv6(networkv6, request.user)
            response.append({'id': vl.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('networkv6_put')
    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([write_objv6_permission])
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Updates list of networkv6
        """

        data = request.DATA

        json_validate(SPECS.get('networkv6_put')).validate(data)

        response = list()
        for networkv6 in data['networks']:
            vl = facade.update_networkipv6(networkv6, request.user)
            response.append({'id': vl.id})

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([write_objv6_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of networkv6
        """

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_networkipv6(obj_ids, request.user)

        return Response(response, status=status.HTTP_200_OK)


class NetworkIPv4DeployView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write, perm_eqpt.Write))
    @permission_obj_apiview([deploy_objv4_permission])
    @commit_on_success
    def post(self, request, *args, **kwargs):

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        for obj_id in obj_ids:
            # deploy network configuration
            status_deploy = facade.deploy_networkipv4(obj_id, request.user)
            response.append({
                'status': status_deploy,
                'id': obj_id,
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write, perm_eqpt.Write))
    @permission_obj_apiview([deploy_objv4_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        for obj_id in obj_ids:
            # deploy network configuration
            status_deploy = facade.undeploy_networkipv4(obj_id, request.user)
            response.append({
                'status': status_deploy,
                'id': obj_id,
            })

        return Response(response, status=status.HTTP_200_OK)


class NetworkIPv6DeployView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write, perm_eqpt.Write))
    @permission_obj_apiview([deploy_objv6_permission])
    @commit_on_success
    def post(self, request, *args, **kwargs):

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        for obj_id in obj_ids:
            # deploy network configuration
            status_deploy = facade.deploy_networkipv6(obj_id, request.user)
            response.append({
                'status': status_deploy,
                'id': obj_id,
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write, perm_eqpt.Write))
    @permission_obj_apiview([deploy_objv6_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')
        for obj_id in obj_ids:
            # deploy network configuration
            status_deploy = facade.undeploy_networkipv6(obj_id, request.user)
            response.append({
                'status': status_deploy,
                'id': obj_id,
            })

        return Response(response, status=status.HTTP_200_OK)
