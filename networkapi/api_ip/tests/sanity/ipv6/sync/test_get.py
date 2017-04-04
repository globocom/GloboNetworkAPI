# -*- coding: utf-8 -*-
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

log = logging.getLogger(__name__)


class IPv6GetTestCase(NetworkApiTestCase):
    maxDiff = None

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_ip/fixtures/initial_base.json',
        'networkapi/api_ip/fixtures/initial_base_v6.json',
    ]

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_try_get_existent_ipv6_by_id(self):
        """Tests if NAPI can return an existing IPv6 by id."""

        name_file = 'api_ip/tests/sanity/ipv6/json/get/ipv6_1_net_5.json'

        # Does get request
        response = self.client.get(
            '/api/v3/ipv6/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_try_get_non_existent_ipv6_by_id(self):
        """Tests if NAPI returns error when ask to return not existing IPv6 by
        id.
        """

        response = self.client.get(
            '/api/v3/ipv6/1000/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Dont there is a IP by pk = 1000.',
            response.data['detail']
        )

    def test_try_get_two_existent_ipv6_by_id(self):
        """Tests if NAPI can return two existent IPv6's by ids."""

        name_file = 'api_ip/tests/sanity/ipv6/json/get/ipv6_1_2_net_5.json'

        # Does get request
        response = self.client.get(
            '/api/v3/ipv6/1;2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_try_get_two_non_existent_ipv6_by_id(self):
        """Tests if NAPI returns a error when ask to
        return two non existing IPv6's by ids.
        """

        response = self.client.get(
            '/api/v3/ipv6/1000;1001/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Dont there is a IP by pk = 1000.',
            response.data['detail']
        )

    def test_try_get_one_existent_and_non_existent_ipv6_by_id(self):
        """Tests if NAPI returns a error when ask to
        return a existing and not existing IPv6's by ids.
        """

        response = self.client.get(
            '/api/v3/ipv6/1;1001/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(404, response.status_code)
        self.compare_values(
            u'Dont there is a IP by pk = 1001.',
            response.data['detail']
        )

    def test_try_get_one_existent_ipv6_by_search(self):
        """Tests if NAPI returns a dict with one IPv6 Addresses
        given a search one existing IPv6 Addresses.
        """

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'block1': 'fc00',
                'block2': '0000',
                'block3': '0000',
                'block4': '0004',
                'block5': '0000',
                'block6': '0000',
                'block7': '0000',
                'block8': '0001'
            }]
        }

        fields = ['ip_formated']

        url = prepare_url('/api/v3/ipv6/', search=search, fields=fields)
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_values(1, response.data['total'])

        self.assertIn(
            {'ip_formated': 'fc00:0000:0000:0004:0000:0000:0000:0001'},
            response.data['ips'])

    def test_try_get_two_existent_ipv6_by_search(self):
        """Tests if NAPI returns a dict with two IPv6 Addresses
        given a search making OR by two IPv6 Addresses.
        """

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'block1': 'fc00',
                'block2': '0000',
                'block3': '0000',
                'block4': '0004',
                'block5': '0000',
                'block6': '0000',
                'block7': '0000',
                'block8': '0001'
            }, {
                'block1': 'fc00',
                'block2': '0000',
                'block3': '0000',
                'block4': '0004',
                'block5': '0000',
                'block6': '0000',
                'block7': '0000',
                'block8': '0002'
            }]
        }

        fields = ['ip_formated']

        url = prepare_url('/api/v3/ipv6/', search=search, fields=fields)
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_values(2, response.data['total'])

        self.assertIn(
            {'ip_formated': 'fc00:0000:0000:0004:0000:0000:0000:0001'},
            response.data['ips'])
        self.assertIn(
            {'ip_formated': 'fc00:0000:0000:0004:0000:0000:0000:0002'},
            response.data['ips'])

    def test_try_get_non_existent_ipv6_by_search(self):
        """Tests if NAPI returns a dict with zero IPv6 Addresses
        given a search by not existent IPv6 Address.
        """

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'block1': 'fc00',
                'block2': '0000',
                'block3': '0000',
                'block4': '0004',
                'block5': '0000',
                'block6': '0000',
                'block7': '0000',
                'block8': '0200'
            }]
        }

        url = prepare_url('/api/v3/ipv6/', search=search)
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_values(0, response.data['total'])
