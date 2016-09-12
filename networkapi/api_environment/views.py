# -*- coding:utf-8 -*-
import ast
import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_environment import exceptions
from networkapi.api_environment import facade
from networkapi.api_environment import serializers
from networkapi.api_environment.permissions import Read
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.util import logs_method_apiview
from networkapi.util import permission_classes_apiview
from networkapi.util.geral import generate_return_json

log = logging.getLogger(__name__)


class EnvironmentDBView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Returns a list of environment by ids ou dict
        """
        try:
            if not kwargs.get('environment_ids'):
                try:
                    search = ast.literal_eval(request.GET.get('search'))
                except:
                    search = {}

                environments = facade.get_environment_by_search(search)
                serializer_env = serializers.EnvironmentV3Serializer(
                    environments['envs'],
                    many=True
                )
                data = generate_return_json(
                    serializer_env,
                    'environments',
                    environments,
                    request
                )

            else:
                environment_ids = kwargs['environment_ids'].split(';')
                environments = facade.get_environment_by_ids(environment_ids)

                if environments:
                    serializer_env = serializers.EnvironmentV3Serializer(
                        environments,
                        many=True
                    )
                    data = generate_return_json(
                        serializer_env,
                        'environments',
                        only_main_property=True
                    )
                else:
                    raise exceptions.EnvironmentDoesNotExistException()

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)


class EnvEnvVipRelatedView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Returns a list of environment by ids ou dict
        """
        try:

            if not kwargs.get('environment_vip_ids'):
                environments = facade.list_environment_environment_vip_related()
                serializer_env = serializers.EnvironmentDetaailsSerializer(
                    environments,
                    many=True
                )
                data = generate_return_json(
                    serializer_env,
                    'environments',
                    only_main_property=True
                )
            else:
                env_id = kwargs.get('environment_vip_ids')
                environments = facade.list_environment_environment_vip_related(env_id)
                serializer_env = serializers.EnvironmentDetaailsSerializer(
                    environments,
                    many=True
                )
                data = generate_return_json(
                    serializer_env,
                    'environments',
                    only_main_property=True
                )

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
