# -*- coding:utf-8 -*-
import ast
from datetime import datetime
import logging

from django.db.transaction import commit_on_success
from networkapi.api_pools import exceptions, facade, serializers
from networkapi.api_pools.permissions import Read, ScriptAlterPermission, \
    ScriptCreatePermission, ScriptRemovePermission, Write
from networkapi.api_rest import exceptions as rest_exceptions
from networkapi.requisicaovips import models as models_vips
from networkapi.settings import SPECS
from networkapi.util import logs_method_apiview, permission_classes_apiview
from networkapi.util.json_validate import json_validate, raise_json_validate, verify_ports
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


log = logging.getLogger(__name__)


class PoolMemberStateView(APIView):

    @permission_classes_apiview((IsAuthenticated, Write, ScriptAlterPermission))
    @logs_method_apiview
    @raise_json_validate('pool_member_status')
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Enable/Disable pool member by list of server pool
        :url /api/v3/pool/deploy/<pool_ids>/member/status/
        :param
        {
            "server_pools": [{
                "id": <server_pool_id>,
                "identifier": <string>,
                "default_port": <interger>,
                environmentvip": <environment_id>,
                "servicedownaction": {
                    "id": <optionvip_id>,
                    "name": <string>
                },
                "lb_method": <string>,
                "healthcheck": {
                    "identifier": <string>,
                    "healthcheck_type": <string>,
                    "healthcheck_request": <string>,
                    "healthcheck_expect": <string>,
                    "destination": <string>
                },
                "default_limit": <interger>,
                "server_pool_members": [{
                    "id": <server_pool_member_id>,
                    "identifier": <string>,
                    "ipv6": {
                        "ip_formated": <ipv6_formated>,
                        "id": <ipv6_id>
                    },
                    "ip": {
                        "ip_formated": <ipv4_formated>,
                        "id": <ipv4_id>
                    },
                    "priority": <interger>,
                    "equipment": {
                        "id": <interger>,
                        "name": <string>
                    },
                    "weight": <interger>,
                    "limit": <interger>,
                    "port_real": <interger>,
                    "last_status_update_formated": <string>,
                    "member_status": <interger>
                }],
                "pool_created": <boolean>
            },..]
        }
        """
        try:
            pools = request.DATA
            json_validate(SPECS.get('pool_member_status')).validate(pools)
            response = facade.set_poolmember_state(pools, request.user)

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
        :url /api/v3/pool/deploy/<pool_ids>/member/status/
        :param pool_ids=<pool_ids>
        :return list of server pool
        {
            "server_pools": [{
                "id": <server_pool_id>,
                "identifier": <string>,
                "default_port": <interger>,
                environmentvip": <environment_id>,
                "servicedownaction": {
                    "id": <optionvip_id>,
                    "name": <string>
                },
                "lb_method": <string>,
                "healthcheck": {
                    "identifier": <string>,
                    "healthcheck_type": <string>,
                    "healthcheck_request": <string>,
                    "healthcheck_expect": <string>,
                    "destination": <string>
                },
                "default_limit": <interger>,
                "server_pool_members": [{
                    "id": <server_pool_member_id>,
                    "identifier": <string>,
                    "ipv6": {
                        "ip_formated": <ipv6_formated>,
                        "id": <ipv6_id>
                    },
                    "ip": {
                        "ip_formated": <ipv4_formated>,
                        "id": <ipv4_id>
                    },
                    "priority": <interger>,
                    "equipment": {
                        "id": <interger>,
                        "name": <string>
                    },
                    "weight": <interger>,
                    "limit": <interger>,
                    "port_real": <interger>,
                    "last_status_update_formated": <string>,
                    "member_status": <interger>
                }],
                "pool_created": <boolean>
            },..]
        }
        """

        try:
            pool_ids = kwargs.get("pool_ids").split(';')
            checkstatus = request.GET.get('checkstatus') or '0'

            data = dict()

            server_pools = models_vips.ServerPool.objects.filter(
                id__in=pool_ids)

            serializer_server_pool = serializers.PoolV3Serializer(
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
    @logs_method_apiview
    def post(self, request, *args, **kwargs):
        """
        Creates pools by list in equipments
        :url /api/v3/pool/deploy/<pool_ids>/
        :param pool_ids=<pool_ids>
        """

        pool_ids = kwargs['pool_ids'].split(';')
        pools = facade.get_pool_by_ids(pool_ids)
        pool_serializer = serializers.PoolV3Serializer(pools, many=True)
        locks_list = facade.create_lock(pool_serializer.data)
        try:
            response = facade.create_real_pool(pool_serializer.data, request.user)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)

        return Response(response)

    @permission_classes_apiview((IsAuthenticated, Write, ScriptAlterPermission))
    @logs_method_apiview
    @raise_json_validate('pool_put')
    def put(self, request, *args, **kwargs):
        """
        Updates pools by list in equipments
        :url /api/v3/pool/deploy/<pool_ids>/
        :param
        {
            "server_pools": [{
                "id": <server_pool_id>,
                "identifier": <string>,
                "default_port": <interger>,
                environmentvip": <environment_id>,
                "servicedownaction": {
                    "id": <optionvip_id>,
                    "name": <string>
                },
                "lb_method": <string>,
                "healthcheck": {
                    "identifier": <string>,
                    "healthcheck_type": <string>,
                    "healthcheck_request": <string>,
                    "healthcheck_expect": <string>,
                    "destination": <string>
                },
                "default_limit": <interger>,
                "server_pool_members": [{
                    "id": <server_pool_member_id>,
                    "identifier": <string>,
                    "ipv6": {
                        "ip_formated": <ipv6_formated>,
                        "id": <ipv6_id>
                    },
                    "ip": {
                        "ip_formated": <ipv4_formated>,
                        "id": <ipv4_id>
                    },
                    "priority": <interger>,
                    "equipment": {
                        "id": <interger>,
                        "name": <string>
                    },
                    "weight": <interger>,
                    "limit": <interger>,
                    "port_real": <interger>,
                    "last_status_update_formated": <string>,
                    "member_status": <interger>
                }],
                "pool_created": <boolean>
            },..]
        }
        """

        server_pools = request.DATA
        json_validate(SPECS.get('pool_put')).validate(server_pools)
        verify_ports(server_pools)
        locks_list = facade.create_lock(server_pools.get('server_pools'))
        try:
            response = facade.update_real_pool(server_pools, request.user)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)
        return Response(response)

    @permission_classes_apiview((IsAuthenticated, Write, ScriptRemovePermission))
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
            response = facade.delete_real_pool(pool_serializer.data, request.user)
        except Exception, exception:
            log.error(exception)
            raise rest_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)
        return Response(response)


class PoolDBDetailsView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        ##############
        ## With ids ##
        ##############
        Return server pools by ids or dict
        :url /api/v3/pool/details/<pool_ids>/
        :param pool_ids=<pool_ids>
        :return list of server pool
        {
            "server_pools": [{
                "id": <server_pool_id>,
                "identifier": <string>,
                "default_port": <interger>,
                environmentvip": {
                    "id": <environment_id>,
                    "finalidade_txt": <string>,
                    "cliente_txt": <string>,
                    "ambiente_p44_txt": <string>,
                    "description": <string>
                }
                "servicedownaction": {
                    "id": <optionvip_id>,
                    "name": <string>
                },
                "lb_method": <string>,
                "healthcheck": {
                    "identifier": <string>,
                    "healthcheck_type": <string>,
                    "healthcheck_request": <string>,
                    "healthcheck_expect": <string>,
                    "destination": <string>
                },
                "default_limit": <interger>,
                "server_pool_members": [{
                    "id": <server_pool_member_id>,
                    "identifier": <string>,
                    "ipv6": {
                        "ip_formated": <ipv6_formated>,
                        "id": <ipv6_id>
                    },
                    "ip": {
                        "ip_formated": <ipv4_formated>,
                        "id": <ipv4_id>
                    },
                    "priority": <interger>,
                    "equipment": {
                        "id": <interger>,
                        "name": <string>
                    },
                    "weight": <interger>,
                    "limit": <interger>,
                    "port_real": <interger>,
                    "last_status_update_formated": <string>,
                    "member_status": <interger>
                }],
                "pool_created": <boolean>
            },..]
        }
        :example
        Return pool with id 1 or 2
        /api/v3/pool/details/1;2/

        ###############
        ## With dict ##
        ###############
        Return list of server pool by dict
        :url /api/v3/pool/details/
        :param GET['search']
        {
            'extends_search': [{
                'environment': <environment_id>
            }],
            'start_record': <interger>,
            'custom_search': '<string>',
            'end_record': <interger>,
            'asorting_cols': [<string>,..],
            'searchable_columns': [<string>,..]
        }
        :return list of server pool with property "total"
        {
            "total": <interger>,
            "server_pools": [..]
        }
        :example
        {
            'extends_search': [{
                'environment': 1
            }],
            'start_record': 0,
            'custom_search': 'pool_123',
            'end_record': 25,
            'asorting_cols': ['identifier'],
            'searchable_columns': [
                'identifier',
                'default_port',
                'pool_created',
                'healthcheck__healthcheck_type'
            ]
        }
        """
        try:
            if not kwargs.get('pool_ids'):
                try:
                    search = ast.literal_eval(request.GET.get('search'))
                except:
                    search = {}

                pools = facade.get_pool_by_search(search)
                pool_serializer = serializers.PoolV3DetailsSerializer(
                    pools['pools'],
                    many=True
                )
                data = {
                    'server_pools': pool_serializer.data,
                    'total': pools['total'],
                }
            else:
                pool_ids = kwargs['pool_ids'].split(';')

                pools = facade.get_pool_by_ids(pool_ids)

                if pools:
                    pool_serializer = serializers.PoolV3DetailsSerializer(
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


class PoolDBView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Return server pools by ids or dict
        ##############
        ## With ids ##
        ##############
        Return server pools by ids
        :url /api/v3/pool/<pool_ids>/
        :param pool_ids=<pool_ids>
        :return list of server pool
        {
            "server_pools": [{
                "id": <server_pool_id>,
                "identifier": <string>,
                "default_port": <interger>,
                environmentvip": <environment_id>,
                "servicedownaction": {
                    "id": <optionvip_id>,
                    "name": <string>
                },
                "lb_method": <string>,
                "healthcheck": {
                    "identifier": <string>,
                    "healthcheck_type": <string>,
                    "healthcheck_request": <string>,
                    "healthcheck_expect": <string>,
                    "destination": <string>
                },
                "default_limit": <interger>,
                "server_pool_members": [{
                    "id": <server_pool_member_id>,
                    "identifier": <string>,
                    "ipv6": {
                        "ip_formated": <ipv6_formated>,
                        "id": <ipv6_id>
                    },
                    "ip": {
                        "ip_formated": <ipv4_formated>,
                        "id": <ipv4_id>
                    },
                    "priority": <interger>,
                    "equipment": {
                        "id": <interger>,
                        "name": <string>
                    },
                    "weight": <interger>,
                    "limit": <interger>,
                    "port_real": <interger>,
                    "last_status_update_formated": <string>,
                    "member_status": <interger>
                }],
                "pool_created": <boolean>
            },..]
        }
        :example
        /api/v3/pool/1;5/
        Return pools with id 1 and 5:
        {
            "server_pools": [
                {
                    "id":1,
                    ...
                    },
                    {
                    "id":5,
                    ...
                }
            ]
        }

        ###############
        ## With dict ##
        ###############
        Return list of server pool by dict
        :url /api/v3/pool/
        :param GET['search']
        {
            'extends_search': [{
                'environment': <environment_id>
            }],
            'start_record': <interger>,
            'custom_search': '<string>',
            'end_record': <interger>,
            'asorting_cols': [<string>,..],
            'searchable_columns': [<string>,..]
        }
        :return list of server pool with property "total"
        {
            "total": <interger>,
            "server_pools": [..]
        }
        :example
        {
            'extends_search': [{
                'environment': 1
            }],
            'start_record': 0,
            'custom_search': 'pool_123',
            'end_record': 25,
            'asorting_cols': ['identifier'],
            'searchable_columns': [
                'identifier',
                'default_port',
                'pool_created',
                'healthcheck__healthcheck_type'
            ]
        }
        """
        try:
            if not kwargs.get('pool_ids'):
                try:
                    search = ast.literal_eval(request.GET.get('search'))
                except:
                    search = {}

                pools = facade.get_pool_by_search(search)
                pool_serializer = serializers.PoolV3DatatableSerializer(
                    pools['pools'],
                    many=True
                )
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
    @raise_json_validate('pool_post')
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Save server pool
        :url /api/v3/pool/
        :param
        {
            "server_pools": [{
                "id": <null>,
                "identifier": <string>,
                "default_port": <interger>,
                environmentvip": <environment_id>,
                "servicedownaction": {
                    "id": <optionvip_id>,
                    "name": <string>
                },
                "lb_method": <string>,
                "healthcheck": {
                    "identifier": <string>,
                    "healthcheck_type": <string>,
                    "healthcheck_request": <string>,
                    "healthcheck_expect": <string>,
                    "destination": <string>
                },
                "default_limit": <interger>,
                "server_pool_members": [{
                    "id": <server_pool_member_id>,
                    "identifier": <string>,
                    "ipv6": {
                        "ip_formated": <ipv6_formated>,
                        "id": <ipv6_id>
                    },
                    "ip": {
                        "ip_formated": <ipv4_formated>,
                        "id": <ipv4_id>
                    },
                    "priority": <interger>,
                    "equipment": {
                        "id": <interger>,
                        "name": <string>
                    },
                    "weight": <interger>,
                    "limit": <interger>,
                    "port_real": <interger>,
                    "last_status_update_formated": <string>,
                    "member_status": <interger>
                }],
                "pool_created": <boolean>
            },..]
        }
        :return [<server_pool_id>,..]
        """
        pools = request.DATA
        json_validate(SPECS.get('pool_post')).validate(pools)
        verify_ports(pools)
        response = list()
        for pool in pools['server_pools']:
            facade.validate_save(pool)

            pl = facade.create_pool(pool)
            response.append({'id': pl.id})

        return Response(response, status=status.HTTP_201_CREATED)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('pool_put')
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Updates server pool
        :url /api/v3/pool/<pool_ids>/
        :param
        {
            "server_pools": [{
                "id": <server_pool_id>,
                "identifier": <string>,
                "default_port": <interger>,
                environmentvip": <environment_id>,
                "servicedownaction": {
                    "id": <optionvip_id>,
                    "name": <string>
                },
                "lb_method": <string>,
                "healthcheck": {
                    "identifier": <string>,
                    "healthcheck_type": <string>,
                    "healthcheck_request": <string>,
                    "healthcheck_expect": <string>,
                    "destination": <string>
                },
                "default_limit": <interger>,
                "server_pool_members": [{
                    "id": <server_pool_member_id>,
                    "identifier": <string>,
                    "ipv6": {
                        "ip_formated": <ipv6_formated>,
                        "id": <ipv6_id>
                    },
                    "ip": {
                        "ip_formated": <ipv4_formated>,
                        "id": <ipv4_id>
                    },
                    "priority": <interger>,
                    "equipment": {
                        "id": <interger>,
                        "name": <string>
                    },
                    "weight": <interger>,
                    "limit": <interger>,
                    "port_real": <interger>,
                    "last_status_update_formated": <string>,
                    "member_status": <interger>
                }],
                "pool_created": <boolean>
            },..]
        }
        :return [<server_pool_id>,..]
        """
        pools = request.DATA
        json_validate(SPECS.get('pool_put')).validate(pools)
        verify_ports(pools)
        response = list()
        for pool in pools['server_pools']:
            facade.validate_save(pool)
            pl = facade.update_pool(pool)
            response.append({'id': pl.id})

        return Response(response, status.HTTP_200_OK)

    @permission_classes_apiview((IsAuthenticated, Write))
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

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Returns list of pool by environment vip
        :url /api/v3/pool/environment-vip/<environment_vip_id>/
        :param environment_vip_id:<environment_vip_id>
        :return
        {
            "server_pools": [{
                "id": <server_pool_id>,
                "identifier": <string>,
                "default_port": <interger>,
                environmentvip": <environment_id>,
                "servicedownaction": {
                    "id": <optionvip_id>,
                    "name": <string>
                },
                "lb_method": <string>,
                "healthcheck": {
                    "identifier": <string>,
                    "healthcheck_type": <string>,
                    "healthcheck_request": <string>,
                    "healthcheck_expect": <string>,
                    "destination": <string>
                },
                "default_limit": <interger>,
                "server_pool_members": [{
                    "id": <server_pool_member_id>,
                    "identifier": <string>,
                    "ipv6": {
                        "ip_formated": <ipv6_formated>,
                        "id": <ipv6_id>
                    },
                    "ip": {
                        "ip_formated": <ipv4_formated>,
                        "id": <ipv4_id>
                    },
                    "priority": <interger>,
                    "equipment": {
                        "id": <interger>,
                        "name": <string>
                    },
                    "weight": <interger>,
                    "limit": <interger>,
                    "port_real": <interger>,
                    "last_status_update_formated": <string>,
                    "member_status": <interger>
                }],
                "pool_created": <boolean>
            },..]
        }
        """
        try:
            environment_vip_id = kwargs['environment_vip_id']
            pools = facade.get_pool_list_by_environmentvip(environment_vip_id)
            pool_serializer = serializers.PoolV3SimpleSerializer(
                pools,
                many=True
            )
            data = {
                'server_pools': pool_serializer.data
            }
            return Response(data, status.HTTP_200_OK)
        except Exception, exception:
            log.exception(exception)
            raise rest_exceptions.NetworkAPIException(exception)


class OptionPoolEnvironmentView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Method to return option vip list by environment id
        Param environment_id: environment id
        Return list of option pool
        """
        try:
            environment_id = kwargs["environment_id"]

            options_pool = facade.get_options_pool_list_by_environment(environment_id)

            options_pool_serializer = serializers.OptionPoolV3DetailsSerializer(
                options_pool,
                many=True
            )
            data = {
                'options_pool': options_pool_serializer.data
            }
            return Response(data, status.HTTP_200_OK)
        except Exception, exception:
            log.exception(exception)
            raise rest_exceptions.NetworkAPIException(exception)
