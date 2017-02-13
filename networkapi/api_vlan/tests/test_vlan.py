# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class VlanTest(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_success_one_vlan(self):
        """Test success of get of one vlan."""

        name_file = 'api_vlan/tests/json/get_one_vlan.json'

        response = self.client.get(
            '/api/v3/vlan/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_get_success_search_vlan(self):
        """Test success of list of vlan."""

        search = {
            'extends_search': [{'nome': 'VLAN 1 - AMBIENTE 1'}],
            'end_record': 50,
            'start_record': 0,
            'searchable_columns': [],
            'asorting_cols': ['-id'],
            'custom_search': None
        }

        response = self.client.get(
            '/api/v3/vlan/?search=%s' % search,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            200,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

    def test_get_search_vlan_field_error(self):
        """Test success of list of vlan."""

        search = {
            'extends_search': [{'vlan': 'VLAN 1 - AMBIENTE 1'}],
            'end_record': 50,
            'start_record': 0,
            'searchable_columns': [],
            'asorting_cols': ['-id'],
            'custom_search': None
        }

        response = self.client.get(
            '/api/v3/vlan/?search=%s' % search,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.assertEqual(
            400,
            response.status_code,
            'Status code should be 200 and was %s' % response.status_code
        )

        expected_data = 'Cannot resolve keyword \'vlan\' into field.' + \
            ' Choices are: acl_draft, acl_draft_v6, acl_file_name,' + \
            ' acl_file_name_v6, acl_valida, acl_valida_v6, ambiente,' + \
            ' ativada, descricao, id, networkipv4, networkipv6, nome,' +\
            ' num_vlan, vrf, vrfvlanequipment'

        self.assertEqual(
            expected_data,
            response.data['detail'],
            'Details should be %s and was %s' % (
                expected_data, response.data['detail'])
        )

    def test_get_success_one_vlan_details(self):
        """Test success of get of one vlan with details."""

        name_file = 'api_vlan/tests/json/get_one_vlan_details.json'

        response = self.client.get(
            '/api/v3/vlan/1/?kind=details',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_post_one_vlan_success(self):
        """Test success of post of one vlan."""

        name_file = 'api_vlan/tests/json/post_one_vlan.json'

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

    def test_post_one_vlan_without_number_success(self):
        """Test success of post of one vlan without number."""

        name_file = 'api_vlan/tests/json/post_one_vlan_without_number.json'

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

        name_file = 'api_vlan/tests/json/post_one_vlan_number_duplicate_env.json'

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

        name_file = 'api_vlan/tests/json/post_one_vlan_name_duplicate_env.json'

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
