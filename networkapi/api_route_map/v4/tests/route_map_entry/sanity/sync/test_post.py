# -*- coding: utf-8 -*-
import json

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import mount_url


class ListConfigBGPPostSuccessTestCase(NetworkApiTestCase):

    list_config_bgp_uri = '/api/v4/list-config-bgp/'

    fixtures = [
        'networkapi/config/fixtures/initial_config.json',
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
    ]

    json_path = 'api_list_config_bgp/v4/tests/sanity/json/post/{}'

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')
        self.content_type = 'application/json'
        self.fields = ['name', 'type', 'config', 'created']

    def tearDown(self):
        pass

    def test_post_lists_config_bgp(self):
        """Test POST ListsConfigBGP."""

        lists_config_bgp_path = self.json_path.\
            format('two_lists_config_bgp.json')

        response = self.client.post(
            self.list_config_bgp_uri,
            data=self.load_json(lists_config_bgp_path),
            content_type=self.content_type,
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(201, response.status_code)

        get_ids = [data['id'] for data in response.data]
        uri = mount_url(self.list_config_bgp_uri,
                        get_ids,
                        kind=['basic'],
                        fields=self.fields)

        response = self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)
        self.compare_json(lists_config_bgp_path,
                          response.data)
