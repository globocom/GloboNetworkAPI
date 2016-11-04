# -*- coding: utf-8 -*-
import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_vrf import facade
from networkapi.api_vrf import serializers
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json

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
                vrf_ids = kwargs.get('environment_ids').split(';')
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
            data = render_to_json(
                serializer_vrf,
                main_property='vrfs',
                obj_model=obj_model,
                request=request,
                only_main_property=only_main_property
            )

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
