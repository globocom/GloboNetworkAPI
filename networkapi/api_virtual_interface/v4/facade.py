# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError

from networkapi.api_virtual_interface.models import VirtualInterface
from networkapi.api_virtual_interface.v4 import exceptions
from networkapi.api_virtual_interface.v4.exceptions import VirtualInterfaceErrorV4
from networkapi.api_virtual_interface.v4.exceptions import VirtualInterfaceNotFoundError
from networkapi.api_virtual_interface.v4.exceptions import  VirtualInterfaceError
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3

log = logging.getLogger(__name__)


def get_virtual_interface_by_search(search=dict()):
    """Return a list of Virtual Interface's by dict."""

    try:
        virtual_interfaces = VirtualInterface.objects.filter()
        virtual_interface_map = build_query_to_datatable_v3(virtual_interfaces,
                                                            search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return virtual_interface_map


def get_virtual_interface_by_id(virtual_interface_id):
    """Return an Virtual Interface by id.

    Args:
        virtual_interface_id: Id of Virtual Interface
    """

    try:
        virtual_interface_ = VirtualInterface.get_by_pk(id=virtual_interface_id)
    except VirtualInterfaceNotFoundError, e:
        raise exceptions.VirtualInterfaceDoesNotExistException(str(e))

    return virtual_interface_


def get_virtual_interface_by_ids(virtual_interface_ids):
    """Return Virtual Interface list by ids.

    Args:
        virtual_interface_ids: List of Ids of Virtual Interfaces.
    """

    vi_ids = list()
    for vi_id in virtual_interface_ids:
        try:
            virtual_interface_ = get_virtual_interface_by_id(vi_id).id
            vi_ids.append(virtual_interface_)
        except exceptions.VirtualInterfaceDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

    virtual_interfaces = VirtualInterface.objects.filter(id__in=vi_ids)

    return virtual_interfaces


def update_virtual_interface(vi_):
    """Update Virtual Interface."""

    try:
        vi_obj = get_virtual_interface_by_id(vi_.get('id'))
        vi_obj.update_v4(vi_)
    except VirtualInterfaceErrorV4, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.VirtualInterfaceDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return vi_obj


def create_virtual_interface(vi_):
    """Create Virtual Interface."""

    try:
        vi_obj = VirtualInterface()
        vi_obj.create_v4(vi_)
    except VirtualInterfaceErrorV4, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return vi_obj


def delete_virtual_interface(vi_ids):
    """Delete Virtual Interface."""

    for vi_id in vi_ids:
        try:
            vi_obj = get_virtual_interface_by_id(vi_id)
            vi_obj.delete_v4()
        except exceptions.VirtualInterfaceDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        # except exceptions.AsAssociatedToEquipmentError, e:
        #     raise ValidationAPIException(str(e))
        except VirtualInterfaceError, e:
            raise NetworkAPIException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

