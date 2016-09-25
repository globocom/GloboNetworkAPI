# -*- coding: utf-8 -*-
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class VipRequestTestV3Case(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_one_vip_success(self):
        """
        Test Success of one vip request
        """
        response = self.client.get(
            '/api/v3/vip-request/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_two_vip_success(self):
        """
        Test Success of two vips request
        """
        response = self.client.get(
            '/api/v3/vip-request/1;2/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_list_vip_success(self):
        """
        Test Success of vip request list
        """
        response = self.client.get(
            '/api/v3/vip-request/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_one_vip_details_success(self):
        """
        Test Success of one vip request(details)
        """
        response = self.client.get(
            '/api/v3/vip-request/details/2/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_two_vip_details_success(self):
        """
        Test Success of two vips request(details)
        """
        response = self.client.get(
            '/api/v3/vip-request/details/1;2/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_list_vip_details_success(self):
        """
        Test Success of vip request list(details)
        """
        response = self.client.get(
            '/api/v3/vip-request/details/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)

    def test_get_list_vip_by_pool_success(self):
        """
        Test Success of request by pool
        """
        response = self.client.get(
            '/api/v3/vip-request/pool/2/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(200, response.status_code, "Status code should be 200 and was %s" % response.status_code)
