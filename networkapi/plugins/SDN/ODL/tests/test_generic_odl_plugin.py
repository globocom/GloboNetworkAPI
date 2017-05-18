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

    def setUp(self):
        self.client = Client()
        self.equipment = Equipamento.objects.filter(id=1)[0]
        self.equipment_access = EquipamentoAcesso.objects.filter(id=1)[0]

        self.odl = ODLPlugin(
            equipment=self.equipment,
            equipment_access=self.equipment_access
        )

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

    def setUp(self):
        self.client = Client()
        self.equipment = Equipamento(id=28)
        self.equipment_access = EquipamentoAcesso(id=1)
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

        assert_raises_regexp(ValueError,
                             'Error building ACL Json. Malformed input data: \n'
                             'Missing icmp-options for icmp protocol',
                             self.odl.add_flow,
                             data)

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

        assert_raises_regexp(ValueError,
                             "Error building ACL Json. Malformed input data: \n"
                             "Missing icmp-code or icmp-type icmp options:\n%s" %
                             rule,
                             self.odl.add_flow,
                             data)

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

        assert_raises_regexp(ValueError,
                             "Error building ACL Json. Malformed input data: \n"
                             "Missing icmp-code or icmp-type icmp options:\n%s" %
                             rule,
                             self.odl.add_flow,
                             data)

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

        assert_raises_regexp(ValueError,
                             "Error building ACL Json. Malformed input data: \n"
                             "Missing icmp-code or icmp-type icmp options:\n%s" %
                             rule,
                             self.odl.add_flow,
                             data)

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

        assert_raises_regexp(ValueError,
                             "Error building ACL Json. Malformed input data: \n%s" %
                             rule,
                             self.odl.add_flow,
                             data)

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

        assert_raises_regexp(ValueError,
                             "Error building ACL Json. Malformed input data: \n%s" %
                             rule,
                             self.odl.add_flow,
                             data)

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

        assert_raises_regexp(ValueError,
                             "Error building ACL Json. Malformed input data: \n%s" %
                             rule,
                             self.odl.add_flow,
                             data)



    # Testar inserindo icmp-options com icmp-code e sem icmp-type
    # Testar inserindo icmp-options com icmp-type
    # Verificar quais tipos de icmp-code e icmp-type são permitidos

