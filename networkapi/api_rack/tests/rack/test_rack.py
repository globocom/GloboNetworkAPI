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
        'networkapi/api_rack/fixtures/initial_fabric.json',
        'networkapi/api_equipment/fixtures/initial_equipments_switches.json',
        verbosity=0
    )


class RackGetTest(NetworkApiTestCase):

    fixtures = [
        'networkapi/api_rack/fixtures/initial_rack.json'
    ]

    def setUp(self):
        self.client = Client()

    def test_list_rack(self):
        """Test of success to list all racks."""

        expected_file = 'api_rack/tests/rack/json/list_rack.json'

        response = self.client.get('/api/rack/',
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_json(expected_file, response.data)

    def test_getbyid_rack(self):
        """Test of success to list all racks."""

        expected_file = 'api_rack/tests/rack/json/get_rack.json'

        response = self.client.get('/api/rack/10/',
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_json(expected_file, response.data)

    def test_getbyfabricid_rack(self):
        """Test of success to list all racks."""

        expected_file = 'api_rack/tests/rack/json/get_rack.json'

        response = self.client.get('/api/rack/fabric/1/',
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_json(expected_file, response.data)


class RackPostTest(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def test_post_rack(self):
        """Test of success to insert a new rack."""

        response = self.client.post('/api/rack/',
                                    data=json.dumps(self.load_json_file(
                                        "api_rack/tests/rack/json/post_rack.json")),
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(201, response.status_code)


class RackPutTest(NetworkApiTestCase):

    fixtures = [
        'networkapi/api_rack/fixtures/initial_rack.json'
    ]

    def setUp(self):
        self.client = Client()

    def test_put_rack(self):
        """Test of success to edit a Rack."""

        expected_file = 'api_rack/tests/rack/json/expected_file_put_rack.json'

        response = self.client.put('/api/rack/10/',
                                   data=json.dumps(self.load_json_file(
                                        "api_rack/tests/rack/json/put_rack.json")),
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)
        self.compare_json(expected_file, response.data)

class RackDeleteTest(NetworkApiTestCase):

    fixtures = [
        'networkapi/api_rack/fixtures/initial_rack.json'
    ]

    def setUp(self):
        self.client = Client()

    def test_delete_rack(self):
        """Test of success for delete one rack."""

        response = self.client.delete('/api/rack/10/',
                                      content_type='application/json',
                                      HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(200, response.status_code)

        # check if the rack was deleted
        response = self.client.get('/api/rack/10/',
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        self.compare_status(500, response.status_code)
