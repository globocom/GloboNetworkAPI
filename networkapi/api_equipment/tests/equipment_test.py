# -*- coding: utf-8 -*-
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class EquipmentTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_success_list_equipment(self):
        """
        Test Success of get equipment list
        """

        response = self.client.get(
            '/api/v3/equipment/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )
