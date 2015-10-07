# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import mock
from django.test import TestCase
from django.test.client import Client
from django.db import IntegrityError
from networkapi.usuario.tests import factory
from networkapi.test.test_case import NetworkApiTestCase

import logging

LOG = logging.getLogger(__name__)

XML_EQUIPMENT_TYPE="""
<networkapi versao="1.0">
    <equipment_type>
        <name>%s</name>
    </equipment_type>
</networkapi>
"""
class TipoEquipamentoTestCase(NetworkApiTestCase):

    def setUp(self):
        self.client = Client()

    def __get_http_authorization(self):
        return "Basic dGVzdDp0ZXN0"

    def tearDown(self):
        pass

    def test_create_equipment_type_with_sucess(self):
        # Issue a GET request.
        data = XML_EQUIPMENT_TYPE % ("teste1")
        response = self.client.post('/equipmenttype/',
                                    data=data,
                                    content_type='text/xml',
                                    HTTP_AUTHORIZATION=self.__get_http_authorization())

        LOG.debug(response)
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
