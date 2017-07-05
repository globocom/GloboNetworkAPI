# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

json_path = 'api_virtual_interface/v4/tests/sanity/sync/json/%s'

class VirtualInterfaceGetSuccessTestCase(NetworkApiTestCase):
    """Class for Test Virtual Interface package Success GET cases."""

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

    def test_get_one_basic_virtual_interface(self):
        """Success Test of GET one Basic Virtual Interface."""

        name_file = json_path % 'get/basic/pk_1.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/virtual-interface/1/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['virtual_interfaces'])

    def test_get_two_basic_virtual_interface(self):
        """Success Test of GET two Basic Virtual Interface."""

        name_file = json_path % 'get/basic/pk_1;2.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/virtual-interface/1;2/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['virtual_interfaces'])

    def test_get_one_virtual_interface_with_ipv4_equipment_field(self):
        """Success Test of GET one Virtual Interface with ipv4_equipment field."""

        name_file = json_path % 'get/basic/pk_1_with_ipv4_equipment.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/virtual-interface/1/?include=ipv4_equipment',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['virtual_interfaces'])

    def test_get_one_virtual_interface_with_ipv6_equipment_field(self):
        """Success Test of GET one Virtual Interface with ipv6_equipment field."""

        name_file = json_path % 'get/basic/pk_1_with_ipv6_equipment.json'

        # Make a GET request
        response = self.client.get(
            '/api/v4/virtual-interface/1/?include=ipv6_equipment',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['virtual_interfaces'])

    def test_get_one_virtual_interface_by_search(self):
        """Success Test of GET basic Virtual Interface."""

        name_file = json_path % 'get/basic/pk_1.json'

        search = {
            'start_record': 0,
            'end_record': 25,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [{
                'ipequipamento__equipamento__in': [1,2],
            }]
        }

        get_url = prepare_url('/api/v4/virtual-interface/',
                              search=search, kind=['basic'])

        # Make a GET request
        response = self.client.get(
            get_url,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        self.compare_json_lists(name_file, response.data['virtual_interfaces'])


class VirtualInterfaceGetErrorTestCase(NetworkApiTestCase):
    """Class for Test Virtual Interface package Error GET cases."""

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

    def test_get_one_inexistent_virtual_interface(self):
        """Error Test of GET one inexistent Virtual Interface."""

        # Make a GET request
        response = self.client.get(
            '/api/v4/virtual-interface/1000/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Virtual Interface 1000 do not exist.',
            response.data['detail']
        )

    def test_get_two_inexistent_virtual_interface(self):
        """Error Test of GET two inexistent Virtual Interface."""

        # Make a GET request
        response = self.client.get(
            '/api/v4/virtual-interface/1000;1001/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Virtual Interface 1000 do not exist.',
            response.data['detail']
        )

    def test_get_one_existent_and_one_inexistent_virtual_interface(self):
        """Error Test of GET one existent and one inexistent Virtual Interface."""

        # Make a GET request
        response = self.client.get(
            '/api/v4/virtual-interface/1;1000/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Virtual Interface 1000 do not exist.',
            response.data['detail']
        )

