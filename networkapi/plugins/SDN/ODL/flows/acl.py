# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from networkapi.plugins.SDN.ODL.utils.cookie_handler import CookieHandler
from networkapi.plugins.SDN.ODL.utils.tcp_control_bits import TCPControlBits
from networkapi.plugins.SDN.ODL.utils.odl_plugin_masks import ODLPluginMasks

import re
import logging
from json import dumps
from copy import deepcopy

to_str_id = ODLPluginMasks.to_str_id
to_str_id_both = ODLPluginMasks.to_str_id_both
to_str_description = ODLPluginMasks.to_str_description
to_str_description_both = ODLPluginMasks.to_str_description_both


class Tokens(object):
    """ Class that holds all key words from the source json that identifies
    a valid ACL to be translated to a OpenDayLight json format
    """

    kind = "kind"
    rules = "rules"

    id_ = "id"
    action = "action"
    description = "description"
    source = "source"
    destination = "destination"
    protocol = "protocol"
    l4_options = "l4-options"
    src_port_op = "src-port-op"
    src_port = "src-port-start"
    src_port_end = "src-port-end"
    dst_port_op = "dest-port-op"
    dst_port = "dest-port-start"
    dst_port_end = "dest-port-end"
    icmp_options = "icmp-options"
    icmp_code = "icmp-code"
    icmp_type = "icmp-type"
    flags = "flags"
    priority = "priority"
    cookie = "cookie"
    sequence = "sequence"
    range = "range"
    eq = "eq"

class AclFlowBuilder(object):
    """ Class responsible for build json data for Access control list flow at
    OpenDayLight controller
    """

    LOG_FORMAT = '%(levelname)s:%(message)s'

    MALFORMED_MESSAGE = "Error building ACL Json. Malformed input data: \n%s"

    PRIORITY_DEFAULT = 65000
    TABLE = 0
    ALLOWED_FLOWS_SIZE = 5

    def __init__(self, data):

        self.raw_data = data  # Original data
        self.flows = {"flow": []}  # Processed data

        self.dumped_rule = None # Actual processing rule in json format

        self._reset_control_members()

        logging.basicConfig(format=self.LOG_FORMAT, level=logging.DEBUG)

    def _reset_control_members(self):

        # Used to build double ranges
        self.current_src_port = None
        self.current_dst_port = None

        # Used to build simple ranges
        self.current_src_or_dst_port = None

        # Used to control flows generation for one rule
        self.generated_all_flows_from_rule = False

    def _clear_flows(self):
        """ Clear flows variable to avoid huge object in memory """
        self.flows["flow"] = []

    def dump(self):
        """ Returns a json of built flows """

        if not isinstance(self.flows, dict):
            raise TypeError("self.flows must be a dictionary")

        flows_set = self.build()

        for flows in flows_set:
            flows_ids = [flow["id"] for flow in flows["flow"]]
            yield flows_ids, dumps(flows)

    def build(self):
        """ Verifies input data and build flows for OpenDayLight controller """

        if Tokens.kind in self.raw_data and Tokens.rules in self.raw_data:
            logging.info("Building ACL Json: %s", self.raw_data["kind"])

            for rule in self.raw_data[Tokens.rules]:

                for current_flows in self._build_rule(rule):

                    if len(current_flows["flow"]) == self.ALLOWED_FLOWS_SIZE:

                        yield current_flows
                        self._clear_flows()

            if len(self.flows["flow"]) > 0:
                yield self.flows
                self._clear_flows()

        else:
            message = "Missing %s or %s fields." % (Tokens.kind, Tokens.rules)
            logging.error(self.MALFORMED_MESSAGE % message)
            raise ValueError(self.MALFORMED_MESSAGE % message)

    def _build_rule(self, rule):
        """ Builds one or more flows based at one ACL rule """

        self.dumped_rule = dumps(rule, sort_keys=True)

        self._reset_control_members()

        while not self.generated_all_flows_from_rule:

            # Assigns the id of the current ACL
            # We always insert in the head of the list to simplify the access
            # to the current index

            self.flows["flow"].insert(0, {Tokens.id_: rule[Tokens.id_]})

            # Flow table and priority
            self.flows["flow"][0]["table_id"] = self.TABLE

            self._build_description(rule)
            self._build_match(rule)
            self._build_action(rule)
            self._build_cookie(rule)
            self._build_sequence(rule)
            self._build_protocol(rule)

            yield self.flows

    def _build_description(self, rule):
        """ Builds the flow name field using OpenDayLight json format """

        if Tokens.description not in rule:
            rule[Tokens.description] = ""

        self.flows["flow"][0]["flow-name"] = rule[Tokens.description]

    def _build_match(self, rule):
        """ Builds the match field that identifies the ACL rule """

        self.flows["flow"][0]["match"] = {
            "ethernet-match": {
                "ethernet-type": {
                    "type": 2048
                }
            }
        }

        if Tokens.destination in rule and Tokens.source in rule:

            self.flows["flow"][0]["match"]["ipv4-destination"] = \
                rule[Tokens.destination]
            self.flows["flow"][0]["match"]["ipv4-source"] = rule[Tokens.source]

        else:
            logging.error(self.MALFORMED_MESSAGE % self.dumped_rule)
            raise ValueError(self.MALFORMED_MESSAGE % self.dumped_rule)

    def _build_action(self, rule):
        """ Builds the Openflow actions to a flow """

        if Tokens.action in rule and rule[Tokens.action] == "permit":
            self.flows["flow"][0]["instructions"] = {
                "instruction": [{
                    "order": 0,
                    "apply-actions": {
                        "action": [{
                            "order": 0,
                            "output-action": {
                                "output-node-connector": "NORMAL"
                            }
                        }]
                    }
                }]
            }

    def _build_cookie(self, rule):
        """ Builds optional 64-bits field named cookie """

        id_rule = rule[Tokens.id_]
        self.flows["flow"][0][Tokens.cookie] = \
            CookieHandler.get_cookie(id_rule)

    def _build_sequence(self, rule):
        """ Build sequence field to set flow priority """

        if Tokens.sequence in rule:
            self.flows["flow"][0]["priority"] = rule[Tokens.sequence]
        else:
            self.flows["flow"][0]["priority"] = self.PRIORITY_DEFAULT

    def _build_protocol(self, rule):
        """ Identifies the protocol of the ACL rule """

        if Tokens.protocol not in rule:
            message = "Missing %s field:\n%s" % (Tokens.protocol,
                                                 self.dumped_rule)
            logging.error(self.MALFORMED_MESSAGE % message)
            raise ValueError(self.MALFORMED_MESSAGE % message)

        else:
            if rule[Tokens.protocol] == "tcp":
                self._build_tcp(rule)
            elif rule[Tokens.protocol] == "udp":
                self._build_udp(rule)
            elif rule[Tokens.protocol] == "icmp":
                self._build_icmp(rule)
            elif rule[Tokens.protocol] == "ip":
                self.generated_all_flows_from_rule = True
                pass  # It is not necessary to process a IP protocol
            else:
                message = "Unknown protocol '%s'" % rule[Tokens.protocol]
                logging.error(self.MALFORMED_MESSAGE % message)
                raise ValueError(self.MALFORMED_MESSAGE % message)

    def _build_tcp(self, rule):
        """ Builds a TCP flow based on OpenDayLight json format """

        self._set_flow_ip_protocol(6)
        self._set_tcp_flags(rule)
        self._check_source_and_destination_ports(rule, "tcp")

    def _build_udp(self, rule):
        """ Builds a UDP flow based on OpenDayLight json format """

        self._set_flow_ip_protocol(17)
        self._check_source_and_destination_ports(rule, "udp")

    def _build_icmp(self, rule):
        """ Builds ICMP protocol acl using OpenDayLight json format """

        self._set_flow_ip_protocol(1)
        self.generated_all_flows_from_rule = True

        if Tokens.icmp_options in rule:

            if Tokens.icmp_code in rule[Tokens.icmp_options] and \
               Tokens.icmp_type in rule[Tokens.icmp_options]:

                icmp_options = rule[Tokens.icmp_options]

                self.flows["flow"][0]["match"]["icmpv4-match"] = {
                    "icmpv4-code": icmp_options[Tokens.icmp_code],
                    "icmpv4-type": icmp_options[Tokens.icmp_type]
                }
            else:
                message = "Missing %s or %s icmp options:\n%s" % (
                    Tokens.icmp_code, Tokens.icmp_type, self.dumped_rule)
                logging.error(self.MALFORMED_MESSAGE % message)
                raise ValueError(self.MALFORMED_MESSAGE % message)
        else:
            message = "Missing %s for icmp protocol" % Tokens.icmp_options
            logging.error(self.MALFORMED_MESSAGE % message)
            raise ValueError(self.MALFORMED_MESSAGE % message)

    def _set_flow_ip_protocol(self, protocol_n):
        """ Sets the IP protocol number inside given flow """

        self.flows["flow"][0]["match"]["ip-match"] = {
            "ip-protocol": protocol_n
        }

    def _check_source_and_destination_ports(self, rule, protocol):
        """ Checks source and destination options inside json """

        l4_options = rule.get(Tokens.l4_options, {})

        if l4_options.get(Tokens.src_port_op) == Tokens.range and \
           l4_options.get(Tokens.dst_port_op) == Tokens.range:
            self._build_double_range(rule, protocol)

        elif l4_options.get(Tokens.src_port_op) == Tokens.range:
            self._build_simple_range(rule, protocol,
                                     Tokens.src_port,
                                     Tokens.src_port_end)

        elif l4_options.get(Tokens.dst_port_op) == Tokens.range:
            self._build_simple_range(rule, protocol,
                                     Tokens.dst_port,
                                     Tokens.dst_port_end)
        else:
            self._build_transport_source_ports(rule, protocol)
            self._build_transport_destination_ports(rule, protocol)
            self.generated_all_flows_from_rule = True

    def _set_tcp_flags(self, rule):
        """ Sets the flags inside given flow """

        l4_options = rule.get(Tokens.l4_options, {})

        if Tokens.flags in l4_options:

            flags = l4_options[Tokens.flags]
            tcp_flags = TCPControlBits(flags).to_int()

            self.flows["flow"][0]["match"]["tcp-flag-match"] = {
                "tcp-flag": tcp_flags,
            }

    def _build_simple_range(self, rule, protocol, start, end):
        """ Builds a TCP|UDP flows when ACL has Src and Dst ranges."""

        port_end = int(rule[Tokens.l4_options][end])

        if self.current_src_or_dst_port is not None:

            # Assigns if the last iteration made flows array to reach
            # ALLOWED_FLOWS_SIZE before reach the last port in range
            port_start = self.current_src_or_dst_port
        else:

            # Assigns if it is the first time building range for rule
            port_start = int(rule[Tokens.l4_options][start])

        for port in xrange(port_start, port_end + 1):

            # Do this to avoid change the first port of range in orig rule
            # We use it to update each flow description field
            rule_copy = deepcopy(rule)
            rule_copy[Tokens.l4_options][start] = str(port)

            self._build_transport_source_ports(rule_copy, protocol)
            self._build_transport_destination_ports(rule_copy, protocol)
            self._build_id_and_description_when_simple_range(
                rule, port,
                rule[Tokens.l4_options][start],
                port_end)

            if port == port_end:
                # If we finished to build all ports in range,
                # set variable below to True to avoid rebuild
                # the same rule
                self.generated_all_flows_from_rule = True
                return

            if len(self.flows["flow"]) == self.ALLOWED_FLOWS_SIZE:
                # If flows array reach ALLOWED_FLOWS_SIZE, we stop to
                # build and save actual state
                self.current_src_or_dst_port = port + 1
                return

            self._insert_new_flow_when_single_range(port, port_end)

    def _build_double_range(self, rule, protocol):
        """ Builds a TCP|UDP flows when ACL has Src or Dst ranges."""

        l4_options = rule[Tokens.l4_options]

        src_port_end = int(l4_options[Tokens.src_port_end])
        dst_port_end = int(l4_options[Tokens.dst_port_end])

        if self.current_src_port is not None and self.current_dst_port is not None:

            # Assigns if the last iteration made flows array to reach
            # ALLOWED_FLOWS_SIZE before reach the last port in range
            src_port_start = self.current_src_port
            dst_port_start = self.current_dst_port
        else:

            # Assigns if it is the first time building range for rule
            src_port_start = int(l4_options[Tokens.src_port])
            dst_port_start = int(l4_options[Tokens.dst_port])

        if dst_port_start > dst_port_end:
            src_port_start += 1
            dst_port_start = int(l4_options[Tokens.dst_port])

        for src_port in xrange(src_port_start, src_port_end + 1):
            for dst_port in xrange(dst_port_start, dst_port_end + 1):

                # Do this to avoid change the first port of range
                # in original rule.
                # We use it to update each flow description field

                rule_copy = deepcopy(rule)
                rule_copy[Tokens.l4_options][Tokens.src_port] = str(src_port)
                rule_copy[Tokens.l4_options][Tokens.dst_port] = str(dst_port)

                self._build_transport_source_ports(rule_copy, protocol)
                self._build_transport_destination_ports(rule_copy, protocol)
                self._build_id_and_description_when_double_range(
                    rule, src_port, dst_port)

                if src_port == src_port_end and dst_port == dst_port_end:
                    # If we finished to build all ports in range,
                    # set variable below to True to avoid rebuild
                    # the same rule
                    self.generated_all_flows_from_rule = True
                    return

                if dst_port == dst_port_end:
                    # When state is save, make sure that in next iteration
                    # of src ranges all related destination ports will be
                    # built together
                    dst_port_start = int(l4_options[Tokens.dst_port])

                if len(self.flows["flow"]) == self.ALLOWED_FLOWS_SIZE:
                    # If flows array reach ALLOWED_FLOWS_SIZE, we stop to
                    # build and save actual state
                    self.current_src_port = src_port
                    self.current_dst_port = dst_port + 1
                    return

                self._insert_new_flow_when_double_range(src_port, src_port_end,
                                                        dst_port, dst_port_end)

    def _insert_new_flow_when_single_range(self, port, port_end):
        """ Check inside single range if still exists ports to build
            allocating one flow more
        """

        if port < port_end:
            self._insert_new_flow()

    def _insert_new_flow_when_double_range(self, src_port, src_port_end,
                                           dst_port, dst_port_end):
        """ Check inside double range if still exists ports to build
            allocating one flow more
        """

        if src_port < src_port_end or dst_port < dst_port_end:
            self._insert_new_flow()

    def _insert_new_flow(self):
        """ Create deep copy of last flow built in the head of the list
            to simplify the access to the current index when building next
            port.
        """

        self.flows["flow"].insert(0, deepcopy(self.flows["flow"][0]))

    def _build_id_and_description_when_simple_range(
            self, rule, port, port_start, port_end):
        """ Builds custom id and description for flows generated
            by ACL that have Src range or Dst range.
        """

        self._build_id_when_only_src_or_dst_range(rule, port)
        self._build_id_when_src_eq_and_dst_range(rule, port)
        self._build_id_when_src_range_and_dst_eq(rule, port)

        self._build_description_when_only_src_or_dst_range(
            rule, port_start, port_end)
        self._build_description_when_src_range_and_dst_eq(
            rule, port_start, port_end)
        self._build_description_when_src_eq_and_dst_range(
            rule, port_start, port_end)

    def _build_id_and_description_when_double_range(
            self, rule, src_port, dst_port):
        """ Builds custom id and description for flows generated
            by ACL that have Src range and Dst range.
        """

        self._build_id_when_src_range_and_dst_range(rule, src_port, dst_port)
        self._build_description_when_src_range_and_dst_range(rule)

    def _build_description_when_src_eq_and_dst_range(
            self, rule, port_start, port_end):

        l4_options = rule[Tokens.l4_options]
        if l4_options.get(Tokens.src_port_op) == Tokens.eq and \
           l4_options.get(Tokens.dst_port_op) == Tokens.range:

            self.flows["flow"][0]["flow-name"] = to_str_description_both(
                rule[Tokens.description],
                rule[Tokens.l4_options].get(Tokens.src_port),
                rule[Tokens.l4_options].get(Tokens.src_port),
                port_start, port_end)

    def _build_description_when_src_range_and_dst_eq(
            self, rule, port_start, port_end):

        l4_options = rule[Tokens.l4_options]
        if l4_options.get(Tokens.src_port_op) == Tokens.range and \
           l4_options.get(Tokens.dst_port_op) == Tokens.eq:

            self.flows["flow"][0]["flow-name"] = to_str_description_both(
                rule[Tokens.description],
                port_start, port_end,
                rule[Tokens.l4_options].get(Tokens.dst_port),
                rule[Tokens.l4_options].get(Tokens.dst_port))

    def _build_description_when_only_src_or_dst_range(
            self, rule, port_start, port_end):

        self.flows["flow"][0]["flow-name"] = to_str_description(
            rule[Tokens.description],
            port_start, port_end)

    def _build_description_when_src_range_and_dst_range(self, rule):

        self.flows["flow"][0]["flow-name"] = to_str_description_both(
            rule[Tokens.description],
            rule[Tokens.l4_options][Tokens.src_port],
            rule[Tokens.l4_options][Tokens.src_port_end],
            rule[Tokens.l4_options][Tokens.dst_port],
            rule[Tokens.l4_options][Tokens.dst_port_end])

    def _build_id_when_src_eq_and_dst_range(self, rule, port):

        l4_options = rule[Tokens.l4_options]
        if l4_options.get(Tokens.src_port_op) == Tokens.eq and \
           l4_options.get(Tokens.dst_port_op) == Tokens.range:

            self.flows["flow"][0]["id"] = to_str_id_both(
                rule[Tokens.id_],
                rule[Tokens.l4_options][Tokens.src_port],
                port)

    def _build_id_when_src_range_and_dst_eq(self, rule, port):

        l4_options = rule[Tokens.l4_options]
        if l4_options.get(Tokens.src_port_op) == Tokens.range and \
           l4_options.get(Tokens.dst_port_op) == Tokens.eq:

            self.flows["flow"][0]["id"] = to_str_id_both(
                rule[Tokens.id_],
                port,
                rule[Tokens.l4_options][Tokens.dst_port])

    def _build_id_when_only_src_or_dst_range(self, rule, port):

        self.flows["flow"][0]["id"] = to_str_id(
            rule[Tokens.id_],
            port)

    def _build_id_when_src_range_and_dst_range(self, rule, src_port, dst_port):

        self.flows["flow"][0]["id"] = to_str_id_both(
            rule[Tokens.id_],
            src_port, dst_port)

    def _build_transport_source_ports(self, rule, protocol):
        """ Builds source ports for transport protocols TCP or UDP """

        l4_options = rule.get(Tokens.l4_options, {})
        if Tokens.src_port_op in l4_options:
            prefix = protocol + "-source-port"
            self._build_transport_ports(rule, prefix, Tokens.src_port_op,
                                        Tokens.src_port,
                                        Tokens.src_port_end)

    def _build_transport_destination_ports(self, rule, protocol):
        """ Builds destination ports for transport protocols TCP or UDP """

        l4_options = rule.get(Tokens.l4_options, {})
        if Tokens.dst_port_op in l4_options:
            prefix = protocol + "-destination-port"
            self._build_transport_ports(rule, prefix, Tokens.dst_port_op,
                                        Tokens.dst_port, Tokens.dst_port_end)

    def _build_transport_ports(self, rule, prefix, operation, start, end):
        """ Builds transport (TCP | UDP) protocols json data """

        self.flows["flow"][0]["match"][prefix] = \
            rule[Tokens.l4_options][start]

