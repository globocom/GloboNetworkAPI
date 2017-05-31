# -*- coding: utf-8 -*-


from nose.tools import assert_raises
from nose.tools import assert_equal
from nose.tools import assert_in
from nose.tools import assert_not_in

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.SDN.ODL.flows.acl import AclFlowBuilder


class OpenDayLightACLTestCase(NetworkApiTestCase):
    """ Opendaylight controller Access Control List test class """

    def test_acl_flow_bulder_raising_type_error(self):
        """ Should rise TypeError when flows variable is not a dict """
        flows = AclFlowBuilder({})
        flows.flows = None

        assert_raises(TypeError, flows.dump)

    def test_acl_flow_builder_empty_json(self):
        """ Should return a json with empty data """
        data = {"kind": "default#acl", "rules": []}
        flows = AclFlowBuilder(data)
        assert_equal(flows.dump(), '{"flow": []}')

    def test_acl_flow_builder_malformed_json(self):
        """ Should return a ValueError """

        acl = AclFlowBuilder({})
        assert_raises(ValueError, acl.dump)

    def test_acl_flow_builder_missing_destination_data(self):
        """ Should have description on flow """

        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "tcp",
                "description": "simple flow",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
            }]
        }

        acl = AclFlowBuilder(data)
        acl.build()

        assert_in("flow-name", acl.flows["flow"][0])
        assert_equal(acl.flows["flow"][0]["flow-name"],
                     data["rules"][0]["description"])

    def test_acl_should_raise_value_error_when_no_destination_is_passed(self):
        """ Should raise ValueError when no destination is passed """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "tcp",
                "description": "simple flow",
                "source": "10.0.0.1/32",
            }]
        }

        acl = AclFlowBuilder(data)
        assert_raises(ValueError, acl.build)

    def test_acl_should_raise_value_error_when_no_source_is_passed(self):
        """ Should raise ValueError when no source is passed """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "tcp",
                "description": "simple flow",
                "destination": "10.0.0.2/32",
            }]
        }

        acl = AclFlowBuilder(data)
        assert_raises(ValueError, acl.build)

    def test_acl_should_have_ethernet_type(self):
        """ Should have ethernet type as match field """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "tcp",
                "description": "simple flow",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
            }]
        }
        acl = AclFlowBuilder(data)
        acl.build()

        assert_equal(
            2048,
            acl.flows["flow"][0]
                     ["match"]["ethernet-match"]["ethernet-type"]["type"])

    def test_acl_should_raise_exception_when_there_is_no_protocol_field(self):
        """ Should raise an exception when there is no protocol field """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "description": "simple flow",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
            }]
        }
        acl = AclFlowBuilder(data)
        assert_raises(ValueError, acl.build)

    def test_acl_should_raise_exception_when_protocol_is_invalid(self):
        """ Should raise an exception when there is no protocol field """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "invalid",
                "description": "simple flow",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
            }]
        }
        acl = AclFlowBuilder(data)
        assert_raises(ValueError, acl.build)

    def test_acl_should_have_tcp_destination_port(self):
        """ Should have tcp destination port """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "tcp",
                "description": "simple flow",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "l4-options": {
                    "dest-port-op": "eq",
                    "dest-port-start": "26379"
                }
            }]
        }
        acl = AclFlowBuilder(data)
        acl.build()
        assert_equal(acl.flows["flow"][0]["match"]["tcp-destination-port"],
                     data["rules"][0]["l4-options"]["dest-port-start"])

    def test_acl_should_have_tcp_source_port(self):
        """ Should have tcp source port """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "tcp",
                "description": "simple flow",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "l4-options": {
                    "src-port-op": "eq",
                    "src-port-start": "26379"
                }
            }]
        }
        acl = AclFlowBuilder(data)
        acl.build()
        assert_equal(acl.flows["flow"][0]["match"]["tcp-source-port"],
                     data["rules"][0]["l4-options"]["src-port-start"])

    def test_acl_should_have_tcp_as_ip_protocol(self):
        """ Should have tcp as ip-protocol field """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "protocol": "tcp"
            }]
        }
        acl = AclFlowBuilder(data)
        acl.build()
        assert_equal(6,
                     acl.flows["flow"][0]["match"]["ip-match"]["ip-protocol"])

    def test_acl_should_have_udp_as_ip_protocol(self):
        """ Should have upd as ip-protocol field """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "protocol": "udp"
            }]
        }
        acl = AclFlowBuilder(data)
        acl.build()
        assert_equal(
            17, acl.flows["flow"][0]["match"]["ip-match"]["ip-protocol"])

    def test_acl_should_have_udp_source_port(self):
        """ Should have udp source port """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "udp",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "l4-options": {
                    "src-port-op": "eq",
                    "src-port-start": "26379"
                }
            }]
        }
        acl = AclFlowBuilder(data)
        acl.build()
        assert_equal(acl.flows["flow"][0]["match"]["udp-source-port"],
                     data["rules"][0]["l4-options"]["src-port-start"])

    def test_acl_should_have_udp_destination_port(self):
        """ Should have udp destination port """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "udp",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "l4-options": {
                    "dest-port-op": "eq",
                    "dest-port-start": "26379"
                }
            }]
        }
        acl = AclFlowBuilder(data)
        acl.build()
        assert_equal(acl.flows["flow"][0]["match"]["udp-destination-port"],
                     data["rules"][0]["l4-options"]["dest-port-start"])

    def test_acl_should_have_tcp_source_and_destination_ports(self):
        """ Should have tcp source and destination ports """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "tcp",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "l4-options": {
                    "dest-port-op": "eq",
                    "dest-port-start": "26379",
                    "src-port-op": "eq",
                    "src-port-start": "26379"
                }
            }]
        }
        acl = AclFlowBuilder(data)
        acl.build()
        assert_equal(acl.flows["flow"][0]["match"]["tcp-source-port"],
                     data["rules"][0]["l4-options"]["src-port-start"])
        assert_equal(acl.flows["flow"][0]["match"]["tcp-destination-port"],
                     data["rules"][0]["l4-options"]["dest-port-start"])

    def test_acl_should_have_udp_source_and_destination_ports(self):
        """ Should have udp source and destination ports """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "udp",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "l4-options": {
                    "dest-port-op": "eq",
                    "dest-port-start": "26379",
                    "src-port-op": "eq",
                    "src-port-start": "26379"
                }
            }]
        }
        acl = AclFlowBuilder(data)
        acl.build()
        assert_equal(acl.flows["flow"][0]["match"]["udp-source-port"],
                     data["rules"][0]["l4-options"]["src-port-start"])
        assert_equal(acl.flows["flow"][0]["match"]["udp-destination-port"],
                     data["rules"][0]["l4-options"]["dest-port-start"])

    def test_acl_should_have_icmp_as_ip_protocol(self):
        """ Should have ICMP as ip protocol """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "icmp",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "icmp-options": {
                    "icmp-code": "0",
                    "icmp-type": "8"
                }
            }]
        }
        acl = AclFlowBuilder(data)
        acl.build()
        assert_equal(
            1, acl.flows["flow"][0]["match"]["ip-match"]["ip-protocol"])

    def test_acl_should_raise_value_error_when_there_are_no_icmp_options(self):
        """ Should raise ValueError when there are no ICMP options """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "icmp",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
            }]
        }
        acl = AclFlowBuilder(data)
        assert_raises(ValueError, acl.build)

    def test_acl_should_raise_error_for_icmp_type_and_code_missing(self):
        """ Should raise error for ICMP type and code missing """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "icmp",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "icmp-options": {
                }
            }]
        }
        acl = AclFlowBuilder(data)
        assert_raises(ValueError, acl.build)

    def test_acl_should_have_icmp_code_and_type_at_flow(self):
        """ Should have icmp code and type at flow """

        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "icmp",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "icmp-options": {
                    "icmp-code": "0",
                    "icmp-type": "8"
                }
            }]
        }
        acl = AclFlowBuilder(data)
        acl.build()
        assert_equal(
            data["rules"][0]["icmp-options"]["icmp-code"],
            acl.flows["flow"][0]["match"]["icmpv4-match"]["icmpv4-code"])
        assert_equal(
            data["rules"][0]["icmp-options"]["icmp-type"],
            acl.flows["flow"][0]["match"]["icmpv4-match"]["icmpv4-type"])

    def test_acl_should_create_internet_protocol_flow(self):
        """ Should create an Internet Protocol flow """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "ip",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
            }]
        }

        acl = AclFlowBuilder(data)
        acl.build()
        assert_equal(acl.flows['flow'][0]['match']['ipv4-source'],
            data['rules'][0]['source'])
        assert_equal(acl.flows['flow'][0]['match']['ipv4-destination'],
            data['rules'][0]['destination'])

    def test_acl_should_have_action_local(self):
        """ Should have the Openflow NORMAL action """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "ip",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "action": "permit",
            }]
        }

        acl = AclFlowBuilder(data)
        acl.build()

        assert_in("instructions", acl.flows["flow"][0])
        instruction = acl.flows["flow"][0]["instructions"]["instruction"][0]
        assert_equal(instruction["apply-actions"]["action"][0]["output-action"]
            ["output-node-connector"], "NORMAL")

    def test_acl_should_not_have_actions(self):
        """ Should not have any action """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "ip",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "action": "drop",
            }]
        }

        acl = AclFlowBuilder(data)
        acl.build()

        assert_not_in("instructions", acl.flows["flow"][0])
