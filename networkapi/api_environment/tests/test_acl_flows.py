# -*- coding: utf-8 -*-

from json import dumps
from json import loads

from mock import patch

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase


class APIEnvironmentFlowsTestCase(NetworkApiTestCase):
    """ Test class for ACL flow using sync and async calls """

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_environment/fixtures/initial_base_pre_environment.json',
        'networkapi/api_environment/fixtures/initial_base_environment.json',
        'networkapi/api_environment/fixtures/initial_environment.json',
        'networkapi/api_environment/fixtures/initial_base.json',
        'networkapi/plugins/SDN/ODL/fixtures/initial_equipments.json',
    ]

    ENV_URL = "/api/v3/environment/%s/"

    ENV_ID = 1

    FLOW_URL = ENV_URL + "flows/%s/"

    def setUp(self):
        self.client = Client()

    def test_add_acl_flow_with_flow_id(self):
        """ Should insert an ACL flow using async call with flow id """
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

        response = self.client.post(
            self.FLOW_URL % (self.ENV_ID, data['rules'][0]['id']),
            dumps(data),
            HTTP_AUTHORIZATION=self.get_http_authorization('test'),
            content_type="application/json")

        resp_data = loads(response.content)

        assert response.status_code == 201
        assert resp_data['id'] == str(data['rules'][0]['id'])

    def test_add_acl_flow_with_no_id(self):
        """ Should insert an ACL flow using async call without ids """
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
        url = self.ENV_URL % self.ENV_ID
        response = self.client.post(
            url + "flows/",
            dumps(data),
            HTTP_AUTHORIZATION=self.get_http_authorization('test'),
            content_type="application/json")

        resp_data = loads(response.content)

        assert response.status_code == 201
        assert resp_data['id'] == str(self.ENV_ID)

    def test_delete_acl_flow_by_id(self, *args):
        """ Should delete an ACL flow """

        response = self.client.delete(
            self.FLOW_URL % (self.ENV_ID, 1),
            HTTP_AUTHORIZATION=self.get_http_authorization('test'),
            content_type="application/json")

        assert response.status_code == 200

    #TODO: test removing a environment. should remove all the flows

    @patch("networkapi.plugins.SDN.ODL.Generic.ODLPlugin.flush_flows")
    def test_delete_all_acl_flow_of_a_environment(self, *args):
        """ Should delete all ACL flows from a environment """

        plugin = args[0]

        response = self.client.delete(
            (self.ENV_URL+'flows/') % self.ENV_ID,
            HTTP_AUTHORIZATION=self.get_http_authorization('test'),
            content_type="application/json")

        assert plugin.called is True
        assert plugin.call_count == 1
        assert response.status_code == 200

    def test_update_acl_flow_with_flow_id(self, *args):
        """ Should update an ACL flow using async call with flow id """

        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "udp",
                "description": "simple flow",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
            }]
        }

        response = self.client.put(
            self.FLOW_URL % (self.ENV_ID, data['rules'][0]['id']),
            dumps(data),
            HTTP_AUTHORIZATION=self.get_http_authorization('test'),
            content_type="application/json")

        assert response.status_code == 200
        resp_data = loads(response.content)
        assert resp_data['id'] == str(data['rules'][0]['id'])

    def test_update_acl_flow_without_flow_id(self, *args):
        """ Should update an ACL flow using async call without flow id """

        data = {
            "kind": "default#acl",
            "rules": [{
                "id": 1,
                "protocol": "udp",
                "description": "simple flow",
                "source": "10.0.0.1/32",
                "destination": "10.0.0.2/32",
            }]
        }

        url = self.ENV_URL % self.ENV_ID
        response = self.client.put(
            url + "flows/",
            dumps(data),
            HTTP_AUTHORIZATION=self.get_http_authorization('test'),
            content_type="application/json")

        assert response.status_code == 200
        resp_data = loads(response.content)
        assert resp_data['id'] == str(self.ENV_ID)
