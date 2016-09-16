# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
# import mock
# from django.db import IntegrityError
# from django.test import TestCase
# from networkapi.usuario.tests import factory


LOG = logging.getLogger(__name__)

XML_EQUIPMENT_TYPE = """
<networkapi versao="1.0">
    <equipment_type>
        <name>%s</name>
    </equipment_type>
</networkapi>
"""


class TipoEquipamentoTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_create_equipment_type_with_sucess(self):
        # Issue a GET request.
        data = XML_EQUIPMENT_TYPE % ("teste1")
        response = self.client.post('/equipmenttype/',
                                    data=data,
                                    content_type='text/xml',
                                    HTTP_AUTHORIZATION=self.get_http_authorization('test'))

        LOG.debug(response)
        expected_response = '<?xml version="1.0" encoding="UTF-8"?><networkapi versao="1.0"><equipment_type><id>3</id></equipment_type></networkapi>'
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, expected_response)
