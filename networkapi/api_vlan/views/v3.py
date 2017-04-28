# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_vlan import permissions
from networkapi.api_vlan import serializers
from networkapi.api_vlan import tasks
from networkapi.api_vlan.facade import v3 as facade
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


class VlanDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @permission_obj_apiview([permissions.read_obj_permission])
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vlans with details by ids ou dict.
        """

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_vlan_by_search(self.search)
            vlans = obj_model['query_set']
            only_main_property = False
        else:
            obj_ids = kwargs['obj_ids'].split(';')
            vlans = facade.get_vlan_by_ids(obj_ids)
            obj_model = None
            only_main_property = True

        # serializer vips
        serializer_vips = serializers.VlanV3Serializer(
            vlans,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        response = render_to_json(
            serializer_vips,
            main_property='vlans',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('vlan_post')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Creates list of vlans."""

        data = request.DATA

        json_validate(SPECS.get('vlan_post')).validate(data)

        response = list()
        for vlan in data['vlans']:
            vl = facade.create_vlan(vlan, request.user)
            response.append({'id': vl.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('vlan_put')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.write_obj_permission])
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Updates list of vlans."""

        data = request.DATA

        json_validate(SPECS.get('vlan_put')).validate(data)

        response = list()
        for vlan in data['vlans']:
            vl = facade.update_vlan(vlan, request.user)
            response.append({'id': vl.id})

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.delete_obj_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Deletes list of vlans."""

        obj_ids = kwargs['obj_ids'].split(';')
        for obj_id in obj_ids:
            facade.delete_vlan(
                obj_id
            )

        return Response({}, status=status.HTTP_200_OK)


class VlanAsyncView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('vlan_post')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Creates list of vlans."""

        response = list()
        data = request.DATA
        json_validate(SPECS.get('vlan_post')).validate(data)

        user = request.user

        for vlan in data['vlans']:
            task_obj = tasks.create_vlan.apply_async(args=[vlan, user.id],
                                                     queue='napi.network')

            task = {
                'task_id': task_obj.id
            }

            response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)

    @logs_method_apiview
    @raise_json_validate('vlan_put')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.write_obj_permission])
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Updates list of vlans."""

        response = list()
        data = request.DATA
        json_validate(SPECS.get('vlan_put')).validate(data)

        user = request.user

        for vlan in data['vlans']:
            task_obj = tasks.update_vlan.apply_async(args=[vlan, user.id],
                                                     queue='napi.network')

            task = {
                'task_id': task_obj.id
            }

            response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.delete_obj_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Deletes list of vlans."""

        response = list()
        obj_ids = kwargs['obj_ids'].split(';')

        user = request.user

        for obj_id in obj_ids:
            task_obj = tasks.delete_vlan.apply_async(args=[obj_id, user.id],
                                                     queue='napi.network')

            task = {
                'task_id': task_obj.id
            }

            response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)
