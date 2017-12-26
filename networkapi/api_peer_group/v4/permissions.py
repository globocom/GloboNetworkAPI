# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission

from networkapi.admin_permission import AdminPermission
from networkapi.auth import has_perm
from networkapi.auth import perm_obj


class Read(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.PEER_GROUP_MANAGEMENT,
            AdminPermission.READ_OPERATION
        )


class Write(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.PEER_GROUP_MANAGEMENT,
            AdminPermission.WRITE_OPERATION
        )


def write_obj_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_obj(
                request,
                AdminPermission.OBJ_WRITE_OPERATION,
                AdminPermission.OBJ_TYPE_PEER_GROUP,
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
                AdminPermission.OBJ_TYPE_PEER_GROUP,
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
                AdminPermission.OBJ_TYPE_PEER_GROUP,
                *args,
                **kwargs
            )

    return Perm
