# Copyright (c) 2014, Brocade Communications Systems, Inc.
#
# All rights reserved.
#
# This software is licensed under the following BSD-license,
# you may not use this file unless in compliance with the
# license below:
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above
#    copyright notice, this list of conditions and the
#    following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

from xml.etree import ElementTree
from xml.etree.ElementTree import Element


# XML element and attribute tags
VLAN_TAG = "Vlan"
NAME_TAG = "name"
PORT_CHANNEL_TAG = "Port-channel"
SWITCHPORT_TAG = "switchport"
SWITCHPORT_BASIC_TAG = "switchport-basic"
BASIC_TAG = "basic"
MODE_TAG = "mode"
VLAN_MODE_TAG = "vlan-mode"
ALLOWED_TAG = "allowed"
VLAN_TAG2 = "vlan"
ADD_TAG = "add"
REMOVE_TAG = "remove"
ACCESSVLAN_TAG = "accessvlan"
SHUTDOWN_TAG = "shutdown"

VLAN_MODE_ACCESS = "access"
VLAN_MODE_TRUNK = "trunk"

# channel group elements
CHANNEL_GROUP_TAG = "channel-group"
PORT_INT_TAG = "port-int"
TYPE_TAG = "type"

# VCS element and attribute tags:

VCS_NODE_INFO = "vcs-node-info"
NODE_PUBLIC_IP_ADDRESS = "node-public-ip-address"

# VRRP Config Tags:

VRRP_GROUP = "vrrp-group"
VRRP_GROUP_EXTENDED = "vrrp-extended-group"
VIRTUAL_IP_TAG = "virtual-ip"
VIRTUAL_IPADDRESS_TAG = "virtual-ipaddr"
VRID_TAG = "vrid"
VERSION_TAG = "version"
ADDRESS = "address"
PREEMPT_MODE_TAG = "preempt-mode"
INTERFACE = "interface"
PRIORITY = "priority"
TRACK = "track"
INTERFACE_TYPE_TAG = "interface-type"
INTERFACE_NAME_TAG = "interface-name"
SHORT_PATH_FORWARDING_TAG = "short-path-forwarding"

# VRF config tags
VRF_TAG = "vrf"
VRF_NAME_TAG = "vrf-name"
IP_TAG = "ip"
ROUTER_ID_TAG = "router-id"
FORWARDING_TAG = "forwarding"
RD_TAG = "rd"
ADDRESS_FAMILY_TAG = "address-family"
UNICAST_TAG = "unicast"
ROUTE_TAG = "route"
IMPORT_TAG = "import"


def create_vlan_payload(name):
    '''Returns xml string bytes for vlan_orig playload
       Example return string: b'<Vlan><name>{name}</name></Vlan>'
       Where {name} is name of the Vlan
    '''
    assert name != None or name != '', "None or Empty name is not allowed for VLAN"

    vlan = Element(VLAN_TAG)
    name_element = ElementTree.SubElement(vlan, NAME_TAG)
    name_element.text = name
    return ElementTree.tostring(vlan)


def create_port_channel_payload(name):
    '''Returns xml byte string for port channel payload
       Example return string:
       b'<Port-channel><name>{name}</name></Port-channel>'
       Where {name} is name of the port channel
    '''
    assert name != None or name != '', \
        "None or Empty name is not allowed for Port-Channel"
    po = Element(PORT_CHANNEL_TAG)
    name_element = ElementTree.SubElement(po, NAME_TAG)
    name_element.text = name
    return ElementTree.tostring(po)


def interface_switchport_payload(interface_type):
    '''
    '''
    payload = Element(interface_type)
    _add_switchport_basic(payload)
    return ElementTree.tostring(payload)


def interface_vlan_mode_payload(interface_type, mode):
    '''
    '''
    payload = Element(interface_type)
    _add_switchport_basic(payload)
    switchport_elem = _switch_port_elem(mode)
    payload.append(switchport_elem)

    return ElementTree.tostring(payload)


def interface_allowed_vlan_payload(interface_type, mode, vlan):
    payload = Element(interface_type)
    _add_switchport_basic(payload)
    switchport_elem = _switch_port_elem(mode, vlan)
    payload.append(switchport_elem)

    return ElementTree.tostring(payload)


def interface_trunk_remove_vlan_payload(vlan_id):
    TEMPLATE = """
                <allowed>
                    <vlan>
                        <remove>{vlan_id}</remove>
                    </vlan>
                </allowed>"""
    payload = TEMPLATE.format(vlan_id=vlan_id).encode()
    return payload


def _switch_port_elem(mode, vlan=None, action=ADD_TAG):
    switchport_elem = Element(SWITCHPORT_TAG)
    mode_elem = ElementTree.SubElement(switchport_elem, MODE_TAG)
    vlan_mode = ElementTree.SubElement(mode_elem, VLAN_MODE_TAG)
    vlan_mode.text = mode
    if vlan is not None:
        if mode == "trunk":
            mode_elem = ElementTree.SubElement(switchport_elem, mode)
            allowed_elem = ElementTree.SubElement(mode_elem, ALLOWED_TAG)
            vlan_elem = ElementTree.SubElement(allowed_elem, VLAN_TAG2)
            if action == "add":
                elem = ElementTree.SubElement(vlan_elem, ADD_TAG)
                elem.text = vlan
            elif action == "remove":
                elem = ElementTree.SubElement(vlan_elem, REMOVE_TAG)
                elem.text = vlan
        elif mode == "access":
            access_elem = ElementTree.SubElement(switchport_elem, mode)
            vlan_elem = ElementTree.SubElement(access_elem, ACCESSVLAN_TAG)
            vlan_elem.text = vlan
    return switchport_elem


def interface_channel_group_payload(interface_type, name, mode, po_type):
    payload = Element(interface_type)
    channel_group = ElementTree.SubElement(payload, CHANNEL_GROUP_TAG)
    port_int = ElementTree.SubElement(channel_group, PORT_INT_TAG)
    port_int.text = name
    mode_elem = ElementTree.SubElement(channel_group, MODE_TAG)
    mode_elem.text = mode
    type_elem = ElementTree.SubElement(channel_group, TYPE_TAG)
    type_elem.text = po_type

    return ElementTree.tostring(payload)


def _add_switchport_basic(interface_elem):
    switchport_basic = ElementTree.SubElement(interface_elem,
                                              SWITCHPORT_BASIC_TAG)
    ElementTree.SubElement(switchport_basic, BASIC_TAG)


def interface_shutdown_payload(interface_type):
    ''' build interface shutdown payload
    '''
    payload = Element(interface_type.lower())
    ElementTree.SubElement(payload, SHUTDOWN_TAG)
    return ElementTree.tostring(payload)


def vrrp_grp_config_payload(group_id, protocol):
    if protocol == "vrrp-extended":
        grp_tag = VRRP_GROUP_EXTENDED
    else:
        grp_tag = VRRP_GROUP
    vrrp_group = Element(grp_tag)
    vrid_element = ElementTree.SubElement(vrrp_group, VRID_TAG)
    vrid_element.text = str(group_id)
    if protocol == "vrrp":
        version_element = ElementTree.SubElement(vrrp_group, VERSION_TAG)
        version_element.text = "2"
    else:
        pass
    return ElementTree.tostring(vrrp_group)


def vrrp_interface_ip_config_payload(interface_ip, interface_ip_mask):
    vrrp_interface_ip = Element(ADDRESS)
    interface_ipaddr_elmnt = ElementTree.SubElement(vrrp_interface_ip, ADDRESS)
    interface_ipaddr_elmnt.text = interface_ip + "/" + str(interface_ip_mask)
    return ElementTree.tostring(vrrp_interface_ip)


def vrrp_virtual_ip_config_payload(virtual_ip):
    vrrp_virtual_ip = Element(VIRTUAL_IP_TAG)
    virtual_ipaddr = ElementTree.SubElement(vrrp_virtual_ip,
                                            VIRTUAL_IPADDRESS_TAG)
    virtual_ipaddr.text = virtual_ip
    return ElementTree.tostring(vrrp_virtual_ip)


def vrrp_protocol_enable(protocol, enable):
    protocol_element = Element(protocol)
    protocol_element.text = enable
    return ElementTree.tostring(protocol_element)


def vrrp_priority_payload(new_priority):
    interface_element = Element(INTERFACE)
    priority_element = ElementTree.SubElement(interface_element, PRIORITY)
    priority_element.text = new_priority
    return ElementTree.tostring(interface_element)


def vrrp_track_payload(interface_link, new_priority):
    # <track> <interface> <interface-type>tengigabitethernet</interface-type>
    # <interface-name>134/0/6</interface-name> <priority>60</priority>
    # </interface> </track>

    interface_details = str(interface_link).split(sep=" ")
    interface_type = interface_details[0]
    interface_name = interface_details[1]

    track_element = Element(TRACK)
    interface_element = ElementTree.SubElement(track_element, INTERFACE)
    interface_type_ele = ElementTree.SubElement(interface_element,
                                                INTERFACE_TYPE_TAG)
    interface_type_ele.text = interface_type.lower()
    interface_name_ele = ElementTree.SubElement(interface_element,
                                                INTERFACE_NAME_TAG)
    interface_name_ele.text = interface_name
    priority_element = ElementTree.SubElement(interface_element, PRIORITY)
    priority_element.text = new_priority
    return ElementTree.tostring(track_element)


def vrrp_shortpath_fwd_payload():
    vrrp_group = Element(VRRP_GROUP_EXTENDED)
    fwd_element = ElementTree.SubElement(vrrp_group, SHORT_PATH_FORWARDING_TAG)
    basic_element = ElementTree.SubElement(fwd_element, BASIC_TAG)
    basic_element.text = "true"
    return ElementTree.tostring(vrrp_group)


def create_vrf_payload(vrf_name, rd):
    vrf_element = Element(VRF_TAG)
    name_element = ElementTree.SubElement(vrf_element, VRF_NAME_TAG)
    name_element.text = vrf_name
    rd_element = ElementTree.SubElement(vrf_element, RD_TAG)
    rd_element.text = rd
    return ElementTree.tostring(vrf_element)


def add_vrf_address_family_payload(vrf_name, address_family):
    vrf_element = Element(VRF_TAG)
    name_element = ElementTree.SubElement(vrf_element, VRF_NAME_TAG)
    name_element.text = vrf_name
    address_family_element = ElementTree.SubElement(vrf_element,
                                                    ADDRESS_FAMILY_TAG)
    addr_family_ipvx_element = ElementTree.SubElement(
        address_family_element, address_family)
    ElementTree.SubElement(addr_family_ipvx_element, UNICAST_TAG)
    return ElementTree.tostring(vrf_element)


def create_vrf_router_id_payload(vrf_name, ipaddress):
    vrf_element = Element(VRF_TAG)
    name_element = ElementTree.SubElement(vrf_element, VRF_NAME_TAG)
    name_element.text = vrf_name
    ip_element = ElementTree.SubElement(vrf_element, IP_TAG)
    router_id_element = ElementTree.SubElement(ip_element, ROUTER_ID_TAG)
    router_id_element.text = ipaddress
    return ElementTree.tostring(vrf_element)


def create_vrf_forwarding_payload(vrf_name):
    vrf_element = Element(VRF_TAG)
    fwding_element = ElementTree.SubElement(vrf_element, FORWARDING_TAG)
    fwding_element.text = vrf_name
    return ElementTree.tostring(vrf_element)

if __name__ == '__main__':
    forwarding = create_vrf_forwarding_payload("vrf-test")
    print(forwarding)

    '''
    po = create_port_channel_payload("200")
    print(po)

    payload = interface_switchport_payload("tengigabitethernet")
    print(payload)
    payload = interface_vlan_mode_payload("tengigabitethernet",
                                          "trunk")
    print(payload)
    #payload = interface_vlan_mode_payload("port-channel", "access")
    #print(payload)
    payload = interface_allowed_vlan_payload("tengigabitethernet",
                                             "trunk", "500")
    print(payload)
    payload = interface_allowed_vlan_payload("tengigabitethernet",
                                             "access", "500")
    print(payload)
    payload = interface_channel_group_payload("tengigabitethernet",
                                              "300", "passive", "standard")
    print(payload)
    payload = interface_shutdown_payload("tengigabitethernet")
    '''
