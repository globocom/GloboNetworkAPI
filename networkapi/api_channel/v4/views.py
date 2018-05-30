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
from networkapi.api_interface.permissions import DeployConfig
from networkapi.api_interface import facade
from networkapi.api_interface import exceptions


class DeployChannelConfV3View(APIView):
    """
    View class to handle requests to deploy configuration on interfaces
    channels on equipments
    """

    log = getLogger(__name__)

    @logs_method_apiview
    @permission_classes((IsAuthenticated, DeployConfig))
    def put(self, request, *args, **kwargs):
        """ Tries to configure interface channel using facade method """

        self.log.info('Deploy Channel Conf')

        interface_id = kwargs.get('channel_id')
        if not interface_id:
            return Response({"error": "Channel not found"},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            data = facade.generate_and_deploy_channel_config_sync(
                request.user, channel_id)

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
            self.log.error(exception)
            raise exception
