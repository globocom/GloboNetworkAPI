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


class Tokens(object):
    kind = "kind"
    rules = "rules"

    id = "id"
    action = "action"
    description = "description"
    source = "source"
    destination = "destination"
    l4_options = "l4-options"


class AclFlowBuilder(object):
    """ Class responsible for build json data for Access control list flow at
    OpenDayLight controller
    """

    LOG_FORMAT = '%(levelname)s:%(message)s'

    MALFORMED_MESSAGE = "Error building ACL Json. Malformed input data: \n%s"

    def __init__(self, data):

        self.raw_data = data  # Original data
        self.flows = {"flow": []}  # Processed data
        self.flow_metadata = {}  # Metadata of the current flows set

        logging.basicConfig(format=self.LOG_FORMAT, level=logging.DEBUG)

    def dump(self):
        """ Returns a json of built flows """

        if not isinstance(self.flows, dict):
            raise TypeError("self.flows must be a dictionary")

        self.build()

        return dumps(self.flows)

    def build(self):
        """ Verifies input data and build flows for OpenDayLight controller """

        if Tokens.kind in self.raw_data and Tokens.rules in self.raw_data:
            logging.info("Building ACL Json: %s", self.raw_data["kind"])

            for rule in self.raw_data[Tokens.rules]:
                self.build_rule(rule)

        else:
            message = "Missing %s or %s fields." % (Tokens.kind, Tokens.rules)
            logging.error(self.MALFORMED_MESSAGE % message)
            raise ValueError(self.MALFORMED_MESSAGE % message)

    def build_rule(self, rule):
        """ Build one single ACL rule """

        # Assigns the id of the current ACL
        if Tokens.id in rule:
            # We always insert in the head of the list to simplify the access
            # to the current index
            self.flows["flow"].insert(0, {Tokens.id: rule[Tokens.id]})

        # Flow description
        if Tokens.description in rule:
            self.flows["flow"][0]["flow-name"] = rule[Tokens.description]

        self.build_match(rule)
        self.build_protocol(rule)

    def build_match(self, rule):
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
            self.flows["flow"][0]["match"]["ipv4-source"] = \
                    rule[Tokens.source]

        else:
            logging.error(self.MALFORMED_MESSAGE % rule)
            raise ValueError(self.MALFORMED_MESSAGE % rule)

    def build_protocol(self, rule):
        """ Identifies the protocol of the ACL rule """

        pass
