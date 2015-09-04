# -*- coding:utf-8 -*-
from rest_framework.permissions import BasePermission
from networkapi.auth import has_perm
from networkapi.admin_permission import AdminPermission


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

class DeployConfig(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.VLAN_MANAGEMENT,
            AdminPermission.WRITE_OPERATION
        )

