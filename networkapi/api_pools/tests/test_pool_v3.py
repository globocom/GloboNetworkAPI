# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class PoolTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_success(self):
        """ test_get_success"""
        response = self.client.get(
            '/api/v3/pool/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(
            self.load_json_file('api_pools/tests/json/test_pool_get.json'),
            response.data
        )
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_details_success(self):
        """ test_get_details_success"""
        response = self.client.get(
            '/api/v3/pool/details/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        log.info(response.data)
        self.assertEqual(
            self.load_json_file('api_pools/tests/json/test_pool_get_details.json'),
            response.data
        )
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_put_success(self):
        """ test_put_success"""
        # update
        response = self.client.put(
            '/api/v3/pool/1/',
            data=json.dumps(self.load_json_file('api_pools/tests/json/test_pool_put.json')),
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
            self.load_json_file('api_pools/tests/json/test_pool_put.json'),
            response.data
        )
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_post_success(self):
        """ test_post_success"""
        response = self.client.post(
            '/api/v3/pool/',
            data=json.dumps(self.load_json_file('api_pools/tests/json/test_pool_post.json')),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(201, response.status_code, "Status code should be 201 and was %s" % response.status_code)
