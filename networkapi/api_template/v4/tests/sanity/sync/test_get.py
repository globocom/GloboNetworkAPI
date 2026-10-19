# -*- coding: utf-8 -*-
import os
import shutil
import tempfile

from django.test.client import Client
from mock import patch

from networkapi.test.test_case import NetworkApiTestCase


class TemplateGetTestCase(NetworkApiTestCase):

    template_uri = '/api/v4/templates/'

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

        self.base_dir = tempfile.mkdtemp()
        self.dirs = dict()
        for dir_name in ('rack', 'config', 'config/bgp'):
            path = os.path.join(self.base_dir, dir_name)
            os.mkdir(path)
            self.dirs[dir_name] = path

        self._write('rack', 'TEMPLATE_R', 'rack content R')
        self._write('config', 'TEMPLATE_A', 'config content A')
        self._write('config/bgp', 'TEMPLATE_A', 'bgp content A')
        with open(os.path.join(self.base_dir, 'SECRET'), 'w') as f:
            f.write('secret')

        self.patcher = patch(
            'networkapi.api_template.v4.facade.get_template_root',
            side_effect=lambda template_type: self.dirs[template_type])
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        shutil.rmtree(self.base_dir)

    def _write(self, dir_name, name, content):
        path = os.path.join(self.base_dir, dir_name, name)
        with open(path, 'w') as f:
            f.write(content)

    def _get(self, uri):
        return self.client.get(
            uri,
            HTTP_AUTHORIZATION=self.authorization
        )

    def _assert_text(self, expected, response):
        self.compare_status(200, response.status_code)
        self.assertTrue(response['Content-Type'].startswith('text/plain'))
        self.compare_values(expected, response.content)

    def test_get_rack_template(self):
        """Test GET rack template returns its exact content as text."""

        response = self._get(self.template_uri + 'rack/TEMPLATE_R/')

        self._assert_text('rack content R', response)

    def test_get_config_template_in_root(self):
        """Test GET config template in the root directory."""

        response = self._get(self.template_uri + 'config/TEMPLATE_A/')

        self._assert_text('config content A', response)

    def test_get_config_template_in_subdirectory(self):
        """Test GET config template following the path."""

        response = self._get(self.template_uri + 'config/bgp/TEMPLATE_A/')

        self._assert_text('bgp content A', response)

    def test_get_template_without_trailing_slash(self):
        """Test GET template without trailing slash."""

        response = self._get(self.template_uri + 'config/bgp/TEMPLATE_A')

        self._assert_text('bgp content A', response)

    def test_get_template_invalid_type(self):
        """Test GET template with invalid type."""

        response = self._get(self.template_uri + 'bgp/TEMPLATE_A/')

        self.compare_status(404, response.status_code)

    def test_get_template_wrong_type(self):
        """Test GET template that does not exist in the given type."""

        response = self._get(self.template_uri + 'rack/TEMPLATE_A/')

        self.compare_status(404, response.status_code)

    def test_get_template_directory(self):
        """Test GET a directory instead of a template."""

        response = self._get(self.template_uri + 'config/bgp/')

        self.compare_status(404, response.status_code)

    def test_get_inexistent_template(self):
        """Test GET inexistent template."""

        response = self._get(self.template_uri + 'config/bgp/INEXISTENT/')

        self.compare_status(404, response.status_code)
        self.compare_values(
            u'Template bgp/INEXISTENT not found.',
            response.data['detail']
        )

    def test_get_template_path_traversal(self):
        """Test GET template rejects `..`, `.` and empty segments."""

        for path in ('config/../SECRET/', 'config/bgp/../../SECRET/',
                     'config/..%2FSECRET/', 'config/..%2F..%2FSECRET/',
                     'config/bgp/../TEMPLATE_A/', 'config/./TEMPLATE_A/',
                     'config/bgp//TEMPLATE_A/', 'config/..',
                     'config/bgp%5C..%5CTEMPLATE_A/',
                     'rack/../config/TEMPLATE_A/'):
            response = self._get(self.template_uri + path)

            self.compare_status(400, response.status_code)

    def test_get_template_without_auth(self):
        """Test GET template without authentication."""

        response = self.client.get(self.template_uri + 'rack/TEMPLATE_R/')

        self.compare_status(401, response.status_code)
