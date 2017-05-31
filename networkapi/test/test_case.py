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

        expected_data = json.dumps(self.load_json_file(name_file),
                                   sort_keys=True)
        received_data = json.dumps(data, sort_keys=True)

        msg = 'Jsons should be same. Expected: {}, Received: {}'
        self.assertEqual(
            expected_data,
            received_data,
            msg.format(expected_data, received_data)
        )

    def compare_json_lists(self, name_file, data):
        expected_data = self.load_json_file(name_file)
        received_data = data
        self.assertEqual(
            sorted(expected_data),
            sorted(received_data),
            'Lists of Jsons should be same.\n Expected:\n %s \n Received:\n %s\n' % (
                json.dumps(expected_data), json.dumps(received_data))
        )

    def compare_status(self, expected_code, code):

        msg = 'Status code should be same. Expected: {}, Received: {}'
        self.assertEqual(
            expected_code,
            code,
            msg.format(expected_code, code)
        )

    def contains_values(self, expected_data, received_data):

        msg = 'Expected data should be in received data. Expected: {}, ' \
            'Received: {}'
        self.assertContains(
            expected_data,
            received_data,
            msg.format(expected_data, received_data)
        )

    def compare_values(self, expected_data, received_data):

        msg = 'Value should be same. Expected: {}, Received: {}'
        self.assertEqual(
            expected_data,
            received_data,
            msg.format(expected_data, received_data)
        )
