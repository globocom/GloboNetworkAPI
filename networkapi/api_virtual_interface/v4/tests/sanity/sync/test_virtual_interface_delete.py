# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

json_path = 'api_virtual_interface/v4/tests/sanity/sync/json/%s'


class VirtualInterfaceDeleteSuccessTestCase(NetworkApiTestCase):
    """Class for Test Virtual Interface package Success DELETE cases."""

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

    def test_delete_one_virtual_interface(self):
        """Success Test of DELETE one Virtual Interface."""

        response = self.client.delete(
            '/api/v4/virtual-interface/3/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v4/virtual-interface/3/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Virtual Interface 3 do not exist.',
            response.data['detail']
        )

    def test_delete_two_virtual_interface(self):
        """Success Test of DELETE two Virtual Interface."""

        response = self.client.delete(
            '/api/v4/virtual-interface/3;4/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        for id_ in xrange(3, 4+1):
            response = self.client.get(
                '/api/v4/virtual-interface/%s/' % id_,
                HTTP_AUTHORIZATION=self.authorization
            )

            self.compare_status(404, response.status_code)

            self.compare_values(
                u'Virtual Interface %s do not exist.' % id_,
                response.data['detail']
            )


class VirtualInterfaceDeleteErrorTestCase(NetworkApiTestCase):
    """Class for Test Virtual Interface package Error DELETE cases."""

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

    def test_delete_one_inexistent_virtual_interface(self):
        """Error Test of DELETE one inexistent Virtual Interface."""

        delete_url = '/api/v4/virtual-interface/1000/'

        response = self.client.delete(
            delete_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Virtual Interface 1000 do not exist.',
            response.data['detail']
        )
