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

from json import dumps
import logging
from networkapi.plugins.SDN.ODL.utils.cookie_handler import CookieHandler
from networkapi.plugins.SDN.ODL.utils.tcp_control_bits import TCPControlBits


class Tokens(object):
    """ Class that holds all key words from the source json that identifies
    a valid ACL to be translated to a OpenDayLight json format
    """

    kind = "kind"
    rules = "rules"

    id = "id"
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

class AclFlowBuilder(object):
    """ Class responsible for build json data for Access control list flow at
    OpenDayLight controller
    """

    LOG_FORMAT = '%(levelname)s:%(message)s'

    MALFORMED_MESSAGE = "Error building ACL Json. Malformed input data: \n%s"

    PRIORITY_DEFAULT = 65000
    TABLE = 0

    def __init__(self, data):

        self.raw_data = data  # Original data
        self.flows = []  # Processed data

        logging.basicConfig(format=self.LOG_FORMAT, level=logging.DEBUG)

    def dump(self):
        """ Returns a json of built flows """

        if not isinstance(self.flows, list):
            raise TypeError("self.flows must be a list")

        self.build()

        return dumps(self.flows)

    def build(self):
        """ Verifies input data and build flows for OpenDayLight controller """

        if Tokens.kind in self.raw_data and Tokens.rules in self.raw_data:
            logging.info("Building ACL Json: %s", self.raw_data["kind"])

            for rule in self.raw_data[Tokens.rules]:
                self._build_rule(rule)

        else:
            message = "Missing %s or %s fields." % (Tokens.kind, Tokens.rules)
            logging.error(self.MALFORMED_MESSAGE % message)
            raise ValueError(self.MALFORMED_MESSAGE % message)

    def _build_rule(self, rule):
        """ Build one single ACL rule """

        # Assigns the id of the current ACL
        if Tokens.id in rule:
            # We always insert in the head of the list to simplify the access
            # to the current index
            self.flows.insert(0, {"flow": {Tokens.id: rule[Tokens.id]}})

        # Flow description
        if Tokens.description in rule:
            self.flows[0]["flow"]["flow-name"] = rule[Tokens.description]

        self._build_match(rule)
        self._build_protocol(rule)
        self._build_action(rule)
        self._build_cookie(rule)

        # Flow table and priority
        self.flows[0]["flow"]["table_id"] = self.TABLE

        if Tokens.sequence in rule:
            self.flows[0]["flow"]["priority"] = rule[Tokens.sequence]
        else:
            self.flows[0]["flow"]["priority"] = self.PRIORITY_DEFAULT

    def _build_cookie(self, rule):

        self.flows[0]["flow"][Tokens.cookie] = \
            CookieHandler.get_cookie(rule[Tokens.id], 1)

    def _build_match(self, rule):
        """ Builds the match field that identifies the ACL rule """

        self.flows[0]["flow"]["match"] = {
            "ethernet-match": {
                "ethernet-type": {
                    "type": 2048
                }
            }
        }

        if Tokens.destination in rule and Tokens.source in rule:

            self.flows[0]["flow"]["match"]["ipv4-destination"] = \
                rule[Tokens.destination]
            self.flows[0]["flow"]["match"]["ipv4-source"] = rule[Tokens.source]

        else:
            logging.error(self.MALFORMED_MESSAGE % rule)
            raise ValueError(self.MALFORMED_MESSAGE % rule)

    def _build_protocol(self, rule):
        """ Identifies the protocol of the ACL rule """

        if Tokens.protocol not in rule:
            message = "Missing %s field:\n%s" % (Tokens.protocol, rule)
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
                pass  # It is not necessary to process a IP protocol
            else:
                message = "Unknown protocol '%s'" % rule[Tokens.protocol]
                logging.error(self.MALFORMED_MESSAGE % message)
                raise ValueError(self.MALFORMED_MESSAGE % message)

    def _build_tcp(self, rule):
        """ Builds a TCP flow based on OpenDayLight json format """

        self._set_flow_ip_protocol(self.flows[0]["flow"], 6)
        self._check_source_and_destination_ports(rule, "tcp")

        if Tokens.l4_options in rule:
            if Tokens.flags in rule[Tokens.l4_options]:
                self._set_tcp_flags(self.flows[0]["flow"],
                                rule[Tokens.l4_options][Tokens.flags])


    def _build_udp(self, rule):
        """ Builds a UDP flow based on OpenDayLight json format """

        self._set_flow_ip_protocol(self.flows[0]["flow"], 17)
        self._check_source_and_destination_ports(rule, "udp")

    def _set_flow_ip_protocol(self, flow, protocol_n):
        """ Sets the IP protocol number inside given flow """

        flow["match"]["ip-match"] = {
            "ip-protocol": protocol_n
        }

    def _set_tcp_flags(self, flow, flags):
        """ Sets the flags inside given flow """

        tcp_flags = TCPControlBits(flags).to_int()

        flow["match"]["tcp-flags-match"] = {
            "tcp-flags": tcp_flags,
        }

    def _check_source_and_destination_ports(self, rule, protocol):
        """ Checks source and destination options inside json """

        if Tokens.l4_options in rule:

            # Checks for source port
            if Tokens.src_port_op in rule[Tokens.l4_options]:
                self._build_transport_source_ports(rule, protocol)

            # Checks for destination port
            if Tokens.dst_port_op in rule[Tokens.l4_options]:
                self._build_transport_destination_ports(rule, protocol)

    def _build_transport_source_ports(self, rule, protocol):
        """ Builds source ports for transport protocols TCP or UDP """
        prefix = protocol + "-source-port"
        self._build_transport_ports(rule, prefix, Tokens.src_port_op,
                                    Tokens.src_port, Tokens.src_port_end)

    def _build_transport_destination_ports(self, rule, protocol):
        """ Builds destination ports for transport protocols TCP or UDP """
        prefix = protocol + "-destination-port"
        self._build_transport_ports(rule, prefix, Tokens.dst_port_op,
                                    Tokens.dst_port, Tokens.dst_port_end)

    def _build_transport_ports(self, rule, prefix, operation, start, end):
        """ Builds transport (TCP | UDP) protocols json data """

        if rule[Tokens.l4_options][operation] == "eq":

            self.flows[0]["flow"]["match"][prefix] = \
                rule[Tokens.l4_options][start]

        elif rule[Tokens.l4_options][operation] == "range":

            # TODO: Implement port range json from opendaylight.
            self.flows[0]["flow"]["match"][prefix] = \
                rule[Tokens.l4_options][start]

    def _build_icmp(self, rule):
        """ Builds ICMP protocol acl using OpenDayLight json format """

        self._set_flow_ip_protocol(self.flows[0]["flow"], 1)

        if Tokens.icmp_options in rule:

            if Tokens.icmp_code in rule[Tokens.icmp_options] and \
               Tokens.icmp_type in rule[Tokens.icmp_options]:

                icmp_options = rule[Tokens.icmp_options]

                self.flows[0]["flow"]["match"]["icmpv4-match"] = {
                    "icmpv4-code": icmp_options[Tokens.icmp_code],
                    "icmpv4-type": icmp_options[Tokens.icmp_type]
                }
            else:
                message = "Missing %s or %s icmp options:\n%s" % (
                    Tokens.icmp_code, Tokens.icmp_type, rule)
                logging.error(self.MALFORMED_MESSAGE % message)
                raise ValueError(self.MALFORMED_MESSAGE % message)
        else:
            message = "Missing %s for icmp protocol" % Tokens.icmp_options
            logging.error(self.MALFORMED_MESSAGE % message)
            raise ValueError(self.MALFORMED_MESSAGE % message)

    def _build_action(self, rule):
        """ Builds the Openflow actions to a flow """

        if Tokens.action in rule and rule[Tokens.action] == "permit":
            self.flows[0]["flow"]["instructions"] = {
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
