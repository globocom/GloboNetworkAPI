# -*- coding: utf-8 -*-
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class PoolV3TestGetCase(NetworkApiTestCase):

    maxDiff = None

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_pool_list_details_success(self):
        """
        Test Success of pool list(details)
        """

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/details/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_one_pool_details_success(self):
        """
        Test Success of one pool(details)
        """

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/details/6/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_two_pool_details_success(self):
        """
        Test Success of two pools(details)
        """

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/details/6;7/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_pool_list_success(self):
        """
        Test Success of pool list
        """

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_one_pool_success(self):
        """
        Test Success of one pool
        """

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/6/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_two_pool_success(self):
        """
        Test Success of two pools
        """

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/6;7/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_pool_list_by_envvip_success(self):
        """
        Test Success of pool by environment vip
        """

        # try to get datas
        response = self.client.get(
            '/api/v3/pool/environment-vip/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_option_pool_list_by_envvip_success(self):
        """
        Test Success of pool by environment vip
        """

        # try to get datas
        response = self.client.get(
            '/api/v3/option-pool/environment/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # test if data were not inserted
        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)
