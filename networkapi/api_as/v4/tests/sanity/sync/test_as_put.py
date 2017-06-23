# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

json_path = 'api_as/v4/tests/sanity/sync/json/%s'


class AsPutSuccessTestCase(NetworkApiTestCase):
    """Class for Test AS package Success PUT cases."""

    fixtures = [

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_put_one_as(self):
        """Success Test of PUT one AS."""

    def test_put_two_as(self):
        """Success Test of PUT two AS."""


class AsPutErrorTestCase(NetworkApiTestCase):
    """Class for Test AS package Error PUT cases."""

    fixtures = [

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_put_one_inexistent_as(self):
        """Error Test of PUT one inexistent AS."""

    def test_put_one_existent_and_one_inexistent_as(self):
        """Error Test of PUT one existent and one inexistent AS."""

