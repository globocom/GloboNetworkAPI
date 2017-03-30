# -*- coding: utf-8 -*-


from django.test.client import Client
from nose.tools import assert_raises
from nose.tools import assert_equal

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.plugins.SDN.ODL.flows.acl import AclFlowBuilder


class OpenDayLightACLTestCase(NetworkApiTestCase):
    """ Opendaylight controller Access Control List test class """

    def setUp(self):
        self.client = Client()

    def test_acl_flow_bulder_raising_type_error(self):
        """ Should rise TypeError when flows variable is not a dict """
        flows = AclFlowBuilder({})
        flows.flows = None

        assert_raises(TypeError, flows.dump)

    def test_acl_flow_builder_empty_json(self):
        """ Should return a json with empty data """

        flows = AclFlowBuilder({})
        assert_equal(flows.dump(), '{}')
