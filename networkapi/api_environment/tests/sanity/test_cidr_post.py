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

    post_path = 'api_environment/tests/sanity/json/post/%s'
    get_path = 'api_environment/tests/sanity/json/get/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_one_cidr(self):
        """Test of success to post 1 CIDR."""

        post_file = self.post_path % 'post_one_cidr.json'
        rcv_file = self.get_path % 'get_one_cidr.json'

        # post request
        response = self.client.post(
            '/api/v3/cidr/',
            data=json.dumps(self.load_json_file(post_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_cidr = response.data[0]['id']

        # get request
        response = self.client.get(
            '/api/v3/cidr/%s/' % id_cidr,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id
        data = response.data
        del data['cidr'][0]['id']

        self.compare_json(rcv_file, data)

    def test_post_two_cidrs(self):
        """Test of success to post 2 cidrs."""

        post_file = self.post_path % 'post_two_cidr.json'
        rcv_file = self.get_path % 'get_two_cidr.json'

        # post request
        response = self.client.post(
            '/api/v3/cidr/',
            data=json.dumps(self.load_json_file(post_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id1_cidr = response.data[0]['id']
        id2_cidr = response.data[1]['id']

        # get request
        response = self.client.get(
            '/api/v3/cidr/%s;%s/' % (id1_cidr, id2_cidr),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id/name in each dict
        data = response.data
        del data['cidr'][0]['id']
        del data['cidr'][1]['id']

        self.compare_json(rcv_file, data)

    def test_post_duplicated_cidr(self):
        """Test of error for post a duplicated cidr."""

        post_file = self.post_path % 'post_cidr_duplicate_error.json'

        # Does post request
        response_error = self.client.post(
            '/api/v3/cidr/',
            data=json.dumps(self.load_json_file(post_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response_error.status_code)

        self.compare_values(
            "10.225.0.0/24 overlaps 10.225.0.0/24",
            response_error.data['detail'])

    def test_post_invalid_cidr(self):
        """Test of error for post an invalid cidr."""

        post_file = self.post_path % 'post_cidr_invalid_error.json'

        # Does post request
        response_error = self.client.post(
            '/api/v3/cidr/',
            data=json.dumps(self.load_json_file(post_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response_error.status_code)

        self.compare_values(
            'invalid IPNetwork 300.0.0.0/24',
            response_error.data['detail'])

    def test_post_overlap_cidr(self):
        """Test of error for post an cidr that overlap."""

        post_file = self.post_path % 'post_cidr_overlap_error.json'

        # Does post request
        response_error = self.client.post(
            '/api/v3/cidr/',
            data=json.dumps(self.load_json_file(post_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(400, response_error.status_code)

        self.compare_values(
            '10.225.0.0/25 overlaps 10.225.0.0/24',
            response_error.data['detail'])

    def test_checkAvailableCIDR(self):
        """Test of Success to get the next available CIDR."""

        from networkapi.ambiente.models import EnvCIDR

        response, _ = EnvCIDR().checkAvailableCIDR(2, "v4")

        self.compare_values("10.0.6.0/24", response)

    def test_checkAvailableCIDRWithTwoBlocks(self):
        """Test of Success to get the next available CIDR
        when the environment father has two cidr and just
        one of them with subnet available."""

        from networkapi.ambiente.models import EnvCIDR

        response, _ = EnvCIDR().checkAvailableCIDR(7, "v4")

        self.compare_values("201.7.1.0/24", response)

    def test_AvailableCIDR(self):
        """Test of Success when the method has to find the
        subnet that was not allocate yeat."""

        from networkapi.ambiente.models import EnvCIDR

        response, _ = EnvCIDR().checkAvailableCIDR(10, "v4")

        self.compare_values("10.143.0.4/31", response)

    def test_allocateFirstSubnetCIDR(self):
        """Test of Success allocate the first subnet."""

        from networkapi.ambiente.models import EnvCIDR

        response, _ = EnvCIDR().checkAvailableCIDR(12, "v4")

        self.compare_values("10.224.0.0/27", response)

    def test_post_cidr_auto(self):
        """Test of success to allocate a new subnet."""

        post_file = self.post_path % 'post_cidr_auto.json'
        rcv_file = self.get_path % 'get_cidr_auto.json'

        # post request
        response = self.client.post(
            '/api/v3/cidr/',
            data=json.dumps(self.load_json_file(post_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        id_cidr = response.data[0]['id']

        # get request
        response = self.client.get(
            '/api/v3/cidr/%s/' % id_cidr,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # Removes property id
        data = response.data
        del data['cidr'][0]['id']

        self.compare_json(rcv_file, data)
