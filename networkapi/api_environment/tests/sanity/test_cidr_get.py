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

    get_path = 'api_environment/tests/sanity/json/get/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_one_cidr(self):
        """Test of success to get 1 CIDR."""

        # get request
        response = self.client.get(
            '/api/v3/cidr/2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

    def test_get_two_cidrs(self):
        """Test of success to get 2 cidrs."""

        # get request
        response = self.client.get(
            '/api/v3/cidr/2;3/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

    def test_get_success_list_cidrs(self):
        """Test of success of the list of cidrs."""

        rcv_file = self.get_path % 'get_list_cidr.json'

        response = self.client.get(
            '/api/v3/cidr/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id
        data = response.data
        del data['next_search']
        del data['total']
        del data['url_next_search']
        del data['url_prev_search']
        del data['prev_search']

        self.compare_json(rcv_file, data)

    def test_get_nonexistent_cidr_error(self):
        """Test of error for get a nonexistent cidr."""

        # Does post request
        response_error = self.client.get(
            '/api/v3/cidr/1000/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response_error.status_code)
