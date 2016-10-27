# -*- coding: utf-8 -*-
from django.db.models import get_model

from networkapi.infrastructure.datatable import build_query_to_datatable_v3

NetworkIPv4 = get_model('ip', 'NetworkIPv4')
NetworkIPv6 = get_model('ip', 'NetworkIPv6')


def get_networkipv4_by_id(network_id):
    """Get NetworkIPv4."""

    network = NetworkIPv4.get_by_pk(network_id)

    return network


def get_networkipv4_by_ids(network_ids):
    """Get Many NetworkIPv4."""

    networks = list()
    for network_id in network_ids:
        networks.append(get_networkipv4_by_id(network_id))

    return networks


def get_networkipv4_by_search(search=dict()):
    """Get List of NetworkIPv4 by Search."""

    networks = NetworkIPv4.objects.all()
    net_map = build_query_to_datatable_v3(networks, search)

    return net_map


def get_networkipv6_by_id(network_id):
    """Get NetworkIPv6."""

    network = NetworkIPv6.get_by_pk(network_id)

    return network


def get_networkipv6_by_ids(network_ids):
    """Get Many NetworkIPv6."""

    networks = list()
    for network_id in network_ids:
        networks.append(get_networkipv6_by_id(network_id))

    return networks


def get_networkipv6_by_search(search=dict()):
    """Get List of NetworkIPv6 by Search."""

    networks = NetworkIPv6.objects.all()
    net_map = build_query_to_datatable_v3(networks, search)

    return net_map


def create_networkipv4(networkv4, user):

    netv4_obj = NetworkIPv4()

    netv4_obj.create_v3(networkv4)

    return netv4_obj
