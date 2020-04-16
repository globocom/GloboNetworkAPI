# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class TestCIDRPostTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_environment/fixtures/initial_base_pre_environment.json',
        'networkapi/api_environment/fixtures/initial_base_environment.json',
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_cidr.json',
    ]

    put_path = 'api_environment/tests/sanity/json/put/%s'
    get_path = 'api_environment/tests/sanity/json/get/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_edit_one_cidr(self):
        """Test of success to edit a CIDR."""

        put_file = self.put_path % 'put_one_cidr.json'

        # post request
        response = self.client.put(
            '/api/v3/cidr/',
            data=json.dumps(self.load_json_file(put_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        id_cidr = response.data[0]['id']

        # get request
        response = self.client.get(
            '/api/v3/cidr/%s/' % id_cidr,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(put_file, response.data)

    def test_put_with_duplicated_cidr(self):
        """Test of error for edit a cidr with a duplicated network."""

        put_file = self.put_path % 'put_cidr_duplicate_error.json'

        # Does post request
        response_error = self.client.put(
            '/api/v3/cidr/',
            data=json.dumps(self.load_json_file(put_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response_error.status_code)

        self.compare_values(
            "192.168.10.0/24 overlaps 192.168.0.0/8",
            response_error.data['detail'])

    def test_put_invalid_cidr(self):
        """Test of error for edit a cidr with an invalid network."""

        put_file = self.put_path % 'put_cidr_invalid_error.json'

        # Does post request
        response_error = self.client.put(
            '/api/v3/cidr/',
            data=json.dumps(self.load_json_file(put_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response_error.status_code)

        self.compare_values(
            'invalid IPNetwork 300.0.0.0/24',
            response_error.data['detail'])

    def test_put_env_cidr(self):
        """Test of error for edit a cidr and change the environment."""

        put_file = self.put_path % 'put_cidr_environment.json'

        # Does post request
        response_error = self.client.put(
            '/api/v3/cidr/',
            data=json.dumps(self.load_json_file(put_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response_error.status_code)

    def test_put_env_cidr_overlap_error(self):
        """Test of error for edit a cidr."""

        put_file = self.put_path % 'put_cidr_env_overlap_error.json'

        # Does post request
        response_error = self.client.put(
            '/api/v3/cidr/',
            data=json.dumps(self.load_json_file(put_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response_error.status_code)

        self.compare_values(
            '201.7.0.0/24 overlaps 201.7.0.0/16',
            response_error.data['detail'])

    def test_put_env_cidr_invalid_error(self):
        """Test of error for edit a cidr."""

        put_file = self.put_path % 'put_cidr_env_invalid_error.json'

        # Does post request
        response_error = self.client.put(
            '/api/v3/cidr/',
            data=json.dumps(self.load_json_file(put_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response_error.status_code)

        self.compare_values(
            'invalid IPNetwork 300.7.0.0/24',
            response_error.data['detail'])
