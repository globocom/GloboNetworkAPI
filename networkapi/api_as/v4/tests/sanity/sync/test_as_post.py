# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

json_path = 'api_as/v4/tests/sanity/sync/json/%s'


class AsPostSuccessTestCase(NetworkApiTestCase):
    """Class for Test AS package Success POST cases."""

    fixtures = [

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_post_one_as(self):
        """Success Test of POST one AS."""

    def test_post_two_as(self):
        """Success Test of POST two AS."""

