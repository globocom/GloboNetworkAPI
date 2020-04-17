# -*- coding: utf-8 -*-
import json
from itertools import izip

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase
from networkapi.util.geral import prepare_url

fixtures_base_path = 'networkapi/api_network/fixtures/integration/%s'


class NetworksIntegrationV4TestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',

        'networkapi/vlan/fixtures/initial_tipo_rede.json',
        'networkapi/filter/fixtures/initial_filter.json',
        'networkapi/filterequiptype/fixtures/initial_filterequiptype.json',
        'networkapi/equipamento/fixtures/initial_tipo_equip.json',
        'networkapi/equipamento/fixtures/initial_equip_marca.json',
        'networkapi/equipamento/fixtures/initial_equip_model.json',

        fixtures_base_path % 'initial_vrf.json',
        fixtures_base_path % 'initial_environment_dc.json',
        fixtures_base_path % 'initial_environment_envlog.json',
        fixtures_base_path % 'initial_environment_gl3.json',
        fixtures_base_path % 'initial_environment.json',
        fixtures_base_path % 'initial_ipconfig.json',
        fixtures_base_path % 'initial_config_environment.json',
        fixtures_base_path % 'initial_equipments.json',
        fixtures_base_path % 'initial_equipments_env.json',
        fixtures_base_path % 'initial_vlan.json',
        fixtures_base_path % 'initial_cidrs.json',
    ]

    def setUp(self):

        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):

        pass

    def test_create_networkv4_by_zero(self):
        """
        Test of integration for create environment, vlan, eqpt networks v4.

        ##################
        Starting test:
            - environment A:
                - eqpt 1, 2, 3
                - vrf 1
                - starting vlans 1,2,3
            - environment B:
                - eqpt 2, 4, 5
                - vrf 1
                - starting vlans 4, 5, 6, 7, 8, 9
            - environment C:
                - EQpt 5, 6
                - vrf 2
                - startinG vlans 10, 11
            - environment D:
                - eqpt 7
                - vrf 1
                - starting vlans 1
        ##################

        ##################
        Starting networks:
            environment A:
                Nothing
            environment B:
                10.0.1.0/24
                10.0.2.0/25
                10.0.3.0/24
            environment C:
                Nothing
            environment D:
                Nothing
        ##################

        ##################
        Inserting networks without octs:
            - environment B: Expected 10.0.0.0/24
            - environment C: Expected 10.0.0.0/25
            - environment C using prefix 24: Expected 10.0.1.0/24
            - environment A: Expected 10.0.2.128/25
            - environment A: Expected 10.0.4.0/25
            - environment B: Expected 10.0.5.0/24
            - environment A: Expected 10.0.4.128/25
            - environment D: Expected 10.0.0.0/24
        ##################

        """

        # Creates networks v4 with octs
        self.create_netv4_with_octs()

        # Creates networks with auto octs and prefix
        self.create_netv4_without_octs()

    def create_networkv4s(self, netv4_dict):

        response = self.client.post(
            '/api/v3/networkv4/',
            data=json.dumps({'networks': netv4_dict}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization
        )

        return response.data

    def search_all_vlans(self, ids_env):
        search_vlan = {
            'start_record': 0,
            'end_record': 100,
            'asorting_cols': [],
            'searchable_columns': [],
            'extends_search': [
                {'ambiente': id_env} for id_env in ids_env
            ]
        }

        url = '/api/v3/vlan/'

        response = self.client.get(
            prepare_url(url, search=search_vlan, fields=['id']),
            HTTP_AUTHORIZATION=self.authorization
        )

        vlans = response.data['vlans']

        ids_vlans = [id_vlan['id'] for id_vlan in vlans]

        return ids_vlans

    def create_netv4_with_octs(self):
        """Creates networks v4 using first vlan."""

        networks = [{
            'oct1': 10,
            'oct2': 0,
            'oct3': 1,
            'oct4': 0,
            'prefix': 24,
            'env': 3
        }, {
            'oct1': 10,
            'oct2': 0,
            'oct3': 2,
            'oct4': 0,
            'prefix': 25,
            'env': 3
        }, {
            'oct1': 10,
            'oct2': 0,
            'oct3': 3,
            'oct4': 0,
            'prefix': 24,
            'env': 3
        }]

        fields = [
            'oct1',
            'oct2',
            'oct3',
            'oct4',
            'prefix',
            'vlan'
        ]
        for network_send in networks:

            # Get all vlans of environment
            ids_vlans = self.search_all_vlans([network_send.get('env')])

            del network_send['env']

            # Creates networks v4
            network_send['vlan'] = ids_vlans[0]
            network = [{
                'oct1': network_send.get('oct1'),
                'oct2': network_send.get('oct2'),
                'oct3': network_send.get('oct3'),
                'oct4': network_send.get('oct4'),
                'prefix': network_send.get('prefix'),
                'vlan': network_send.get('vlan'),
                'network_type': 3,
                'environmentvip': None
            }]

            id_network = self.create_networkv4s(network)[0]['id']

            # Get object created
            url = '/api/v3/networkv4/%s/' % id_network
            url = prepare_url(url, fields=fields)
            response = self.client.get(
                url, HTTP_AUTHORIZATION=self.authorization
            )

            # Verify if object is right
            self.compare_values(
                json.dumps(network_send, sort_keys=True),
                json.dumps(response.data['networks'][0], sort_keys=True)
            )

    def create_netv4_without_octs(self):

        networks = [
            {
                'prefix': None,
                'env': 3,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': 4,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': 24,
                'env': 4,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': 2,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': 2,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': 3,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': 2,
                'network_type': 3,
                'environmentvip': None
            },
            {
                'prefix': None,
                'env': 5,
                'network_type': 3,
                'environmentvip': None
            }
        ]

        expected_networks = [
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 0,
                'prefix': 24,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 0,
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 0,
                'prefix': 25,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 128,
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 1,
                'oct4': 0,
                'prefix': 24,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 0,
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 2,
                'oct4': 128,
                'prefix': 25,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 128
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 4,
                'oct4': 0,
                'prefix': 25,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 128
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 5,
                'oct4': 0,
                'prefix': 24,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 0
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 4,
                'oct4': 128,
                'prefix': 25,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 128
            },
            {
                'oct1': 10,
                'oct2': 0,
                'oct3': 0,
                'oct4': 0,
                'prefix': 24,
                'mask_oct1': 255,
                'mask_oct2': 255,
                'mask_oct3': 255,
                'mask_oct4': 0
            }
        ]

        fields = [
            'oct1',
            'oct2',
            'oct3',
            'oct4',
            'prefix',
            'mask_oct1',
            'mask_oct2',
            'mask_oct3',
            'mask_oct4',
            'vlan',
        ]
        for network_send, expected_network in izip(networks, expected_networks):

            # Get all vlans of environment
            ids_vlans = self.search_all_vlans([network_send.get('env')])

            # Creates networks v4
            network_send['vlan'] = ids_vlans[0]
            expected_network['vlan'] = ids_vlans[0]

            id_network = self.create_networkv4s([network_send])[0]['id']

            # Get object created
            url = '/api/v3/networkv4/%s/' % id_network
            url = prepare_url(url, fields=fields)
            response = self.client.get(
                url, HTTP_AUTHORIZATION=self.authorization
            )

            # Verify if object is right
            self.compare_values(
                json.dumps(expected_network, sort_keys=True),
                json.dumps(response.data['networks'][0], sort_keys=True)
            )
