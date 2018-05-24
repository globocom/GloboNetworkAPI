# -*- coding: utf-8 -*-

import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class InterfaceDeleteTestCase(NetworkApiTestCase):

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
        'networkapi/api_interface/fixtures/initial_interface_connected.json',
    ]

    json_path = 'api_interface/tests/sanity/json/%s'

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_delete_interface_not_connected(self):
        """Test of success to delete one interface."""

        interface_id = "1"

        response = self.client.delete('/api/v3/interface/%s/' % interface_id,
                                      content_type='application/json',
                                      HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

    def test_delete_interface_connected(self):
        """
        Test of success to delete one connected interface.
        It should not delete an interface connected.
        """

        interface_id = "3"

        try:
            response = self.client.delete('/api/v3/interface/%s/' % interface_id,
                                          content_type='application/json',
                                          HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        except:
            pass

        self.compare_status(500, response.status_code)

        response = self.client.get('/api/v3/interface/%s/' % interface_id,
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
