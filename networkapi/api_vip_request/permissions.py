# -*- coding: utf-8 -*-
"""
@author: William Vedroni da Silva
@organization: S2it
@copyright: 2014 globo.com todos os direitos reservados.
"""
from rest_framework.permissions import BasePermission

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.auth import perm_vip


class Read(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.VIPS_REQUEST,
            AdminPermission.READ_OPERATION
        )


class Write(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.VIPS_REQUEST,
            AdminPermission.WRITE_OPERATION
        )


class DeployUpdate(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.VIP_ALTER_SCRIPT,
            AdminPermission.WRITE_OPERATION
        )


class DeployCreate(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.VIP_CREATE_SCRIPT,
            AdminPermission.WRITE_OPERATION
        )


class DeployDelete(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.VIP_REMOVE_SCRIPT,
            AdminPermission.WRITE_OPERATION
        )


def deploy_vip_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_vip(request, AdminPermission.VIP_UPDATE_CONFIG_OPERATION, *args, **kwargs)

    return Perm


def write_vip_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_vip(request, AdminPermission.VIP_WRITE_OPERATION, *args, **kwargs)

    return Perm


def delete_vip_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_vip(request, AdminPermission.VIP_DELETE_OPERATION, *args, **kwargs)

    return Perm


def read_vip_ermission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_vip(request, AdminPermission.VIP_READ_OPERATION, *args, **kwargs)

    return Perm
