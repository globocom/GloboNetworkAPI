# -*- coding: utf-8 -*-

from django.test.client import Client

from networkapi.plugins.SDN.ODL.generic import ODLPlugin
from networkapi.test.test_case import NetworkApiTestCase


class GenericOpenDayLightTestCase(NetworkApiTestCase):
    """ Class for testing the generic OpenDayLight plugin """

    def setUp(self):
        self.client = Client()

    def test_add_simple_acl_flow(self):
        """ Adding simple ACL flow through generic ODL plugin """

        odl = ODLPlugin()
        odl.add_flow({})
