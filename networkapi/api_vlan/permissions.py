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
from rest_framework.permissions import BasePermission

from networkapi.admin_permission import AdminPermission
from networkapi.api_ogp.facade import perm_obj
from networkapi.auth import has_perm


class Read(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.VLAN_MANAGEMENT,
            AdminPermission.READ_OPERATION
        )


class Write(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.VLAN_MANAGEMENT,
            AdminPermission.WRITE_OPERATION
        )


def deploy_obj_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_obj(
                request,
                AdminPermission.OBJ_UPDATE_CONFIG_OPERATION,
                AdminPermission.OBJ_TYPE_VLAN,
                *args,
                **kwargs
            )

    return Perm


def write_obj_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_obj(
                request,
                AdminPermission.OBJ_WRITE_OPERATION,
                AdminPermission.OBJ_TYPE_VLAN,
                *args,
                **kwargs
            )

    return Perm


def delete_obj_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_obj(
                request,
                AdminPermission.OBJ_DELETE_OPERATION,
                AdminPermission.OBJ_TYPE_VLAN,
                *args,
                **kwargs
            )

    return Perm


def read_obj_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_obj(
                request,
                AdminPermission.OBJ_READ_OPERATION,
                AdminPermission.OBJ_TYPE_VLAN,
                *args,
                **kwargs
            )

    return Perm
