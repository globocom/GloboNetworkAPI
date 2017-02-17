# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import base64
import json
import logging

from django.test import TestCase

from networkapi.settings import local_files
from networkapi.test import load_json

LOG = logging.getLogger(__name__)


class NetworkApiTestCase(TestCase):

    def setUp(self):
        pass

    def get_http_authorization(self, user):
        return 'Basic %s' % base64.b64encode('%s:teste' % user)

    def tearDown(self):
        pass

    def load_json_file(self, file_name):
        return load_json(local_files(file_name))

    def compare_json(self, name_file, data):
        expected_data = json.dumps(
            self.load_json_file(name_file), sort_keys=True)
        received_data = json.dumps(data, sort_keys=True)
        self.assertEqual(
            expected_data,
            received_data,
            'Jsons should be same. Expected %s Received %s' % (
                expected_data, received_data)
        )

    def compare_status(self, expected_code, code):
        self.assertEqual(
            expected_code,
            code,
            'Status code should be %s and was %s' % (
                expected_code, code)
        )

    def compare_values(self, expected_data, received_data):
        self.assertEqual(
            expected_data,
            received_data,
            'Value should be same. Expected %s Received %s' % (
                expected_data, received_data)
        )
