# -*- coding: utf-8 -*-
import json
import logging

from django.core.management import call_command
from networkapi.test.test_case import NetworkApiTestCase
from networkapi.usuario.models import Usuario
from rest_framework.test import APIClient

log = logging.getLogger(__name__)


def setup():
    call_command(
        'loaddata',
        'networkapi/system/fixtures/basic_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        verbosity=0
    )


class DatacenterPostTest(NetworkApiTestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def test_datacenter_post(self):
        """Test of success to insert a new datacenter."""

        response = self.client.post('/api/dc/',
                                    data=json.dumps(self.load_json_file(
                                        "api_rack/tests/datacenter/json/post_datacenter.json")),
                                    content_type='application/json'
                                    )

        self.compare_status(201, response.status_code)


class DatacenterGetTest(NetworkApiTestCase):
    fixtures = [
        'networkapi/api_rack/fixtures/initial_datacenter.json'
    ]

    def setUp(self):
        self.client = APIClient()
        self.user = Usuario.objects.get(user='test')
        self.client.force_authenticate(user=self.user)

    def test_list_datacenter(self):
        """Test of success to list all datacenters."""

        expected_file = 'api_rack/tests/datacenter/json/listdc.json'

        response = self.client.get('/api/dc/',
                                   content_type='application/json'
                                   )

        self.compare_status(200, response.status_code)
        self.compare_json(expected_file, response.data)
