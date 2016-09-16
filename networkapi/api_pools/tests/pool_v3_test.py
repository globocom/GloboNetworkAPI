# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class PoolTestV3Case(NetworkApiTestCase):

    maxDiff = None

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def execute_some_put_verify_error(self, name_file):
        # update
        response = self.client.put(
            '/api/v3/pool/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(400, response.status_code,
                         "Status code should be 400 and was %s" % response.status_code)

        # get datas updated
        # response = self.client.get(
        #     '/api/v3/pool/1/',
        #     content_type="application/json",
        #     HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if datas were not updated
        # self.assertEqual(
        #     json.dumps(self.load_json_file(name_file), sort_keys=True),
        #     json.dumps(response.data, sort_keys=True),
        #     "jsons should same"
        # )
        # self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def execute_some_put_verify_success(self, name_file):
        # update
        response = self.client.put(
            '/api/v3/pool/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        # get datas updated
        response = self.client.get(
            '/api/v3/pool/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if datas were updated
        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(response.data, sort_keys=True),
            "jsons should same"
        )
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def execute_some_post_verify_error(self, name_file):
        # delete
        self.client.delete(
            '/api/v3/pool/1/',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # insert
        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(400, response.status_code, "Status code should be 400 and was %s" % response.status_code)

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(500, response.status_code, "Status code should be 500 and was %s" % response.status_code)

    def execute_some_post_verify_success(self, name_file):
        # delete
        self.client.delete(
            '/api/v3/pool/1/',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if does not exist data inserted
        self.assertEqual(500, response.status_code, "Status code should be 500 and was %s" % response.status_code)

        # insert
        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(201, response.status_code, "Status code should be 201 and was %s" % response.status_code)

        id_pool = response.data[0]['id']

        # get data inserted
        response = self.client.get(
            '/api/v3/pool/%s/' % id_pool,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        data = response.data
        del data['server_pools'][0]['id']

        # test if data were inserted

        self.assertEqual(
            json.dumps(self.load_json_file(name_file), sort_keys=True),
            json.dumps(data, sort_keys=True),
            "jsons should same"
        )
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_put_valid_file(self):
        """ test_put_valid_file"""
        self.execute_some_put_verify_success(
            'api_pools/tests/json/put/test_pool_put_valid_file.json')

    def test_put_out_of_range_port(self):
        """ test_put_out_of_range_port"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_out_of_range_port.json')

    def test_put_negative_port(self):
        """ test_put_negative_port"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_negative_port.json')

    def test_put_float_port(self):
        """ test_put_float_port"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_float_port.json')

    def test_put_zero_port(self):
        """ test_put_zero_port"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_zero_port.json')

    def test_put_string_port(self):
        """ test_put_string_port"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_string_port.json')

    def test_put_float_environment(self):
        """ test_put_float_environment"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_float_environment.json')

    def test_put_string_environment(self):
        """ test_put_string_environment"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_string_environment.json')

    def test_put_zero_environment(self):
        """ test_put_zero_environment"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_zero_environment.json')

    def test_put_negative_environment(self):
        """ test_put_negative_environment"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_negative_environment.json')

    def test_put_integer_name_servicedownaction(self):
        """ test_put_integer_name_servicedownaction"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_integer_name_servicedownaction.json')

    def test_put_invalid_healthcheck_type(self):
        """ test_put_invalid_healthcheck_type"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_invalid_healthcheck_type.json')

    def test_put_invalid_destination(self):
        """ test_put_invalid_destination"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_invalid_destination.json')

    def test_put_negative_default_limit(self):
        """ test_put_negative_default_limit"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_negative_default_limit.json')

    def test_put_integer_lb_method(self):
        """ test_put_integer_lb_method"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_integer_lb_method.json')

    def test_put_string_id_servicedownaction(self):
        """  test_put_string_id_servicedownaction"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_string_id_servicedownaction.json')

    def test_put_zero_id_servicedownaction(self):
        """  test_put_zero_id_servicedownaction"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_zero_id_servicedownaction.json')

    def test_put_negative_id_servicedownaction(self):
        """  test_put_negative_id_servicedownaction"""
        self.execute_some_put_verify_error(
            'api_pools/tests/json/put/test_pool_put_negative_id_servicedownaction.json')

    def test_post_valid_file(self):
        """ test_post_valid_file"""
        self.execute_some_post_verify_success('api_pools/tests/json/post/test_pool_post_valid_file.json')

    def test_post_out_of_range_port(self):
        """ test_post_out_of_range_port"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_out_of_range_port.json')

    def test_post_negative_port(self):
        """ test_post_negative_port"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_negative_port.json')

    def test_post_float_port(self):
        """ test_post_float_port"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_float_port.json')

    def test_post_zero_port(self):
        """ test_post_zero_port"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_zero_port.json')

    def test_post_string_port(self):
        """ test_post_string_port"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_string_port.json')

    def test_post_float_environment(self):
        """ test_post_float_environment"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_float_environment.json')

    def test_post_string_environment(self):
        """ test_post_string_environment"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_string_environment.json')

    def test_post_zero_environment(self):
        """ test_post_zero_environment"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_zero_environment.json')

    def test_post_negative_environment(self):
        """ test_post_negative_environment"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_negative_environment.json')

    def test_post_integer_name_servicedownaction(self):
        """ test_post_integer_name_servicedownaction"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_integer_name_servicedownaction.json')

    def test_post_invalid_healthcheck_type(self):
        """ test_post_invalid_healthcheck_type"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_invalid_healthcheck_type.json')

    def test_post_invalid_destination(self):
        """ test_post_invalid_destination"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_invalid_destination.json')

    def test_post_negative_default_limit(self):
        """ test_post_negative_default_limit"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_negative_default_limit.json')

    def test_post_integer_lb_method(self):
        """ test_post_integer_lb_method"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_integer_lb_method.json')

    def test_post_string_id_servicedownaction(self):
        """  test_post_string_id_servicedownaction"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_string_id_servicedownaction.json')

    def test_post_zero_id_servicedownaction(self):
        """  test_post_zero_id_servicedownaction"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_zero_id_servicedownaction.json')

    def test_post_negative_id_servicedownaction(self):
        """  test_post_negative_id_servicedownaction"""
        self.execute_some_post_verify_error('api_pools/tests/json/post/test_pool_post_negative_id_servicedownaction.json')

    def test_valid_post_after_equals_valid_put(self):
        """ test_valid_post_after_equals_valid_put"""

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        response = self.client.put(
            '/api/v3/pool/1/',
            data=json.dumps(self.load_json_file('api_pools/tests/json/test_pool_put_and_post.json')),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file('api_pools/tests/json/test_pool_put_and_post.json')),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(400, response.status_code, "Status code should be 500 and was %s" % response.status_code)
