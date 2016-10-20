# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model

from networkapi.infrastructure.datatable import build_query_to_datatable_v3

Ip = get_model('ip', 'Ip')
Ipv6 = get_model('ip', 'Ipv6')

log = logging.getLogger(__name__)


def delete_ipv4_list(ipv4_list):
    """Delete Ipv4."""

    for ipv4 in ipv4_list:
        ip = Ip.objects.get(id=ipv4)
        ip.delete()


def delete_ipv6_list(ipv6_list):
    """Delete Ipv6."""

    for ipv6 in ipv6_list:
        ip = Ipv6.objects.get(id=ipv6)
        ip.delete()


def get_ipv4_by_id(ip_id):
    """Get Ipv4."""

    network = Ip.get_by_pk(ip_id)

    return network


def get_ipv4_by_ids(ip_ids):
    """Get Many Ipv4."""

    networks = list()
    for ip_id in ip_ids:
        networks.append(get_ipv4_by_id(ip_id))

    return networks


def get_ipv4_by_search(search=dict()):
    """Get List of Ipv4 by Search."""

    networks = Ip.objects.all()
    net_map = build_query_to_datatable_v3(networks, search)

    return net_map


def get_ipv6_by_id(ip_id):
    """Get Ipv6."""

    network = Ipv6.get_by_pk(ip_id)

    return network


def get_ipv6_by_ids(ip_ids):
    """Get Many Ipv6."""

    networks = list()
    for ip_id in ip_ids:
        networks.append(get_ipv6_by_id(ip_id))

    return networks


def get_ipv6_by_search(search=dict()):
    """Get List of Ipv6 by Search."""

    networks = Ipv6.objects.all()
    net_map = build_query_to_datatable_v3(networks, search)

    return net_map
