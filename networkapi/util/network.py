# -*- coding: utf-8 -*-
import logging

from django.db.models.query_utils import Q

from networkapi.api_network.exceptions import NetworkConflictException
from networkapi.infrastructure.ipaddr import IPNetwork
from networkapi.util.geral import get_app

log = logging.getLogger(__name__)


def get_free_space_network(free_nets, used_nets):
    """Return list of free subnets."""

    for excluded_net in used_nets:
        temp_net_list = list(free_nets)
        free_nets = []
        while temp_net_list:
            temp_net = temp_net_list.pop()
            used_nets = []
            try:
                used_nets = list(temp_net.address_exclude(excluded_net))
            except ValueError:
                used_nets = [temp_net]
                pass
            free_nets.extend(used_nets)

    free_nets.sort()

    return free_nets


def verify_networks(subnets, supernets):
    """Verify a list of networks has make intersect with a second list and
    contrariwise.
    """

    msg = 'One of the equipment associated with the environment ' \
        'of this Vlan is also associated with other environment ' \
        'that has a network with the same track, add filters in ' \
        'environments if necessary. Your Network: {}, Network ' \
        'already created: {}'

    subnet, supernet = verify_intersect(supernets, subnets)
    if subnet or supernet:
        raise NetworkConflictException(msg.format(subnet, supernet))

    subnet, supernet = verify_intersect(subnets, supernets)
    if subnet or supernet:
        raise NetworkConflictException(msg.format(supernet, subnet))


def verify_intersect(supernets, subnets):
    """Verify if a item of a list of networks has make intersect with a
    second list.
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


def validate_vlan_conflict(equips, num_vlan, exclude=None):
    """Verify if num vlan make conflict in environment or environment related.
    """

    models = get_app('vlan', 'models')

    # get vlans with same num_vlan
    vlans = models.Vlan.objects.filter(
        ambiente__equipamentoambiente__equipamento__in=equips,
        num_vlan=num_vlan
    )

    if exclude:
        vlans = vlans.exclude(
            id=exclude
        )

    if vlans:
        ids_env = [vlan.ambiente.name for vlan in vlans]
        msg = 'There is a registered VLAN with the number in ' \
            'equipments of environments: {}'.format(ids_env)
        log.error(msg)
        raise models.VlanErrorV3(msg)


def validate_conflict_join_envs(env_ip, equipments):

    models_env = get_app('ambiente', 'models')
    models_vrf = get_app('api_vrf', 'models')

    nums_vlan_rel_ip = [vlan.num_vlan for vlan in env_ip.vlans]

    for equipment in equipments:

        # Equipment without environment related, do not need validate
        # Validate if equipment is not in related in environment
        if equipment.id not in list(env_ip.eqpts):

            # Validate if equipment has environments related
            for env_rel in equipment.environments:
                env_rel_eqpt = env_rel.ambiente

                use_filter = True
                if env_rel_eqpt.filter != env_ip.filter:
                    use_filter = False

                # Exists differents filters, so is need to validate
                # all equipments
                eqpts = env_rel_eqpt.filtered_eqpts \
                    if use_filter else env_rel_eqpt.eqpts

                eqpts_env_ip = env_ip.filtered_eqpts \
                    if use_filter else env_ip.eqpts

                # Verify if vlans of environment of IP make conflict in
                # new relationship
                nums_vlan_rel_eqpt = [vlan.num_vlan
                                      for vlan in env_rel_eqpt.vlans]
                vlans_conflict = list(
                    set(nums_vlan_rel_eqpt) & set(nums_vlan_rel_ip))
                if vlans_conflict:
                    msg = 'VLANs {} already registred with same ' \
                        'number in equipments of environment: {}'
                    msg = msg.format(vlans_conflict, env_rel_eqpt.name)
                    log.error(msg)
                    raise models_env.IpErrorV3(msg)

                # Verify if networks of environment of IP make conflict in new
                # relationship
                for vlan_rel_ip in env_ip.vlans:
                    # Get vrfs of 1 vlan of environment of IP
                    vrfs_vlan_rel_ip = models_vrf.Vrf.objects.filter(Q(
                        Q(vrfvlanequipment__equipment__in=eqpts) &
                        Q(vrfvlanequipment__vlan__id=vlan_rel_ip.id)) |
                        Q(id=vlan_rel_ip.ambiente.default_vrf_id)
                    )

                    # Get vrfs of 1 vlan of environment related with
                    # equipment
                    for vlan_rel_eqpt in env_rel_eqpt.vlans:
                        vrfs_vlan_rel_eqpt = models_vrf.Vrf.objects.filter(Q(
                            Q(vrfvlanequipment__equipment__in=eqpts_env_ip) &
                            Q(vrfvlanequipment__vlan__id=vlan_rel_eqpt.id)) |
                            Q(id=vlan_rel_eqpt.ambiente.default_vrf_id)
                        )

                        # Validate conflict of network if has intersect
                        # of vrfs
                        vrfs_intersect = list(
                            set(vrfs_vlan_rel_ip) & set(vrfs_vlan_rel_eqpt))

                        if vrfs_intersect:

                            netv4 = vrfs_vlan_rel_eqpt\
                                .networkipv4_set.filter()
                            netv6 = vrfs_vlan_rel_eqpt\
                                .networkipv6_set.filter()
                            netv4_eqpt = [IPNetwork(net.networkv4)
                                          for net in netv4]
                            netv6_eqpt = [IPNetwork(net.networkv6)
                                          for net in netv6]

                            netv4 = vrfs_vlan_rel_ip.networkipv4_set.filter()
                            netv6 = vrfs_vlan_rel_ip.networkipv6_set.filter()
                            netv4_ip = [IPNetwork(net.networkv4)
                                        for net in netv4]
                            netv6_ip = [IPNetwork(net.networkv6)
                                        for net in netv6]

                            verify_networks(netv4_ip, netv4_eqpt)
                            verify_networks(netv6_ip, netv6_eqpt)
                            # get nets de cada vlan e valida conflito


def get_networks_related(vrfs, eqpts, has_netv4=True,
                         has_netv6=True, exclude=None):

    models = get_app('vlan', 'models')

    vlans_env_eqpt = models.Vlan.objects.filter(
        # get vlans of environment or environment assoc
        ambiente__equipamentoambiente__equipamento__in=eqpts
    ).filter(
        # get vlans with customized vrfs
        Q(vrfvlanequipment__vrf__in=vrfs) |
        # get vlans using vrf of environment
        Q(ambiente__default_vrf__in=vrfs)
    ).distinct()

    if exclude:
        vlans_env_eqpt = vlans_env_eqpt.exclude(
            # exclude current vlan
            id=exclude
        )

    vlans_env_eqpt = vlans_env_eqpt.distinct()

    netv4 = list()
    if has_netv4:
        netv4 = reduce(list.__add__, [
            list(vlan_env.networkipv4_set.all())
            for vlan_env in vlans_env_eqpt if vlan_env.networkipv4_set.all()], [])

    netv6 = list()
    if has_netv6:
        netv6 = reduce(list.__add__, [
            list(vlan_env.networkipv6_set.all())
            for vlan_env in vlans_env_eqpt if vlan_env.networkipv6_set.all()], [])

    return netv4, netv6


def validate_network(envs, net_ip, version):
    """Verify if network make conflict in environment or environment related.
    """

    models = get_app('ambiente', 'models')
    cidr = models.EnvCIDR()

    # Filter network_ipv4 where environment has config permiting to insert
    # current network.
    nets_envs = list()
    for env in envs:
        # get configs v4 of environment
        nts = [IPNetwork(config.network)
               for config in cidr.get(env_id=env.id).filter(ip_version=version)]

        # get networks that can be intersect with current network
        if verify_intersect(nts, net_ip)[0]:

            log.info('Environment %s has config(%s) permiting to insert '
                     'in this network %s' % (env.name, nts, net_ip))

            if version == models.IP_VERSION.IPv4[0]:
                for vlan in env.vlans:
                    for network_ipv4 in vlan.networks_ipv4:
                        nets_envs.append(IPNetwork(network_ipv4.networkv4))
            else:
                for vlan in env.vlans:
                    for network_ipv6 in vlan.networks_ipv6:
                        nets_envs.append(IPNetwork(network_ipv6.networkv6))

    if nets_envs:
        verify_networks(net_ip, nets_envs)
