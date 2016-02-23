# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.test import TestCase


import logging

LOG = logging.getLogger(__name__)

class NetworkApiTestCase(TestCase):

    fixtures = ['initial_ugrupo.json',
                'initial_equip_grupos.json',
                'initial_permissions.json',
                'initial_permissoes_administrativas.json',
                'initial_direitos_grupos_equip.json',
                'initial_usuario.json',
                'initial_variables.json',
                'initial_tipo_equip.json',
                'initial_equip_marca.json',
                'initial_equip_model.json',
                'initial_equipments.json']

    def setUp(self):
        pass

    def get_http_authorization(self):
        return "Basic dGVzdDp0ZXN0"

    def tearDown(self):
        pass

