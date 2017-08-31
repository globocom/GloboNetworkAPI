
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.SDN.ODL.flows.acl import AclFlowBuilder


class TestSendFlowsWithTCPFlags(NetworkApiTestCase):
    """ Class to test flows that have tcp flags on it """

    def test_flow_with_ack_flag(self):
        """ Try to send a flow with ACK flag """

        acl = {
            "kind": "acl_with_tcp_flags",
            "rules": [{
                "action": "permit",
                "description": "ACK access",
                "destination": "10.0.0.0/8",
                "id": "300",
                "l4-options": {
                    "flags": [
                        "ACK"
                    ]
                },
                "owner": "networkapi",
                "protocol": "tcp",
                "source": "0.0.0.0/0"
            }]
        }

        flows = AclFlowBuilder(acl)
        flow = flows.build().next()
        tcp_flag = flow['flow'][0]['match']['tcp-flag-match']['tcp-flag']

        assert tcp_flag == 16

    def test_flow_with_RST_flag(self):
        """ Try to send a flow with RST flag """
        acl = {
            "kind": "acl_with_tcp_flags",
            "rules": [{
                "action": "permit",
                "description": "RST access",
                "destination": "10.0.0.0/8",
                "id": "200",
                "l4-options": {
                    "flags": [
                        "RST"
                    ]
                },
                "owner": "networkapi",
                "protocol": "tcp",
                "source": "0.0.0.0/0"
            }]
        }

        flows = AclFlowBuilder(acl)
        flow = flows.build().next()
        tcp_flag = flow['flow'][0]['match']['tcp-flag-match']['tcp-flag']

        assert tcp_flag == 4
