# -*- coding:utf-8 -*-
import ast
import logging

from django.db.transaction import commit_on_success

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_vip_request import exceptions, facade
from networkapi.api_vip_request.permissions import DeployCreate, DeployDelete, DeployUpdate, Read, Write
from networkapi.api_vip_request.serializers import VipRequestDetailsSerializer, VipRequestSerializer, VipRequestTableSerializer
from networkapi.settings import SPECS
from networkapi.util import logs_method_apiview, permission_classes_apiview
from networkapi.util.json_validate import json_validate, raise_json_validate

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


log = logging.getLogger(__name__)


class VipRequestDeployView(APIView):

    @permission_classes_apiview((IsAuthenticated, Write, DeployCreate))
    @logs_method_apiview
    def post(self, request, *args, **kwargs):
        """
        Creates list of vip request in equipments
        :url /api/v3/vip-request/deploy/<vip_request_ids>/
        :param vip_request_ids=<vip_request_ids>
        """

        vip_request_ids = kwargs['vip_request_ids'].split(';')
        vips = facade.get_vip_request(vip_request_ids)

        if vips:
            vip_serializer = VipRequestSerializer(vips, many=True)
        else:
            raise exceptions.VipRequestDoesNotExistException()

        locks_list = facade.create_lock(vip_serializer.data)
        try:
            response = facade.create_real_vip_request(vip_serializer.data, request.user)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)

        return Response(response)

    @permission_classes_apiview((IsAuthenticated, Write, DeployDelete))
    @logs_method_apiview
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of vip request in equipments
        :url /api/v3/vip-request/deploy/<vip_request_ids>/
        :param vip_request_ids=<vip_request_ids>
        """

        vip_request_ids = kwargs['vip_request_ids'].split(';')
        vips = facade.get_vip_request(vip_request_ids)
        if vips:
            vip_serializer = VipRequestSerializer(vips, many=True)
        else:
            raise exceptions.VipRequestDoesNotExistException()

        locks_list = facade.create_lock(vip_serializer.data)
        try:
            response = facade.delete_real_vip_request(vip_serializer.data, request.user)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)

        return Response(response)

    @permission_classes_apiview((IsAuthenticated, Write, DeployUpdate))
    @logs_method_apiview
    def put(self, request, *args, **kwargs):
        """
        Updates list of vip request in equipments
        :url /api/v3/vip-request/deploy/<vip_request_ids>/
        :param
        {
            "vips": [{
                "business": <string>,
                "created": <boolean>,
                "environmentvip": <environmentvip_id>,
                "id": <vip_id>,
                "ipv4": <ipv4_id>,
                "ipv6": <ipv6_id>,
                "name": <string>,
                "options": {
                    "cache_group": <optionvip_id>,
                    "persistence": <optionvip_id>,
                    "timeout": <optionvip_id>,
                    "traffic_return": <optionvip_id>
                },
                "ports": [{
                    "id": <vip_port_id>,
                    "options": {
                        "l4_protocol": <optionvip_id>,
                        "l7_protocol": <optionvip_id>
                    },
                    "pools": [{
                            "l7_rule": <optionvip_id>,
                            "l7_value": <string>,
                            "server_pool": <server_pool_id>
                        },..],
                    "port": <integer>
                    },..],
                "service": <string>
            },..]
        }

        """

        vips = request.DATA
        json_validate(SPECS.get('vip_put')).validate(vips)
        locks_list = facade.create_lock(vips.get('vips'))
        try:
            response = facade.update_real_vip_request(vips['vips'], request.user)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)

        return Response(response)


class VipRequestDBView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vip request by ids ou dict
        ##############
        ## With ids ##
        ##############
        :url /api/v3/vip-request/<vip_request_ids>
        :param vip_request_ids=<vip_request_ids>
        :return
        {
            "vips": [{
                "business": <string>,
                "created": <boolean>,
                "environmentvip": <environmentvip_id>,
                "id": <vip_id>,
                "ipv4": <ipv4_id>,
                "ipv6": <ipv6_id>,
                "name": <string>,
                "options": {
                    "cache_group": <optionvip_id>,
                    "persistence": <optionvip_id>,
                    "timeout": <optionvip_id>,
                    "traffic_return": <optionvip_id>
                },
                "ports": [{
                    "id": <vip_port_id>,
                    "options": {
                        "l4_protocol": <optionvip_id>,
                        "l7_protocol": <optionvip_id>
                    },
                    "pools": [{
                            "l7_rule": <optionvip_id>,
                            "l7_value": <string>,
                            "server_pool": <server_pool_id>
                        },..],
                    "port": <integer>
                    },..],
                "service": <string>
            },..]
        }
        :example
            /api/v3/vip-request/1;5/
            Return vips request with id 1 and 5
            {"vips": [{"id":1,...},{"id":5,... }]}

        ###############
        ## With dict ##
        ###############
        Return list of vip request by dict
        :url /api/v3/vip-request/
        :param search:GET['search']
            {'extends_search': [{
                    'ipv4__oct1': <ipv4__oct1>,
                    'ipv4__oct2': <ipv4__oct2>,
                    'ipv4__oct3': <ipv4__oct3>,
                    'ipv4__oct4': <ipv4__oct4>,
                    'ipv6__block1__iexact': <ipv6_block1>,
                    'ipv6__block2__iexact': <ipv6_block2>,
                    'ipv6__block3__iexact': <ipv6_block3>,
                    'ipv6__block4__iexact': <ipv6_block4>,
                    'ipv6__block5__iexact': <ipv6_block5>,
                    'ipv6__block6__iexact': <ipv6_block6>,
                    'ipv6__block7__iexact': <ipv6_block7>,
                    'ipv6__block8__iexact': <ipv6_block8>,
                    'created': <boolean>,
                }],
                'start_record': <interger>,
                'custom_search': '<string>',
                'end_record': <interger>,
                'asorting_cols': [<string>,..],
                'searchable_columns': [<string>,..]
                }
        :return list of vips request with property "total"
        {"total": <interger>,
            "vips": [..]
        }

        :example
        Search server pools where the ipv4 "192.168.x.x" and are created,
        or the ipv4 "x.168.17.x" and are not created.
        {
            'extends_search': [{
                'ipv4__oct1': "192",
                'ipv4__oct2': "168",
                'created': True,
            },{
                'ipv4__oct2': "168",
                'ipv4__oct3': "17",
                'created': False,
            }],
            'start_record': 0,
            'custom_search': '',
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': []
        }
        """
        try:
            if not kwargs.get('vip_request_ids'):

                try:
                    search = ast.literal_eval(request.GET.get('search'))
                except:
                    search = {}

                vips_requests = facade.get_vip_request_by_search(search)

                serializer_vips = VipRequestTableSerializer(
                    vips_requests['vips'],
                    many=True
                )
                data = {
                    'vips': serializer_vips.data,
                    'total': vips_requests['total']
                    # 'search': vips_requests['search']
                }

            else:
                vip_request_ids = kwargs['vip_request_ids'].split(';')

                vips_requests = facade.get_vip_request(vip_request_ids)

                if vips_requests:
                    serializer_vips = VipRequestSerializer(
                        vips_requests,
                        many=True
                    )
                    data = {
                        'vips': serializer_vips.data
                    }
                else:
                    raise exceptions.VipRequestDoesNotExistException()

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('vip_post')
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Creates list of vip request
        :url /api/v3/vip-request/<vip_request_ids>/
        :param vip_request_ids=<vip_request_ids>
        {
            "vips": [{
                "business": <string>,
                "created": <boolean>,
                "environmentvip": <environmentvip_id>,
                "id": <vip_id>,
                "ipv4": <ipv4_id>,
                "ipv6": <ipv6_id>,
                "name": <string>,
                "options": {
                    "cache_group": <optionvip_id>,
                    "persistence": <optionvip_id>,
                    "timeout": <optionvip_id>,
                    "traffic_return": <optionvip_id>
                },
                "ports": [{
                    "id": <vip_port_id>,
                    "options": {
                        "l4_protocol": <optionvip_id>,
                        "l7_protocol": <optionvip_id>
                    },
                    "pools": [{
                            "l7_rule": <optionvip_id>,
                            "l7_value": <string>,
                            "server_pool": <server_pool_id>
                        },..],
                    "port": <integer>
                    },..],
                "service": <string>
            },..]
        }
        """

        data = request.DATA

        json_validate(SPECS.get('vip_post')).validate(data)

        response = list()
        for vip in data['vips']:
            facade.validate_save(vip)
            vp = facade.create_vip_request(vip)
            response.append({'id': vp.id})

        return Response(response, status.HTTP_201_CREATED)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate('vip_put')
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Updates list of vip request
        :url /api/v3/vip-request/<vip_request_ids>/
        :param vip_request_ids=<vip_request_ids>
        {
            "vips": [{
                "business": <string>,
                "created": <boolean>,
                "environmentvip": <environmentvip_id>,
                "id": <vip_id>,
                "ipv4": <ipv4_id>,
                "ipv6": <ipv6_id>,
                "name": <string>,
                "options": {
                    "cache_group": <optionvip_id>,
                    "persistence": <optionvip_id>,
                    "timeout": <optionvip_id>,
                    "traffic_return": <optionvip_id>
                },
                "ports": [{
                    "id": <vip_port_id>,
                    "options": {
                        "l4_protocol": <optionvip_id>,
                        "l7_protocol": <optionvip_id>
                    },
                    "pools": [{
                            "l7_rule": <optionvip_id>,
                            "l7_value": <string>,
                            "server_pool": <server_pool_id>
                        },..],
                    "port": <integer>
                    },..],
                "service": <string>
            },..]
        }
        """
        data = request.DATA

        json_validate(SPECS.get('vip_put')).validate(data)

        locks_list = facade.create_lock(data['vips'])
        try:
            for vip in data['vips']:
                facade.validate_save(vip)
                facade.update_vip_request(vip)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)

        return Response({})

    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Deletes list of vip request
        :url /api/v3/vip-request/<vip_request_ids>/
        :param vip_request_ids=<vip_request_ids>
        """
        vip_request_ids = kwargs['vip_request_ids'].split(';')
        locks_list = facade.create_lock(vip_request_ids)
        try:
            facade.delete_vip_request(vip_request_ids)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
        finally:
            facade.destroy_lock(locks_list)

        return Response({})


class VipRequestDBDetailsView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        ##############
        ## With ids ##
        ##############
        Return vip request by ids
        :url /api/v3/vip-request/details/<vip_request_ids>/
        :param vip_request_ids=<vip_request_ids>
        :return list of vip request
        {
            "vips": [{
                "id": <vip_id>,
                "name": <string>,
                "service": <string>,
                "business": <string>,
                "environmentvip": {
                    "id": <environmentvip_id>,
                    "finalidade_txt": <string>,
                    "cliente_txt": <string>,
                    "ambiente_p44_txt": <string>,
                    "description": <string>
                },
                "ipv4": {
                    "id": <ipv4_id>
                    "ip_formated": <ipv4_formated>,
                    "description": <string>
                },
                "ipv6": null,
                "equipments": [{
                    "id": <equipment_id>,
                    "name": <string>,
                    "equipment_type": <equipment_type_id>,
                    "model": <model_id>,
                    "groups": [<group_id>,..]
                }],
                "default_names": [<string>,..],
                "ports": [{
                    "id": <vip_port_id>,
                    "port": <interger>,
                    "options": {
                        "l4_protocol": {
                            "id": <optionvip_id>,
                            "tipo_opcao": <string>,
                            "nome_opcao_txt": <string>
                        },
                        "l7_protocol": {
                            "id": <optionvip_id>,
                            "tipo_opcao": <string>,
                            "nome_opcao_txt": <string>
                        }
                    },
                    "pools": [{
                        "server_pool": {
                            'id': <server_pool_id>,
                            ...
                            information from the pool,
                            same as GET /api/v3/pool/details/<server_pool_id>/
                        },
                        "l7_rule": {
                            "id": <optionvip_id>,
                            "tipo_opcao": <string>,
                            "nome_opcao_txt": <string>
                        },
                        "l7_value": <string>
                    },..]
                },..],
                "options": {
                    "cache_group": {
                        "id": <optionvip_id>,
                        "tipo_opcao": <string>,
                        "nome_opcao_txt": <string>
                    },
                    "traffic_return": {
                        "id": <optionvip_id>,
                        "tipo_opcao": <string>,
                        "nome_opcao_txt": <string>
                    },
                    "timeout": {
                        "id": <optionvip_id>,
                        "tipo_opcao": <string>,
                        "nome_opcao_txt": <string>
                    },
                    "persistence": {
                        "id": <optionvip_id>,
                        "tipo_opcao": <string>,
                        "nome_opcao_txt": <string>
                    }
                },
                "created": <boolean>
            },..]
        }
        :example
            /api/v3/vip-request/details/1;5/
            Return vips request with id 1 and 5
            {"vips": [{"id":1,...},{"id":5,... }]}

        ###############
        ## With dict ##
        ###############
        Return list of vip request by dict
        :url /api/v3/vip-request/details/
        :param search:GET['search']
            {'extends_search': [{
                    'ipv4__oct1': <ipv4__oct1>,
                    'ipv4__oct2': <ipv4__oct2>,
                    'ipv4__oct3': <ipv4__oct3>,
                    'ipv4__oct4': <ipv4__oct4>,
                    'ipv6__block1__iexact': <ipv6_block1>,
                    'ipv6__block2__iexact': <ipv6_block2>,
                    'ipv6__block3__iexact': <ipv6_block3>,
                    'ipv6__block4__iexact': <ipv6_block4>,
                    'ipv6__block5__iexact': <ipv6_block5>,
                    'ipv6__block6__iexact': <ipv6_block6>,
                    'ipv6__block7__iexact': <ipv6_block7>,
                    'ipv6__block8__iexact': <ipv6_block8>,
                    'created': <boolean>,
                }],
                'start_record': <interger>,
                'custom_search': '<string>',
                'end_record': <interger>,
                'asorting_cols': [<string>,..],
                'searchable_columns': [<string>,..]
                }
        :return list of vips request with property "total"
        {"total": <interger>,
            "vips": [..]
        }

        :example
        Search server pools where the ipv4 "192.168.x.x" and are created,
        or the ipv4 "x.168.17.x" and are not created.
        {
            'extends_search': [{
                'ipv4__oct1': "192",
                'ipv4__oct2': "168",
                'created': True,
            },{
                'ipv4__oct2': "168",
                'ipv4__oct3': "17",
                'created': False,
            }],
            'start_record': 0,
            'custom_search': '',
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': []
        }
        """
        try:
            if not kwargs.get('vip_request_ids'):

                try:
                    search = ast.literal_eval(request.GET.get('search'))
                except:
                    search = {}

                vips_requests = facade.get_vip_request_by_search(search)

                serializer_vips = VipRequestDetailsSerializer(
                    vips_requests['vips'],
                    many=True
                )
                data = {
                    'vips': serializer_vips.data,
                    'total': vips_requests['total']
                    # 'search': vips_requests['search']
                }

            else:
                vip_request_ids = kwargs['vip_request_ids'].split(';')

                vips_requests = facade.get_vip_request(vip_request_ids)

                if vips_requests:
                    serializer_vips = VipRequestDetailsSerializer(
                        vips_requests,
                        many=True
                    )
                    data = {
                        'vips': serializer_vips.data
                    }
                else:
                    raise exceptions.VipRequestDoesNotExistException()

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)


class VipRequestPoolView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """
        Returns a list of vip request by pool id and dict(optional)
        ##############
        ## With ids ##
        ##############
        :url /api/v3/vip-request/pool/<pool_id>
        :param vip_request_ids=<vip_request_ids>
        :return
        {
            "vips": [{
                "business": <string>,
                "created": <boolean>,
                "environmentvip": <environmentvip_id>,
                "id": <vip_id>,
                "ipv4": <ipv4_id>,
                "ipv6": <ipv6_id>,
                "name": <string>,
                "options": {
                    "cache_group": <optionvip_id>,
                    "persistence": <optionvip_id>,
                    "timeout": <optionvip_id>,
                    "traffic_return": <optionvip_id>
                },
                "ports": [{
                    "id": <vip_port_id>,
                    "options": {
                        "l4_protocol": <optionvip_id>,
                        "l7_protocol": <optionvip_id>
                    },
                    "pools": [{
                            "l7_rule": <optionvip_id>,
                            "l7_value": <string>,
                            "server_pool": <server_pool_id>
                        },..],
                    "port": <integer>
                    },..],
                "service": <string>
            },..]
        }
        :example
            /api/v3/vip-request/pool/1/
            Return vips request with pool id 1
            {"vips": [{"id":2,...},{"id":6,... }]}


        ###############
        ## With dict ##
        ###############
        Return list of vip request by dict
        :url /api/v3/vip-request/pool/<pool_id>/?search=<dict>
        :param <dict>
            {'extends_search': [{
                    'ipv4__oct1': <ipv4__oct1>,
                    'ipv4__oct2': <ipv4__oct2>,
                    'ipv4__oct3': <ipv4__oct3>,
                    'ipv4__oct4': <ipv4__oct4>,
                    'ipv6__block1__iexact': <ipv6_block1>,
                    'ipv6__block2__iexact': <ipv6_block2>,
                    'ipv6__block3__iexact': <ipv6_block3>,
                    'ipv6__block4__iexact': <ipv6_block4>,
                    'ipv6__block5__iexact': <ipv6_block5>,
                    'ipv6__block6__iexact': <ipv6_block6>,
                    'ipv6__block7__iexact': <ipv6_block7>,
                    'ipv6__block8__iexact': <ipv6_block8>,
                    'created': <boolean>,
                }],
                'start_record': <interger>,
                'custom_search': '<string>',
                'end_record': <interger>,
                'asorting_cols': [<string>,..],
                'searchable_columns': [<string>,..]
        """
        try:

            try:
                search = ast.literal_eval(request.GET.get('search'))
            except:
                search = {
                    'extends_search': []
                }

            pool_id = int(kwargs['pool_id'])

            extends_search = {'viprequestport__viprequestportpool__server_pool': pool_id}
            search['extends_search'] = [ex.append(extends_search) for ex in search['extends_search']] \
                if search['extends_search'] else [extends_search]

            log.info(search)
            vips_requests = facade.get_vip_request_by_search(search)

            serializer_vips = VipRequestTableSerializer(
                vips_requests['vips'],
                many=True
            )
            data = {
                'vips': serializer_vips.data,
                'total': vips_requests['total']
                # 'search': vips_requests['search']
            }

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)
