# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from networkapi.api_pools.facade.v3 import base as facade
from networkapi.api_pools.facade.v3 import deploy as facade_pool_deploy
from networkapi.api_pools.permissions import delete_pool_permission
from networkapi.api_pools.permissions import deploy_pool_permission
from networkapi.api_pools.permissions import Read
from networkapi.api_pools.permissions import ScriptAlterPermission
from networkapi.api_pools.permissions import ScriptCreatePermission
from networkapi.api_pools.permissions import ScriptRemovePermission
from networkapi.api_pools.permissions import Write
from networkapi.api_pools.permissions import write_pool_permission
from networkapi.api_pools.serializers import v3 as serializers
from networkapi.api_rest import exceptions as rest_exceptions
from networkapi.distributedlock import LOCK_POOL
from networkapi.requisicaovips import models as models_vips
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
from networkapi.util.json_validate import verify_ports

log = logging.getLogger(__name__)


class PoolMemberStateView(APIView):

    @permission_classes_apiview((IsAuthenticated, Write, ScriptAlterPermission))
    @permission_obj_apiview([deploy_pool_permission])
    @logs_method_apiview
    @raise_json_validate('pool_member_status')
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Enable/Disable pool member by list of server pool
        """
        try:
            pools = request.DATA
            json_validate(SPECS.get('pool_member_status')).validate(pools)
            response = facade_pool_deploy.set_poolmember_state(
                pools, request.user)

            return CustomResponse(response, status=status.HTTP_200_OK, request=request)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)

    @commit_on_success
    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Returns a list of pools with updated states of members
        """

        try:
            pool_ids = kwargs.get('pool_ids').split(';')
            checkstatus = request.GET.get('checkstatus') or '0'

            response = dict()

            server_pools = models_vips.ServerPool.objects.filter(
                id__in=pool_ids)

            if checkstatus == '1':

                serializer_server_pool = serializers.PoolV3Serializer(
                    server_pools,
                    many=True
                )

                status = facade_pool_deploy.get_poolmember_state(
                    serializer_server_pool.data)

                for server_pool in server_pools:

                    if status.get(server_pool.id):
                        query_pools = models_vips.ServerPoolMember.objects.filter(
                            server_pool=server_pool)

                        for pm in query_pools:

                            member_checked_status = status[
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
            return CustomResponse(response, status=status.HTTP_200_OK, request=request)

        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)


class PoolDeployView(APIView):

    @permission_classes_apiview((IsAuthenticated, Write, ScriptCreatePermission))
    @permission_obj_apiview([deploy_pool_permission])
    @logs_method_apiview
    def post(self, request, *args, **kwargs):
        """
        Creates pools by list in equipments
        """

        pool_ids = kwargs['pool_ids'].split(';')
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

        return CustomResponse(response, status=status.HTTP_200_OK, request=request)

    @permission_classes_apiview((IsAuthenticated, Write, ScriptAlterPermission))
    @permission_obj_apiview([deploy_pool_permission])
    @logs_method_apiview
    @raise_json_validate('pool_put')
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
                server_pools, request.user)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            destroy_lock(locks_list)
            return CustomResponse(response, status=status.HTTP_200_OK, request=request)

    @permission_classes_apiview((IsAuthenticated, Write, ScriptRemovePermission))
    @permission_obj_apiview([deploy_pool_permission])
    @logs_method_apiview
    def delete(self, request, *args, **kwargs):
        """
        Deletes pools by list in equipments
        :url /api/v3/pool/deploy/<pool_ids>/
        :param pool_ids=<pool_ids>
        """

        pool_ids = kwargs['pool_ids'].split(';')
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
        return CustomResponse(response, status=status.HTTP_200_OK, request=request)


class PoolDBDetailsView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Return server pools by ids or dict
        """
        try:
            if not kwargs.get('pool_ids'):
                obj_model = facade.get_pool_by_search(self.search)
                pools = obj_model['query_set']
                only_main_property = False
            else:
                pool_ids = kwargs['pool_ids'].split(';')
                pools = facade.get_pool_by_ids(pool_ids)
                only_main_property = True
                obj_model = None

            self.include = (
                'servicedownaction__details',
                'environment__details',
                'groups_permissions__details',
            )

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

            return CustomResponse(response, status=status.HTTP_200_OK, request=request)

        except Exception, exception:
            log.exception(exception)
            raise rest_exceptions.NetworkAPIException(exception)


class PoolDBView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Return server pools by ids or dict
        """
        try:
            if not kwargs.get('pool_ids'):
                obj_model = facade.get_pool_by_search(self.search)
                pools = obj_model['query_set']
                only_main_property = False
            else:
                pool_ids = kwargs['pool_ids'].split(';')
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

            return CustomResponse(response, status=status.HTTP_200_OK, request=request)

        except Exception, exception:
            log.exception(exception)
            raise rest_exceptions.NetworkAPIException(exception)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('pool_post')
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
            facade.validate_save(pool)

            pl = facade.create_pool(pool, request.user)
            response.append({'id': pl.id})

        return CustomResponse(response, status=status.HTTP_200_OK, request=request)

    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([write_pool_permission])
    @logs_method_apiview
    @raise_json_validate('pool_put')
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
            facade.validate_save(pool)
            facade.update_pool(pool, request.user)
            # pl = facade.update_pool(pool)
            # response.append({'id': pl.id})

        return CustomResponse(response, status=status.HTTP_200_OK, request=request)

    @permission_classes_apiview((IsAuthenticated, Write))
    @permission_obj_apiview([delete_pool_permission])
    @logs_method_apiview
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Method to delete
        Delete server pool
        :url /api/v3/pool/<pool_ids>/
        :param pool_ids=<pool_ids>
        """
        pool_ids = kwargs['pool_ids'].split(';')
        response = {}
        facade.delete_pool(pool_ids)

        return CustomResponse(response, status=status.HTTP_200_OK, request=request)


class PoolEnvironmentVip(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Returns list of pool by environment vip
        """
        try:
            environment_vip_id = kwargs['environment_vip_id']
            pools = facade.get_pool_list_by_environmentvip(environment_vip_id)
            only_main_property = True

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
                obj_model=pools,
                request=request,
                only_main_property=only_main_property
            )

            return CustomResponse(response, status=status.HTTP_200_OK, request=request)
        except Exception, exception:
            log.exception(exception)
            raise rest_exceptions.NetworkAPIException(exception)


class OptionPoolEnvironmentView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Method to return option vip list by environment id
        Param environment_id: environment id
        Return list of option pool
        """
        try:
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

            return CustomResponse(response, status=status.HTTP_200_OK, request=request)
        except Exception, exception:
            log.exception(exception)
            raise rest_exceptions.NetworkAPIException(exception)
