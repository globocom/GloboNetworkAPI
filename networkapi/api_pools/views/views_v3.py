# -*- coding:utf-8 -*-
from datetime import datetime
import logging

from django.db.transaction import commit_on_success

from networkapi.api_pools import exceptions, facade, serializers
from networkapi.api_pools.permissions import Read, Write
from networkapi.api_rest import exceptions as rest_exceptions
# from networkapi.api_task import facade as task_facade
from networkapi.requisicaovips import models as models_vips
from networkapi.util import logs_method_apiview, permission_classes_apiview
from networkapi.util.json_validate import json_validate, raise_json_validate, verify_ports

from rest_framework import status
# from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


log = logging.getLogger(__name__)


class PoolMemberStateView(APIView):

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Enable/Disable pool member by list"""

        try:
            pools = request.DATA
            json_validate('networkapi/api_pools/specs/pool_member_status.json').validate(pools)
            response = facade.set_poolmember_state(pools)

            return Response(response)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)

    @commit_on_success
    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Return pool member list by POST request method
        """

        try:
            pool_ids = kwargs.get("pool_ids").split(';')
            checkstatus = request.GET.get('checkstatus') or '0'

            data = dict()

            server_pools = models_vips.ServerPool.objects.filter(
                id__in=pool_ids)

            serializer_server_pool = serializers.PoolV3SimpleSerializer(
                server_pools,
                many=True
            )

            if checkstatus == '1':

                status = facade.get_poolmember_state(
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

            data["server_pools"] = serializer_server_pool.data

            return Response(data)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)


class PoolDeployView(APIView):

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate
    def post(self, request, *args, **kwargs):
        """Create real pool by list"""

        pool_ids = kwargs['pool_ids'].split(';')
        pools = facade.get_pool_by_ids(pool_ids)
        pool_serializer = serializers.PoolV3Serializer(pools, many=True)
        locks_list = facade.create_lock(pool_serializer.data)
        try:
            response = facade.create_real_pool(pool_serializer.data)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)

        return Response(response)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate
    def put(self, request, *args, **kwargs):
        """Update real pool by list """

        server_pools = request.DATA
        json_validate('networkapi/api_pools/specs/pool_put.json').validate(server_pools)
        verify_ports(server_pools)
        locks_list = facade.create_lock(server_pools.get('server_pools'))
        try:
            response = facade.update_real_pool(server_pools)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)
        return Response(response)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate
    def delete(self, request, *args, **kwargs):
        """Delete real pool by list"""

        pool_ids = kwargs['pool_ids'].split(';')
        pools = facade.get_pool_by_ids(pool_ids)
        pool_serializer = serializers.PoolV3Serializer(pools, many=True)
        locks_list = facade.create_lock(pool_serializer.data)
        try:
            response = facade.delete_real_pool(pool_serializer.data)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)
        return Response(response)


# @permission_classes((IsAuthenticated, Write))
# class PoolDeployTaskView(APIView):

#     @logs_method_apiview
#     def post(self, request, *args, **kwargs):
#         try:
#             pools = request.DATA.get("pools", [])
#             task = tasks.create_real_pool.apply_async([pools])
#             key = '%s:%s' % ('tasks', request.user.id)
#             value = task_facade.set_task_cache(task, key)

#             return Response(value, status.HTTP_200_OK)

#         except Exception, exception:
#             log.error(exception)
#             raise rest_exceptions.NetworkAPIException(exception)

#     @logs_method_apiview
#     def put(self, request, *args, **kwargs):

#         try:
#             pools = request.DATA.get("pools", [])
#             task = tasks.update_real_pool.apply_async([pools])
#             key = '%s:%s' % ('tasks', request.user.id)
#             value = task_facade.set_task_cache(task, key)

#             return Response(value, status.HTTP_200_OK)

#         except Exception, exception:
#             log.error(exception)
#             raise rest_exceptions.NetworkAPIException(exception)

#     @logs_method_apiview
#     def delete(self, request, *args, **kwargs):

#         try:
#             pools = request.DATA.get("pools", [])
#             task = tasks.delete_real_pool.apply_async([pools])
#             key = '%s:%s' % ('tasks', request.user.id)
#             value = task_facade.set_task_cache(task, key)

#             return Response(value, status.HTTP_200_OK)

#         except Exception, exception:
#             log.error(exception)
#             raise rest_exceptions.NetworkAPIException(exception)


class PoolDBView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Method to return pool by id
        Param pool_id: pool id
        Return pool object
        """

        try:
            if not kwargs.get('pool_ids'):
                search = request.GET or {}
                pools = facade.get_pool_by_search(search)
                pool_serializer = serializers.PoolV3Serializer(
                    pools['pools'],
                    many=True
                )
                log.info(pool_serializer.data)
                data = {
                    'server_pools': pool_serializer.data,
                    'total': pools['total'],
                }
            else:
                pool_ids = kwargs['pool_ids'].split(';')

                pools = facade.get_pool_by_ids(pool_ids)

                if pools:
                    pool_serializer = serializers.PoolV3Serializer(
                        pools,
                        many=True
                    )
                    data = {
                        'server_pools': pool_serializer.data
                    }
                else:
                    raise exceptions.PoolDoesNotExistException()

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.exception(exception)
            raise rest_exceptions.NetworkAPIException(exception)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Method to save
        """
        pools = request.DATA
        json_validate('networkapi/api_pools/specs/pool_post.json').validate(pools)
        verify_ports(pools)
        response = {}
        for pool in pools['server_pools']:
            facade.validate_save(pool)
            facade.create_pool(pool)

        return Response(response)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Method to save
        """

        pools = dict()

        pools = request.DATA
        json_validate('networkapi/api_pools/specs/pool_put.json').validate(pools)
        verify_ports(pools)
        response = {}
        for pool in pools['server_pools']:
            facade.validate_save(pool)
            facade.update_pool(pool)

        return Response(response)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Method to delete
        """
        pool_ids = kwargs['pool_ids'].split(';')
        response = {}
        facade.delete_pool(pool_ids)

        return Response(response)
