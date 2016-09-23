# -*- coding:utf-8 -*-
import ast
import json
import logging
from datetime import datetime

from django.db.transaction import commit_on_success
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_pools import exceptions
from networkapi.api_pools import serializers
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
from networkapi.api_rest import exceptions as rest_exceptions
from networkapi.requisicaovips import models as models_vips
from networkapi.settings import SPECS
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import permission_obj_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.geral import generate_return_json
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
            response = facade_pool_deploy.set_poolmember_state(pools, request.user)

            return Response(response)
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
            pool_ids = kwargs.get("pool_ids").split(';')
            checkstatus = request.GET.get('checkstatus') or '0'

            data = dict()

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

            data["server_pools"] = serializer_server_pool.data
            return Response(data)

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
        locks_list = facade.create_lock(pool_serializer.data)
        try:
            response = facade_pool_deploy.create_real_pool(pool_serializer.data, request.user)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)

        return Response(response)

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
        locks_list = facade.create_lock(server_pools.get('server_pools'))
        try:
            response = facade_pool_deploy.update_real_pool(server_pools, request.user)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)
        return Response(response)

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
        locks_list = facade.create_lock(pool_serializer.data)
        try:
            response = facade_pool_deploy.delete_real_pool(pool_serializer.data, request.user)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)
        return Response(response)


class PoolDBDetailsView(APIView):

    def render(self, obj, **kwargs):

        obj_model = None
        if isinstance(obj, dict):
            obj_model = obj
            obj = obj['pools']

        pool_serializer = serializers.PoolV3DetailsSerializer(
            obj,
            many=True,
            fields=kwargs.get('fields'),
            include=kwargs.get('include'),
            exclude=kwargs.get('exclude')
        )
        data = generate_return_json(
            pool_serializer,
            'server_pools',
            obj_model=obj_model,
            request=kwargs.get('request', None),
            only_main_property=kwargs.get('only_main_property', False)
        )
        return data

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    @prepare_search
    def get(self, request, *args, **kwargs):
        """
        Return server pools by ids or dict
        """
        try:
            if not kwargs.get('pool_ids'):
                pools = facade.get_pool_by_search(self.search)
                only_main_property = False
            else:
                pool_ids = kwargs['pool_ids'].split(';')
                pools = facade.get_pool_by_ids(pool_ids)
                only_main_property = True

            data = self.render(
                pools,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude,
                only_main_property=only_main_property,
                request=request
            )

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.exception(exception)
            raise rest_exceptions.NetworkAPIException(exception)


class PoolDBView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Return server pools by ids or dict
        """
        try:
            if not kwargs.get('pool_ids'):
                try:
                    search = json.loads(request.GET.get('search'))
                except:
                    try:
                        search = ast.literal_eval(request.GET.get('search'))
                    except:
                        search = {
                            'extends_search': []
                        }

                pools = facade.get_pool_by_search(search)
                pool_serializer = serializers.PoolV3DatatableSerializer(
                    pools['pools'],
                    many=True
                )
                data = generate_return_json(
                    pool_serializer,
                    'server_pools',
                    obj_model=pools,
                    request=request
                )
            else:
                pool_ids = kwargs['pool_ids'].split(';')

                pools = facade.get_pool_by_ids(pool_ids)

                if pools:
                    pool_serializer = serializers.PoolV3Serializer(
                        pools,
                        many=True
                    )
                    data = generate_return_json(
                        pool_serializer,
                        'server_pools',
                        only_main_property=True
                    )
                else:
                    raise exceptions.PoolDoesNotExistException()

            return Response(data, status.HTTP_200_OK)

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

        return Response(response, status=status.HTTP_201_CREATED)

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

        return Response(response, status.HTTP_200_OK)

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

        return Response(response, status.HTTP_200_OK)


class PoolEnvironmentVip(APIView):

    def render(self, obj, **kwargs):

        pool_serializer = serializers.PoolV3MinimumSerializer(
            obj,
            many=True,
            fields=kwargs.get('fields'),
            include=kwargs.get('include'),
            exclude=kwargs.get('exclude')
        )
        data = generate_return_json(
            pool_serializer,
            'server_pools',
            only_main_property=kwargs.get('only_main_property', False)
        )
        return data

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

            data = self.render(
                pools,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude,
                only_main_property=only_main_property,
            )

            return Response(data, status.HTTP_200_OK)
        except Exception, exception:
            log.exception(exception)
            raise rest_exceptions.NetworkAPIException(exception)


class OptionPoolEnvironmentView(APIView):

    def render(self, obj, **kwargs):

        options_pool_serializer = serializers.OptionPoolV3DetailsSerializer(
            obj,
            many=True,
            fields=kwargs.get('fields'),
            include=kwargs.get('include'),
            exclude=kwargs.get('exclude')
        )
        data = generate_return_json(
            options_pool_serializer,
            'options_pool',
            only_main_property=kwargs.get('only_main_property', False)
        )
        return data

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
            environment_id = kwargs["environment_id"]

            options_pool = facade.get_options_pool_list_by_environment(environment_id)

            data = self.render(
                options_pool,
                fields=self.fields,
                include=self.include,
                exclude=self.exclude,
                only_main_property=True,
            )

            return Response(data, status.HTTP_200_OK)
        except Exception, exception:
            log.exception(exception)
            raise rest_exceptions.NetworkAPIException(exception)
