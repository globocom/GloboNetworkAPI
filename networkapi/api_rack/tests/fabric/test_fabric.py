# -*- coding: utf-8 -*-
import json
import os
import logging

from django.core.management import call_command
from django.test.client import Client

from networkapi.rack.models import Datacenter
from networkapi.test.test_case import NetworkApiTestCase

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
        'networkapi/api_rack/fixtures/initial_datacenter.json',
        verbosity=0
    )


class FabricGetTest(NetworkApiTestCase):

    fixtures = [
        'networkapi/api_rack/fixtures/initial_fabric.json'
    ]

    def setUp(self):
        self.client = Client()

    def test_list_fabric(self):
        """Test of success to list all fabrics."""

        expected_file = 'api_rack/tests/fabric/json/list_fabric.json'

        response = self.client.get('/api/dcrooms/',
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_json(expected_file, response.data)

    def test_getfabricbyid(self):
        """Test of success to get a fabric by idt."""

        expected_file = 'api_rack/tests/fabric/json/get_fabric.json'

        response = self.client.get('/api/dcrooms/id/1/',
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_json(expected_file, response.data)

    def test_getfabricbydcid(self):
        """Test of success to get a fabric by datacenter id."""

        expected_file = 'api_rack/tests/fabric/json/get_fabric.json'

        response = self.client.get('/api/dcrooms/dc/1/',
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_json(expected_file, response.data)

    def test_getfabricbyname(self):
        """Test of success to get a fabric by name."""

        expected_file = 'api_rack/tests/fabric/json/get_fabric.json'
        uri = '/api/dcrooms/name/%s' % "FabricTest"

        response = self.client.get(uri,
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_json(expected_file, response.data)


class FabricPostTest(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def test_fabric_post(self):
        """Test of success to insert a new fabric."""

        response = self.client.post('/api/dcrooms/',
                                    data=json.dumps(self.load_json_file(
                                        "api_rack/tests/fabric/json/post_fabric.json")),
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)


class FabricPutTest(NetworkApiTestCase):

    fixtures = [
        'networkapi/api_rack/fixtures/initial_fabric.json'
    ]

    def setUp(self):
        self.client = Client()

    def test_put_fabric(self):
        """Test of success to edit a fabric."""

        expected_file = 'api_rack/tests/fabric/json/put_fabric.json'

        response = self.client.put('/api/dcrooms/id/1/',
                                   data=json.dumps(self.load_json_file(
                                        "api_rack/tests/fabric/json/put_fabric.json")),
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_json(expected_file, response.data)