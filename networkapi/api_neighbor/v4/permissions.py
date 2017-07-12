# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.auth import perm_obj


class Read(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.NEIGHBOR_MANAGEMENT,
            AdminPermission.READ_OPERATION
        )


class Write(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.NEIGHBOR_MANAGEMENT,
            AdminPermission.WRITE_OPERATION
        )


class DeployCreate(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.NEIGHBOR_CREATE_SCRIPT,
            AdminPermission.WRITE_OPERATION
        )


class DeployDelete(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.NEIGHBOR_REMOVE_SCRIPT,
            AdminPermission.WRITE_OPERATION
        )


def deploy_obj_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_obj(
                request,
                AdminPermission.OBJ_UPDATE_CONFIG_OPERATION,
                AdminPermission.OBJ_TYPE_NEIGHBOR,
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
                AdminPermission.OBJ_TYPE_NEIGHBOR,
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
                AdminPermission.OBJ_TYPE_NEIGHBOR,
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
                AdminPermission.OBJ_TYPE_NEIGHBOR,
                *args,
                **kwargs
            )

    return Perm

