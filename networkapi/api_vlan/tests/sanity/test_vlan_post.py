# -*- coding: utf-8 -*-
import json
import logging

from django.core.management import call_command
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class VlanPostTestCase(NetworkApiTestCase):

    fixtures = [
        'loaddata',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/requisicaovips/fixtures/initial_optionsvip.json',
        'networkapi/api_vlan/fixtures/initial_base.json',
    ]

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_one_vlan_success(self):
        """Test success of post of one vlan."""

        name_file = 'api_vlan/tests/sanity/json/post/post_one_vlan.json'

        # Does post request
        response = self.client.post(
            '/api/v3/vlan/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/vlan/%s/' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id
        data = response.data
        del data['vlans'][0]['id']

        self.compare_json(name_file, data)

    def test_post_one_vlan_with_networks_success(self):
        """Test success of post of one vlan."""

        name_file = 'api_vlan/tests/sanity/json/post/post_one_vlan_with_networks.json'

        # Does post request
        response = self.client.post(
            '/api/v3/vlan/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/vlan/%s/' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        expected_data = self.load_json_file(name_file)
        received_data = response.data
        del received_data['vlans'][0]['id']
        del expected_data['vlans'][0]['create_networkv4']
        del expected_data['vlans'][0]['create_networkv6']

        expected_data = json.dumps(expected_data, sort_keys=True)
        received_data = json.dumps(received_data, sort_keys=True)

        self.assertEqual(
            expected_data,
            received_data,
            'Jsons should be same. Expected %s Received %s' % (
                expected_data, received_data)
        )

        search = {
            'extends_search': [{'vlan': id_env}],
            'end_record': 50,
            'start_record': 0,
            'searchable_columns': [],
            'asorting_cols': ['-id'],
            'custom_search': None
        }

        response = self.client.get(
            '/api/v3/networkv4/?search=%s' % search,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            1,
            response.data['total'],
            'Total of itens. Expected 1, Received %s' % (
                response.data['total'])
        )

        response = self.client.get(
            '/api/v3/networkv6/?search=%s' % search,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            1,
            response.data['total'],
            'Total of itens. Expected 1, Received %s' % (
                response.data['total'])
        )

    def test_post_one_vlan_without_number_success(self):
        """Test success of post of one vlan without number."""

        name_file = 'api_vlan/tests/sanity/json/post/post_one_vlan_without_number.json'

        # Does post request
        response = self.client.post(
            '/api/v3/vlan/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_env = response.data[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/vlan/%s/' % id_env,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id
        data = response.data
        del data['vlans'][0]['id']
        num_vlan = data['vlans'][0]['num_vlan']
        del data['vlans'][0]['num_vlan']

        self.compare_status(200, response.status_code)
        self.assertEqual(
            3,
            num_vlan,
            'Number Vlan should be %s and was %s' % (
                3, num_vlan)
        )

        self.compare_json(name_file, data)

    def test_post_one_vlan_number_duplicate_env_error(self):
        """Test error of post of one vlan duplicated number."""

        name_file = 'api_vlan/tests/sanity/json/post/post_one_vlan_number_duplicate_env.json'

        # Does post request
        response = self.client.post(
            '/api/v3/vlan/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        expected_data = 'Number VLAN can not be duplicated in the environment.'
        self.assertEqual(
            expected_data,
            response.data['detail'],
            'Details should be %s and was %s' % (
                expected_data, response.data['detail'])
        )

    def test_post_one_vlan_name_duplicate_env_error(self):
        """Test error of post of one vlan duplicated name."""

        name_file = 'api_vlan/tests/sanity/json/post/post_one_vlan_name_duplicate_env.json'

        # Does post request
        response = self.client.post(
            '/api/v3/vlan/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        expected_data = 'Name VLAN can not be duplicated in the environment.'
        self.assertEqual(
            expected_data,
            response.data['detail'],
            'Details should be %s and was %s' % (
                expected_data, response.data['detail'])
        )
