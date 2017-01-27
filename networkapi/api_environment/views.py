# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_environment import facade
from networkapi.api_environment import serializers
from networkapi.api_environment.permissions import Read
from networkapi.api_environment.permissions import Write
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate

log = logging.getLogger(__name__)


class EnvironmentDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of environment by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_environment_by_search(self.search)
            environments = obj_model['query_set']
            only_main_property = False
        else:
            environment_ids = kwargs.get('obj_ids').split(';')
            environments = facade.get_environment_by_ids(environment_ids)
            only_main_property = True
            obj_model = None

        # serializer environments
        serializer_env = serializers.EnvironmentV3Serializer(
            environments,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        data = render_to_json(
            serializer_env,
            main_property='environments',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('environment_post')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create new environment."""

        envs = request.DATA
        json_validate(SPECS.get('environment_post')).validate(envs)
        response = list()
        for env in envs['environments']:

            env_obj = facade.create_environment(env)
            response.append({'id': env_obj.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('environment_put')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Update environment."""

        envs = request.DATA
        json_validate(SPECS.get('environment_put')).validate(envs)
        response = list()
        for env in envs['environments']:

            env_obj = facade.update_environment(env)
            response.append({
                'id': env_obj.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Delete environment."""

        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_environment(obj_ids)

        return Response({}, status=status.HTTP_200_OK)


class EnvEnvVipRelatedView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of environment by ids ou dict."""

        only_main_property = True
        if not kwargs.get('environment_vip_id'):
            environments = facade.list_environment_environment_vip_related()
        else:
            env_id = kwargs.get('environment_vip_id')
            environments = facade.list_environment_environment_vip_related(
                env_id)

        # serializer environments
        serializer_env = serializers.EnvironmentV3Serializer(
            environments,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        data = render_to_json(
            serializer_env,
            main_property='environments',
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)
