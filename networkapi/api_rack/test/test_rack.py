# -*- coding: utf-8 -*-

import os
from django.test.client import Client
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.test import load_json



class RackTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_success(self):
        """ resultado esperado status 201"""
        response = self.client.post('/api/rack/', self.load_rack_json('rack.json'), HTTP_AUTHORIZATION=self.get_http_authorization())
        self.assertEqual(201, response.status_code, "Status code should be 201 and was %s" % response.status_code)

    def load_rack_json(self, file_name):
        path = os.path.dirname(os.path.realpath(__file__)) + '/' + file_name
        return load_json(path)