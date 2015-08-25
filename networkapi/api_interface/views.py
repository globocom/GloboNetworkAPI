# -*- coding:utf-8 -*-

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

from django.db.transaction import commit_on_success
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from networkapi.log import Log
from networkapi.api_rest import exceptions as api_exceptions
from networkapi.exception import InvalidValueError, EnvironmentVipNotFoundError
from networkapi.interface.models import InterfaceNotFoundError
from networkapi.api_interface.permissions import Read, Write, DeployConfig
from networkapi.api_interface import exceptions
from networkapi.api_interface import facade



log = Log(__name__)


@api_view(['PUT'])
@permission_classes((IsAuthenticated, DeployConfig))
def deploy_interface_configuration(request, id_interface):
    """
    Deploy interface configuration on equipment(s)
    """

    try:
        data = facade.generate_and_deploy_interface_config(request.user, id_interface)

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
        raise api_exceptions.NetworkAPIException()

@api_view(['PUT'])
@permission_classes((IsAuthenticated, DeployConfig))
def deploy_channel_configuration(request, id_channel):
    """
    Deploy interface channel configuration on equipment(s)
    """

    try:
        data = facade.generate_and_deploy_channel_config(request.user, id_channel)

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
        raise api_exceptions.NetworkAPIException()



