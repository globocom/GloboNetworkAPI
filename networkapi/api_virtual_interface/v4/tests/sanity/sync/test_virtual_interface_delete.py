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
        'networkapi/api_virtual_interface/v4/fixtures/initial_ipv6.json',
        'networkapi/api_virtual_interface/v4/fixtures/initial_ipv6_equipment.json',

    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_delete_virt_interf_related_to_ipv4_v6_equipment_and_neighbor(self):
        """Success Test of DELETE one Virtual Interface present in IpEquipment,
           Ipv6Equipment relationships and related to Neighbor."""

        # Test delete Virtual Interface 3 that is associated to Neighbor 2 and
        # has relationship Ip-Equipment 1-3 and Ipv6-Equipment 1-3

        response = self.client.delete(
            '/api/v4/virtual-interface/3/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v4/virtual-interface/3/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Virtual Interface 3 do not exist.',
            response.data['detail']
        )

        # Check if neighbor was deleted
        response = self.client.get(
            '/api/v4/neighbor/2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Neighbor 2 do not exist.',
            response.data['detail']
        )

        # Chech if in Ip-Equipment 2-3, Virtual-Interface was changed to None
        response = self.client.get(
            '/api/v4/ipv4/2/?include=equipments',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        expected = {'equipment': 3, 'virtual_interface': None}
        equipments = response.data['ips'][0]['equipments'][0]
        self.assertEqual(expected, equipments)

        # Chech if in Ipv6-Equipment 2-3, Virtual-Interface was changed to None
        response = self.client.get(
            '/api/v4/ipv6/2/?include=equipments',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        expected = {'equipment': 3, 'virtual_interface': None}
        equipments = response.data['ips'][0]['equipments'][0]
        self.assertEqual(expected, equipments)

    def test_delete_two_virtual_interface(self):
        """Success Test of DELETE two Virtual Interface."""

        # Test delete Virtual Interface

        response = self.client.delete(
            '/api/v4/virtual-interface/2;4/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v4/virtual-interface/2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Virtual Interface 2 do not exist.',
            response.data['detail']
        )

        response = self.client.get(
            '/api/v4/virtual-interface/4/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Virtual Interface 4 do not exist.',
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
