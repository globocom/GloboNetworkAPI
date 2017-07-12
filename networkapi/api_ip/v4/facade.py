# -*- coding: utf-8 -*-
import logging

from networkapi.api_ip.facade import get_ipv6_by_id
from django.core.exceptions import FieldError
from networkapi.api_ip.facade import get_ipv4_by_id

from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.ip.models import Ip
from networkapi.ip.models import IpCantBeRemovedFromVip
from networkapi.ip.models import IpError
from networkapi.ip.models import IpErrorV3
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import OperationalError

log = logging.getLogger(__name__)

def create_ipv4(ipv4, user):
    """Creates a Ipv4."""

    try:
        ipv4_obj = Ip()
        ipv4_obj.create_v4(ipv4)
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)
    except (IpError, IpErrorV3), e:
        raise ValidationAPIException(e.message)
    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))
    else:
        return ipv4_obj


def update_ipv4(ipv4, user):
    """Updates a Ipv4."""

    try:
        ipv4_obj = get_ipv4_by_id(ipv4.get('id'))
        ipv4_obj.update_v4(ipv4)
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)
    except (IpError, IpErrorV3), e:
        raise ValidationAPIException(e.message)
    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))
    else:
        return ipv4_obj


def delete_ipv4(ipv4_id):
    """Delete Ipv4."""

    try:
        ipv4_obj = get_ipv4_by_id(ipv4_id)
        ipv4_obj.delete_v4()
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)
    except IpCantBeRemovedFromVip, e:
        raise ValidationAPIException(e.message)
    except (IpError, IpErrorV3), e:
        raise ValidationAPIException(e.message)
    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))


def create_ipv6(ipv6, user):
    """Creates a Ipv6."""

    try:
        ipv6_obj = Ipv6()
        ipv6_obj.create_v4(ipv6)
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)
    except (IpError, IpErrorV3), e:
        raise ValidationAPIException(e.message)
    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))
    else:
        return ipv6_obj


def update_ipv6(ipv6, user):
    """Updates a Ipv6."""

    try:
        ipv6_obj = get_ipv6_by_id(ipv6.get('id'))
        ipv6_obj.update_v4(ipv6)
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.detail)
    except (IpError, IpErrorV3), e:
        raise ValidationAPIException(e.message)
    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))
    else:
        return ipv6_obj


def delete_ipv6(ipv6_id):
    """Delete Ipv6."""

    try:
        ipv6_obj = get_ipv6_by_id(ipv6_id)
        ipv6_obj.delete_v4()
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(e.message)
    except IpCantBeRemovedFromVip, e:
        raise ValidationAPIException(e.message)
    except (IpError, IpErrorV3), e:
        raise ValidationAPIException(e.message)
    except ValidationAPIException, e:
        raise ValidationAPIException(e.detail)
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))





