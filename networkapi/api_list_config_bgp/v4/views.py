from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from networkapi.api_list_config_bgp.v4 import facade
from networkapi.api_list_config_bgp.v4 import serializers
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate
from networkapi.api_list_config_bgp.v4.permissions import Read
from networkapi.api_list_config_bgp.v4.permissions import Write
import logging

log = logging.getLogger(__name__)

class ListConfigBGPDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of List Config BGP's by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_list_config_bgp_by_search(self.search)
            objects = obj_model['query_set']
            only_main_property = False
        else:
            ids = kwargs.get('obj_ids').split(';')
            objects = facade.get_list_config_bgp_by_ids(ids)
            only_main_property = True
            obj_model = None

        # serializer
        serializer = serializers.ListConfigBGPV4Serializer(
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
            main_property='lists_config_bgp',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('list_config_bgp_post_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create new List Config BGP."""

        objects = request.DATA
        json_validate(SPECS.get('list_config_bgp_post_v4')).validate(objects)
        response = list()
        for obj in objects['lists_config_bgp']:

            created_obj = facade.create_list_config_bgp(obj)
            response.append({'id': created_obj.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('list_config_bgp_put_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Update List Config BGP."""

        objects = request.DATA
        json_validate(SPECS.get('list_config_bgp_put_v4')).validate(objects)
        response = list()
        for obj in objects['lists_config_bgp']:

            created_obj = facade.update_list_config_bgp(obj)
            response.append({
                'id': created_obj.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Delete List Config BGP."""

        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_list_config_bgp(obj_ids)

        return Response({}, status=status.HTTP_200_OK)