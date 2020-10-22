# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError

from networkapi.api_asn.models import Asn
from networkapi.api_asn.models import AsnEquipment
from networkapi.api_asn.v4 import exceptions
from networkapi.api_asn.v4.exceptions import AsnErrorV4
from networkapi.api_asn.v4.exceptions import AsnNotFoundError, AsnError
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3

log = logging.getLogger(__name__)


def get_as_by_search(search=dict()):
    """Return a list of AS's by dict."""

    try:
        as_s = Asn.objects.filter()
        as_map = build_query_to_datatable_v3(as_s, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return as_map


def get_as_by_id(as_id):
    """Return an AS by id.

    Args:
        as_id: Id of AS
    """

    try:
        as_ = Asn.get_by_pk(id=as_id)
    except AsnNotFoundError as e:
        raise exceptions.AsnDoesNotExistException(str(e))

    return as_


def get_as_by_ids(autonomous_systems_ids):
    """Return AS list by ids.

    Args:
        as_ids: List of Ids of AS's.
    """

    as_ids = list()
    for as_id in autonomous_systems_ids:
        try:
            as_ = get_as_by_id(as_id).id
            as_ids.append(as_)
        except exceptions.AsnDoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except Exception as e:
            raise NetworkAPIException(str(e))

    as_s = Asn.objects.filter(id__in=as_ids)

    return as_s


def update_as(as_):
    """Update AS."""

    try:
        as_obj = get_as_by_id(as_.get('id'))
        as_obj.update_v4(as_)
    except AsnErrorV4 as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except exceptions.AsnDoesNotExistException as e:
        raise ObjectDoesNotExistException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return as_obj


def create_as(as_):
    """Create AS."""

    try:
        as_obj = Asn()
        as_obj.create_v4(as_)
    except AsnErrorV4 as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return as_obj


def delete_as(as_ids):
    """Delete AS."""

    for as_id in as_ids:
        try:
            as_obj = get_as_by_id(as_id)
            as_obj.delete_v4()
        except exceptions.AsnDoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except exceptions.AsnAssociatedToEquipmentError as e:
            raise ValidationAPIException(str(e))
        except AsnError as e:
            raise NetworkAPIException(str(e))
        except Exception as e:
            raise NetworkAPIException(str(e))


def get_as_equipment_by_search(search=dict()):
    """Return a list of ASEquipment's by dict."""

    try:
        as_equipment = AsnEquipment.get_by_pk()
        as_map = build_query_to_datatable_v3(as_equipment, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return as_map


def get_as_equipment_by_id(as_equipment_id=None):
    """Return an ASEquipment by id.

    Args:
        as_equipment_id: Id of ASEquipment

    """

    try:
        as_equipment_list = list()
        for asn in as_equipment_id:
            as_equipment = AsnEquipment.get_by_pk(ids=asn)
            as_equipment_list.append(as_equipment)
    except AsnNotFoundError as e:
        raise exceptions.AsnDoesNotExistException(str(e))

    return as_equipment_list


def get_as_equipment_by_asn(asn_id=None):
    """Return an ASEquipment by asn id.

    Args:
        asn_id: Id of ASN

    """

    try:
        as_equipment = list()
        for asn in asn_id:
            as_equipment += AsnEquipment.get_by_pk(asn=asn)

    except AsnNotFoundError as e:
        raise exceptions.AsnDoesNotExistException(str(e))

    return as_equipment


def get_as_equipment_by_equip(equipment_id=None):
    """Return an ASEquipment by equipment id.

    Args:
        equipment_id: Id of Equipment

    """

    try:
        as_equipment = list()
        for equip in equipment_id:
            as_equipment += AsnEquipment.get_by_pk(equipment=equip)

    except AsnNotFoundError as e:
        raise exceptions.AsnDoesNotExistException(str(e))

    return as_equipment


def create_asn_equipment(asn_equipment):
    """Create ASNEquipment."""

    try:
        asn_equipment_list = list()

        for equipment in asn_equipment.get("equipment"):
            obj = dict()
            obj["equipment"] = equipment
            obj["asn"] = asn_equipment.get("asn")
            as_obj = AsnEquipment()
            as_obj.create_v4(obj)
            asn_equipment_list.append({'id': as_obj.id})

    except AsnErrorV4 as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return asn_equipment_list


def delete_as_equipment(as_ids):
    """Delete ASNEquipment."""

    for as_id in as_ids:
        try:
            as_obj = get_as_equipment_by_id(as_id)[0]
            log.debug(as_obj)
            as_obj.delete_v4()
        except exceptions.AsnDoesNotExistException as e:
            raise ObjectDoesNotExistException(str(e))
        except exceptions.AsnAssociatedToEquipmentError as e:
            raise ValidationAPIException(str(e))
        except AsnError as e:
            raise NetworkAPIException(str(e))
        except Exception as e:
            raise NetworkAPIException(str(e))


def update_asn_equipment(as_):
    """Update AS."""

    try:
        as_obj = AsnEquipment()
        asn_equipment = as_obj.get_by_pk(ids=as_.get('id'))
        asn_equipment.update_v4(as_)
    except AsnErrorV4 as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except exceptions.AsnDoesNotExistException as e:
        raise ObjectDoesNotExistException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return as_obj


def update_asn_equipment_by_asn(asn_id, as_):
    """Update AS. Return new asn_equipments new ids"""

    try:
        as_obj = AsnEquipment()
        asn_equipment = as_obj.get_by_pk(asn=asn_id)
        log.debug(asn_equipment)
        log.debug(type(asn_equipment))
        for obj in asn_equipment:
            obj.delete_v4()

        asn_equipment_obj = create_asn_equipment(as_)

    except AsnErrorV4 as e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException as e:
        raise ValidationAPIException(str(e))
    except exceptions.AsnDoesNotExistException as e:
        raise ObjectDoesNotExistException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))

    return asn_equipment_obj

