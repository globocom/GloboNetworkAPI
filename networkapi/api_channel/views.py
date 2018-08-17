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

from logging import getLogger

from django.db.transaction import commit_on_success

from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from networkapi.settings import SPECS

from networkapi.api_channel.permissions import ChannelDeploy
from networkapi.api_channel.permissions import ChannelRead
from networkapi.api_channel.permissions import ChannelWrite
from networkapi.api_channel.facade import ChannelV3

from networkapi.api_interface import facade
from networkapi.api_interface.exceptions import UnsupportedEquipmentException
from networkapi.api_interface.exceptions import InvalidIdInterfaceException
from networkapi.api_interface.exceptions import InterfaceTemplateException

from networkapi.interface.models import InterfaceNotFoundError

from networkapi.util.decorators import logs_method_apiview
from networkapi.util.json_validate import json_validate
from networkapi.util.json_validate import raise_json_validate


log = getLogger(__name__)


class ChannelV3View(APIView):
    """ Implements CRUD routes handlers of Channels """

    log = getLogger(__name__)

    @logs_method_apiview
    @permission_classes((IsAuthenticated, ChannelRead))
    def get(self, request, *args, **kwargs):
        """ Http handler to route v3/interface/channel/ for GET method """

        data = None
        channel_name = kwargs.get('channel_id')
        try:
            channel_id = int(channel_name)
            channel = ChannelV3()
            data = channel.retrieve_by_id(channel_id)

        except ValueError:  # In case we have a name instead of a ID
            channel = ChannelV3()
            data = channel.retrieve(channel_name)

        if data is None:
            error = {"error": "Channel not found: '%s'" % channel_name}
            return Response(error, status=status.HTTP_404_NOT_FOUND)

        return Response(data, status=status.HTTP_200_OK)

    @logs_method_apiview
    @permission_classes((IsAuthenticated, ChannelWrite))
    @raise_json_validate('channel_post_v3')
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """ Http handler to route v3/channel for POST method """

        log.info("POST - api_channel")

        channels = request.DATA

        #json_validate(SPECS.get('channel_post_v3')).validate(channels)

        response = []
        try:
            for channel_data in channels.get('channels'):

                channel = ChannelV3()
                data = channel.create(channel_data)

                response.append({'id': data.get('channels')})

        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(response, status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @permission_classes((IsAuthenticated, ChannelWrite))
    def put(self, request, *args, **kwargs):
        """ Http handler to route v3/interface/channel for PUT method """

        channels = request.DATA
        json_validate(SPECS.get('channel_put')).validate(channels)

        response = []
        for channel_data in channels:

            channel = ChannelV3(request.user)
            data = channel.update(channel_data)

            if "error" in data:
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            response.append({'id': channel.id})

        return Response(response, status=status.HTTP_200_OK)

    @logs_method_apiview
    @permission_classes((IsAuthenticated, ChannelWrite))
    def delete(self, request, *args, **kwargs):
        """ Http handler to route v3/interface/channel/id for DELETE method """

        channel_id = kwargs.get('channel_id')

        channel = ChannelV3(request.user)

        deletion = {}
        try:
            deletion = channel.delete(channel_id)

        except InterfaceNotFoundError:
            return Response(
                {"error": "Could not find channel '%s'" % channel_id},
                status=status.HTTP_404_NOT_FOUND
            )

        if "error" in deletion:
            return Response(deletion, status=status.HTTP_400_BAD_REQUEST)

        return Response(deletion, status=status.HTTP_200_OK)


class DeployChannelConfV3View(APIView):
    """
    View class to handle requests to deploy configuration on interfaces
    channels on equipments
    """

    log = getLogger(__name__)

    @logs_method_apiview
    @permission_classes((IsAuthenticated, ChannelDeploy))
    def put(self, request, *args, **kwargs):
        """ Tries to configure interface channel using facade method """

        interface_id = kwargs.get('channel_id')
        if not interface_id:
            return Response({"error": "Channel not found"},
                            status=status.HTTP_404_NOT_FOUND)
        try:
            data = facade.generate_and_deploy_channel_config_sync(
                request.user, interface_id)

            return Response(data, status=status.HTTP_200_OK)

        except (InvalidIdInterfaceException, UnsupportedEquipmentException,
                InterfaceTemplateException) as err:
            raise err

        except InterfaceNotFoundError:
            raise InvalidIdInterfaceException

        except Exception as err:
            self.log.error(err)
            raise err
