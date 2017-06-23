# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

json_path = 'api_as/v4/tests/sanity/sync/json/%s'


class AsDeleteSuccessTestCase(NetworkApiTestCase):
    """Class for Test AS package Success DELETE cases."""

    fixtures = [

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_one_as(self):
        """Success Test of DELETE one AS."""

    def test_delete_two_as(self):
        """Success Test of DELETE two AS."""


class AsPutErrorTestCase(NetworkApiTestCase):
    """Class for Test AS package Error DELETE cases."""

    fixtures = [

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_one_as_with_equipments(self):
        """Error Test of DELETE one AS that is related to two Equipments."""

    def test_delete_one_as_with_equipments_and_as_without_equipments(self):
        """Error Test of DELETE one AS that is related to two Equipments
            and AS that is not related with Equipments.
        """

    def test_delete_one_inexistent_as(self):
        """Error Test of DELETE one inexistent AS."""

    def test_delete_one_existent_and_one_inexistent_as(self):
        """Error Test of DELETE one existent and one inexistent AS."""

