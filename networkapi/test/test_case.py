# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import base64
import json
import logging

from django.test import TestCase

from networkapi.settings import local_files
from networkapi.test import load_json

LOG = logging.getLogger(__name__)


class NetworkApiTestCase(TestCase):

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

        # Environment Vip
        'initial_environment_vip.json',

        # Vlans
        'initial_vlan.json',

        # Networkv4
        'initial_networkipv4.json',

        # Ipv4
        'initial_ipv4.json',

        # Ipv4 related with equipment
        'initial_ipv4_eqpt.json',

        # Equipment related with Equipment Group
        'initial_equipments_group.json',

        # Users related with User Group
        'initial_usuariogrupo.json',

        # Equipaments related with environment
        'initial_equipments_env.json',
        # Environment Vip related with environment
        'initial_environment_env_vip.json',

        # Pools
        'initial_pools.json',
        # Pool Members
        'initial_pool_members.json',

        # Vips
        'initial_vip_request.json',
        'initial_vip_request_port.json',
        'initial_vip_request_port_options_vip.json',
        'initial_vip_request_port_pool.json',
        'initial_vip_request_options_vip.json',
        'initial_vip_request_dscp.json',

        # Config
        'initial_config.json'
    ]

    def setUp(self):
        pass

    def get_http_authorization(self, user):
        return 'Basic %s' % base64.b64encode('%s:teste' % user)

    def tearDown(self):
        pass

    def load_json_file(self, file_name):
        return load_json(local_files(file_name))

    def compare_json(self, name_file, data):
        expected_data = json.dumps(
            self.load_json_file(name_file), sort_keys=True)
        received_data = json.dumps(data, sort_keys=True)
        self.assertEqual(
            expected_data,
            received_data,
            'Jsons should be same. Expected %s Received %s' % (
                expected_data, received_data)
        )

    def compare_status(self, expected_code, code):
        self.assertEqual(
            expected_code,
            code,
            'Status code should be %s and was %s' % (
                expected_code, code)
        )
