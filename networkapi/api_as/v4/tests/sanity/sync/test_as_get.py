# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

json_path = 'api_as/v4/tests/sanity/sync/json/%s'

class AsGetSuccessTestCase(NetworkApiTestCase):
    """Class for Test AS package Success GET cases."""

    fixtures = [

    ]


    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_get_one_basic_as(self):
        """Success Test of GET one Basic AS."""

    def test_get_two_basic_as(self):
        """Success Test of GET two Basic AS."""

    def test_get_one_as_with_equipments_ids(self):
        """Success Test of GET one AS with Equipments ids."""

    def test_get_one_as_with_equipments_details(self):
        """Success Test of GET one AS with Equipments details."""


class AsGetErrorTestCase(NetworkApiTestCase):
    """Class for Test AS package Error GET cases."""

    fixtures = [

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_get_one_basic_as(self):
        """Error Test of GET one Basic AS."""

    def test_get_two_basic_as(self):
        """Error Test of GET two Basic AS."""

    def test_get_one_as_with_equipments_ids(self):
        """Error Test of GET one AS with Equipments ids."""

    def test_get_one_as_with_equipments_details(self):
        """Error Test of GET one AS with Equipments details."""





