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
        verbosity=0
    )

class RackTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def test_post_success(self):
        """ Should post a new Rack """

        response = self.client.post('/api/rack/',
                                    data=json.dumps(self.load_json_file(
                                        "api_rack/tests/rack/json/rack.json")),
                                    content_type='application/json',
                                    HTTP_AUTHORIZATION=self.get_http_authorization('test'))

