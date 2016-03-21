# -*- coding:utf-8 -*-
from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm

from rest_framework.permissions import BasePermission


class Read(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.ENVIRONMENT_MANAGEMENT,
            AdminPermission.READ_OPERATION
        )


class Write(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.ENVIRONMENT_MANAGEMENT,
            AdminPermission.WRITE_OPERATION
        )
