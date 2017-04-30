# -*- coding: utf-8 -*-
import os

from django.test.client import Client

from networkapi.test import load_json
from networkapi.test.test_case import NetworkApiTestCase


class RackTestCase(NetworkApiTestCase):
    fixtures = [

        # Vrfs
        'initial_vrf.json',

        # Filter
        'initial_filter.json',

        # Equipment Types
        'initial_tipo_equip.json',

        # Filter Equipment Type
        'initial_filterequiptype.json',

        # Network Type
        'initial_tipo_rede.json',

        # System Variables
        'initial_variables.json',

        # Options Pool
        'initial_optionspool.json',

        # Options Vip
        'initial_optionsvip.json',

        # Healthcheck
        'initial_healthcheck.json',

        # Equipment Brands
        'initial_equip_marca.json',
        # Equipment Models
        'initial_equip_model.json',
        # Equipments
        'initial_equipments.json',
        # Equipment Groups
        'initial_equip_grupos.json',

        # Users
        'initial_usuario.json',
        # User Groups
        'initial_ugrupo.json',

        # Object Types in Permissions
        'initial_objecttype.json',
        # Object Group Permission General
        'initial_objectgrouppermissiongeneral.json',
        # Permissions
        'initial_permissions.json',
        # Permissions by User Group
        'initial_permissoes_administrativas.json',
        # Permissions of Equipment Group by User Group
        'initial_direitos_grupos_equip.json',

        # Environment DCs
        'initial_environment_dc.json',
        # Logic environments
        'initial_environment_envlog.json',
        # L3 Group
        'initial_environment_gl3.json',
        # Environments
        'initial_environment.json',

        # Ip Config
        'initial_ipconfig.json',
        # Config Environment
        'initial_config_environment.json',

        # Equipment related with Equipment Group
        'initial_equipments_group.json',

        # Users related with User Group
        'initial_usuariogrupo.json',

        # Config
        'initial_config.json'
    ]

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_post_success(self):
        """ resultado esperado status 201"""
        response = self.client.post(
            '/api/rack/',
            self.load_rack_json('rack.json'),
            HTTP_AUTHORIZATION=self.get_http_authorization('test'))
        self.assertEqual(201, response.status_code,
                         'Status code should be 201 and was %s' % response.status_code)

    def load_rack_json(self, file_name):
        path = os.path.dirname(os.path.realpath(__file__)) + '/' + file_name
        return load_json(path)
