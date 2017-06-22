# -*- coding: utf-8 -*-

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase


class APIEnvironmentFlowsTestCase(NetworkApiTestCase):

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
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_base.json',
        'networkapi/plugins/SDN/ODL/fixtures/initial_equipments.json',
    ]

    ENV_URL = "/api/v3/environment/%s/"

    ENV_ID = 1

    FLOW_URL = ENV_URL + "flows/%s"

    def setUp(self):
        self.client = Client()

    def test_add_acl_flow(self):
        """ Should insert a flow using async call """
        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "tcp",
                "description": "simple flow",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
            }]
        }

        response = self.client.put(
            self.FLOW_URL % (self.ENV_ID, data['rules'][0]['id']),
            data,
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))

    def test_delete_acl_flow(self):
        pass

    def test_update_acl_flow(self):
        pass
