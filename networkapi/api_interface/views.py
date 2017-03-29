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
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from networkapi.api_interface import exceptions
from networkapi.api_interface import facade
from networkapi.api_interface.permissions import DeployConfig
from networkapi.api_interface.permissions import Read
from networkapi.api_interface.permissions import Write
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_INTERFACE
from networkapi.interface.models import Interface
from networkapi.interface.models import InterfaceNotFoundError


log = logging.getLogger(__name__)


@api_view(['PUT'])
@permission_classes((IsAuthenticated, DeployConfig))
def deploy_interface_configuration_sync(request, id_interface):
    """
    Deploy interface configuration on equipment(s)
    """

    try:
        data = facade.generate_and_deploy_interface_config_sync(
            request.user, id_interface)

        return Response(data)

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


@api_view(['PUT'])
@permission_classes((IsAuthenticated, DeployConfig))
def deploy_channel_configuration_sync(request, id_channel):
    """
    Deploy interface channel configuration on equipment(s)
    """

    try:
        data = facade.generate_and_deploy_channel_config_sync(
            request.user, id_channel)

        return Response(data)

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
