# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

log = logging.getLogger(__name__)


class IPv6PutTestCase(NetworkApiTestCase):
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

    def test_try_update_ip_associating_to_equipment(self):
        """Tests if NAPI can update IPv6 associating it to equipment."""

        name_file = 'api_ip/tests/sanity/ipv6/json/put/ipv6_put_1_net_5_eqpt_1.json'

        response = self.client.put(
            '/api/v3/ipv6/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # API will return success but network will not be changed
        self.compare_status(200, response.status_code)

        # Does get request
        url = prepare_url('/api/v3/ipv6/1/', fields=['id', 'equipments'])
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_try_update_ip_disassociating_it_of_all_equipments(self):
        """Tests if NAPI can update IPv6 disassociating it of equipment and
        keep this IPv6.
        """

        name_file = 'api_ip/tests/sanity/ipv6/json/put/ipv6_put_2_net_5_eqpt_none.json'

        response = self.client.put(
            '/api/v3/ipv6/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # API will return success but network will not be changed
        self.compare_status(200, response.status_code)

        # Does get request
        url = prepare_url('/api/v3/ipv6/2/', fields=['id', 'equipments'])
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

    def test_try_update_ip_disassociating_it_of_equipments_and_associating_to_others_after(self):
        """Tests if NAPI can update IPv6 disassociating it of equipment
        and at same time associating it to other equipment.
        """

        name_file = 'api_ip/tests/sanity/ipv6/json/put/ipv6_put_2_net_5_eqpt_2.json'

        response = self.client.put(
            '/api/v3/ipv6/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # API will return success but network will not be changed
        self.compare_status(200, response.status_code)

        # Does get request
        url = prepare_url('/api/v3/ipv6/2/', fields=['id', 'equipments'])
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_try_update_ip_changing_network(self):
        """Tests if NAPI deny or ignore update of IPv6 Address changing its network."""

        name_file = 'api_ip/tests/sanity/ipv6/json/put/ipv6_put_1_net_6.json'

        response = self.client.put(
            '/api/v3/ipv6/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # API will return success but network will not be changed
        self.compare_status(200, response.status_code)

        # Does get request
        url = prepare_url('/api/v3/ipv6/1/', fields=['id', 'networkipv6'])
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_values(5, response.data['ips'][0]['networkipv6'])

    def test_try_update_ip_changing_octets(self):
        """Tests if NAPI deny or ignore update of IPv6 Address changing its octets."""

        name_file = 'api_ip/tests/sanity/ipv6/json/put/ipv6_put_1_change_block_net_5.json'

        response = self.client.put(
            '/api/v3/ipv6/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        # API will return success but network will not be changed
        self.compare_status(200, response.status_code)

        # Does get request
        url = prepare_url('/api/v3/ipv6/1/', fields=['id', 'ip_formated'])
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_values('fc00:0000:0000:0004:0000:0000:0000:0001',
                            response.data['ips'][0]['ip_formated'])
