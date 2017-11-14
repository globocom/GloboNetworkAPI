# -*- coding: utf-8 -*-
from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url_with_ids
from networkapi.util.geral import prepare_url


class ListConfigBGPGetSuccessTestCase(NetworkApiTestCase):

    list_config_bgp_uri = '/api/v4/list-config-bgp/'
    fixtures_path = 'networkapi/api_list_config_bgp/v4/fixtures/{}'

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        fixtures_path.format('initial_list_config_bgp.json'),

    ]

    json_path = 'api_list_config_bgp/v4/tests/sanity/json/get/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_get_basic_lists_config_bgp(self):
        """Test of success to get lists config bgp with kind=basic."""

        lists_config_bgp_path = self.json_path.format('pk_1;2_basic.json')

        get_ids = [1, 2]
        uri = mount_url_with_ids(self.list_config_bgp_uri, get_ids)
        uri = prepare_url(uri,
                          kind=['basic'])

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(lists_config_bgp_path, response.data)

    def test_get_details_lists_config_bgp(self):
        """Test of success to get lists config bgp with kind=details."""

        lists_config_bgp_path = self.json_path.format('pk_1;2_details.json')

        get_ids = [1, 2]
        uri = mount_url_with_ids(self.list_config_bgp_uri, get_ids)
        uri = prepare_url(uri,
                          kind=['details'])

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(lists_config_bgp_path, response.data)


class ListConfigBGPGetErrorTestCase(NetworkApiTestCase):

    pass
