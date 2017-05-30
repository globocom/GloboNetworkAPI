# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class VlanPutTestCase(NetworkApiTestCase):

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

    def test_put_one_vlan_success(self):
        """Test success of simple put of one vlan."""

        name_file = 'api_vlan/tests/sanity/json/put/put_one_vlan.json'

        # Does post request
        response = self.client.put(
            '/api/v3/vlan/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/vlan/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_put_one_vlan_change_env_success(self):
        """Test success of put of one vlan changing environment."""

        name_file = 'api_vlan/tests/sanity/json/put/put_one_change_env_vlan.json'

        # Does post request
        response = self.client.put(
            '/api/v3/vlan/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/vlan/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_put_one_vlan_change_env_with_net_success(self):
        """Test success of put of one vlan with networks, changing environment.
        """

        name_file = 'api_vlan/tests/sanity/json/put/put_one_change_env_vlan_with_nets.json'

        # Does post request
        response = self.client.put(
            '/api/v3/vlan/4/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v3/vlan/4/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_put_one_activate_vlan_changing_env_error(self):
        """Test error of put of one activate vlan changing environment."""

        name_file = 'api_vlan/tests/sanity/json/put/put_one_change_env_' + \
            'vlan_activate_error.json'

        # Does post request
        response = self.client.put(
            '/api/v3/vlan/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        expected_data = 'Environment can not be changed in vlan actived.'
        self.assertEqual(
            expected_data,
            response.data['detail'],
            'Details should be %s and was %s' % (
                expected_data, response.data['detail'])
        )

    def test_put_one_activate_vlan_changing_num_vlan_error(self):
        """Test error of put of one activated vlan changing num vlan."""

        name_file = 'api_vlan/tests/sanity/json/put/put_one_change_num' + \
            '_vlan_activate_error.json'

        # Does post request
        response = self.client.put(
            '/api/v3/vlan/2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        expected_data = 'Number Vlan can not be changed in vlan actived.'
        self.assertEqual(
            expected_data,
            response.data['detail'],
            'Details should be %s and was %s' % (
                expected_data, response.data['detail'])
        )

    def test_put_one_activate_vlan_changing_name_vlan_error(self):
        """Test error of put of one activate vlan changing name vlan."""

        name_file = 'api_vlan/tests/sanity/json/put/put_one_change_name_' + \
            'vlan_activate_error.json'

        # Does post request
        response = self.client.put(
            '/api/v3/vlan/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        expected_data = 'Name Vlan can not be changed in vlan actived.'
        self.assertEqual(
            expected_data,
            response.data['detail'],
            'Details should be %s and was %s' % (
                expected_data, response.data['detail'])
        )

    def test_put_one_vlan_changing_env_net_with_envvip_error(self):
        """Test error of put of one vlan changing environments
        with networks related environment vip.
        """

        name_file = 'api_vlan/tests/sanity/json/put/put_one_change_env_net' + \
            '_with_envvip_error.json'

        # Does post request
        response = self.client.put(
            '/api/v3/vlan/3/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response.status_code)

        expected_data = 'Not change vlan when networks are of environment Vip.'
        self.assertEqual(
            expected_data,
            response.data['detail'],
            'Details should be %s and was %s' % (
                expected_data, response.data['detail'])
        )
