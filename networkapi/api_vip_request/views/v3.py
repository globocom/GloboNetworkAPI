# -*- coding: utf-8 -*-
import logging

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_vip_request import permissions
from networkapi.api_vip_request import tasks
from networkapi.api_vip_request.facade import v3 as facade
from networkapi.api_vip_request.serializers.v3 import VipRequestV3Serializer
from networkapi.distributedlock import LOCK_VIP
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import permission_obj_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import create_lock
from networkapi.util.geral import destroy_lock
from networkapi.util.geral import render_to_json
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate
from networkapi.util.json_validate import verify_ports_vip
# from networkapi.api_vip_request.serializers.v3 import VipRequestV3Serializer


log = logging.getLogger(__name__)


class VipRequestDeployView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.DeployCreate))
    @permission_obj_apiview([permissions.deploy_obj_permission])
    def post(self, request, *args, **kwargs):
        """
        Creates list of vip request in equipments
        :url /api/v3/vip-request/deploy/<vip_request_ids>/
        :param vip_request_ids=<vip_request_ids>
        """

        vip_request_ids = kwargs['obj_ids'].split(';')
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

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.DeployDelete))
    @permission_obj_apiview([permissions.deploy_obj_permission])
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of vip request in equipments
        :url /api/v3/vip-request/deploy/<vip_request_ids>/
        :param vip_request_ids=<vip_request_ids>
        """

        vip_request_ids = kwargs['obj_ids'].split(';')
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

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('vip_request_put')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.DeployUpdate))
    @permission_obj_apiview([permissions.deploy_obj_permission])
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

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('vip_request_patch')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.DeployUpdate))
    @permission_obj_apiview([permissions.deploy_obj_permission])
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

        return Response(response, status=status.HTTP_200_OK)


class VipRequestAsyncDeployView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.DeployCreate))
    @permission_obj_apiview([permissions.deploy_obj_permission])
    def post(self, request, *args, **kwargs):

        response = list()
        vip_ids = kwargs.get('obj_ids').split(',')
        user = request.user

        for vip_id in vip_ids:
            task_obj = tasks.vip_deploy.apply_async(args=[vip_id, user.id],
                                                    queue='napi.vip')

            task = {
                'id': vip_id,
                'task_id': task_obj.id
            }

        response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.DeployDelete))
    @permission_obj_apiview([permissions.deploy_obj_permission])
    def delete(self, request, *args, **kwargs):

        response = list()
        vip_ids = kwargs.get('obj_ids').split(',')
        user = request.user

        for vip_id in vip_ids:
            task_obj = tasks.vip_undeploy.apply_async(args=[vip_id, user.id],
                                                      queue='napi.vip')

            task = {
                'id': vip_id,
                'task_id': task_obj.id
            }

        response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)

    @logs_method_apiview
    @raise_json_validate('vip_request_put')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.DeployUpdate))
    @permission_obj_apiview([permissions.deploy_obj_permission])
    def put(self, request, *args, **kwargs):

        response = list()
        vips = request.DATA
        user = request.user
        json_validate(SPECS.get('vip_request_put')).validate(vips)
        verify_ports_vip(vips)

        for vip in vips.get('vips'):
            task_obj = tasks.vip_redeploy.apply_async(args=[vip, user.id],
                                                      queue='napi.vip')

            task = {
                'id': vip.get('id'),
                'task_id': task_obj.id
            }

        response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)


class VipRequestDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vip request by ids ou dict
        """

        if not kwargs.get('obj_ids'):

            obj_model = facade.get_vip_request_by_search(self.search)
            vips_requests = obj_model['query_set']
            only_main_property = False

        else:

            vip_request_ids = kwargs['obj_ids'].split(';')
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

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('vip_request_post')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
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

            vp = facade.create_vip_request(vip, request.user)
            response.append({'id': vp.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('vip_request_put')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.write_obj_permission])
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
                facade.update_vip_request(vip, request.user)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return Response({}, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.delete_obj_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of vip request
        """

        vip_request_ids = kwargs['obj_ids'].split(';')
        locks_list = create_lock(vip_request_ids, LOCK_VIP)
        keepip = request.GET.get('keepip', '0')
        try:
            facade.delete_vip_request(
                vip_request_ids, keepip)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return Response({}, status=status.HTTP_200_OK)


class VipRequestDBDetailsView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vip request with details by ids ou dict

        """
        if not kwargs.get('obj_ids'):
            obj_model = facade.get_vip_request_by_search(self.search)
            vips_requests = obj_model['query_set']
            only_main_property = False
        else:
            vip_request_ids = kwargs['obj_ids'].split(';')
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

        return Response(response, status=status.HTTP_200_OK)


class VipRequestPoolView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vip request by pool id
        """

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

        return Response(response, status=status.HTTP_200_OK)
