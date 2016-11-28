# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_vip_request.facade import v3 as facade
from networkapi.api_vip_request.permissions import delete_vip_permission
from networkapi.api_vip_request.permissions import deploy_vip_permission
from networkapi.api_vip_request.permissions import DeployCreate
from networkapi.api_vip_request.permissions import DeployDelete
from networkapi.api_vip_request.permissions import DeployUpdate
from networkapi.api_vip_request.permissions import Read
from networkapi.api_vip_request.permissions import Write
from networkapi.api_vip_request.permissions import write_vip_permission
from networkapi.api_vip_request.serializers.v3 import VipRequestV3Serializer
from networkapi.distributedlock import LOCK_VIP
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
from networkapi.util.json_validate import verify_ports_vip
# from networkapi.api_vip_request.serializers.v3 import VipRequestV3Serializer


log = logging.getLogger(__name__)


class VipRequestDeployView(APIView):

    @permission_classes_apiview((IsAuthenticated, Write, DeployCreate))
    @permission_obj_apiview([deploy_vip_permission])
    @logs_method_apiview
    def post(self, request, *args, **kwargs):
        """
        Creates list of vip request in equipments
        :url /api/v3/vip-request/deploy/<vip_request_ids>/
        :param vip_request_ids=<vip_request_ids>
        """

        vip_request_ids = kwargs['vip_request_ids'].split(';')
        vips = facade.get_vip_request_by_ids(vip_request_ids)
        vip_serializer = VipRequestV3Serializer(
            vips, many=True, include=('ports__identifier',))

        locks_list = create_lock(vip_serializer.data, LOCK_VIP)
        try:
            response = facade.create_real_vip_request(
                vip_serializer.data, request.user)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return CustomResponse(response, status=status.HTTP_200_OK, request=request)

    @permission_classes_apiview((IsAuthenticated, Write, DeployDelete))
    @permission_obj_apiview([deploy_vip_permission])
    @logs_method_apiview
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of vip request in equipments
        :url /api/v3/vip-request/deploy/<vip_request_ids>/
        :param vip_request_ids=<vip_request_ids>
        """

        vip_request_ids = kwargs['vip_request_ids'].split(';')
        vips = facade.get_vip_request_by_ids(vip_request_ids)
        vip_serializer = VipRequestV3Serializer(
            vips, many=True, include=('ports__identifier',))

        locks_list = create_lock(vip_serializer.data, LOCK_VIP)
        try:
            response = facade.delete_real_vip_request(
                vip_serializer.data, request.user)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return CustomResponse(response, status=status.HTTP_200_OK, request=request)

    @permission_classes_apiview((IsAuthenticated, Write, DeployUpdate))
    @permission_obj_apiview([deploy_vip_permission])
    @raise_json_validate('vip_request_put')
    @logs_method_apiview
    def put(self, request, *args, **kwargs):
        """
        Updates list of vip request in equipments

        """

        vips = request.DATA
        json_validate(SPECS.get('vip_request_put')).validate(vips)
        locks_list = create_lock(vips.get('vips'), LOCK_VIP)
        verify_ports_vip(vips)
        try:
            response = facade.update_real_vip_request(
                vips['vips'], request.user)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return CustomResponse(response, status=status.HTTP_200_OK, request=request)

    @permission_classes_apiview((IsAuthenticated, Write, DeployUpdate))
    @permission_obj_apiview([deploy_vip_permission])
    @raise_json_validate('vip_request_patch')
    @logs_method_apiview
    def patch(self, request, *args, **kwargs):
        """
        Updates list of vip request in equipments

        """
        vips = request.DATA
        json_validate(SPECS.get('vip_request_patch')).validate(vips)
        locks_list = create_lock(vips.get('vips'), LOCK_VIP)
        try:
            response = facade.patch_real_vip_request(
                vips['vips'], request.user)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return CustomResponse(response, status=status.HTTP_200_OK, request=request)


class VipRequestDBView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vip request by ids ou dict
        """
        try:
            if not kwargs.get('vip_request_ids'):

                obj_model = facade.get_vip_request_by_search(self.search)
                vips_requests = obj_model['query_set']
                only_main_property = False

            else:

                vip_request_ids = kwargs['vip_request_ids'].split(';')
                vips_requests = facade.get_vip_request_by_ids(vip_request_ids)
                obj_model = None
                # serializer vips
                only_main_property = True

            serializer_vips = VipRequestV3Serializer(
                vips_requests,
                many=True,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude,
                kind=self.kind
            )

            # prepare serializer with customized properties
            response = render_to_json(
                serializer_vips,
                main_property='vips',
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
    @raise_json_validate('vip_request_post')
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Creates list of vip request
        """

        data = request.DATA

        json_validate(SPECS.get('vip_request_post')).validate(data)

        response = list()
        verify_ports_vip(data)
        for vip in data['vips']:
            facade.validate_save(vip)
            vp = facade.create_vip_request(vip, request.user)
            response.append({'id': vp.id})

        return CustomResponse(response, status=status.HTTP_201_CREATED, request=request)

    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([write_vip_permission])
    @logs_method_apiview
    @raise_json_validate('vip_request_put')
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Updates list of vip request
        """
        data = request.DATA

        json_validate(SPECS.get('vip_request_put')).validate(data)

        locks_list = create_lock(data['vips'], LOCK_VIP)
        try:
            verify_ports_vip(data)
            for vip in data['vips']:
                facade.validate_save(vip)
                facade.update_vip_request(vip, request.user)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return CustomResponse({}, status=status.HTTP_200_OK, request=request)

    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([delete_vip_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of vip request
        """

        vip_request_ids = kwargs['vip_request_ids'].split(';')
        locks_list = create_lock(vip_request_ids, LOCK_VIP)
        keepip = request.GET.get('keepip') or '0'
        try:
            facade.delete_vip_request(
                vip_request_ids, keepip)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return CustomResponse({}, status=status.HTTP_200_OK, request=request)


class VipRequestDBDetailsView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vip request with details by ids ou dict

        """
        try:

            if not kwargs.get('vip_request_ids'):
                obj_model = facade.get_vip_request_by_search(self.search)
                vips_requests = obj_model['query_set']
                only_main_property = False
            else:
                vip_request_ids = kwargs['vip_request_ids'].split(';')
                vips_requests = facade.get_vip_request_by_ids(vip_request_ids)
                obj_model = None
                only_main_property = True

            # serializer vips
            serializer_vips = VipRequestV3Serializer(
                vips_requests,
                many=True,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude,
                kind='details'
            )

            # prepare serializer with customized properties
            response = render_to_json(
                serializer_vips,
                main_property='vips',
                obj_model=obj_model,
                request=request,
                only_main_property=only_main_property
            )

            return CustomResponse(response, status=status.HTTP_200_OK, request=request)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)


class VipRequestPoolView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vip request by pool id
        """
        try:

            pool_id = int(kwargs['pool_id'])

            extends_search = {
                'viprequestport__viprequestportpool__server_pool': pool_id
            }
            self.search['extends_search'] = \
                [ex.append(extends_search) for ex in self.search['extends_search']] \
                if self.search['extends_search'] else [extends_search]

            vips_requests = facade.get_vip_request_by_search(self.search)

            only_main_property = False

            # serializer vips
            serializer_vips = VipRequestV3Serializer(
                vips_requests['query_set'],
                many=True,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude,
                kind=self.kind
            )

            # prepare serializer with customized properties
            response = render_to_json(
                serializer_vips,
                main_property='vips',
                obj_model=vips_requests,
                request=request,
                only_main_property=only_main_property
            )

            return CustomResponse(response, status=status.HTTP_200_OK, request=request)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
