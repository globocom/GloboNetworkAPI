# -*- coding: utf-8 -*-
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class EnvironmentVipTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_success_one_environment(self):
        """
        Test Success of get one environment vip
        """

        response = self.client.get(
            '/api/v3/environment-vip/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )

    def test_get_success_two_environments_vip(self):
        """
        Test Success of get two environment vip
        """

        response = self.client.get(
            '/api/v3/environment-vip/1;2/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )

    # def test_get_success_list_environments_vip(self):
    #     """
    #     Test Success of environment vip list
    #     """

    #     response = self.client.get(
    #         '/api/v3/environment-vip/',
    #         content_type="application/json",
    #         HTTP_AUTHORIZATION=self.get_http_authorization('test'))

    #     self.assertEqual(
    #         200,
    #         response.status_code,
    #         "Status code should be 200 and was %s" % response.status_code
    #     )

    def test_get_success_list_envvip_step(self):
        """
        Test Success of environment vip by step
        """

        # get finalities
        url = '/api/v3/environment-vip/step/'
        response = self.client.get(
            url,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )

        # get clients
        url = '{0}?finality={1}'.format(
            url, response.data[0].get('finalidade_txt')
        )
        response = self.client.get(
            url,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )

        # get environments
        url = '{0}&client={1}'.format(
            url, response.data[0].get('cliente_txt')
        )
        response = self.client.get(
            url,
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )

    def test_get_success_list_options_by_envvip(self):
        """
        Test Success of options list by environment vip id
        """

        response = self.client.get(
            '/api/v3/option-vip/environment-vip/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )

    def test_get_success_list_options_by_envvip_and_type(self):
        """
        Test Success of options list by environment vip id and type option
        """

        response = self.client.get(
            '/api/v3/type-option/environment-vip/1/',
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )

        response = self.client.get(
            '/api/v3/option-vip/environment-vip/1/type-option/{0}/'.format(
                response.data[0]
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            "Status code should be 200 and was %s" % response.status_code
        )
