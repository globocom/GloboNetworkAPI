# -*- coding: utf-8 -*-
import json
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class InterfacePostTestCase(NetworkApiTestCase):

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
        'networkapi/api_equipment/fixtures/initial_equipments_switches.json',
        'networkapi/api_interface/fixtures/initial_interface.json',
    ]

    json_path = 'api_interface/tests/sanity/json/interface_environments/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_one_interface_environments(self):
        """Test of success associating an interface to an environment."""

        post_file = self.json_path % 'post/post_interface_environments.json'
        expected_file = self.json_path % 'get/get_interface_environments.json'

        # Does post request
        response = self.client.post(
            '/api/v3/interface/environments/',
            data=json.dumps(self.load_json_file(post_file)),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)

        interface_environments_id = response.data.get('interface_environments')[0]['id']

        # Does get request
        response = self.client.get(
            '/api/v3/interface/environments/%s/' % interface_environments_id,
            content_type='application/json',
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        data = response.data
        del data['interface_environments'][0]['id']

        self.compare_json(expected_file, data)
