# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class InterfacePutTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_environment/fixtures/initial_base_pre_environment.json',
        'networkapi/api_environment/fixtures/initial_base_environment.json',
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_base.json',
        'networkapi/api_equipment/fixtures/initial_pre_equipment.json',
        'networkapi/api_equipment/fixtures/initial_equipments_switches.json',  # 2leafes e 1 oob
        'networkapi/api_interface/fixtures/initial_interface.json',  # uma interface desconectada
        'networkapi/api_interface/fixtures/initial_interface_connected.json',  # 3 interfaces

    ]

    json_path = 'api_interface/tests/sanity/json/interface/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_put_interface(self):
        """Test of success to put one interface."""

        name_file = self.json_path % 'put/put_one_interface.json'

        put_response = self.client.put('/api/v3/interface/%s/' % 2,
                                       data=json.dumps(self.load_json_file(name_file)),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, put_response.status_code)

        get_response = self.client.get('/api/v3/interface/%s/' % 2,
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        data = get_response.data
        del data['interfaces'][0]['channel']

        self.compare_status(200, get_response.status_code)
        self.compare_json(name_file, get_response.data)

    def test_edit_interface(self):
        """Test of success to edit one interface."""

        name_file = self.json_path % 'put/put_interface_configs.json'

        put_response = self.client.put('/api/v3/interface/%s/' % 2,
                                       data=json.dumps(self.load_json_file(name_file)),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, put_response.status_code)

        get_response = self.client.get('/api/v3/interface/%s/' % 2,
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        data = get_response.data
        del data['interfaces'][0]['channel']

        self.compare_status(200, get_response.status_code)
        self.compare_json(name_file, get_response.data)

    def test_edit_equip_of_interface(self):
        """Test of success to edit the equipment of an interface."""

        name_file = self.json_path % 'put/put_interface_equipment.json'

        put_response = self.client.put('/api/v3/interface/%s/' % 2,
                                       data=json.dumps(self.load_json_file(name_file)),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, put_response.status_code)

        get_response = self.client.get('/api/v3/interface/%s/' % 2,
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, get_response.status_code)
        self.compare_json(name_file, get_response.data)

    def test_connect_interfaces(self):
        """Test of success to connect two interfaces."""

        name_file = self.json_path % 'put/put_connect_interfaces.json'
        expected_file = self.json_path % 'put/expected_file_put_connect_interfaces.json'

        interface_id = 2
        interface_linked = 4

        put_response = self.client.put('/api/v3/interface/%s/' % interface_id,
                                       data=json.dumps(self.load_json_file(name_file)),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, put_response.status_code)

        get_response = self.client.get('/api/v3/interface/%s;%s/' % (interface_id, interface_linked),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, get_response.status_code)
        self.compare_json(expected_file, get_response.data)

    def test_remove_interface_link(self):
        """Test of success to remove the link between two interfaces."""

        name_file = self.json_path % 'put/put_remove_link_interfaces.json'
        expected_file = self.json_path % 'put/expected_file_put_remove_link_interfaces.json'
        interface_id = 3
        interface_linked = 5

        put_response = self.client.put('/api/v3/interface/%s/' % interface_id,
                                       data=json.dumps(self.load_json_file(name_file)),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, put_response.status_code)

        get_response = self.client.get('/api/v3/interface/%s;%s/' % (interface_id, interface_linked),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        data = get_response.data.get('interfaces')

        for interface in data:
            del interface['channel']
            del interface['back_interface']

        self.compare_status(200, get_response.status_code)
        self.compare_json(expected_file, get_response.data)

    def test_edit_linked_interface(self):
        """Test of success to edit a linked interface."""

        name_file = self.json_path % 'put/put_edit_linked_interface.json'
        expected_file = self.json_path % 'put/expected_file_put_edit_linked_interface.json'
        interface_id = 6
        interface_linked = 7

        put_response = self.client.put('/api/v3/interface/%s/' % interface_id,
                                       data=json.dumps(self.load_json_file(name_file)),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, put_response.status_code)

        get_response = self.client.get('/api/v3/interface/%s;%s/' % (interface_id, interface_linked),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, get_response.status_code)
        self.compare_json(expected_file, get_response.data)

    def test_update_interface_link(self):
        """Test of success to update the interface link."""

        name_file = self.json_path % 'put/update_interface_link.json'
        expected_file = self.json_path % 'put/expected_file_update_interface_link.json'
        interface_id = 9
        interface_after = 10
        interface_before = 8

        put_response = self.client.put('/api/v3/interface/%s/' % interface_id,
                                       data=json.dumps(self.load_json_file(name_file)),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, put_response.status_code)

        get_response = self.client.get('/api/v3/interface/%s;%s;%s/' %(interface_id, interface_after, interface_before),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, get_response.status_code)
        self.compare_json(expected_file, get_response.data)

    def test_update_interface_link_err(self):
        """Test of failure when trying to link an interface to other that already linked."""

        name_file = self.json_path % 'put/update_interface_link_err.json'
        expected_file = self.json_path % 'put/expected_file_update_interface_link_err.json'
        interface_id = 1
        interface_linked_1 = 11
        interface_linked_2 = 12
        interfaces = "%s;%s;%s" % (interface_id, interface_linked_1, interface_linked_2)

        try:
            put_response = self.client.put('/api/v3/interface/%s/' % interface_id,
                                           data=json.dumps(self.load_json_file(name_file)),
                                           content_type='application/json',
                                           HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        except:
            pass

        self.compare_status(500, put_response.status_code)

        get_response = self.client.get('/api/v3/interface/%s/' % interfaces,
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, get_response.status_code)
        self.compare_json(expected_file, get_response.data)

    def test_update_interface_link_err_2(self):
        """Test of failure when trying to link an interface connected to other interface already connected."""

        name_file = self.json_path % 'put/update_interface_link_err_2.json'
        expected_file = self.json_path % 'put/expected_file_update_interface_link_err_2.json'
        interface_id = 9
        interface_other = 8
        interface_linked_1 = 11
        interface_linked_2 = 12
        interfaces = "%s;%s;%s;%s" % (interface_other, interface_id, interface_linked_1, interface_linked_2)

        try:
            put_response = self.client.put('/api/v3/interface/%s/' % interface_id,
                                           data=json.dumps(self.load_json_file(name_file)),
                                           content_type='application/json',
                                           HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        except:
            pass

        self.compare_status(500, put_response.status_code)

        get_response = self.client.get('/api/v3/interface/%s/' % interfaces,
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, get_response.status_code)
        self.compare_json(expected_file, get_response.data)
