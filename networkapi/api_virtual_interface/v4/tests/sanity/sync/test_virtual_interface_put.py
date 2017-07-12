# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url
import json

json_path = 'api_virtual_interface/v4/tests/sanity/sync/json/%s'


class VirtualInterfacePutSuccessTestCase(NetworkApiTestCase):
    """Class for Test Virtual Interface package Success PUT cases."""

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
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_put_one_virtual_interface(self):
        """Success Test of PUT one Virtual Interface."""

        name_file = json_path % 'put/one_virtual_interface.json'

        # Does PUT request
        response = self.client.put(
            '/api/v4/virtual-interface/1/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v4/virtual-interface/1/?kind=basic'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)

    def test_put_two_virtual_interface(self):
        """Success Test of PUT two Virtual Interface."""

        name_file = json_path % 'put/two_virtual_interface.json'

        # Does PUT request
        response = self.client.put(
            '/api/v4/virtual-interface/1;2/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

        get_url = '/api/v4/virtual-interface/1;2/?kind=basic'

        response = self.client.get(
            get_url,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        self.compare_json(name_file, response.data)


class VirtualInterfacePutErrorTestCase(NetworkApiTestCase):
    """Class for Test Virtual Interface package Error PUT cases."""

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
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_put_one_inexistent_virtual_interface(self):
        """Error Test of PUT one inexistent Virtual Interface."""

        name_file = json_path % 'put/inexistent_virtual_interface.json'

        response = self.client.put(
            '/api/v4/virtual-interface/1000/',
            data=json.dumps(self.load_json_file(name_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Virtual Interface 1000 do not exist.',
            response.data['detail']
        )
