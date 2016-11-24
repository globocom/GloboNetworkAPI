# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from networkapi.api_environment.permissions import Write
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_vrf import facade
from networkapi.api_vrf import serializers
from networkapi.settings import SPECS
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import CustomResponse
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate

log = logging.getLogger(__name__)


class VrfDBView(APIView):

    @logs_method_apiview
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vrf by ids ou dict
        """

        try:

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

            return CustomResponse(response, status=status.HTTP_200_OK, request=request)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('vrf_post')
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

        return CustomResponse(response, status=status.HTTP_201_CREATED, request=request)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('vrf_put')
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

        return CustomResponse(response, status=status.HTTP_200_OK, request=request)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Delete vrfs
        """
        vrf_ids = kwargs['vrf_ids'].split(';')
        response = {}
        for id in vrf_ids:
            pass  # TODO When key is related to other tables, Django removes tuples of these tables
            # facade.delete_vrf(id)

        return CustomResponse(response, status=status.HTTP_200_OK, request=request)
