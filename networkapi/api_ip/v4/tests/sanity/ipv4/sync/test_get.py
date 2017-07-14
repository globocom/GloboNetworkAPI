# -*- coding: utf-8 -*-
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

log = logging.getLogger(__name__)


class IPv4GetTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_ip/v4/fixtures/initial_base.json',
        'networkapi/api_ip/v4/fixtures/initial_base_v4.json',
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_try_get_existent_ipv4_by_id(self):
        """V4 Tests if NAPI can return an existing IPv4 by id."""

        name_file = 'api_ip/v4/tests/sanity/ipv4/json/get/ipv4_1_net_5.json'

        # Does get request
        response = self.client.get(
            '/api/v4/ipv4/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_try_get_non_existent_ipv4_by_id(self):
        """V4 Tests if NAPI returns error when ask
        to return not existing IPv4 by id.
        """

        response = self.client.get(
            '/api/v4/ipv4/1000/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'There is no IP with pk = 1000.',
            response.data['detail']
        )

    def test_try_get_two_existent_ipv4_by_id(self):
        """V4 Tests if NAPI can return two existent IPv4's by ids."""

        name_file = 'api_ip/v4/tests/sanity/ipv4/json/get/ipv4_1_2_net_5.json'

        # Does get request
        response = self.client.get(
            '/api/v4/ipv4/1;2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_try_get_two_non_existent_ipv4_by_id(self):
        """V4 Tests if NAPI returns a error when ask to
        return two non existing IPv4's by ids.
        """

        response = self.client.get(
            '/api/v4/ipv4/1000;1001/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'There is no IP with pk = 1000.',
            response.data['detail']
        )

    def test_try_get_one_existent_and_non_existent_ipv4_by_id(self):
        """V4 Tests if NAPI returns a error when ask to
        return a existing and not existing IPv4's by ids.
        """

        response = self.client.get(
            '/api/v4/ipv4/1;1001/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)
        self.compare_values(
            u'There is no IP with pk = 1001.',
            response.data['detail']
        )

    def test_try_get_one_existent_ipv4_by_search(self):
        """V4 Tests if NAPI returns a dict with one IPv4 Addresses
        given a search one existing IPv4 Addresses.
        """

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 1
            }]
        }

        fields = ['ip_formated']

        url = prepare_url('/api/v4/ipv4/', search=search, fields=fields)
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        self.compare_values(1, response.data['total'])

        self.assertIn({'ip_formated': '10.0.0.1'}, response.data['ips'])

    def test_try_get_two_existent_ipv4_by_search(self):
        """V4 Tests if NAPI returns a dict with two IPv4 Addresses
        given a search making OR by two IPv4 Addresses.
        """

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 1
            }, {
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 2
            }]
        }

        fields = ['ip_formated']

        url = prepare_url('/api/v4/ipv4/', search=search, fields=fields)
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        self.compare_values(2, response.data['total'])

        self.assertIn({'ip_formated': '10.0.0.1'}, response.data['ips'])
        self.assertIn({'ip_formated': '10.0.0.2'}, response.data['ips'])

    def test_try_get_non_existent_ipv4_by_search(self):
        """V4 Tests if NAPI returns a dict with zero IPv4 Addresses
        given a search by not existent IPv4 Address.
        """

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 200
            }]
        }

        url = prepare_url('/api/v4/ipv4/', search=search)
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)
        self.compare_values(0, response.data['total'])

    def test_try_get_ipv4_with_equipments_and_virtual_interfaces(self):
        """V4 Test to GET ipv4 with associated equipments and virtual
           interfaces.
        """

        name_file = 'api_ip/v4/tests/sanity/ipv4/json/get/' \
                    'ipv4_with_eqpts_and_virtual_interfaces.json'

        # Does get request
        response = self.client.get(
            '/api/v4/ipv4/6/?include=equipments',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_get_ipv4_by_kind_details(self):
        """V4 Test of success to get IPv4 with kind details."""

        name_file = 'api_ip/v4/tests/sanity/ipv4/json/get/' \
                    'details/pk_6.json'

        response = self.client.get(
            '/api/v4/ipv4/6/?kind=details',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)
