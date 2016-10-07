import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_vlan import serializers
from networkapi.api_vlan.facade import v3 as facade
from networkapi.api_vlan.permissions import delete_obj_permission
from networkapi.api_vlan.permissions import Read
from networkapi.api_vlan.permissions import Write
from networkapi.api_vlan.permissions import write_obj_permission
from networkapi.settings import SPECS
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import permission_obj_apiview
from networkapi.util.decorators import prepare_search
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
            serializer_vips = serializers.VlanSerializerV3(
                vlans,
                many=True,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude
            )

            # prepare serializer with customized properties
            data = render_to_json(
                serializer_vips,
                main_property='vlans',
                obj_model=obj_model,
                request=request,
                only_main_property=only_main_property
            )

            return Response(data, status.HTTP_200_OK)

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

        return Response(response, status.HTTP_201_CREATED)

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

        locks_list = facade.create_lock(data['vlans'])
        try:
            for vlan in data['vlans']:
                facade.update_vlan(vlan, request.user)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)

        return Response({})

    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([delete_obj_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of vip request
        """

        obj_ids = kwargs['obj_ids'].split(';')
        locks_list = facade.create_lock(obj_ids)
        try:
            facade.delete_vlan(
                obj_ids
            )
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)

        return Response({})
