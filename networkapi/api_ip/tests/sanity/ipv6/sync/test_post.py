# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

log = logging.getLogger(__name__)


class IPv6PostTestCase(NetworkApiTestCase):
    fixtures = [
        'networkapi/config/fixtures/initial_config.json',
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

    def test_try_create_auto_ip(self):
        """Tests if NAPI can allocate automatically an IPv6 Address
        in a Network with available addresses.
        """

        name_file = 'api_ip/tests/sanity/ipv6/json/post/ipv6_auto_net_free.json'

        # Does get request
        response = self.client.post(
            '/api/v3/ipv6/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        url = prepare_url('/api/v3/ipv6/%s/' % response.data[0]['id'],
                          fields=['ip_formated'])
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_values(
            'fc00:0000:0000:0004:0000:0000:0000:0004',
            response.data['ips'][0]['ip_formated'])

    def test_try_create_invalid_ip(self):
        """Tests if NAPI deny manually creation of invalid IPv6 Address
        (e.g.: fc00:0000:0000:0004:0000:0000:0000:gggg).
        """

        name_file = 'api_ip/tests/sanity/ipv6/json/post/ipv6_invalid_ip_manual_net_5.json'
        response = self.client.post(
            '/api/v3/ipv6/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)
        self.compare_values(
            'Error save new IPV6.: fc00:0000:0000:0004:0000:0000:0000:gggg',
            response.data['detail'])

    def test_try_create_ip_associating_to_equipment(self):
        """Tests if NAPI can allocate an IPv6 Address manually and associate it to
        an equipment in a Network with available addresses.
        """

        name_file = 'api_ip/tests/sanity/ipv6/json/post/ipv6_new_ip_manual_net_5.json'
        response = self.client.post(
            '/api/v3/ipv6/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        url = prepare_url('/api/v3/ipv6/%s/' % response.data[0]['id'],
                          fields=['ip_formated'])
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_values('fc00:0000:0000:0004:0000:0000:0000:0099',
                            response.data['ips'][0]['ip_formated'])

    def test_try_create_ip_in_full_network(self):
        """Tests if NAPI deny an IPv6 manually creation in a full network."""

        name_file = 'api_ip/tests/sanity/ipv6/json/post/ipv6_new_ip_manual_net_8_full.json'
        response = self.client.post(
            '/api/v3/ipv6/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)
        self.compare_values(
            'Ip fc00:0000:0000:0007:0000:0000:0000:0001 not available for network 8.',
            response.data['detail'])

    def test_try_create_out_of_range_ip_in_network(self):
        """Tests if NAPI deny out of range network IPv6 manually creation."""

        name_file = 'api_ip/tests/sanity/ipv6/json/post/out_of_range_ipv6_fc00_0000_0000_0005_0000_0000_0000_0005_net_5.json'
        response = self.client.post(
            '/api/v3/ipv6/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)
        self.compare_values(
            'Ip fc00:0000:0000:0005:0000:0000:0000:0005 not available for network 5.',
            response.data['detail'])
