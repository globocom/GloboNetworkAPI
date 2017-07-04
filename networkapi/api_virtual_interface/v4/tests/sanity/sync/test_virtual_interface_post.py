# -*- coding: utf-8 -*-
import json

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

json_path = 'api_virtual_interface/v4/tests/sanity/sync/json/%s'


class VirtualInterfacePostSuccessTestCase(NetworkApiTestCase):
    """Class for Test Virtual Interface package Success POST cases."""

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/api_virtual_interface/v4/fixtures/initial_base.json',
        'networkapi/api_virtual_interface/v4/fixtures/initial_vrf.json',
        'networkapi/api_virtual_interface/v4/fixtures/initial_virtual_interface.json',
        'networkapi/api_virtual_interface/v4/fixtures/initial_neighbor.json',
        'networkapi/api_virtual_interface/v4/fixtures/initial_equipment.json',
        'networkapi/api_virtual_interface/v4/fixtures/initial_ipv4.json',
        'networkapi/api_virtual_interface/v4/fixtures/initial_ipv4_equipment.json',
        'networkapi/api_virtual_interface/v4/fixtures/initial_ipv6.json'
        'networkapi/api_virtual_interface/v4/fixtures/initial_ipv6_equipment.json',

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_post_one_virtual_interface(self):
        """Success Test of POST one Virtual Interface."""

        name_file = json_path % 'post/one_virtual_interface.json'

        # Does POST request
        response = self.client.post(
            '/api/v4/virtual-interface/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v4/virtual-interface/%s/?kind=basic' % response.data[0]['id']

        name_file_get = json_path % 'get/basic/pk_1.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        response.data['virtual_interfaces'][0]['id'] = 1
        self.compare_json(name_file_get, response.data['virtual_interfaces'])

    def test_post_two_virtual_interface(self):
        """Success Test of POST two Virtual Interface."""

        name_file = json_path % 'post/two_virtual_interface.json'

        # Does POST request
        response = self.client.post(
            '/api/v4/virtual-interface/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_url = '/api/v4/virtual-interface/%s;%s/?kind=basic' \
                  % (response.data[0]['id'],
                     response.data[1]['id'])

        name_file_get = json_path % 'get/basic/pk_1;2.json'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        response.data['virtual_interfaces'][0]['id'] = 1
        response.data['virtual_interfaces'][1]['id'] = 2

        self.compare_json(name_file_get, response.data['virtual_interfaces'])

