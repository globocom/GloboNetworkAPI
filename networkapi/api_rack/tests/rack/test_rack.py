# -*- coding: utf-8 -*-
import os

from django.test.client import Client

from networkapi.test import load_json
from networkapi.test.test_case import NetworkApiTestCase


class RackTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_success(self):
        """ Should post a new Rack """

        #response = self.client.post('/api/rack/',
         #                           self._load_json('rack.json'),
          #                          HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        #self.assertEqual(201, response.status_code, 'Status code should be 201 and was %s' % response.status_code)
        pass

    def _load_json(self, json_name):
        path = os.path.dirname(os.path.realpath(__file__)) + '/' + json_name
        return load_json(path)


s