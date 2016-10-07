# -*- coding: utf-8 -*-
from rest_framework.views import Response

from networkapi.api_vlan import exceptions
from networkapi.util import is_valid_int_greater_zero_param
from networkapi.vlan.models import Vlan

TYPE_ACL_V4 = 'v4'
TYPE_ACL_V6 = 'v6'


def acl_save_draft(request, id_vlan, type_acl):

    type_to_check = type_acl.strip().lower()
    content_draft = request.DATA.get('content_draft', '')

    if not is_valid_int_greater_zero_param(id_vlan):
        raise exceptions.InvalidIdVlanException()

    vlan_obj = Vlan.objects.get(pk=id_vlan)

    if type_to_check == TYPE_ACL_V4:
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

    if type_to_check == TYPE_ACL_V4:
        vlan_obj.acl_draft = None
    else:
        vlan_obj.acl_draft_v6 = None

    vlan_obj.save(request.user)

    return Response()
