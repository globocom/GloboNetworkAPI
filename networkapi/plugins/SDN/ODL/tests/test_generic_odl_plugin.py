# -*- coding: utf-8 -*-

from django.test.client import Client

from nose.tools import assert_raises_regexp
from nose.tools import assert_raises
from nose.tools import assert_equal
from requests.exceptions import HTTPError
import random

from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.plugins.SDN.ODL.Generic import ODLPlugin
from networkapi.plugins.SDN.ODL.tests.utils import OpenDaylightTestUtils
from networkapi.test.test_case import NetworkApiTestCase

class GenericOpenDayLightTestCaseSuccess(NetworkApiTestCase):
    """ Class for testing the generic OpenDayLight plugin """

    fixtures = [
        'networkapi/plugins/SDN/ODL/fixtures/initial_equipments.json'
    ]

    utils = OpenDaylightTestUtils()

    def setUp(self):
        self.client = Client()
        self.equipment = Equipamento.objects.filter(id=1)[0]
        self.equipment_access = EquipamentoAcesso.objects.filter(id=1)[0]
        self.utils.set_controller_endpoint(self.equipment_access)
        self.DEFAULT_PRIORITY = 65000
        self.TCP_PROTOCOL_NUMBER = 6
        self.UDP_PROTOCOL_NUMBER = 17
        self.ICMP_PROTOCOL_NUMBER = 1

        self.odl = ODLPlugin(
            equipment=self.equipment,
            equipment_access=self.equipment_access
        )


    # TODO Create test to verify persistence in the three OVS's

    def test_add_flow_one_acl_rule_with_tcp_protocol_dest_eq_l4(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol and dest eq in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "10.128.24.3/32",
                "id": "82338",
                "l4-options": {
                    "dest-port-op": "eq",
                    "dest-port-start": "123"
                },
                "owner": "networkapi",
                "protocol": "tcp",
                "source": "0.0.0.0/0"

            }]
        }

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['description'], flow['flow-name'])

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        assert_equal(int(data['rules'][0]['l4-options']['dest-port-start']),
                     flow['match']['tcp-destination-port'])

        assert_equal(self.TCP_PROTOCOL_NUMBER,
                     flow['match']['ip-match']['ip-protocol'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])

        assert_equal(self.DEFAULT_PRIORITY, flow['priority'])


    def test_add_flow_one_acl_rule_with_tcp_protocol_flags_rst_l4(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol and flags RST in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "10.0.0.0/8",
                "id": "101301",
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

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['description'], flow['flow-name'])

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        for flag in data['rules'][0]['l4-options']['flags']:
            # TODO Check if flag is present
            pass

        assert_equal(self.TCP_PROTOCOL_NUMBER,
                     flow['match']['ip-match']['ip-protocol'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])

        assert_equal(self.DEFAULT_PRIORITY, flow['priority'])


    def test_add_flow_one_acl_rule_with_tcp_protocol_flags_ack_l4(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol and flags ACK in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "10.0.0.0/8",
                "id": "101302",
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

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['description'], flow['flow-name'])

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        for flag in data['rules'][0]['l4-options']['flags']:
            # TODO Check if flag is present
            pass

        assert_equal(self.TCP_PROTOCOL_NUMBER,
                     flow['match']['ip-match']['ip-protocol'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])

        assert_equal(self.DEFAULT_PRIORITY, flow['priority'])


    def test_add_flow_one_acl_rule_with_tcp_protocol(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "0.0.0.0/0",
                "id": "106966",
                "owner": "networkapi",
                "protocol": "tcp",
                "source": "10.128.0.64/27"
            }]
        }

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['description'], flow['flow-name'])

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        assert_equal(self.TCP_PROTOCOL_NUMBER,
                     flow['match']['ip-match']['ip-protocol'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])

        assert_equal(self.DEFAULT_PRIORITY, flow['priority'])


    def test_add_flow_one_acl_rule_with_tcp_protocol_dest_eq_l4_and_sequence(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol and dest eq in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "destination": "10.130.2.0/24",
                "id": "107480",
                "l4-options": {
                    "dest-port-op": "eq",
                    "dest-port-start": "27017"
                },
                "owner": "networkapi",
                "protocol": "tcp",
                "sequence": 2,
                "source": "10.129.195.0/24"
            }]
        }

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        assert_equal(int(data['rules'][0]['l4-options']['dest-port-start']),
                     flow['match']['tcp-destination-port'])

        assert_equal(self.TCP_PROTOCOL_NUMBER,
                     flow['match']['ip-match']['ip-protocol'])

        assert_equal(data['rules'][0]['sequence'],
                     flow['priority'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])


    def test_add_flow_one_acl_rule_with_tcp_protocol_and_sequence(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol and sequence."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "destination": "10.143.224.54/32",
                "id": "110886",
                "owner": "networkapi",
                "protocol": "tcp",
                "sequence": 6,
                "source": "10.129.200.96/27"
            }]
        }

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        assert_equal(self.TCP_PROTOCOL_NUMBER,
                     flow['match']['ip-match']['ip-protocol'])

        assert_equal(data['rules'][0]['sequence'],
                     flow['priority'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])


    def test_add_flow_one_acl_rule_with_tcp_protocol_dest_range_l4(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol and dest range in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "10.0.0.0/8",
                "id": "141239",
                "l4-options": {
                    "dest-port-end": "162",
                    "dest-port-op": "range",
                    "dest-port-start": "161"
                },
                "owner": "networkapi",
                "protocol": "tcp",
                "sequence": 214,
                "source": "10.129.199.192/27"
            }]
        }

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['description'],
                     flow['flow-name'])

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        assert_equal(int(data['rules'][0]['l4-options']['dest-port-start']),
                     flow['match']['tcp-destination-port'])

        assert_equal(self.TCP_PROTOCOL_NUMBER,
                     flow['match']['ip-match']['ip-protocol'])

        assert_equal(data['rules'][0]['sequence'],
                     flow['priority'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])


    def test_add_flow_one_acl_rule_with_udp_protocol_src_eq_and_dest_eq_l4(self):
        """Test of success to add flow with one ACL rule
            with udp protocol and src eq, dest eq in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "224.0.0.102/32",
                "id": "82324",
                "l4-options": {
                    "dest-port-op": "eq",
                    "dest-port-start": "1985",
                    "src-port-op": "eq",
                    "src-port-start": "1985"
                },
                "owner": "networkapi",
                "protocol": "udp",
                "source": "0.0.0.0/0"
            }]
        }

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['description'],
                     flow['flow-name'])

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        assert_equal(int(data['rules'][0]['l4-options']['dest-port-start']),
                     flow['match']['udp-destination-port'])

        assert_equal(int(data['rules'][0]['l4-options']['src-port-start']),
                     flow['match']['udp-source-port'])

        assert_equal(self.UDP_PROTOCOL_NUMBER,
                     flow['match']['ip-match']['ip-protocol'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])

        assert_equal(self.DEFAULT_PRIORITY,
                     flow['priority'])


    def test_add_flow_one_acl_rule_with_udp_protocol_dest_eq_l4(self):
        """Test of success to add flow with one ACL rule
            with udp protocol and dest eq in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "10.128.24.2/32",
                "id": "82337",
                "l4-options": {
                    "dest-port-op": "eq",
                    "dest-port-start": "53"
                },
                "owner": "networkapi",
                "protocol": "udp",
                "source": "0.0.0.0/0"
            }]
        }

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['description'],
                     flow['flow-name'])

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        assert_equal(int(data['rules'][0]['l4-options']['dest-port-start']),
                     flow['match']['udp-destination-port'])

        assert_equal(self.UDP_PROTOCOL_NUMBER,
                     flow['match']['ip-match']['ip-protocol'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])

        assert_equal(self.DEFAULT_PRIORITY,
                     flow['priority'])


    def test_add_flow_one_acl_rule_with_udp_protocol_src_eq_l4(self):
        """Test of success to add flow with one ACL rule
            with udp protocol and src eq in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "10.128.160.32/27",
                "id": "112140",
                "l4-options": {
                    "src-port-op": "eq",
                    "src-port-start": "161"
                },
                "owner": "networkapi",
                "protocol": "udp",
                "source": "0.0.0.0/0"
            }]
        }

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['description'],
                     flow['flow-name'])

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        assert_equal(int(data['rules'][0]['l4-options']['src-port-start']),
                     flow['match']['udp-source-port'])

        assert_equal(self.UDP_PROTOCOL_NUMBER,
                     flow['match']['ip-match']['ip-protocol'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])

        assert_equal(self.DEFAULT_PRIORITY,
                     flow['priority'])


    def test_add_flow_one_acl_rule_with_udp_protocol_dest_range_l4(self):
        """Test of success to add flow with one ACL rule
            with udp protocol and dest range in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "destination": "10.130.70.224/27",
                "id": "141880",
                "l4-options": {
                    "dest-port-end": "65535",
                    "dest-port-op": "range",
                    "dest-port-start": "1024"
                },
                "owner": "networkapi",
                "protocol": "udp",
                "sequence": 42,
                "source": "10.129.193.32/27"
            }]
        }

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        assert_equal(int(data['rules'][0]['l4-options']['dest-port-start']),
                     flow['match']['udp-destination-port'])

        assert_equal(self.UDP_PROTOCOL_NUMBER,
                     flow['match']['ip-match']['ip-protocol'])

        assert_equal(data['rules'][0]['sequence'],
                     flow['priority'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])


    def test_add_flow_one_acl_rule_with_ip_protocol(self):
        """Test of success to add flow with one ACL rule
            with ip protocol."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "10.254.0.0/16",
                "id": "82332",
                "owner": "networkapi",
                "protocol": "ip",
                "source": "0.0.0.0/0"
            }]
        }

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['description'],
                     flow['flow-name'])

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])

        assert_equal(self.DEFAULT_PRIORITY,
                     flow['priority'])


    def test_add_flow_one_acl_rule_with_ip_protocol_and_sequence(self):
        """Test of success to add flow with one ACL rule
            with ip protocol and sequence."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "destination": "10.130.64.0/27",
                "id": "107200",
                "owner": "networkapi",
                "protocol": "ip",
                "sequence": 2,
                "source": "10.129.192.32/27"
            }]
        }

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        assert_equal(data['rules'][0]['sequence'],
                     flow['priority'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])


    def test_add_flow_one_acl_rule_with_icmp_protocol(self):
        """Test of success to add flow with one ACL rule
            with icmp protocol."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "10.0.0.0/8",
                "icmp-options": {
                    "icmp-code": "0",
                    "icmp-type": "8"
                },
                "id": "82325",
                "owner": "networkapi",
                "protocol": "icmp",
                "source": "0.0.0.0/0"
            }]
        }

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(
            flow_id)[random_idx]['flow-node-inventory:flow'][0]

        output_node_connector = \
            flow.get('instructions').get('instruction')[0] \
                .get("apply-actions").get("action")[0] \
                .get("output-action").get("output-node-connector")
        assert_equal(
            output_node_connector,
            "LOCAL")

        assert_equal(data['rules'][0]['description'],
                     flow['flow-name'])

        assert_equal(data['rules'][0]['destination'],
                     flow['match']['ipv4-destination'])

        assert_equal(int(data['rules'][0]['icmp-options']['icmp-code']),
                     flow['match']['icmpv4-match']['icmpv4-code'])

        assert_equal(int(data['rules'][0]['icmp-options']['icmp-type']),
                     flow['match']['icmpv4-match']['icmpv4-type'])

        assert_equal(data['rules'][0]['id'], flow['id'])

        assert_equal(self.ICMP_PROTOCOL_NUMBER,
                     flow['match']['ip-match']['ip-protocol'])

        assert_equal(data['rules'][0]['source'],
                     flow['match']['ipv4-source'])

        assert_equal(self.DEFAULT_PRIORITY,
                     flow['priority'])


    def test_remove_flow(self):
        """Test of success to remove flow."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "10.128.24.3/32",
                "id": "80000",
                "l4-options": {
                    "dest-port-op": "eq",
                    "dest-port-start": "123"
                },
                "owner": "networkapi",
                "protocol": "tcp",
                "source": "0.0.0.0/0"

            }]
        }

        self.odl.add_flow(data)

        id_flow = data['rules'][0]['id']
        self.odl.del_flow(id_flow)

        assert_raises(HTTPError, self.odl.get_flow, id_flow)


class GenericOpenDayLightTestCaseError(NetworkApiTestCase):
    """ Class for testing the generic OpenDayLight plugin """

    utils = OpenDaylightTestUtils()

    def setUp(self):
        self.client = Client()
        self.equipment = Equipamento(id=28)
        self.equipment_access = EquipamentoAcesso(id=1)
        self.utils.set_controller_endpoint(self.equipment_access)

        self.odl = ODLPlugin(
            equipment=self.equipment,
            equipment_access=self.equipment_access
        )

    def test_add_flow_one_acl_rule_without_icmp_options(self):
        """Test of error to add flow with one ACL rule
            without ICMP options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "icmp",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
            }]
        }

        assert_raises_regexp(
            ValueError,
            'Error building ACL Json. Malformed input data: \n'
            'Missing icmp-options for icmp protocol',
            self.odl.add_flow,
            data
        )

    def test_add_flow_one_acl_rule_with_only_icmp_code(self):
        """Test of error to add flow with one ACL rule
            with only icmp-code."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "icmp",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "icmp-options": {
                    "icmp-code": "0"
                }
            }]
        }

        rule = data['rules'][0]

        assert_raises_regexp(
            ValueError,
            "Error building ACL Json. Malformed input data: \n"
            "Missing icmp-code or icmp-type icmp options:\n%s" %
            rule,
            self.odl.add_flow,
            data
        )

    def test_add_flow_one_acl_rule_with_only_icmp_type(self):
        """Test of error to add flow with one ACL rule
            with only icmp-type."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "icmp",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "icmp-options": {
                    "icmp-type": "8"
                }
            }]
        }

        rule = data['rules'][0]

        assert_raises_regexp(
            ValueError,
            "Error building ACL Json. Malformed input data: \n"
            "Missing icmp-code or icmp-type icmp options:\n%s" %
            rule,
            self.odl.add_flow,
            data
        )

    def test_add_flow_one_acl_rule_without_icmp_code_and_icmp_type(self):
        """Test of error to add flow with one ACL rule
            without icmp-code and icmp-type."""

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

        rule = data['rules'][0]

        assert_raises_regexp(
            ValueError,
            "Error building ACL Json. Malformed input data: \n"
            "Missing icmp-code or icmp-type icmp options:\n%s" %
            rule,
            self.odl.add_flow,
            data
        )

    def test_add_flow_one_acl_rule_with_only_source(self):
        """Test of error to add flow with one ACL rule
            with only source."""

        data = {
            "kind": "Access Control List",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "10.0.0.0/8",
                "icmp-options": {
                    "icmp-code": "0",
                    "icmp-type": "8"
                },
                "id": "82325",
                "owner": "networkapi",
                "protocol": "icmp",
                "source": "0.0.0.0/0"
            }]
        }

        rule = data['rules'][0]

        assert_raises_regexp(
            ValueError,
            "Error building ACL Json. Malformed input data: \n%s" %
            rule,
            self.odl.add_flow,
            data
        )

    def test_add_flow_one_acl_rule_with_only_destination(self):
        """Test of error to add flow with one ACL rule
            with only destination."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "destination": "10.0.0.0/8",
                "icmp-options": {
                    "icmp-code": "0",
                    "icmp-type": "8"
                },
                "id": "82325",
                "owner": "networkapi",
                "protocol": "icmp"
            }]
        }

        rule = data['rules'][0]

        assert_raises_regexp(
            ValueError,
            "Error building ACL Json. Malformed input data: \n%s" %
            rule,
            self.odl.add_flow,
            data
        )

    def test_add_flow_one_acl_rule_without_source_and_destination(self):
        """Test of error to add flow with one ACL rule
            without source and destination."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "generic",
                "icmp-options": {
                    "icmp-code": "0",
                    "icmp-type": "8"
                },
                "id": "82325",
                "owner": "networkapi",
                "protocol": "icmp"
            }]
        }

        rule = data['rules'][0]

        assert_raises_regexp(
            ValueError,
            "Error building ACL Json. Malformed input data: \n%s" %
            rule,
            self.odl.add_flow,
            data
        )

    # Testar inserindo icmp-options com icmp-code e sem icmp-type
    # Testar inserindo icmp-options com icmp-type
    # Verificar quais tipos de icmp-code e icmp-type são permitidos
