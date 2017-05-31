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
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_vlan import exceptions
from networkapi.api_vlan.facade import v1 as facade
from networkapi.api_vlan.permissions import Write
from networkapi.vlan.models import Vlan


log = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes((IsAuthenticated, Write))
@commit_on_success
def acl_remove_draft(request, id_vlan, acl_type):
    """
        Remove draft for acl

    :param request: Request From Client
    :param id_vlan: Identifier Vlan
    :param acl_type: Type acl v4 or v6

    :return: Response obj
    """

    try:

        response = facade.acl_remove_draft(request, id_vlan, acl_type)

        return response

    except Vlan.DoesNotExist, exception:
        log.error(exception)
        raise exceptions.VlanDoesNotExistException()

    except exceptions.InvalidIdVlanException, exception:
        log.error(exception)
        raise exception

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()


@api_view(['POST'])
@permission_classes((IsAuthenticated, Write))
@commit_on_success
def acl_save_draft(request, id_vlan, acl_type):
    """
        Save draft for acl

    :param request: Request From Client
    :param id_vlan: Identifier Vlan
    :param acl_type: Type acl v4 or v6

    :return: Response obj
    """
    try:

        response = facade.acl_save_draft(request, id_vlan, acl_type)

        return response

    except Vlan.DoesNotExist, exception:
        log.error(exception)
        raise exceptions.VlanDoesNotExistException()

    except exceptions.InvalidIdVlanException, exception:
        log.error(exception)
        raise exception

    except Exception, exception:
        log.error(exception)
        raise api_exceptions.NetworkAPIException()
