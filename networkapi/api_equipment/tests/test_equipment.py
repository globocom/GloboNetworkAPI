# -*- coding: utf-8 -*-
import json
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
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_post_one_equipment_success(self):
        """Test Success of post of one equipment."""

        name_file = 'api_equipment/tests/json/post_one_equipment.json'

        # Does post request
        response = self.client.post(
            '/api/v3/equipment/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(201, response.status_code,
                         'Status code should be 201 and was %s' %
                         response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/equipment/%s/' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Removes property id
        data = response.data
        del data['equipments'][0]['id']
        print json.dumps(self.load_json_file(name_file), sort_keys=True)
        print json.dumps(data, sort_keys=True)
        # Tests if data was inserted
        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(data, sort_keys=True),
            'Jsons should be same.'
        )

    def test_put_one_equipment_success(self):
        """Test Success of put of one equipment."""

        name_file = 'api_equipment/tests/json/put_one_equipment.json'

        # Does put request
        response = self.client.put(
            '/api/v3/equipment/60/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/equipment/60/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # Tests code returned
        self.assertEqual(200, response.status_code,
                         'Status code should be 200 and was %s' %
                         response.status_code)

        data = response.data
        print json.dumps(self.load_json_file(name_file), sort_keys=True)
        print json.dumps(data, sort_keys=True)

        # Tests if data was updated
        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(data, sort_keys=True),
            'Jsons should be same.'
        )

    def test_delete_one_equipment_success(self):
        """Test success of delete of one equipment."""

        response = self.client.delete(
            '/api/v3/equipment/61/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

        response = self.client.get(
            '/api/v3/equipment/61/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            404,
            response.status_code,
            'Status code should be 404 and was %s' % response.status_code
        )
