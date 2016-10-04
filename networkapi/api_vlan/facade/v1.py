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
from rest_framework.views import Response

from networkapi.api_vlan import exceptions
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.vlan.models import Vlan

type_acl_v4 = "v4"
type_acl_v6 = "v6"


def acl_save_draft(request, id_vlan, type_acl):

    type_to_check = type_acl.strip().lower()
    content_draft = request.DATA.get('content_draft', '')

    if not is_valid_int_greater_zero_param(id_vlan):
        raise exceptions.InvalidIdVlanException()

    vlan_obj = Vlan.objects.get(pk=id_vlan)

    if type_to_check == type_acl_v4:
        vlan_obj.acl_draft = content_draft
    else:
        vlan_obj.acl_draft_v6 = content_draft

    vlan_obj.save(request.user)

    return Response()


def acl_remove_draft(request, id_vlan, type_acl):

    type_to_check = type_acl.strip().lower()

    if not is_valid_int_greater_zero_param(id_vlan):
        raise exceptions.InvalidIdVlanException()

    vlan_obj = Vlan.objects.get(pk=id_vlan)

    if type_to_check == type_acl_v4:
        vlan_obj.acl_draft = None
    else:
        vlan_obj.acl_draft_v6 = None

    vlan_obj.save(request.user)

    return Response()
