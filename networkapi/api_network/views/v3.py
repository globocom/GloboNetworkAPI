# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_network.facade import v3 as facade
from networkapi.api_network.permissions import Read
from networkapi.api_network.permissions import Write
from networkapi.api_network.serializers import v3 as serializers
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import raise_json_validate
log = logging.getLogger(__name__)


class NetworkIPv4View(APIView):

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vip request by ids ou dict
        """
        try:

            if not kwargs.get('obj_id'):
                obj_model = facade.get_networkipv4_by_search(self.search)
                networks = obj_model['query_set']
                only_main_property = False
            else:
                obj_ids = kwargs.get('obj_id').split(';')
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

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('networkv4_post')
    @commit_on_success
    def post(self, *args, **kwargs):
        pass

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('networkv4_put')
    @commit_on_success
    def put(self, *args, **kwargs):
        pass


class NetworkIPv6View(APIView):

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):

        try:

            if not kwargs.get('obj_id'):
                obj_model = facade.get_networkipv6_by_search(self.search)
                networks = obj_model['query_set']
                only_main_property = False
            else:
                obj_ids = kwargs.get('obj_id').split(';')
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

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('networkv6_post')
    @commit_on_success
    def post(self, *args, **kwargs):
        pass

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('networkv6_put')
    @commit_on_success
    def put(self, *args, **kwargs):
        pass
