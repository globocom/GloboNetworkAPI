# -*- coding: utf-8 -*-

import logging
import urllib

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class InterfaceGetTestCase(NetworkApiTestCase):

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

    json_path = 'api_interface/tests/sanity/json/interface/get/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_get_interface_by_id(self):
        """Test of success to get interface."""

        expected_data = self.json_path % 'get_interface.json'

        response = self.client.get('/api/v3/interface/1/',
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_json(expected_data, response.data["interfaces"])

    def test_get_interface_by_search(self):
        """Test of success to get interface."""

        expected_data = self.json_path % 'get_interface.json'

        search = urllib.urlencode({'extends_search': [],
                                   'start_record': 0,
                                   'custom_search': '',
                                   'end_record': 10000,
                                   'asorting_cols': [],
                                   'searchable_columns': []})

        url = '/api/v3/interface/?search=%s' % search

        response = self.client.get(url,
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_json(expected_data, response.data["interfaces"])
