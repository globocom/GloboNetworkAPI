# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import logging

from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.ip.models import Ip
from networkapi.ip.models import IpError
from networkapi.ip.models import IpErrorV3
from networkapi.ip.models import IpNotFoundError
from networkapi.ip.models import Ipv6
from networkapi.ip.models import OperationalError

log = logging.getLogger(__name__)


def get_ipv4_by_search(search=dict()):
    """Get List of Ipv4 by Search."""

    networks = Ip.objects.all()
    net_map = build_query_to_datatable_v3(networks, search)

    return net_map


def get_ipv4_by_id(ip_id):
    """Get Ipv4."""

    try:
        network = Ip.get_by_pk(ip_id)
    except IpNotFoundError, e:
        raise ObjectDoesNotExistException(str(e))
    except (Exception, OperationalError), e:
        raise NetworkAPIException(str(e))
    else:
        return network


def get_ipv4_by_ids(ip_ids):
    """Get Many Ipv4."""

    ipv4_ids = list()
    for ip_id in ip_ids:
        ipv4_ids.append(get_ipv4_by_id(ip_id).id)

    ipv4s = Ip.objects.filter(id__in=ipv4_ids)

    return ipv4s


def create_ipv4(ipv4, user):
    """Creates a Ipv4."""

    try:
        ipv4_obj = Ip()
        ipv4_obj.create_v3(ipv4)
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except (IpError, IpErrorV3, ValidationAPIException), e:
        raise ValidationAPIException(str(e))
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))
    else:
        return ipv4_obj


def update_ipv4(ipv4, user):
    """Updates a Ipv4."""

    try:
        ipv4_obj = get_ipv4_by_id(ipv4.get('id'))
        ipv4_obj.update_v3(ipv4)
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except (IpError, IpErrorV3, ValidationAPIException), e:
        raise ValidationAPIException(str(e))
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))
    else:
        return ipv4_obj


def delete_ipv4_list(ipv4_list):
    """Delete Ipv4."""

    try:
        for ipv4 in ipv4_list:
            ipv4_obj = get_ipv4_by_id(ipv4)
            ipv4_obj.delete_v3()
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except (IpError, IpErrorV3, ValidationAPIException), e:
        raise ValidationAPIException(str(e))
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))


def create_ipv6(ipv6, user):
    """Creates a Ipv6."""

    try:
        ipv6_obj = Ipv6()
        ipv6_obj.create_v3(ipv6)
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except (IpError, IpErrorV3, ValidationAPIException), e:
        raise ValidationAPIException(str(e))
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))
    else:
        return ipv6_obj


def update_ipv6(ipv6, user):
    """Updates a Ipv6."""

    try:
        ipv6_obj = get_ipv6_by_id(ipv6.get('id'))
        ipv6_obj.update_v3(ipv6)
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except (IpError, IpErrorV3, ValidationAPIException), e:
        raise ValidationAPIException(str(e))
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))
    else:
        return ipv6_obj


def delete_ipv6_list(ipv6_list):
    """Delete Ipv6."""

    try:
        for ipv6 in ipv6_list:
            ipv6_obj = get_ipv6_by_id(ipv6)
            ipv6_obj.delete_v3()
    except ObjectDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except (IpError, IpErrorV3, ValidationAPIException), e:
        raise ValidationAPIException(str(e))
    except (Exception, NetworkAPIException), e:
        raise NetworkAPIException(str(e))


def get_ipv6_by_id(ip_id):
    """Get Ipv6."""

    try:
        network = Ipv6.get_by_pk(ip_id)
    except IpNotFoundError, e:
        raise ObjectDoesNotExistException(str(e))
    except (Exception, OperationalError), e:
        raise NetworkAPIException(str(e))
    else:
        return network


def get_ipv6_by_ids(ip_ids):
    """Get Many Ipv4."""

    ipv6_ids = list()
    for ip_id in ip_ids:
        ipv6_ids.append(get_ipv6_by_id(ip_id).id)

    ipv6s = Ipv6.objects.filter(id__in=ipv6_ids)

    return ipv6s


def get_ipv6_by_search(search=dict()):
    """Get List of Ipv6 by Search."""

    networks = Ipv6.objects.all()
    net_map = build_query_to_datatable_v3(networks, search)

    return net_map
