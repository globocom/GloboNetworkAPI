# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import base64
import logging

from django.test import TestCase

from networkapi.settings import local_files
from networkapi.test import load_json

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
        'initial_healthcheck.json',
        'initial_pools.json',
        'initial_optionsvip.json',
        'initial_tipo_rede.json',
        'initial_vlan.json',
    ]

    def setUp(self):
        pass

    def get_http_authorization(self, user):
        return 'Basic %s' % base64.b64encode("%s:teste" % user)

    def tearDown(self):
        pass

    def load_json_file(self, file_name):
        return load_json(local_files(file_name))
