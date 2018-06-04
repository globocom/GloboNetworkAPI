# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging

from django.db.transaction import commit_on_success

from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_interface import exceptions
from networkapi.api_interface import facade
from networkapi.api_interface import serializers
from networkapi.api_interface.permissions import DeployConfig
from networkapi.api_interface.permissions import Read
from networkapi.api_interface.permissions import Write
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_INTERFACE
from networkapi.interface.models import Interface
from networkapi.interface.models import InterfaceNotFoundError
from networkapi.settings import SPECS
from networkapi.util.classes import CustomAPIView
from networkapi.util.decorators import logs_method_apiview
from networkapi.util.decorators import permission_classes_apiview
from networkapi.util.decorators import prepare_search
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate
from networkapi.util.geral import create_lock
from networkapi.util.geral import destroy_lock
from networkapi.util.geral import render_to_json


log = logging.getLogger(__name__)


class DeployInterfaceConfV3View(APIView):
    """
    View class to handle requests to deploy configuration on equipments
    interfaces.
    """

    @logs_method_apiview
    @permission_classes((IsAuthenticated, DeployConfig))
    def put(self, request, *args, **kwargs):
        """ Tries to configure interface using facade method """

        log.info('Deploy Interface Conf')

        interface_id = kwargs.get('interface_id')
        if not interface_id:
            return Response({"error": "Interface not found"},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            data = facade.generate_and_deploy_interface_config_sync(
                request.user, interface_id)

            return Response(data, status=status.HTTP_201_CREATED)

        except exceptions.InvalidIdInterfaceException, exception:
            raise exception
        except exceptions.UnsupportedEquipmentException, exception:
            raise exception
        except exceptions.InterfaceTemplateException, exception:
            raise exception
        except InterfaceNotFoundError:
            raise exceptions.InvalidIdInterfaceException
        except Exception, exception:
            log.error(exception)
            raise exception


class DisconnectView(APIView):

    @permission_classes((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """URL: api/interface/disconnect/(?P<id_interface_1>\d+)/(?P<id_interface_2>\d+)/"""

        try:
            log.info('API_Disconnect')

            data = dict()

            id_interface_1 = kwargs.get('id_interface_1')
            id_interface_2 = kwargs.get('id_interface_2')

            interface_1 = Interface.get_by_pk(int(id_interface_1))
            interface_2 = Interface.get_by_pk(int(id_interface_2))

            with distributedlock(LOCK_INTERFACE % id_interface_1):

                if interface_1.channel or interface_2.channel:
                    raise exceptions.InterfaceException(
                        'Interface está em um Port Channel')

                if interface_1.ligacao_front_id == interface_2.id:
                    interface_1.ligacao_front = None
                    if interface_2.ligacao_front_id == interface_1.id:
                        interface_2.ligacao_front = None
                    else:
                        interface_2.ligacao_back = None
                elif interface_1.ligacao_back_id == interface_2.id:
                    interface_1.ligacao_back = None
                    if interface_2.ligacao_back_id == interface_1.id:
                        interface_2.ligacao_back = None
                    else:
                        interface_2.ligacao_front = None
                elif not interface_1.ligacao_front_id and not interface_1.ligacao_back_id:
                    raise exceptions.InterfaceException(
                        'Interface id %s não connectada' % interface_1)

                interface_1.save()
                interface_2.save()

            return Response(data, status=status.HTTP_200_OK)

        except exceptions.InterfaceException, exception:
            raise exception
        except InterfaceNotFoundError, exception:
            log.error(exception)
            raise api_exceptions.ObjectDoesNotExistException(
                'Interface Does Not Exist. %s' % exception)
        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)


class InterfaceTypeV3View(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """URL: api/v3/interface-type/"""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_interface_type_by_search(self.search)
            interfaces_type = obj_model['query_set']
            only_main_property = False
        else:
            interface_ids = kwargs.get('obj_ids').split(';')
            interfaces_type = facade.get_interface_by_ids(interface_ids)
            only_main_property = True
            obj_model = None

        serializer_interface_type = serializers.InterfaceTypeSerializer(
            interfaces_type,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        data = render_to_json(
            serializer_interface_type,
            main_property='interfaces_type',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)


class InterfaceEnvironmentsV3View(CustomAPIView):

    @logs_method_apiview
    @raise_json_validate('')
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """URL: api/v3/interface/environments/<obj_ids>"""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_interfaces_environments_by_search(self.search)
            interface_environments = obj_model['query_set']
            only_main_property = False
        else:
            ids = kwargs.get('obj_ids').split(';')
            interface_environments = facade.get_interfaces_environments_by_ids(ids)
            only_main_property = True
            obj_model = None

        serializer_interface_environment = serializers.InterfaceEnvironmentV3Serializer(
            interface_environments,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        data = render_to_json(
            serializer_interface_environment,
            main_property='interface_environments',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """
        Remove the relationship between an interface and environments.

        :param kwargs: obj_ids
        :return: 200 OK
        """

        obj_ids = kwargs.get('obj_ids').split(';')
        locks_list = create_lock(obj_ids, LOCK_INTERFACE)

        for obj in obj_ids:
            try:
                facade.delete_interface_environments(obj)
            finally:
                destroy_lock(locks_list)

        return Response({}, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('interface_environments_post')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Associates an interface to an environment.
        URL: api/v3/interface/environments/
        """

        response = list()

        interface_environments = request.DATA
        json_validate(SPECS.get('interface_environments_post')).validate(interface_environments)

        for i in interface_environments.get('interface_environments'):
            try:
                int_envs = facade.create_interface_environments(i)
                response.append({'id': int_envs.id})
            except api_exceptions.NetworkAPIException, e:
                log.error(e)
                raise api_exceptions.NetworkAPIException(e)
            except api_exceptions.ValidationAPIException, e:
                log.error(e)
                raise api_exceptions.NetworkAPIException(e)

        data = dict()
        data['interface_environments'] = response

        return Response(data, status=status.HTTP_201_CREATED)


class InterfaceV3View(CustomAPIView):

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Read))
    @prepare_search
    def get(self, request, *args, **kwargs):
        """URL: api/v3/interface/"""

        if not kwargs.get('obj_ids'):
            obj_model = facade.get_interface_by_search(self.search)
            interfaces = obj_model['query_set']
            only_main_property = False
        else:
            interface_ids = kwargs.get('obj_ids').split(';')
            interfaces = facade.get_interface_by_ids(interface_ids)
            only_main_property = True
            obj_model = None

        serializer_interface = serializers.InterfaceV3Serializer(
            interfaces,
            many=True,
            fields=self.fields,
            include=self.include,
            exclude=self.exclude,
            kind=self.kind
        )

        data = render_to_json(
            serializer_interface,
            main_property='interfaces',
            obj_model=obj_model,
            request=request,
            only_main_property=only_main_property
        )

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('interface_post')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Create Interface
        URL: api/v3/interface/
        """

        response = list()

        interfaces = request.DATA
        json_validate(SPECS.get('interface_post')).validate(interfaces)

        for i in interfaces.get('interfaces'):
            try:
                interface = facade.create_interface(i)
                response.append({'id': interface.id})
            except api_exceptions.NetworkAPIException, e:
                log.error(e)
                raise api_exceptions.NetworkAPIException(e)
            except api_exceptions.ValidationAPIException, e:
                log.error(e)
                raise api_exceptions.NetworkAPIException(e)

        data = dict()
        data['interfaces'] = response

        return Response(data, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def delete(self, request, *args, **kwargs):
        """Deletes list of interfaces."""

        obj_ids = kwargs.get('obj_ids').split(';')
        locks_list = create_lock(obj_ids, LOCK_INTERFACE)

        for obj in obj_ids:
            try:
                facade.delete_interface(obj)
            finally:
                destroy_lock(locks_list)

        return Response({}, status=status.HTTP_200_OK)

    @logs_method_apiview
    @raise_json_validate('interface_put')
    @permission_classes_apiview((IsAuthenticated, Write))
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """Updates list of interfaces."""

        response = list()
        data = request.DATA

        json_validate(SPECS.get('interface_put')).validate(data)
        locks_list = create_lock(data['interfaces'], LOCK_INTERFACE)

        for interface in data['interfaces']:
            try:
                interface = facade.update_interface(interface)
                response.append({'id': interface.id})
            finally:
                destroy_lock(locks_list)

        return Response(response, status=status.HTTP_200_OK)
