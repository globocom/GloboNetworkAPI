# -*- coding: utf-8 -*-
"""
@author: William Vedroni da Silva
@organization: S2it
@copyright: 2014 globo.com todos os direitos reservados.
"""
from rest_framework.permissions import BasePermission

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.auth import perm_obj


class Read(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.POOL_MANAGEMENT,
            AdminPermission.READ_OPERATION
        )


class Write(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.POOL_MANAGEMENT,
            AdminPermission.WRITE_OPERATION
        )


class ScriptRemovePermission(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.POOL_REMOVE_SCRIPT,
            AdminPermission.WRITE_OPERATION
        )


class ScriptCreatePermission(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.POOL_CREATE_SCRIPT,
            AdminPermission.WRITE_OPERATION
        )


class ScriptAlterPermission(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.POOL_ALTER_SCRIPT,
            AdminPermission.WRITE_OPERATION
        )


def deploy_pool_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_obj(
                request,
                AdminPermission.POOL_UPDATE_CONFIG_OPERATION,
                'ServerPool',
                *args,
                **kwargs
            )

    return Perm


def write_pool_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_obj(
                request,
                AdminPermission.POOL_WRITE_OPERATION,
                'ServerPool',
                *args,
                **kwargs
            )

    return Perm


def delete_pool_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_obj(
                request,
                AdminPermission.POOL_DELETE_OPERATION,
                'ServerPool',
                *args,
                **kwargs
            )

    return Perm


def read_pool_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_obj(
                request,
                AdminPermission.POOL_READ_OPERATION,
                'ServerPool',
                *args,
                **kwargs
            )

    return Perm
