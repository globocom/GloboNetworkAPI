# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_vlan import serializers
from networkapi.api_vlan.facade import v3 as facade
from networkapi.api_vlan.permissions import delete_obj_permission
from networkapi.api_vlan.permissions import Read
from networkapi.api_vlan.permissions import Write
from networkapi.api_vlan.permissions import write_obj_permission
from networkapi.distributedlock import LOCK_VLAN
from networkapi.settings import SPECS
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import permission_obj_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import create_lock
from networkapi.util.geral import CustomResponse
from networkapi.util.geral import destroy_lock
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate
log = logging.getLogger(__name__)


class VlanDBView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vlans with details by ids ou dict

        """
        try:

            if not kwargs.get('obj_ids'):
                obj_model = facade.get_vlan_by_search(self.search)
                vlans = obj_model['query_set']
                only_main_property = False
            else:
                obj_ids = kwargs['obj_ids'].split(';')
                vlans = facade.get_vlan_by_ids(obj_ids)
                obj_model = None
                only_main_property = True

            # serializer vips
            serializer_vips = serializers.VlanV3Serializer(
                vlans,
                many=True,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude,
                kind=self.kind
            )

            # prepare serializer with customized properties
            response = render_to_json(
                serializer_vips,
                main_property='vlans',
                obj_model=obj_model,
                request=request,
                only_main_property=only_main_property
            )

            return CustomResponse(response, status=status.HTTP_200_OK, request=request)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('vlan_post')
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Creates list of vlans
        """

        data = request.DATA

        json_validate(SPECS.get('vlan_post')).validate(data)

        response = list()
        for vlan in data['vlans']:
            vl = facade.create_vlan(vlan, request.user)
            response.append({'id': vl.id})

        return CustomResponse(response, status=status.HTTP_201_CREATED, request=request)

    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([write_obj_permission])
    @logs_method_apiview
    @raise_json_validate('vlan_put')
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Updates list of vlans
        """
        data = request.DATA

        json_validate(SPECS.get('vlan_put')).validate(data)

        locks_list = create_lock(data['vlans'], LOCK_VLAN)

        response = list()
        try:
            for vlan in data['vlans']:
                vl = facade.update_vlan(vlan, request.user)
                response.append({'id': vl.id})
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return CustomResponse(response, status=status.HTTP_200_OK, request=request)

    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([delete_obj_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of vlans
        """

        obj_ids = kwargs['obj_ids'].split(';')
        locks_list = facade.create_lock(obj_ids, LOCK_VLAN)
        try:
            facade.delete_vlan(
                obj_ids
            )
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return CustomResponse({}, status=status.HTTP_200_OK, request=request)
