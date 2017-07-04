# -*- coding: utf-8 -*-
# Create your views here.
from django.db.transaction import commit_on_success
from networkapi.api_virtual_interface.v4.permissions import Read
from networkapi.api_virtual_interface.v4.permissions import Write
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_virtual_interface.v4 import facade
from networkapi.api_virtual_interface.v4 import serializers
from networkapi.settings import SPECS_V4
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate


class VirtualInterfaceDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of Virtual Interface's by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_virtual_interface_by_search(self.search)
            virtual_interfaces = obj_model['query_set']
            only_main_property = False
        else:
            vi_ids = kwargs.get('obj_ids').split(';')
            virtual_interfaces = facade.get_virtual_interface_by_ids(vi_ids)
            only_main_property = True
            obj_model = None

        # serializer Virtual Interface's
        serializer_vi = serializers.VirtualInterfaceV4Serializer(
            virtual_interfaces,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        data = render_to_json(
            serializer_vi,
            main_property='virtual_interfaces',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('virtual_interface_post_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create new Virtual Interface."""

        virtual_interfaces = request.DATA
        json_validate(SPECS_V4.get('virtual_interface_post_v4')).\
            validate(virtual_interfaces)
        response = list()
        for vi_ in virtual_interfaces['virtual_interfaces']:

            vi_obj = facade.create_virtual_interface(vi_)
            response.append({'id': vi_obj.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('virtual_interface_put_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Update Virtual Interface."""

        virtual_interfaces = request.DATA
        json_validate(SPECS_V4.get('virtual_interface_put_v4')).\
            validate(virtual_interfaces)
        response = list()
        for vi_ in virtual_interfaces['virtual_interfaces']:

            vi_obj = facade.update_virtual_interface(vi_)
            response.append({
                'id': vi_obj.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Delete Virtual Interface."""

        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_virtual_interface(obj_ids)

        return Response({}, status=status.HTTP_200_OK)
