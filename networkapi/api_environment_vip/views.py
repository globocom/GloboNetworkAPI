# -*- coding: utf-8 -*-
import logging
import urllib

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.ambiente.models import EnvironmentVip
from networkapi.api_environment_vip import facade
from networkapi.api_environment_vip import serializers
from networkapi.api_environment_vip.permissions import Read
from networkapi.api_environment_vip.permissions import Write
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate

log = logging.getLogger(__name__)


class OptionVipEnvironmentVipOneView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Method to return option vip list by environment id
        Param environment_vip_id: environment id
        Return option vip object list
        """

        environment_vip_id = kwargs['environment_vip_id'].split(';')

        options_vip = facade.get_option_vip_by_environment_vip_ids(
            environment_vip_id)

        if options_vip:
            options_vip = options_vip[0]

        self.include += ('option__details',)
        serializer_options = serializers.OptionVipEnvironmentVipV3Serializer(
            options_vip,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )
        return Response(serializer_options.data, status=status.HTTP_200_OK)


class EnvironmentVipStepOneView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
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

        data = request.GET

        finality = data.get('finality', '')
        client = data.get('client', '')
        environmentp44 = data.get('environmentp44', '')

        if client != '' and finality != '':
            if environmentp44 != '':
                obj = EnvironmentVip().get_by_values(
                    finality, client, environmentp44)
                many = False
            else:
                obj = EnvironmentVip().list_all_ambientep44_by_finality_and_cliente(
                    finality, client)
                many = True

            evip_values = serializers.EnvironmentVipV3Serializer(
                obj,
                many=many,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude,
                kind=self.kind
            ).data
        elif finality != '':
            evip_values = EnvironmentVip().list_all_clientes_by_finalitys(finality)
        else:
            evip_values = EnvironmentVip().list_all_finalitys()

        return Response(evip_values, status=status.HTTP_200_OK)


class EnvironmentVipView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Method to return environment vip list.
        Param obj_ids: obj_ids
        """
        if not kwargs.get('obj_id'):
            obj_model = facade.get_environmentvip_by_search(self.search)
            environments_vip = obj_model['query_set']
            only_main_property = False
        else:
            obj_ids = kwargs['obj_id'].split(';')
            environments_vip = facade.get_environmentvip_by_ids(obj_ids)
            only_main_property = True
            obj_model = None

        environmentvip_serializer = serializers.EnvironmentVipV3Serializer(
            environments_vip,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        response = render_to_json(
            environmentvip_serializer,
            main_property='environments_vip',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('environment_vip_put')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):

        envs = request.DATA
        json_validate(SPECS.get('environment_vip_put')).validate(envs)
        response = list()
        for env in envs['environments_vip']:

            ret = facade.update_environment_vip(env)
            response.append({
                'id': ret.id,
                'msg': 'success'
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('environment_vip_post')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):

        envs = request.DATA
        json_validate(SPECS.get('environment_vip_post')).validate(envs)
        response = list()
        for env in envs['environments_vip']:

            ret = facade.create_environment_vip(env)
            response.append({
                'id': ret.id
            })

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):

        response = {}
        obj_ids = kwargs['obj_id'].split(';')
        facade.delete_environment_vip(obj_ids)

        return Response(response, status=status.HTTP_200_OK)


class OptionVipEnvironmentTypeVipView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Method to return option vip list by environment id and option vip type
        Param environment_vip_id: environment id
        Param type_option: environment id
        Return option vip object list
        """

        environment_vip_ids = kwargs['environment_vip_id'].split(';')
        type_option = urllib.unquote(kwargs['type_option']).decode('utf8')
        search_list = list()

        for environment_vip_id in environment_vip_ids:
            search_list.append({
                'environment_vip_id': environment_vip_id,
                'type_option': type_option
            })

        options_vips = facade.get_option_vip_by_environment_vip_type(
            search_list)

        data = dict()
        data['optionsvip'] = list()
        for options_vip in options_vips:
            serializer_options = serializers.OptionVipV3Serializer(
                options_vip,
                many=True,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude,
                kind=self.kind
            )
            data['optionsvip'].append(serializer_options.data)

        return Response(data, status=status.HTTP_200_OK)


class TypeOptionEnvironmentVipView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    def get(self, request, *args, **kwargs):
        """
        Method to return option vip list by environment id and option vip type
        Param environment_vip_id: environment id
        Param type_option: environment id
        Return option vip object list
        """
        environment_vip_ids = kwargs['environment_vip_id'].split(';')
        type_option_vip = facade.get_type_option_vip_by_environment_vip_ids(
            environment_vip_ids)

        return Response(type_option_vip, status=status.HTTP_200_OK)
