# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class VlanTest(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_success_one_vlan(self):
        """ Test success of get of one vlan."""

        name_file = 'api_vlan/tests/json/get_one_vlan.json'

        response = self.client.get(
            '/api/v3/vlan/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_get_success_one_vlan_details(self):
        """ Test success of get of one vlan with details."""

        name_file = 'api_vlan/tests/json/get_one_vlan_details.json'

        response = self.client.get(
            '/api/v3/vlan/1/?kind=details',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_post_one_vlan_success(self):
        """ Test success of post of one vlan."""

        name_file = 'api_vlan/tests/json/post_one_vlan.json'

        # Does post request
        response = self.client.post(
            '/api/v3/vlan/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/vlan/%s/' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id
        data = response.data
        del data['vlans'][0]['id']

        self.compare_json(name_file, data)

    def test_post_one_vlan_without_number_success(self):
        """ Test success of post of one vlan without number."""

        name_file = 'api_vlan/tests/json/post_one_vlan_without_number.json'

        # Does post request
        response = self.client.post(
            '/api/v3/vlan/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/vlan/%s/' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id
        data = response.data
        del data['vlans'][0]['id']
        num_vlan = data['vlans'][0]['num_vlan']
        del data['vlans'][0]['num_vlan']

        self.compare_status(200, response.status_code)
        self.assertEqual(
            3,
            num_vlan,
            'Number Vlan should be %s and was %s' % (
                3, num_vlan)
        )

        self.compare_json(name_file, data)

    def test_post_one_vlan_number_duplicate_env_error(self):
        """Test error of post of one vlan duplicated number."""

        name_file = 'api_vlan/tests/json/post_one_vlan_number_duplicate_env.json'

        # Does post request
        response = self.client.post(
            '/api/v3/vlan/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        expected_data = 'Number VLAN can not be duplicated in the environment.'
        self.assertEqual(
            expected_data,
            response.data['detail'],
            'Details should be %s and was %s' % (
                expected_data, response.data['detail'])
        )

    def test_post_one_vlan_name_duplicate_env_error(self):
        """Test error of post of one vlan duplicated name."""

        name_file = 'api_vlan/tests/json/post_one_vlan_name_duplicate_env.json'

        # Does post request
        response = self.client.post(
            '/api/v3/vlan/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        expected_data = 'Name VLAN can not be duplicated in the environment.'
        self.assertEqual(
            expected_data,
            response.data['detail'],
            'Details should be %s and was %s' % (
                expected_data, response.data['detail'])
        )

    # def test_get_details_success(self):
    #     """ test_get_details_success"""
    #     response = self.client.get(
    #         '/api/v3/pool/details/1/',
    #         content_type="application/json",
    #         HTTP_AUTHORIZATION=self.get_http_authorization('test'))
    #     log.info(response.data)
    #     self.assertEqual(
    #         self.load_json_file('api_pools/tests/json/test_pool_get_details.json'),
    #         response.data
    #     )
    #     self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    # def test_put_success(self):
    #     """ test_put_success"""
    #     # update
    #     response = self.client.put(
    #         '/api/v3/pool/1/',
    #         data=json.dumps(self.load_json_file('api_pools/tests/json/test_pool_put.json')),
    #         content_type="application/json",
    #         HTTP_AUTHORIZATION=self.get_http_authorization('test'))
    #     self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    #     # get datas updated
    #     response = self.client.get(
    #         '/api/v3/pool/1/',
    #         content_type="application/json",
    #         HTTP_AUTHORIZATION=self.get_http_authorization('test'))

    #     # test if datas were updated
    #     self.assertEqual(
    #         self.load_json_file('api_pools/tests/json/test_pool_put.json'),
    #         response.data
    #     )
    #     self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    # def test_post_success(self):
    #     """ test_post_success"""
    #     response = self.client.post(
    #         '/api/v3/pool/',
    #         data=json.dumps(self.load_json_file('api_pools/tests/json/test_pool_post.json')),
    #         content_type="application/json",
    #         HTTP_AUTHORIZATION=self.get_http_authorization('test'))

    #     self.assertEqual(201, response.status_code, "Status code should be 201 and was %s" % response.status_code)
