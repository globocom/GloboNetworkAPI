# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_aws import facade
from networkapi.api_aws import serializers
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


class AwsVpcView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @prepare_search
    @permission_classes_apiview((IsAuthenticated, Read))
    def get(self, request, *args, **kwargs):
        """
        Returns a list of aws vpc by ids ou dict
        """

        if not kwargs.get('aws_vpc_ids'):
            obj_model = facade.get_aws_vpc_by_search(self.search)
            aws_vpc = obj_model['query_set']
            only_main_property = False
        else:
            aws_vpc_ids = kwargs.get('aws_vpc_ids').split(';')
            aws_vpc = facade.get_aws_vpc_by_ids(aws_vpc_ids)
            only_main_property = True
            obj_model = None

        serializer_class = serializers.AwsVPCSerializer

        # serializer aws_vpc
        serializer_aws_vpc = serializer_class(
            aws_vpc,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude
        )

        # prepare serializer with customized properties
        response = render_to_json(
            serializer_aws_vpc,
            main_property='aws_vpc',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('aws_vpc_post')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Create new aws_vpc
        """
        aws_vpc = request.DATA
        json_validate(SPECS.get('aws_vpc_post')).validate(aws_vpc)
        response = list()
        for aws_vpc in aws_vpc['aws_vpc']:
            aws_vpc = facade.create_aws_vpc(aws_vpc)
            response.append({'id': aws_vpc.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('aws_vpc_put')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Update aws_vpc
        """
        aws_vpc = request.DATA
        json_validate(SPECS.get('aws_vpc_put')).validate(aws_vpc)
        response = list()
        for aws_vpc in aws_vpc['aws_vpc']:
            aws_vpc = facade.update_aws_vpc(aws_vpc)
            response.append({
                'id': aws_vpc.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Delete aws_vpc
        """
        aws_vpc_ids = kwargs['aws_vpc_ids'].split(';')
        response = {}
        for id in aws_vpc_ids:
            facade.delete_aws_vpc(id)

        return Response(response, status=status.HTTP_200_OK)
