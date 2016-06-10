# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import base64
import logging

from django.test import TestCase

LOG = logging.getLogger(__name__)


class NetworkApiTestCase(TestCase):

    fixtures = [
        'initial_ugrupo.json',
        'initial_equip_grupos.json',
        'initial_permissions.json',
        'initial_permissoes_administrativas.json',
        'initial_direitos_grupos_equip.json',
        'initial_usuario.json',
        'initial_variables.json',
        'initial_tipo_equip.json',
        'initial_equip_marca.json',
        'initial_equip_model.json',
        'initial_equipments.json',
        'initial_environment_dc.json',
        'initial_environment_envlog.json',
        'initial_environment_gl3.json',
        'initial_environment.json',
        'initial_optionspool.json',
        'initial_pools_healthcheck.json',
        'initial_pools.json',
    ]

    def setUp(self):
        pass

    def get_http_authorization(self, user):
        return 'Basic %s' % base64.b64encode("%s:teste" % user)

    def tearDown(self):
        pass
