# -*- coding: utf-8 -*-

from django.test.client import Client

from nose.tools import assert_raises_regexp
from nose.tools import assert_equal
from nose.tools import assert_in
from nose.tools import assert_not_in

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

        self.odl = ODLPlugin(
            equipment=self.equipment,
            equipment_access=self.equipment_access
        )

    def test_add_flow_one_acl_rule_with_tcp_protocol_dest_eq_l4(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol and dest eq in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "NTP",
                "destination": "10.128.24.3/32",
                "id": "82338",
                "l4-options": {
                    "dest-port-op": "eq",
                    "dest-port-start": "123"
                },
                "owner": "ralmeida",
                "protocol": "tcp",
                "source": "0.0.0.0/0"

            }]
        }

        self.odl.add_flow(data)

    def test_add_flow_one_acl_rule_with_tcp_protocol_flags_rst_l4(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol and flags RST in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "Acessos estabelecidos - RST",
                "destination": "10.0.0.0/8",
                "id": "101301",
                "l4-options": {
                    "flags": [
                        "RST"
                    ]
                },
                "owner": "vicente.fiebig",
                "protocol": "tcp",
                "source": "0.0.0.0/0"
            }]
        }

        self.odl.add_flow(data)

    def test_add_flow_one_acl_rule_with_tcp_protocol_flags_ack_l4(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol and flags ACK in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "Acessos estabelecidos - ACK",
                "destination": "10.0.0.0/8",
                "id": "101302",
                "l4-options": {
                    "flags": [
                        "ACK"
                    ]
                },
                "owner": "vicente.fiebig",
                "protocol": "tcp",
                "source": "0.0.0.0/0"
            }]
        }

        self.odl.add_flow(data)

    def test_add_flow_one_acl_rule_with_tcp_protocol(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "GERENCIA SO A (volta L2)",
                "destination": "0.0.0.0/0",
                "id": "106966",
                "owner": "manoel.junior",
                "protocol": "tcp",
                "source": "10.128.0.64/27"
            }]
        }

        self.odl.add_flow(data)

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
                "owner": "ricardo.dias",
                "protocol": "tcp",
                "sequence": 2,
                "source": "10.129.195.0/24"
            }]
        }

        self.odl.add_flow(data)

    def test_add_flow_one_acl_rule_with_tcp_protocol_and_sequence(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol and sequence."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "destination": "10.143.224.54/32",
                "id": "110886",
                "owner": "frederico.costa",
                "protocol": "tcp",
                "sequence": 6,
                "source": "10.129.200.96/27"
            }]
        }

        self.odl.add_flow(data)

    def test_add_flow_one_acl_rule_with_tcp_protocol_dest_range_l4(self):
        """Test of success to add flow with one ACL rule
            with tcp protocol and dest range in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "Sumarizando Supseg",
                "destination": "10.0.0.0/8",
                "id": "141239",
                "l4-options": {
                    "dest-port-end": "162",
                    "dest-port-op": "range",
                    "dest-port-start": "161"
                },
                "owner": "ralmeida",
                "protocol": "tcp",
                "sequence": 214,
                "source": "10.129.199.192/27"
            }]
        }

        self.odl.add_flow(data)

    def test_add_flow_one_acl_rule_with_udp_protocol_src_eq_and_dest_eq_l4(self):
        """Test of success to add flow with one ACL rule
            with udp protocol and src eq, dest eq in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "Acesso HSRP",
                "destination": "224.0.0.102/32",
                "id": "82324",
                "l4-options": {
                    "dest-port-op": "eq",
                    "dest-port-start": "1985",
                    "src-port-op": "eq",
                    "src-port-start": "1985"
                },
                "owner": "ralmeida",
                "protocol": "udp",
                "source": "0.0.0.0/0"
            }]
        }

        self.odl.add_flow(data)

    def test_add_flow_one_acl_rule_with_udp_protocol_dest_eq_l4(self):
        """Test of success to add flow with one ACL rule
            with udp protocol and dest eq in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "DNS",
                "destination": "10.128.24.2/32",
                "id": "82337",
                "l4-options": {
                    "dest-port-op": "eq",
                    "dest-port-start": "53"
                },
                "owner": "ralmeida",
                "protocol": "udp",
                "source": "0.0.0.0/0"
            }]
        }

        self.odl.add_flow(data)

    def test_add_flow_one_acl_rule_with_udp_protocol_src_eq_l4(self):
        """Test of success to add flow with one ACL rule
            with udp protocol and src eq in l4 options."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "Retorno SNMP ACS",
                "destination": "10.128.160.32/27",
                "id": "112140",
                "l4-options": {
                    "src-port-op": "eq",
                    "src-port-start": "161"
                },
                "owner": "vicente.fiebig",
                "protocol": "udp",
                "source": "0.0.0.0/0"
            }]
        }

        self.odl.add_flow(data)

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
                "owner": "nedimar",
                "protocol": "udp",
                "sequence": 42,
                "source": "10.129.193.32/27"
            }]
        }

        self.odl.add_flow(data)

    def test_add_flow_one_acl_rule_with_ip_protocol(self):
        """Test of success to add flow with one ACL rule
            with ip protocol."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "Retorno redes de usuarios - VPN",
                "destination": "10.254.0.0/16",
                "id": "82332",
                "owner": "ralmeida",
                "protocol": "ip",
                "source": "0.0.0.0/0"
            }]
        }

        self.odl.add_flow(data)

    def test_add_flow_one_acl_rule_with_ip_protocol_and_sequence(self):
        """Test of success to add flow with one ACL rule
            with ip protocol and sequence."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "destination": "10.130.64.0/27",
                "id": "107200",
                "owner": "paulo.sousa",
                "protocol": "ip",
                "sequence": 2,
                "source": "10.129.192.32/27"
            }]
        }

        self.odl.add_flow(data)

    def test_add_flow_one_acl_rule_with_icmp_protocol(self):
        """Test of success to add flow with one ACL rule
            with icmp protocol."""

        data = {
            "kind": "default#acl",
            "rules": [{
                "action": "permit",
                "description": "Acesso ICMP restritivo BE",
                "destination": "10.0.0.0/8",
                "icmp-options": {
                    "icmp-code": "0",
                    "icmp-type": "8"
                },
                "id": "82325",
                "owner": "ralmeida",
                "protocol": "icmp",
                "source": "0.0.0.0/0"
            }]
        }

        self.odl.add_flow(data)





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
                "description": "Restrict environment",
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
                "description": "Acesso ICMP restritivo BE",
                "destination": "10.0.0.0/8",
                "icmp-options": {
                    "icmp-code": "0",
                    "icmp-type": "8"
                },
                "id": "82325",
                "owner": "ralmeida",
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
                "description": "Acesso ICMP restritivo BE",
                "icmp-options": {
                    "icmp-code": "0",
                    "icmp-type": "8"
                },
                "id": "82325",
                "owner": "ralmeida",
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
