# -*- coding: utf-8 -*-
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.permissions import BasePermission

from networkapi.admin_permission import AdminPermission
from networkapi.api_network.facade.v3 import get_networkipv4_by_ids
from networkapi.api_network.facade.v3 import get_networkipv6_by_ids
from networkapi.auth import has_perm
from networkapi.auth import validate_object_perm


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

class WriteForce(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.NETWORK_FORCE,
            AdminPermission.WRITE_OPERATION
        )

class DeployConfig(BasePermission):

    def has_permission(self, request, view):
        return has_perm(
            request.user,
            AdminPermission.VLAN_MANAGEMENT,
            AdminPermission.WRITE_OPERATION
        )


def perm_objv4(request, operation, object_type, *args, **kwargs):

    if request.method == 'POST':
        try:
            objs = [net['vlan'] for net in request.DATA['networks']]
        except Exception:
            objs = get_networkipv4_by_ids(kwargs.get('obj_ids', []).split(';')) \
                .values_list('vlan', flat=True)
    else:
        objs = get_networkipv4_by_ids(kwargs.get('obj_ids', []).split(';'))\
            .values_list('vlan', flat=True)

    return validate_object_perm(
        objs,
        request.user,
        operation,
        object_type
    )


def perm_objv6(request, operation, object_type, *args, **kwargs):

    if request.method == 'POST':
        try:
            objs = [net['vlan'] for net in request.DATA['networks']]
        except Exception:
            objs = get_networkipv6_by_ids(kwargs.get('obj_ids', []).split(';')) \
                .values_list('vlan', flat=True)
    else:
        objs = get_networkipv6_by_ids(kwargs.get('obj_ids', []).split(';'))\
            .values_list('vlan', flat=True)

    return validate_object_perm(
        objs,
        request.user,
        operation,
        object_type
    )


def deploy_objv4_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_objv4(
                request,
                AdminPermission.OBJ_UPDATE_CONFIG_OPERATION,
                AdminPermission.OBJ_TYPE_VLAN,
                *args,
                **kwargs
            )

    return Perm


def write_objv4_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_objv4(
                request,
                AdminPermission.OBJ_WRITE_OPERATION,
                AdminPermission.OBJ_TYPE_VLAN,
                *args,
                **kwargs
            )

    return Perm


def delete_objv4_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_objv4(
                request,
                AdminPermission.OBJ_DELETE_OPERATION,
                AdminPermission.OBJ_TYPE_VLAN,
                *args,
                **kwargs
            )

    return Perm


def read_objv4_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_objv4(
                request,
                AdminPermission.OBJ_READ_OPERATION,
                AdminPermission.OBJ_TYPE_VLAN,
                *args,
                **kwargs
            )

    return Perm


def deploy_objv6_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_objv6(
                request,
                AdminPermission.OBJ_UPDATE_CONFIG_OPERATION,
                AdminPermission.OBJ_TYPE_VLAN,
                *args,
                **kwargs
            )

    return Perm


def write_objv6_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_objv6(
                request,
                AdminPermission.OBJ_WRITE_OPERATION,
                AdminPermission.OBJ_TYPE_VLAN,
                *args,
                **kwargs
            )

    return Perm


def delete_objv6_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_objv6(
                request,
                AdminPermission.OBJ_DELETE_OPERATION,
                AdminPermission.OBJ_TYPE_VLAN,
                *args,
                **kwargs
            )

    return Perm


def read_objv6_permission(request, *args, **kwargs):

    class Perm(BasePermission):

        def has_permission(self, request, view):
            return perm_objv6(
                request,
                AdminPermission.OBJ_READ_OPERATION,
                AdminPermission.OBJ_TYPE_VLAN,
                *args,
                **kwargs
            )

    return Perm

