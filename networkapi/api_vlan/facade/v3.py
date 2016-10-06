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
from django.core.exceptions import ObjectDoesNotExist

from networkapi.api_vlan import exceptions
from networkapi.distributedlock import distributedlock
from networkapi.distributedlock import LOCK_VLAN
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.vlan.models import Vlan

type_acl_v4 = "v4"
type_acl_v6 = "v6"


def get_vlan_by_id(vlan_id):
    """
    Get vlan by id
    """
    try:
        vlan = Vlan.objects.get(id=vlan_id)
    except ObjectDoesNotExist:
        raise exceptions.VlanDoesNotExistException()

    return vlan


def get_vlan_by_ids(vlan_ids):
    """
    Get vlans by ids
    """
    vlans = list()
    for vlan_id in vlan_ids:
        vlans.append(get_vlan_by_id(vlan_id))

    return vlans


def get_vlan_by_search(search=dict()):
    """
    Get vlans by search
    """

    vlans = Vlan.objects.filter()

    vlan_map = build_query_to_datatable_v3(vlans, search)

    return vlan_map


def update_vlan(vlan, user):
    """
    Update vlan
    """
    vlan_obj = get_vlan_by_id(vlan.get('id'))
    vlan_obj.name = vlan.get('name')
    vlan_obj.num_vlan = vlan.get('num_vlan')
    vlan_obj.environment_id = EnvironmentVip.get_by_pk(vlan.get('environment'))
    vlan_obj.description = vlan.get('description')
    vlan_obj.acl_file_name = vlan.get('acl_file_name')
    vlan_obj.acl_valida = vlan.get('acl_valida')
    vlan_obj.acl_file_name_v6 = vlan.get('acl_file_name_v6')
    vlan_obj.acl_valida_v6 = vlan.get('acl_valida_v6')
    vlan_obj.active = vlan.get('active')
    vlan_obj.vrf = vlan.get('vrf')
    vlan_obj.acl_draft = vlan.get('acl_draft')
    vlan_obj.acl_draft_v6 = vlan.get('acl_draft_v6')
    vlan_obj.save()


def create_vlan(vlan, user):
    """
    Create vlan
    """
    vlan_obj = Vlan()
    vlan_obj.name = vlan.get('name')
    vlan_obj.num_vlan = vlan.get('num_vlan')
    vlan_obj.environment_id = EnvironmentVip.get_by_pk(vlan.get('environment'))
    vlan_obj.description = vlan.get('description')
    vlan_obj.acl_file_name = vlan.get('acl_file_name')
    vlan_obj.acl_valida = vlan.get('acl_valida')
    vlan_obj.acl_file_name_v6 = vlan.get('acl_file_name_v6')
    vlan_obj.acl_valida_v6 = vlan.get('acl_valida_v6')
    vlan_obj.active = vlan.get('active')
    vlan_obj.vrf = vlan.get('vrf')
    vlan_obj.acl_draft = vlan.get('acl_draft')
    vlan_obj.acl_draft_v6 = vlan.get('acl_draft_v6')
    vlan_obj.save()


def delete_vlan(vlans):
    """
    Delete vlans by ids
    """
    for vlan in vlans:
        vlan_obj = get_vlan_by_id(vlan)
        vlan_obj.remove()


#############
# helpers
#############
def create_lock(vlans):
    """
    Create locks for vlans list
    """
    locks_list = list()
    for vlan in vlans:
        if isinstance(vlan, dict):
            lock = distributedlock(LOCK_VLAN % vlan['id'])
        else:
            lock = distributedlock(LOCK_VLAN % vlan)
        lock.__enter__()
        locks_list.append(lock)

    return locks_list


def destroy_lock(locks_list):
    """
    Destroy locks by vlans list
    """
    for lock in locks_list:
        lock.__exit__('', '', '')
