# -*- coding: utf-8 -*-
import json
import logging

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from networkapi.util.geral import prepare_url
from rest_framework.test import APIClient

log = logging.getLogger(__name__)


class IPv4GetTestCaseV4(NetworkApiTestCase):
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
        'networkapi/api_ip/fixtures/initial_base_v4.json',
    ]

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        pass

    def test_try_create_auto_ip(self):
        """V4 Tests if NAPI can allocate automatically an IPv4 Address
        in a Network with available addresses.
        """

        name_file = 'api_ip/tests/sanity/ipv4/json/post/ipv4_auto_net_free.json'

        # Does get request
        response = self.client.post(
            '/api/v4/ipv4/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json')

        self.compare_status(201, response.status_code)

        url = prepare_url('/api/v4/ipv4/%s/' % response.data[0]['id'],
                          fields=['ip_formated'])
        response = self.client.get(
            url,
            content_type='application/json')

        self.compare_status(200, response.status_code)
        self.compare_values('10.0.1.2', response.data['ips'][0]['ip_formated'])

    def test_try_create_invalid_ip(self):
        """V4 Tests if NAPI deny manually creation of invalid IPv4 Address
        (e.g.: 10.0.0.430).
        """

        name_file = 'api_ip/tests/sanity/ipv4/json/post/ipv4_10_0_0_430_net_5.json'
        response = self.client.post(
            '/api/v4/ipv4/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json')

        self.compare_status(400, response.status_code)
        self.compare_values(
            'Error save new IP.: 10.0.0.430',
            response.data['detail'])

    def test_try_create_ip_associating_to_equipment(self):
        """V4 Tests if NAPI can allocate an IPv4 Address manually and associate
        it to an equipment in a Network with available addresses.
        """

        name_file = 'api_ip/tests/sanity/ipv4/json/post/ipv4_10_0_0_99_net_5_eqpt_1.json'
        response = self.client.post(
            '/api/v4/ipv4/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json')

        self.compare_status(201, response.status_code)

        url = prepare_url('/api/v4/ipv4/%s/' % response.data[0]['id'],
                          fields=['ip_formated'])
        response = self.client.get(
            url,
            content_type='application/json')

        self.compare_status(200, response.status_code)
        self.compare_values('10.0.0.99',
                            response.data['ips'][0]['ip_formated'])

    def test_try_create_ip_in_full_network(self):
        """ V4 Tests if NAPI deny an IPv4 manually creation in a full network.
            Refactor to allow create the ip."""

        name_file = 'api_ip/tests/sanity/ipv4/json/post/ipv4_10_0_4_1_net_8.json'
        response = self.client.post(
            '/api/v4/ipv4/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json')

        self.compare_status(201, response.status_code)

    def test_try_create_out_of_range_ip_in_network(self):
        """V4 Tests if NAPI deny out of range network IPv4 manually creation."""

        name_file = 'api_ip/tests/sanity/ipv4/json/post/out_of_range_ipv4_172_0_0_5_net_5.json'
        response = self.client.post(
            '/api/v4/ipv4/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json')

        self.compare_status(400, response.status_code)
        self.compare_values(
            'Ip 172.0.0.5 not available for network 5.',
            response.data['detail'])
