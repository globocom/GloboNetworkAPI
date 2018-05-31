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

from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from networkapi.util.decorators import logs_method_apiview

from networkapi.api_channel.permissions import ChannelDeploy
from networkapi.api_channel.permissions import ChannelRead
from networkapi.api_channel.permissions import ChannelWrite

from networkapi.api_interface import facade
from networkapi.api_interface.exceptions import InvalidIdInterfaceException
from networkapi.api_interface.exceptions import InterfaceTemplateException
from networkapi.api_interface.exceptions import UnsupportedEquipmentException
from networkapi.api_interface.exceptions import InvalidIdInterfaceException

from networkapi.interface.models import InterfaceNotFoundError


class ChannelV3View(APIView):
    """ Implements CRUD routes handlers of Channels """

    log = getLogger(__name__)

    @logs_method_apiview
    @permission_classes((IsAuthenticated, ChannelRead))
    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)

    @logs_method_apiview
    @permission_classes((IsAuthenticated, ChannelWrite))
    def post(self, request, *args, **kwargs):
        return Response(status=status.HTTP_201_CREATED)

    @logs_method_apiview
    @permission_classes((IsAuthenticated, ChannelWrite))
    def put(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)

    @logs_method_apiview
    @permission_classes((IsAuthenticated, ChannelWrite))
    def delete(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


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

        self.log.info('Deploy Channel Conf')

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
