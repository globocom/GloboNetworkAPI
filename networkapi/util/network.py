# -*- coding: utf-8 -*-
import logging

from django.db.models import get_model

from networkapi.infrastructure.ipaddr import IPNetwork

log = logging.getLogger(__name__)


def verify_networks(subnets, supernets):
    """
        Verify a list of networks has make intersect with a second list
        and contrariwise.
    """

    subnet, supernet = verify_intersect(supernets, subnets)
    if subnet or supernet:
        raise Exception(
            'One of the equipment associated with the environment '
            'of this Vlan is also associated with other environment '
            'that has a network with the same track, add filters in '
            'environments if necessary. Your Network: %s, Network'
            'already created: %s' % (subnet, supernet))

    subnet, supernet = verify_intersect(subnets, supernets)
    if subnet or supernet:
        raise Exception(
            'One of the equipment associated with the environment '
            'of this Vlan is also associated with other environment '
            'that has a network with the same track, add filters in '
            'environments if necessary. Your Network: %s, Network'
            'already created: %s' % (supernet, subnet))


def verify_intersect(supernets, subnets):
    """
        Verify if a item of a list of networks has make intersect
        with a second list.
    """

    for supernet in supernets:
        try:
            # has subnet is inside of supernet
            for subnet in subnets:
                if subnet in supernet:
                    log.debug(
                        'Subnet %s is inside of supernet: %s' %
                        (subnet, supernet))
                    return subnet, supernet
        except:
            pass

    return None, None


def validate_network(envs, net_ip, version):
    """
    Verify if network make conflict in environment or environment related.
    """
    ip_version = get_model('ambiente', 'IP_VERSION')

    # Filter network_ipv4 where environment has config permiting to insert
    # current network.
    nets_envs = list()
    for env in envs:
        # get configs v4 of environment
        nts = [IPNetwork(config.ip_config.subnet)
               for config in env.configs.filter(ip_config__type=version)]

        # get networks that can be intersect with current network
        if verify_intersect(nts, net_ip)[0]:

            log.info('Environment %s has config(%s) permiting to insert '
                     'in this network %s' % (env.name, nts, net_ip))

            if version == ip_version.IPv4[0]:
                for vlan in env.vlans:
                    for network_ipv4 in vlan.networks_ipv4:
                        nets_envs.append(IPNetwork(network_ipv4.networkv4))
            else:
                for vlan in env.vlans:
                    for network_ipv6 in vlan.networks_ipv6:
                        nets_envs.append(IPNetwork(network_ipv6.networkv6))

    if nets_envs:
        subnet, supernet = verify_intersect(nets_envs, net_ip)
        if subnet or supernet:
            raise Exception(
                'One of the equipment associated with the environment '
                'of this Vlan is also associated with other environment '
                'that has a network with the same track, add filters in '
                'environments if necessary. Your Network: %s, Network'
                'already created: %s' % (subnet, supernet))

        subnet, supernet = verify_intersect(net_ip, nets_envs)
        if subnet or supernet:
            raise Exception(
                'One of the equipment associated with the environment '
                'of this Vlan is also associated with other environment '
                'that has a network with the same track, add filters in '
                'environments if necessary. Your Network: %s, Network'
                'already created: %s' % (supernet, subnet))
