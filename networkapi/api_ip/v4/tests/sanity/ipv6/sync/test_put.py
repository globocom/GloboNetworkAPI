# -*- coding: utf-8 -*-
import json
import logging

from networkapi.usuario.models import Usuario
from rest_framework.test import APIClient

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

log = logging.getLogger(__name__)


class IPv6PutTestCaseV4(NetworkApiTestCase):
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
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        pass

    def test_try_update_ip_associating_to_equipment(self):
        """V4 Tests if NAPI can update IPv6 associating it to equipment."""

        name_file = 'api_ip/tests/sanity/ipv6/json/put/ipv6_put_1_net_5_eqpt_1.json'

        response = self.client.put(
            '/api/v4/ipv6/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json')

        # API will return success but network will not be changed
        self.compare_status(200, response.status_code)

        # Does get request
        url = prepare_url('/api/v4/ipv6/1/', fields=['id', 'equipments'])
        response = self.client.get(
            url,
            content_type='application/json')

        self.compare_status(200, response.status_code)

        name_file = 'api_ip/v4/tests/sanity/ipv6/json/get/ipv6_put_1_net_5_eqpt_1.json'

        for ip in response.data['ips']:
            for equipment in ip['equipments']:
                del equipment['id']

        self.compare_json(name_file, response.data)

    def test_try_update_ip_disassociating_it_of_all_equipments(self):
        """V4 Tests if NAPI can update IPv6 disassociating it of equipment and
        keep this IPv6.
        """

        name_file = 'api_ip/tests/sanity/ipv6/json/put/ipv6_put_2_net_5_eqpt_none.json'

        response = self.client.put(
            '/api/v4/ipv6/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json')

        # API will return success but network will not be changed
        self.compare_status(200, response.status_code)

        # Does get request
        url = prepare_url('/api/v4/ipv6/2/', fields=['id', 'equipments'])
        response = self.client.get(
            url,
            content_type='application/json')

        self.compare_status(200, response.status_code)

    def test_try_update_ip_disassociating_it_of_equipments_and_associating_to_others_after(self):
        """V4 Tests if NAPI can update IPv6 disassociating it of equipment
        and at same time associating it to other equipment.
        """

        name_file = 'api_ip/tests/sanity/ipv6/json/put/ipv6_put_2_net_5_eqpt_2.json'

        response = self.client.put(
            '/api/v4/ipv6/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json')

        # API will return success but network will not be changed
        self.compare_status(200, response.status_code)

        # Does get request
        url = prepare_url('/api/v4/ipv6/2/', fields=['id', 'equipments'])
        response = self.client.get(
            url,
            content_type='application/json')

        self.compare_status(200, response.status_code)

        name_file = 'api_ip/v4/tests/sanity/ipv6/json/get/ipv6_put_2_net_5_eqpt_2.json'

        for ip in response.data['ips']:
            for equipment in ip['equipments']:
                del equipment['id']

        self.compare_json(name_file, response.data)

    def test_try_update_ip_changing_network(self):
        """V4 Tests if NAPI deny or ignore update of IPv6 Address changing its network."""

        name_file = 'api_ip/tests/sanity/ipv6/json/put/ipv6_put_1_net_6.json'

        response = self.client.put(
            '/api/v4/ipv6/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json')

        # API will return success but network will not be changed
        self.compare_status(200, response.status_code)

        # Does get request
        url = prepare_url('/api/v4/ipv6/1/', fields=['id', 'networkipv6'])
        response = self.client.get(
            url,
            content_type='application/json')

        self.compare_status(200, response.status_code)

        self.compare_values(5, response.data['ips'][0]['networkipv6'])

    def test_try_update_ip_changing_octets(self):
        """V4 Tests if NAPI deny or ignore update of IPv6 Address changing its octets."""

        name_file = 'api_ip/tests/sanity/ipv6/json/put/ipv6_put_1_change_block_net_5.json'

        response = self.client.put(
            '/api/v4/ipv6/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json')

        # API will return success but network will not be changed
        self.compare_status(200, response.status_code)

        # Does get request
        url = prepare_url('/api/v4/ipv6/1/', fields=['id', 'ip_formated'])
        response = self.client.get(
            url,
            content_type='application/json')

        self.compare_status(200, response.status_code)

        self.compare_values('fc00:0000:0000:0004:0000:0000:0000:0001',
                            response.data['ips'][0]['ip_formated'])
