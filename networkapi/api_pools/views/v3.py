# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from networkapi.api_pools import permissions
from networkapi.api_pools import tasks
from networkapi.api_pools.facade.v3 import base as facade
from networkapi.api_pools.facade.v3 import deploy as facade_pool_deploy
from networkapi.api_pools.serializers import v3 as serializers
from networkapi.api_rest import exceptions as rest_exceptions
from networkapi.distributedlock import LOCK_POOL
from networkapi.requisicaovips import models as models_vips
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
from networkapi.util.json_validate import verify_ports

log = logging.getLogger(__name__)


class PoolMemberStateView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('pool_member_status')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.ScriptAlterPermission))
    @permission_obj_apiview([permissions.deploy_obj_permission])
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Enable/Disable pool member by list of server pool."""

        pools = request.DATA
        json_validate(SPECS.get('pool_member_status')).validate(pools)
        response = facade_pool_deploy.set_poolmember_state(
            pools, request.user)

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @commit_on_success
    def get(self, request, *args, **kwargs):
        """
        Returns a list of pools with updated states of members
        """

        pool_ids = kwargs.get('obj_ids').split(';')
        checkstatus = request.GET.get('checkstatus') or '0'

        response = dict()

        server_pools = models_vips.ServerPool.objects.filter(
            id__in=pool_ids)

        if checkstatus == '1':

            serializer_server_pool = serializers.PoolV3Serializer(
                server_pools,
                many=True
            )

            mbr_state = facade_pool_deploy.get_poolmember_state(
                serializer_server_pool.data)

            for server_pool in server_pools:

                if mbr_state.get(server_pool.id):
                    query_pools = models_vips.ServerPoolMember.objects.filter(
                        server_pool=server_pool)

                    for pm in query_pools:

                        member_checked_status = mbr_state[
                            server_pool.id][pm.id]
                        pm.member_status = member_checked_status
                        pm.last_status_update = datetime.now()
                        pm.save(request.user)

            # get pools updated
            server_pools = models_vips.ServerPool.objects.filter(
                id__in=pool_ids)

        serializer_server_pool = serializers.PoolV3Serializer(
            server_pools,
            many=True
        )

        response['server_pools'] = serializer_server_pool.data
        return Response(response, status=status.HTTP_200_OK)


class PoolDeployView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.ScriptCreatePermission))
    @permission_obj_apiview([permissions.deploy_obj_permission])
    def post(self, request, *args, **kwargs):
        """
        Creates pools by list in equipments
        """

        pool_ids = kwargs['obj_ids'].split(';')
        pools = facade.get_pool_by_ids(pool_ids)
        pool_serializer = serializers.PoolV3Serializer(pools, many=True)
        locks_list = create_lock(pool_serializer.data, LOCK_POOL)
        try:
            response = facade_pool_deploy.create_real_pool(
                pool_serializer.data, request.user)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('pool_put')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.ScriptAlterPermission))
    @permission_obj_apiview([permissions.deploy_obj_permission])
    def put(self, request, *args, **kwargs):
        """
        Updates pools by list in equipments
        """

        server_pools = request.DATA
        json_validate(SPECS.get('pool_put')).validate(server_pools)
        verify_ports(server_pools)
        locks_list = create_lock(server_pools.get('server_pools'), LOCK_POOL)
        try:
            response = facade_pool_deploy.update_real_pool(
                server_pools.get('server_pools'), request.user)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.ScriptRemovePermission))
    @permission_obj_apiview([permissions.deploy_obj_permission])
    def delete(self, request, *args, **kwargs):
        """
        Deletes pools by list in equipments
        :url /api/v3/pool/deploy/<pool_ids>/
        :param pool_ids=<pool_ids>
        """

        pool_ids = kwargs['obj_ids'].split(';')
        pools = facade.get_pool_by_ids(pool_ids)
        pool_serializer = serializers.PoolV3Serializer(pools, many=True)
        locks_list = create_lock(pool_serializer.data, LOCK_POOL)
        try:
            response = facade_pool_deploy.delete_real_pool(
                pool_serializer.data, request.user)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)
        return Response(response, status=status.HTTP_200_OK)


class PoolAsyncDeployView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.ScriptCreatePermission))
    @permission_obj_apiview([permissions.deploy_obj_permission])
    def post(self, request, *args, **kwargs):

        response = list()
        pool_ids = kwargs['obj_ids'].split(';')
        user = request.user

        for pool_id in pool_ids:
            task_obj = tasks.pool_deploy.apply_async(args=[pool_id, user.id],
                                                     queue='napi.vip')

            task = {
                'id': pool_id,
                'task_id': task_obj.id
            }

            response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.ScriptRemovePermission))
    @permission_obj_apiview([permissions.deploy_obj_permission])
    def delete(self, request, *args, **kwargs):

        response = list()
        pool_ids = kwargs.get('obj_ids').split(';')
        user = request.user

        for pool_id in pool_ids:
            task_obj = tasks.pool_undeploy.apply_async(args=[pool_id, user.id],
                                                       queue='napi.vip')

            task = {
                'id': pool_id,
                'task_id': task_obj.id
            }

            response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)

    @logs_method_apiview
    @raise_json_validate('pool_put')
    @permission_classes_apiview((IsAuthenticated, permissions.Write,
                                 permissions.ScriptAlterPermission))
    @permission_obj_apiview([permissions.deploy_obj_permission])
    def put(self, request, *args, **kwargs):

        response = list()

        pools = request.DATA
        user = request.user
        json_validate(SPECS.get('pool_put')).validate(pools)
        verify_ports(pools)

        for pool in pools.get('server_pools'):
            task_obj = tasks.pool_redeploy.apply_async(args=[pool, user.id],
                                                       queue='napi.vip')

            task = {
                'id': pool.get('id'),
                'task_id': task_obj.id
            }

            response.append(task)

        return Response(response, status=status.HTTP_202_ACCEPTED)


class PoolDBDetailsView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Return server pools by ids or dict."""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_pool_by_search(self.search)
            pools = obj_model['query_set']
            only_main_property = False
        else:
            pool_ids = kwargs['obj_ids'].split(';')
            pools = facade.get_pool_by_ids(pool_ids)
            only_main_property = True
            obj_model = None

        # serializer pools
        pool_serializer = serializers.PoolV3Serializer(
            pools,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind='details'
        )

        # prepare serializer with customized properties
        response = render_to_json(
            pool_serializer,
            main_property='server_pools',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(response, status=status.HTTP_200_OK)


class PoolDBView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """Return server pools by ids or dict"""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_pool_by_search(self.search)
            pools = obj_model['query_set']
            only_main_property = False
        else:
            pool_ids = kwargs['obj_ids'].split(';')
            pools = facade.get_pool_by_ids(pool_ids)
            only_main_property = True
            obj_model = None

        # serializer pools
        pool_serializer = serializers.PoolV3Serializer(
            pools,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        response = render_to_json(
            pool_serializer,
            main_property='server_pools',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('pool_post')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Save server pool
        """

        pools = request.DATA
        json_validate(SPECS.get('pool_post')).validate(pools)
        verify_ports(pools)
        response = list()
        for pool in pools['server_pools']:
            pl = facade.create_pool(pool, request.user)
            response.append({'id': pl.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @raise_json_validate('pool_put')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.write_obj_permission])
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Updates server pool
        """

        pools = request.DATA
        json_validate(SPECS.get('pool_put')).validate(pools)
        verify_ports(pools)
        response = dict()
        # response = list()
        for pool in pools['server_pools']:
            facade.update_pool(pool, request.user)
            # pl = facade.update_pool(pool)
            # response.append({'id': pl.id})

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Write))
    @permission_obj_apiview([permissions.delete_obj_permission])
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Delete server pool
        """

        pool_ids = kwargs['obj_ids'].split(';')
        response = {}
        facade.delete_pool(pool_ids)

        return Response(response, status=status.HTTP_200_OK)


class PoolEnvironmentVip(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns list of pool by environment vip
        """

        environment_vip_id = kwargs['environment_vip_id']
        pools = facade.get_pool_list_by_environmentvip(environment_vip_id)
        only_main_property = True

        # serializer pools
        pool_serializer = serializers.PoolV3Serializer(
            pools,
            many=True,
            fields=('id', 'identifier', ) + self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        response = render_to_json(
            pool_serializer,
            main_property='server_pools',
            obj_model=pools,
            request=request,
            only_main_property=only_main_property
        )

        return Response(response, status=status.HTTP_200_OK)


class OptionPoolEnvironmentView(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, permissions.Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Method to return option pool list by environment id
        Param environment_id: environment id
        Return list of option pool
        """

        environment_id = kwargs['environment_id']

        options_pool = facade.get_options_pool_list_by_environment(
            environment_id)

        only_main_property = True

        self.include += ('type',)

        # serializer pools
        options_pool_serializer = serializers.OptionPoolV3Serializer(
            options_pool,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        # prepare serializer with customized properties
        response = render_to_json(
            options_pool_serializer,
            main_property='options_pool',
            only_main_property=only_main_property
        )

        return Response(response, status=status.HTTP_200_OK)


# class OptionPoolView(CustomAPIView):

#     @logs_method_apiview
#     @raise_json_validate('')
#     @permission_classes_apiview((IsAuthenticated, Read))
#     @prepare_search
#     def get(self, request, *args, **kwargs):
#         """
#         Method to return option pool list
#         Param obj_ids: environment id
#         Return list of option pool
#         """

#         obj_ids = kwargs['obj_ids']

#         options_pool = facade.get_options_pool_list_by_environment(
#             environment_id)

#         only_main_property = True

#         self.include += ('type',)

#         # serializer pools
#         options_pool_serializer = serializers.OptionPoolV3Serializer(
#             options_pool,
#             many=True,
#             fields=self.fields,
#             include=self.include,
#             exclude=self.exclude,
#             kind=self.kind
#         )

#         # prepare serializer with customized properties
#         response = render_to_json(
#             options_pool_serializer,
#             main_property='options_pool',
#             only_main_property=only_main_property
#         )

#         return Response(response, status=status.HTTP_200_OK)
