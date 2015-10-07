# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import mock
from django.test import TestCase
from django.db import IntegrityError
from networkapi.usuario.tests import factory

import logging

LOG = logging.getLogger(__name__)

XML_EQUIPMENT_TYPE="""
<?xml version="1.0" encoding="UTF-8"?>
<networkapi versao="1.0">
    <equipment_type>
        <name>teste1</name>
    </equipment_type>
</networkapi>
"""
class TipoEquipamentoTestCase(TestCase):

    #fixtures = ['initial_usuario.json']

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_equipment_type_with_sucess(self):
        pass
