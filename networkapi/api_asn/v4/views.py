# -*- coding: utf-8 -*-
# Create your views here.
import logging
from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_asn.v4 import facade
from networkapi.api_asn.v4 import serializers
from networkapi.api_asn.v4.permissions import Read
from networkapi.api_asn.v4.permissions import Write
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate


log = logging.getLogger(__name__)


class AsDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of AS's by ids ou dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_as_by_search(self.search)
            as_s = obj_model['query_set']
            only_main_property = False
        else:
            as_ids = kwargs.get('obj_ids').split(';')
            as_s = facade.get_as_by_ids(as_ids)
            only_main_property = True
            obj_model = None

        # serializer AS's
        serializer_as = serializers.AsnV4Serializer(
            as_s,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        data = render_to_json(
            serializer_as,
            main_property='asns',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('as_post_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create new AS."""

        as_s = request.DATA
        json_validate(SPECS.get('as_post_v4')).validate(as_s)
        response = list()
        for as_ in as_s['asns']:

            as_obj = facade.create_as(as_)
            response.append({'id': as_obj.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('as_put_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Update AS."""

        as_s = request.DATA
        json_validate(SPECS.get('as_put_v4')).validate(as_s)
        response = list()
        for as_ in as_s['asns']:

            as_obj = facade.update_as(as_)
            response.append({
                'id': as_obj.id
            })

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Delete AS."""

        obj_ids = kwargs['obj_ids'].split(';')
        facade.delete_as(obj_ids)

        return Response({}, status=status.HTTP_200_OK)


class AsEquipmentDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Returns a list of AS's by ids ou dict."""

        if not kwargs.get('obj_ids') and\
            not kwargs.get('asn_ids') and\
            not kwargs.get('equip_ids'):
            obj_model = facade.get_as_equipment_by_search(self.search)
            as_s = obj_model['query_set']
            only_main_property = False
        else:
            obj_model = None
            only_main_property = True
            if kwargs.get('obj_ids'):
                as_ids = kwargs.get('obj_ids').split(';')
                as_s = facade.get_as_equipment_by_id(as_ids)
            elif kwargs.get('asn_ids'):
                as_ids = kwargs.get('asn_ids').split(';')
                as_s = facade.get_as_equipment_by_asn(as_ids)
            elif kwargs.get('equip_ids'):
                as_ids = kwargs.get('equip_ids').split(';')
                as_s = facade.get_as_equipment_by_equip(as_ids)

        serializer_as = serializers.AsnEquipmentV4Serializer(
            as_s,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        data = render_to_json(
            serializer_as,
            main_property='asn_equipment',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('asn_equipment_post_v4')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """Create new ASNEquipment."""

        as_s = request.DATA
        json_validate(SPECS.get('asn_equipment_post_v4')).validate(as_s)
        response = list()
        for as_ in as_s['asn_equipment']:
            response = facade.create_asn_equipment(as_)

        return Response(response, status=status.HTTP_201_CREATED)
