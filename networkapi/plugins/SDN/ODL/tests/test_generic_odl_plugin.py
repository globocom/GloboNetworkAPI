# -*- coding: utf-8 -*-

from nose.tools import assert_raises_regexp
from nose.tools import assert_raises
from requests.exceptions import HTTPError
import random
from json import dumps

from django.test.utils import override_settings
from mock import patch

from networkapi.equipamento.models import Equipamento
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.plugins.SDN.ODL.Generic import ODLPlugin
from networkapi.plugins.SDN.ODL.tests.utils import OpenDaylightTestUtils
from networkapi.test.test_case import NetworkApiTestCase


class GenericOpenDayLightTestCaseSuccess(NetworkApiTestCase):
    """Class for testing the generic OpenDayLight plugin for success cases."""
    fixtures = [
        'networkapi/vlan/fixtures/initial_tipo_rede.json',
        'networkapi/api_network/fixtures/integration/initial_environment_envlog.json',
        'networkapi/api_network/fixtures/integration/initial_environment_dc.json',
        'networkapi/api_network/fixtures/integration/initial_environment_gl3.json',
        'networkapi/api_network/fixtures/sanity/initial_vrf.json',
        'networkapi/plugins/SDN/ODL/fixtures/initial_equipments.json',
    ]

    utils = OpenDaylightTestUtils()
    json_aclapi_input_path = 'plugins/SDN/ODL/json/aclapi_input/%s'
    json_odl_output_path = 'plugins/SDN/ODL/json/odl_output/%s'

    def setUp(self):
        self.equipment = Equipamento.objects.filter(id=10)[0]
        self.equipment_access = EquipamentoAcesso.objects.filter(id=1)[0]
        self.utils.set_controller_endpoint(self.equipment_access)

        self.odl = ODLPlugin(
            equipment=self.equipment,
            equipment_access=self.equipment_access
        )

        self.flow_key = "flow-node-inventory:flow"

    @patch("networkapi.plugins.SDN.ODL.Generic.ODLPlugin._get_nodes")
    def test_get_nodes_ids_empty(self, *args):
        """Test get nodes with a empty result"""

        fake_get_nodes = args[0]
        fake_get_nodes.return_value=[]

        self.assertEqual(self.odl._get_nodes_ids(), [])

    @patch("networkapi.plugins.SDN.ODL.Generic.ODLPlugin._get_nodes")
    def test_get_nodes_ids_one_id(self, *args):
        """Test get nodes ids with one result"""

        fake_get_nodes = args[0]
        fake_get_nodes.return_value=[{'id':'fake_id'}]

        self.assertEqual(self.odl._get_nodes_ids(), ['fake_id'])

    def test_add_flow_checking_if_persisted_in_all_ovss(self):
        """Test add flow checking if ACL was persisted at all OVS's."""

        input = self.json_aclapi_input_path % 'acl_id_83000.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        flow_id = data['rules'][0]['id']

        flows = self.odl.get_flow(flow_id)

        for flow in flows:

            output = self.json_odl_output_path % 'odl_id_83000.json'
            self.compare_json_lists(output, flow[self.flow_key])

    def test_add_two_flows(self):
        pass

    def test_add_flow_one_acl_rule_with_tcp_protocol_dest_eq_l4(self):
        """Test add flow with tcp protocol and dest eq in l4 options."""

        input = self.json_aclapi_input_path % 'acl_id_82338.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

        output = self.json_odl_output_path % 'odl_id_82338.json'
        self.compare_json_lists(output, flow)

    def test_add_flow_one_acl_rule_with_tcp_protocol_flags_rst_l4(self):
        """Test add flow with tcp protocol and flags RST in l4 options."""

        input = self.json_aclapi_input_path % 'acl_id_101301.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

        output = self.json_odl_output_path % 'odl_id_101301.json'

        self.compare_json_lists(output, flow)

    def test_add_flow_one_acl_rule_with_tcp_protocol_flags_ack_l4(self):
        """Test add flow with tcp protocol and flags ACK in l4 options."""

        input = self.json_aclapi_input_path % 'acl_id_101302.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

        output = self.json_odl_output_path % 'odl_id_101302.json'
        self.compare_json_lists(output, flow)

    def test_add_flow_one_acl_rule_with_tcp_protocol(self):
        """Test add flow with tcp protocol."""

        input = self.json_aclapi_input_path % 'acl_id_106966.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

        output = self.json_odl_output_path % 'odl_id_106966.json'
        self.compare_json_lists(output, flow)

    def test_add_flow_with_tcp_protocol_dest_eq_l4_and_sequence(self):
        """Test add flow with tcp protocol and dest eq in l4 options."""

        input = self.json_aclapi_input_path % 'acl_id_107480.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

        output = self.json_odl_output_path % 'odl_id_107480.json'
        self.compare_json_lists(output, flow)

    def test_add_flow_one_acl_rule_with_tcp_protocol_and_sequence(self):
        """Test add flow with tcp protocol and sequence."""

        input = self.json_aclapi_input_path % 'acl_id_110886.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

        output = self.json_odl_output_path % 'odl_id_110886.json'
        self.compare_json_lists(output, flow)

    def test_add_flow_with_udp_protocol_src_eq_and_dest_eq_l4(self):
        """Test add flow with udp protocol and src eq, dest eq in l4 options."""

        input = self.json_aclapi_input_path % 'acl_id_82324.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

        output = self.json_odl_output_path % 'odl_id_82324.json'
        self.compare_json_lists(output, flow)

    def test_add_flow_one_acl_rule_with_udp_protocol_dest_eq_l4(self):
        """Test add flow with udp protocol and dest eq in l4 options."""

        input = self.json_aclapi_input_path % 'acl_id_82337.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

        output = self.json_odl_output_path % 'odl_id_82337.json'
        self.compare_json_lists(output, flow)

    def test_add_flow_one_acl_rule_with_udp_protocol_src_eq_l4(self):
        """Test add flow with udp protocol and src eq in l4 options."""

        input = self.json_aclapi_input_path % 'acl_id_112140.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

        output = self.json_odl_output_path % 'odl_id_112140.json'
        self.compare_json_lists(output, flow)


    def test_add_flow_one_acl_rule_with_ip_protocol(self):
        """Test add flow with ip protocol."""

        input = self.json_aclapi_input_path % 'acl_id_82332.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

        output = self.json_odl_output_path % 'odl_id_82332.json'
        self.compare_json_lists(output, flow)

    def test_add_flow_one_acl_rule_with_ip_protocol_and_sequence(self):
        """Test add flow with ip protocol and sequence."""

        input = self.json_aclapi_input_path % 'acl_id_107200.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()
        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

        output = self.json_odl_output_path % 'odl_id_107200.json'
        self.compare_json_lists(output, flow)

    def test_add_flow_one_acl_rule_with_icmp_protocol(self):
        """Test add flow with icmp protocol."""

        input = self.json_aclapi_input_path % 'acl_id_82325.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

        output = self.json_odl_output_path % 'odl_id_82325.json'
        self.compare_json_lists(output, flow)

    def test_add_a_list_of_acls_in_one_request(self):
        """ Should insert many flows with one request """

        input = self.json_aclapi_input_path % 'acl_id_40000.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']
        flow = self.odl.get_flow(flow_id)[random_idx][self.flow_key]

    def test_remove_flow(self):
        """Test of success to remove flow."""

        input = self.json_aclapi_input_path % 'acl_id_80000.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        id_flow = data['rules'][0]['id']
        self.odl.del_flow(id_flow)

        assert_raises(HTTPError, self.odl.get_flow, id_flow)

    def test_add_flow_one_acl_rule_with_udp_protocol_dest_range_l4(self):
        """Test add flow with udp protocol and dest range in l4 options."""

        input = self.json_aclapi_input_path % 'acl_id_141880.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']

        for id_ in xrange(1024, 1027+1):

            flow = self.odl.get_flow(flow_id + '_%s' % id_)[random_idx][self.flow_key]
            output = self.json_odl_output_path % 'odl_id_141880_%s.json' % id_
            self.compare_json_lists(output, flow)

    def test_add_flow_one_acl_rule_with_tcp_protocol_dest_range_l4(self):
        """Test add flow with tcp protocol and dest range in l4 options."""

        input = self.json_aclapi_input_path % 'acl_id_141239.json'
        data = self.load_json_file(input)

        self.odl.add_flow(data)

        nodes_ids = self.odl._get_nodes_ids()

        random_idx = random.randint(0, len(nodes_ids) - 1)

        flow_id = data['rules'][0]['id']

        for id_ in xrange(161, 162+1):

            flow = self.odl.get_flow(flow_id + '_%s' % id_)[random_idx][self.flow_key]
            output = self.json_odl_output_path % 'odl_id_141239_%s.json' % id_
            self.compare_json_lists(output, flow)


class GenericOpenDayLightTestCaseError(NetworkApiTestCase):
    """Class for testing the generic OpenDayLight plugin for error cases."""

    fixtures = [
        'networkapi/vlan/fixtures/initial_tipo_rede.json',
        'networkapi/api_network/fixtures/integration/initial_environment_envlog.json',
        'networkapi/api_network/fixtures/integration/initial_environment_dc.json',
        'networkapi/api_network/fixtures/integration/initial_environment_gl3.json',
        'networkapi/api_network/fixtures/sanity/initial_vrf.json',
        'networkapi/plugins/SDN/ODL/fixtures/initial_equipments.json',
    ]

    utils = OpenDaylightTestUtils()

    def setUp(self):
        self.equipment = Equipamento.objects.filter(id=10)[0]
        self.equipment_access = EquipamentoAcesso.objects.filter(id=1)[0]
        self.utils.set_controller_endpoint(self.equipment_access)

        self.odl = ODLPlugin(
            equipment=self.equipment,
            equipment_access=self.equipment_access
        )

    def test_add_flow_without_icmp_options(self):
        """Test plugin deny add flow without ICMP options."""

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

    def test_add_flow_with_only_icmp_code(self):
        """Test plugin deny add flow with only icmp-code."""

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

        rule = dumps(data['rules'][0], sort_keys=True)

        assert_raises_regexp(
            ValueError,
            "Error building ACL Json. Malformed input data: \n"
            "Missing icmp-code or icmp-type icmp options:\n%s" %
            rule,
            self.odl.add_flow,
            data
        )

    def test_add_flow_with_only_icmp_type(self):
        """Test plugin deny add flow with only icmp-type."""

        data = {
            "kind": "Access Control List",
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

        rule = dumps(data['rules'][0], sort_keys=True)

        assert_raises_regexp(
            ValueError,
            "Error building ACL Json. Malformed input data: \n"
            "Missing icmp-code or icmp-type icmp options:\n%s" %
            rule,
            self.odl.add_flow,
            data
        )

    def test_add_flow_without_icmp_code_and_icmp_type(self):
        """Test plugin deny add flow without icmp-code and icmp-type."""

        data = {
            "kind": "Access Control List",
            "rules": [{
                "id": 1,
                "protocol": "icmp",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
                "icmp-options": {
                }
            }]
        }

        rule = dumps(data['rules'][0], sort_keys=True)

        assert_raises_regexp(
            ValueError,
            "Error building ACL Json. Malformed input data: \n"
            "Missing icmp-code or icmp-type icmp options:\n%s" %
            rule,
            self.odl.add_flow,
            data
        )

    def test_add_flow_with_only_source(self):
        """Test plugin deny add flow with only source."""

        data = {
            "kind": "Access Control List",
            "rules": [{
                "action": "permit",
                "description": "Restrict environment",
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

        rule = dumps(data['rules'][0], sort_keys=True)

        assert_raises_regexp(
            ValueError,
            "Error building ACL Json. Malformed input data: \n%s" %
            rule,
            self.odl.add_flow,
            data
        )

    def test_add_flow_with_only_destination(self):
        """Test plugin deny add flow with only destination."""

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

        rule = dumps(data['rules'][0], sort_keys=True)

        assert_raises_regexp(
            ValueError,
            "Error building ACL Json. Malformed input data: \n%s" %
            rule,
            self.odl.add_flow,
            data
        )

    def test_add_flow_without_source_and_destination(self):
        """Test plugin deny add flow without source and destination."""

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

        rule = dumps(data['rules'][0], sort_keys=True)

        assert_raises_regexp(
            ValueError,
            "Error building ACL Json. Malformed input data: \n%s" %
            rule,
            self.odl.add_flow,
            data
        )
