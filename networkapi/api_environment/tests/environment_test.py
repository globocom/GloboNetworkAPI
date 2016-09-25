# -*- coding: utf-8 -*-
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class EnvironmentTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_success_one_environment(self):
        """
        Test Success of get one environment
        """

        response = self.client.get(
            '/api/v3/environment/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )

    def test_get_success_two_environments(self):
        """
        Test Success of get two environment
        """

        response = self.client.get(
            '/api/v3/environment/1;2/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )

    def test_get_success_list_environments(self):
        """
        Test Success of environment list
        """

        response = self.client.get(
            '/api/v3/environment/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )

    def test_get_success_list_envs_rel_envvip(self):
        """
        Test Success of environment list related with environments vip
        """

        response = self.client.get(
            '/api/v3/environment/environment-vip/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )

    def test_get_success_list_envs_by_envvip(self):
        """
        Test Success of environment list by environment vip id
        """

        response = self.client.get(
            '/api/v3/environment/environment-vip/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )
