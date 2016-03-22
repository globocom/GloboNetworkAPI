# -*- coding:utf-8 -*-
import logging

from networkapi.ambiente.models import EnvironmentVip
from networkapi.api_environment_vip import facade
from networkapi.api_environment_vip.permissions import Read
from networkapi.api_environment_vip.serializers import EnvironmentVipSerializer, OptionVipEnvironmentVipSerializer, \
    OptionVipSerializer
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.util import logs_method_apiview


from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

log = logging.getLogger(__name__)


@permission_classes((IsAuthenticated, Read))
class OptionVipEnvironmentVipOneView(APIView):

    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Method to return option vip list by environment id
        Param environment_vip_id: environment id
        Return option vip object list
        """
        try:
            environment_vip_id = kwargs["environment_vip_id"]

            options_vip = facade.get_option_vip_by_environment_vip_ids([environment_vip_id])

            if options_vip:
                options_vip = options_vip[0]

            serializer_options = OptionVipEnvironmentVipSerializer(
                options_vip,
                many=True
            )
            return Response(serializer_options.data, status.HTTP_200_OK)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException()


@permission_classes((IsAuthenticated, Read))
class EnvironmentVipStepOneView(APIView):

    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Method to return finality, client or environment vip list.
        Param request.GET["finality"]: finality of environment(optional)
        Param request.GET["client"]: client of environment(optional)
        Param request.GET["environmentp44"]: environmentp44(optional)
        Return finality list: when request has no finality and client.
        Return client list: when request has only finality.
        Return environment vip list: when request has finality and client.
        Return object environment vip: when request has finality and client and environmentp44.
        """

        try:
            data = request.GET

            finality = data.get('finality')
            client = data.get('client')
            environmentp44 = data.get('environmentp44')

            if client != '' and finality != '' and environmentp44 != '':
                obj = EnvironmentVip().get_by_values(finality, client, environmentp44)
                evip_values = EnvironmentVipSerializer(
                    obj,
                    many=False
                ).data
            elif client != '' and finality != '':
                obj = EnvironmentVip().list_all_ambientep44_by_finality_and_cliente(finality, client)
                evip_values = EnvironmentVipSerializer(
                    obj,
                    many=True
                ).data
            elif finality != '':
                evip_values = EnvironmentVip().list_all_clientes_by_finalitys(finality)
            else:
                evip_values = EnvironmentVip().list_all_finalitys()

            return Response(evip_values, status=status.HTTP_200_OK)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException()


class OptionVipEnvironmentTypeVipOneView(APIView):

    @permission_classes((IsAuthenticated, Read))
    def get(self, request, *args, **kwargs):
        """
        Method to return option vip list by environment id and option vip type
        Param environment_vip_id: environment id
        Param type_option: environment id
        Return option vip object list
        """
        log.info("View:OptionVipEnvironmentTypeVipOneView, method:get")
        try:
            environment_vip_id = kwargs["environment_vip_id"]
            type_option = kwargs["type_option"]
            search_list = {
                'environment_vip_id': environment_vip_id,
                'type_option': type_option
            }

            options_vip = facade.get_option_vip_by_environment_vip_type([search_list])

            if options_vip:
                options_vip = options_vip[0]

            serializer_options = OptionVipSerializer(
                options_vip,
                many=True
            )
            return Response(serializer_options.data, status.HTTP_200_OK)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException()
