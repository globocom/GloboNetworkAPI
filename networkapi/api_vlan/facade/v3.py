# -*- coding: utf-8 -*-
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.vlan.models import OperationalError
from networkapi.vlan.models import Vlan
from networkapi.vlan.models import VlanError
from networkapi.vlan.models import VlanErrorV3
from networkapi.vlan.models import VlanNotFoundError


def get_vlan_by_id(vlan_id):
    """Get vlan by id"""

    try:
        vlan = Vlan().get_by_pk(vlan_id)
    except VlanNotFoundError, e:
        raise ObjectDoesNotExistException(str(e))
    except (Exception, OperationalError), e:
        raise NetworkAPIException(str(e))
    else:
        return vlan


def get_vlan_by_ids(vlan_ids):
    """Get vlans by ids"""

    vl_ids = list()
    for vlan_id in vlan_ids:
        vl_ids.append(get_vlan_by_id(vlan_id).id)

    vlans = Vlan.objects.filter(id__in=vl_ids)

    return vlans


def get_vlan_by_search(search=dict()):
    """Get vlans by search"""

    vlans = Vlan.objects.filter()
    vlan_map = build_query_to_datatable_v3(vlans, search)

    return vlan_map


def update_vlan(vlan, user):
    """Update vlan"""

    try:
        vlan_obj = get_vlan_by_id(vlan.get('id'))
        vlan_obj.update_v3(vlan, user)
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except (VlanError, VlanErrorV3, ValidationAPIException), e:
        raise ValidationAPIException(str(e))
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))
    else:
        return vlan_obj


def create_vlan(vlan, user):
    """Create vlan"""

    try:
        vlan_obj = Vlan()
        vlan_obj.create_v3(vlan, user)
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except (VlanError, VlanErrorV3, ValidationAPIException), e:
        raise ValidationAPIException(str(e))
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))
    else:
        return vlan_obj


def delete_vlan(vlans):
    """Delete vlans by ids"""

    try:
        for vlan in vlans:
            vlan_obj = get_vlan_by_id(vlan)
            vlan_obj.delete_v3()
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except (VlanError, VlanErrorV3, ValidationAPIException), e:
        raise ValidationAPIException(str(e))
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))
