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

from networkapi.util.appcache import get_cached_search
from networkapi.util.appcache import set_cache_search_with_list
from networkapi.util.appcache import ENVIRONMENT_CACHE_ENTRY


log = logging.getLogger(__name__)


class EnvironmentLogicDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of environment by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_logic_environment_by_search(self.search)
            environments = obj_model['query_set']
            only_main_property = False
        else:
            return Response(dict(), status=status.HTTP_400_BAD_REQUEST)

        # serializer environments
        serializer_env = serializers.AmbienteLogicoV3Serializer(
            environments,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        data = render_to_json(
            serializer_env,
            main_property='logic_environments',
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
        json_validate(SPECS.get('simple_env_post')).validate(envs)
        response = list()
        for env in envs['logic']:
            env_obj = facade.create_logic_environment(env)
            response.append(dict(id=env_obj.id))

        return Response(response, status=status.HTTP_201_CREATED)


class EnvironmentL3DBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of environment by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_l3_environment_by_search(self.search)
            environments = obj_model['query_set']
            only_main_property = False
        else:
            return Response(dict(), status=status.HTTP_400_BAD_REQUEST)

        # serializer environments
        serializer_env = serializers.GrupoL3Serializer(
            environments,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        data = render_to_json(
            serializer_env,
            main_property='l3_environments',
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
        json_validate(SPECS.get('simple_env_post')).validate(envs)
        response = list()
        for env in envs['l3']:
            env_obj = facade.create_l3_environment(env)
            response.append(dict(id=env_obj.id))

        return Response(response, status=status.HTTP_201_CREATED)


class EnvironmentDCDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of environment by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_dc_environment_by_search(self.search)
            environments = obj_model['query_set']
            only_main_property = False
        else:
            return Response(dict(), status=status.HTTP_400_BAD_REQUEST)

        # serializer environments
        serializer_env = serializers.DivisaoDcV3Serializer(
            environments,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        data = render_to_json(
            serializer_env,
            main_property='environments_dc',
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
        json_validate(SPECS.get('simple_env_post')).validate(envs)
        response = list()
        for env in envs['dc']:
            env_obj = facade.create_dc_environment(env)
            response.append(dict(id=env_obj.id))

        return Response(response, status=status.HTTP_201_CREATED)


class EnvironmentDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of environment by ids ou dict."""

        # String with all important fields to define response
        request_identifier_to_cache = str(
            self.search)+str(self.fields)+str(self.include)+str(self.exclude)+str(self.kind)

        if not kwargs.get('obj_ids'):
            data = get_cached_search(
                ENVIRONMENT_CACHE_ENTRY, request_identifier_to_cache)
            if data:
                return Response(data, status=status.HTTP_200_OK)

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

        set_cache_search_with_list(
            ENVIRONMENT_CACHE_ENTRY, request_identifier_to_cache, data, facade.get_environment_cache_time())
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


class EnvFlowView(CustomAPIView):

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Read))
    def get(self, request, *args, **kwargs):
        """Returns a list of environment by ids ou dict."""
        environment_id = kwargs.get('environment_id')

        if kwargs.get('flow_id') is not None:
            flow_id = kwargs.get('flow_id')
            flows = facade.list_flows_by_envid(environment_id, flow_id=flow_id)
        else:
            flows = facade.list_flows_by_envid(environment_id)

        return Response(flows, status=status.HTTP_200_OK)

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Write))
    def post(self, request, *args, **kwargs):
        """ Inserts new SDN flows on the remote Controller """
        environment_id = kwargs.get('environment_id')
        flow_id = kwargs.get('flow_id')

        user = request.user

        task = facade.insert_flow(environment_id, request.DATA, user.id)

        response = {
            'id': flow_id or environment_id,
            'task_id': task.id
        }

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Write))
    def delete(self, request, *args, **kwargs):
        """ Deletes a single flow by id or all flows if no id was given """

        environment_id = kwargs.get('environment_id')
        flow_id = kwargs.get('flow_id', None)
        user = request.user

        if flow_id:
            facade.delete_flow(environment_id, flow_id, user.id)
        else:
            # Flush all the flows
            facade.flush_flows(environment_id)

        return Response({}, status=status.HTTP_200_OK)

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Write))
    def put(self, request, *args, **kwargs):
        """ Updates an Environment by flushing it and then inserting flows """
        environment_id = kwargs.get('environment_id')
        flow_id = kwargs.get('flow_id')

        user = request.user

        if flow_id:
            task = facade.insert_flow(environment_id, request.DATA, user.id)
        else:
            task = facade.update_flows(environment_id, request.DATA, user.id)

        response = {
            'id': flow_id or environment_id,
            'task_id': task.id
        }

        return Response(response, status=status.HTTP_200_OK)


class EnvironmentCIDRDBView(CustomAPIView):

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of environment by ids ou dict."""

        if kwargs.get('cidr_id'):
            cidr_ids = kwargs.get('cidr_id').split(';')
            cidr = list()
            for ids in cidr_ids:
                cidr += facade.get_cidr(cidr=ids)
            only_main_property = True
            obj_model = None
        elif kwargs.get('env_id'):
            env_id = kwargs.get('env_id')
            cidr = facade.get_cidr(environment=env_id)
            only_main_property = True
            obj_model = None
        else:
            obj_model = facade.get_cidr_by_search(self.search)
            cidr = obj_model.get('query_set')
            only_main_property = False

        serializer = serializers.EnvCIDRSerializer(
            cidr,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        data = render_to_json(
            serializer,
            main_property='cidr',
            request=request,
            obj_model=obj_model,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create new environment."""

        objects = request.DATA
        response = list()

        if objects.get('cidr')[0].get('network'):
            json_validate(SPECS.get('cidr_post')).validate(objects)
            for cidr in objects['cidr']:
                cidr_obj, msg = facade.post_cidr(cidr)
                response.append(dict(id=cidr_obj, message=msg))
        else:
            json_validate(SPECS.get('cidr_post_auto')).validate(objects)
            for cidr in objects['cidr']:
                cidr_obj, msg = facade.post_cidr_auto(cidr)
                response.append(dict(id=cidr_obj, message=msg))

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Write))
    def delete(self, request, *args, **kwargs):
        """ Deletes a single cidr by id or all cidr associate to an environment. """

        if kwargs.get('cidr_id'):
            ids = kwargs.get('cidr_id').split(';')
            for _id in ids:
                facade.delete_cidr(cidr=_id)
        elif kwargs.get('env_id'):
            _id = kwargs.get('env_id')
            facade.delete_cidr(environment=_id)

        return Response({}, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('cidr_put')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Update CIDR."""

        cidrs = request.DATA

        json_validate(SPECS.get('cidr_put')).validate(cidrs)

        response = list()

        for cidr in cidrs['cidr']:
            cidr_obj = facade.update_cidr(cidr)
            response.append(dict(id=cidr_obj))

        return Response(response, status=status.HTTP_200_OK)
