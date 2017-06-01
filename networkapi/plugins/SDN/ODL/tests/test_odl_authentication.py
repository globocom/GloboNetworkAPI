# -*- coding: utf-8 -*-


from json import dumps

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase


class OpenDayLightAuthTestCase(NetworkApiTestCase):
    """ Opendaylight controller authentication test class """

    def setUp(self):
        self.client = Client()
