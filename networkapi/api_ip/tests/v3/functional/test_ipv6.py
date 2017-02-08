# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.api_ip import facade
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.ip.models import IpNotFoundError
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario

log = logging.getLogger(__name__)


class IPv6FunctionalTestV3(NetworkApiTestCase):
    maxDiff = None

    def setUp(self):
        self.client = Client()
        self.user = Usuario(id=1, nome='test')
        self.url_prefix = '/api/v3/ipv6/%s/'
        self.status_code_msg = 'Status code should be %s and was %s'

    def tearDown(self):
        pass

    def test_try_get_existent_ipv6(self):
        id = 60

        response = self.client.get(
            self.url_prefix % id,
            HTTP_AUTHORIZATION=self.get_http_authorization('test')
        )

        ipv6 = response.data['ips'][0]
        expect_st_code = 200
        st_code = response.status_code

        self.assertIn('ips', response.data,
                      'Key "ips" should be present on response data.')

        self.assertEqual(id, ipv6['id'],
                         'IPv6 id retrieved should be equals')
        self.assertEqual(expect_st_code, st_code,
                         self.status_code_msg % (expect_st_code, st_code))

    def test_try_get_non_existent_ipv6(self):
        id = 1000

        response = self.client.get(
            self.url_prefix % id,
            HTTP_AUTHORIZATION=self.get_http_authorization('test'),
            raise_view_exceptions=True
        )

        self.assertNotIn('ips', response.data,
                         'Key "ips" should not be present on response data.')
