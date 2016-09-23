# -*- coding:utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_environment import facade
from networkapi.api_environment import serializers
from networkapi.api_environment.permissions import Read
from networkapi.api_environment.permissions import Write
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.settings import SPECS
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import generate_return_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate

log = logging.getLogger(__name__)


class EnvironmentDBView(APIView):

    def render(self, obj, **kwargs):

        obj_model = None
        if isinstance(obj, dict):
            obj_model = obj
            obj = obj['envs']

        serializer_env = serializers.EnvironmentV3Serializer(
            obj,
            many=True,
            fields=kwargs.get('fields'),
            include=kwargs.get('include'),
            exclude=kwargs.get('exclude')
        )
        data = generate_return_json(
            serializer_env,
            'environments',
            obj_model=obj_model,
            request=kwargs.get('request', None),
            only_main_property=kwargs.get('only_main_property', False)
        )
        return data

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of environment by ids ou dict
        """
        default_fields = (
            'id',
            'grupo_l3',
            'ambiente_logico',
            'divisao_dc',
            'filter',
            'acl_path',
            'ipv4_template',
            'ipv6_template',
            'link',
            'min_num_vlan_1',
            'max_num_vlan_1',
            'min_num_vlan_2',
            'max_num_vlan_2',
            'vrf',
            'father_environment'
        )
        try:
            if not kwargs.get('environment_ids'):
                environments = facade.get_environment_by_search(self.search)
                only_main_property = False
            else:
                environment_ids = kwargs.get('environment_ids').split(';')
                environments = facade.get_environment_by_ids(environment_ids)
                default_list = list(default_fields)
                default_list.append('configs')
                default_fields = tuple(default_list)
                only_main_property = True

            fields = self.fields if self.fields else default_fields

            data = self.render(
                environments,
                fields=fields,
                include=self.include,
                exclude=self.exclude,
                only_main_property=only_main_property,
                request=request
            )

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('pool_post')
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Create new environment
        """
        envs = request.DATA
        json_validate(SPECS.get('environment_post')).validate(envs)
        response = list()
        for pool in envs['environments']:

            env = facade.create_environment(pool)
            response.append({'id': env.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('pool_post')
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Update environment
        """
        envs = request.DATA
        json_validate(SPECS.get('environment_put')).validate(envs)
        response = list()
        for env in envs['environments']:

            env = facade.update_environment(env)
            response.append({
                'id': env.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Delete environment
        """
        env_ids = kwargs['environment_ids'].split(';')
        response = {}
        facade.delete_environment(env_ids)

        return Response(response, status.HTTP_200_OK)


class EnvEnvVipRelatedView(APIView):

    def render(self, obj, **kwargs):
        serializer_env = serializers.EnvironmentDetailsSerializer(
            obj,
            many=True,
            fields=kwargs.get('fields'),
            include=kwargs.get('include'),
            exclude=kwargs.get('exclude')
        )
        data = generate_return_json(
            serializer_env,
            'environments',
            only_main_property=kwargs.get('only_main_property', False)
        )
        return data

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of environment by ids ou dict
        """
        try:
            only_main_property = True
            if not kwargs.get('environment_vip_ids'):
                environments = facade.list_environment_environment_vip_related()
            else:
                env_id = kwargs.get('environment_vip_ids').split(';')
                environments = facade.list_environment_environment_vip_related(env_id)

            data = self.render(
                environments,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude,
                only_main_property=only_main_property
            )

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
