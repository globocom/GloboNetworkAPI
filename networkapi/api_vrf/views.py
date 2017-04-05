# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_environment.permissions import Write
from networkapi.api_vrf import facade
from networkapi.api_vrf import serializers
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate

log = logging.getLogger(__name__)


class VrfDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vrf by ids ou dict
        """

        if not kwargs.get('vrf_ids'):
            obj_model = facade.get_vrfs_by_search(self.search)
            vrfs = obj_model['query_set']
            only_main_property = False
        else:
            vrf_ids = kwargs.get('vrf_ids').split(';')
            vrfs = facade.get_vrfs_by_ids(vrf_ids)
            only_main_property = True
            obj_model = None

        serializer_class = serializers.VrfV3Serializer

        # serializer vrfs
        serializer_vrf = serializer_class(
            vrfs,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude
        )

        # prepare serializer with customized properties
        response = render_to_json(
            serializer_vrf,
            main_property='vrfs',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('vrf_post')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Create new vrfs
        """
        vrfs = request.DATA
        json_validate(SPECS.get('vrf_post')).validate(vrfs)
        response = list()
        for vrf in vrfs['vrfs']:
            vrf = facade.create_vrf(vrf)
            response.append({'id': vrf.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('vrf_put')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Update vrfs
        """
        vrfs = request.DATA
        json_validate(SPECS.get('vrf_put')).validate(vrfs)
        response = list()
        for vrf in vrfs['vrfs']:
            vrf = facade.update_vrf(vrf)
            response.append({
                'id': vrf.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Delete vrfs
        """
        vrf_ids = kwargs['vrf_ids'].split(';')
        response = {}
        for id in vrf_ids:
            facade.delete_vrf(id)

        return Response(response, status=status.HTTP_200_OK)
