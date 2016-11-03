# -*- coding: utf-8 -*-
from django.db.models import get_model

from networkapi.infrastructure.datatable import build_query_to_datatable_v3

######################
# Models's Instances #
######################
NetworkIPv4 = get_model('ip', 'NetworkIPv4')
NetworkIPv6 = get_model('ip', 'NetworkIPv6')


###############
# NetworkIPv4 #
###############
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


def create_networkipv4(networkv4, user):
    """Creates a NetworkIPv4."""

    netv4_obj = NetworkIPv4()

    netv4_obj.create_v3(networkv4)

    return netv4_obj


def update_networkipv4(networkv4, user):
    """Updates a NetworkIPv4."""
    netv4_obj = get_networkipv4_by_id(networkv4.get('id'))
    netv4_obj.update_v3(networkv4)

    return netv4_obj


def delete_networkipv4(network_ids, user):
    """Deletes a list of NetworkIPv4."""

    for network_id in network_ids:
        netv4_obj = get_networkipv4_by_id(network_id)

        netv4_obj.delete_v3()


###############
# NetworkIPv6 #
###############
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


def create_networkipv6(networkv6, user):
    """Creates a NetworkIPv6."""

    netv6_obj = NetworkIPv6()
    netv6_obj.create_v3(networkv6)

    return netv6_obj


def update_networkipv6(networkv6, user):
    """Updates a NetworkIPv6."""

    netv6_obj = NetworkIPv6()
    netv6_obj.update_v3(networkv6)

    return netv6_obj


def delete_networkipv6(network_ids, user):
    """Deletes a list of NetworkIPv6."""

    for network_id in network_ids:
        netv6_obj = get_networkipv6_by_id(network_id)

        netv6_obj.delete_v3()
