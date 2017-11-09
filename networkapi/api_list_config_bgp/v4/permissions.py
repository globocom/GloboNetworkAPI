# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm


class Read(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.LIST_CONFIG_BGP_MANAGEMENT,
            AdminPermission.READ_OPERATION
        )


class Write(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.LIST_CONFIG_BGP_MANAGEMENT,
            AdminPermission.WRITE_OPERATION
        )


class DeployCreate(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.LIST_CONFIG_BGP_DEPLOY_SCRIPT,
            AdminPermission.WRITE_OPERATION
        )


class DeployDelete(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.LIST_CONFIG_BGP_UNDEPLOY_SCRIPT,
            AdminPermission.WRITE_OPERATION
        )
